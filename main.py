import pandas as pd
from pathlib import Path

def load_odds_excel(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    df = pd.read_excel(path)
    df = df[["event_id", "market_type", "outcome", "odds", "source"]].copy()
    df["event_id"] = df["event_id"].astype(str)
    df["market_type"] = df["market_type"].astype(str)
    df["outcome"] = df["outcome"].astype(str)
    df["source"] = df["source"].astype(str)
    df["odds"] = df["odds"].astype(float)
    return df

def find_surebets(df: pd.DataFrame, bankroll: float = 1000.0, min_edge: float = 0.0) -> list[dict]:
    results = []
    grouped = df.groupby(["event_id", "market_type"])
    for (event_id, market_type), group in grouped:
        best_rows = group.loc[group.groupby("outcome")["odds"].idxmax()]
        if best_rows.shape[0] < 2:
            continue
        odds = best_rows["odds"].values
        S = (1.0 / odds).sum()
        if S < 1.0:
            edge = 1.0 - S
            if edge < min_edge:
                continue
            payout = bankroll / S
            profit = payout - bankroll
            stakes = bankroll / (odds * S)
            legs = []
            for i, (_, row) in enumerate(best_rows.iterrows()):
                legs.append({
                    "outcome": row["outcome"],
                    "odds": float(row["odds"]),
                    "source": row["source"],
                    "stake": float(stakes[i]),
                })
            results.append({
                "event_id": event_id,
                "market_type": market_type,
                "edge": float(edge),
                "profit_abs": float(profit),
                "profit_pct": float(profit / bankroll),
                "bankroll": bankroll,
                "legs": legs,
            })
    return results

def main():
    excel_path = "table1.xlsx"
    bankroll = 1000.0
    df = load_odds_excel(excel_path)
    surebets = find_surebets(df, bankroll=bankroll, min_edge=0.0005)
    if not surebets:
        print("Арбитражей не найдено.")
        return
    for arb in surebets:
        print("=" * 60)
        print(f"Событие: {arb['event_id']} | Рынок: {arb['market_type']}")
        print(f"Edge: {arb['edge']*100:.3f}% | Профит: {arb['profit_abs']:.2f} ({arb['profit_pct']*100:.3f}%)")
        for leg in arb["legs"]:
            print(f"  - {leg['outcome']} @ {leg['odds']} в {leg['source']}: ставка {leg['stake']:.2f}")

if __name__ == "__main__":
    main()
