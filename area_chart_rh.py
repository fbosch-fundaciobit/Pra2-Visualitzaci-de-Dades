import pandas as pd
from pathlib import Path

INPUT_PATH = Path("Dataset") / "produccio_vs_fertilitzant_ajustada.csv"
OUTPUT_PATH = Path("Dataset") / "mean_yield_per_ha_by_rh.csv"

RH_COL = "rh_mitjana_4_periodes"
NURSERY_COL = "Nursery"
YIELD_PER_HA_COL = "YeldPerHectarea"


def to_numeric(s: pd.Series) -> pd.Series:
    if s.dtype == object:
        s = s.astype(str).str.strip().str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce")


def main():
    df = pd.read_csv(INPUT_PATH)

    needed = [RH_COL, NURSERY_COL, YIELD_PER_HA_COL]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(
            f"Falten columnes requerides: {missing}\n"
            f"Columnes disponibles: {list(df.columns)}"
        )

    # Neteja bàsica
    df[RH_COL] = to_numeric(df[RH_COL])
    df[YIELD_PER_HA_COL] = to_numeric(df[YIELD_PER_HA_COL])
    df[NURSERY_COL] = df[NURSERY_COL].astype(str).str.strip().str.lower()

    df = df[df[NURSERY_COL].isin(["dry", "wet"])].dropna(subset=[RH_COL, YIELD_PER_HA_COL])

    # Mitjana per humitat i tipus de regadiu
    grouped = (
        df.groupby([RH_COL, NURSERY_COL])[YIELD_PER_HA_COL]
        .mean()
        .reset_index()
    )

    # Rotacio de files i columnes per tipus de regadiu.
    pivoted = (
        grouped.pivot(index=RH_COL, columns=NURSERY_COL, values=YIELD_PER_HA_COL)
        .reset_index()
        .rename(columns={
            "dry": "meanYeld_Dry",
            "wet": "meanYeld_Wet",
            RH_COL: RH_COL
        })
        .sort_values(by=RH_COL)
    )

    pivoted.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    print("CSV creat:", OUTPUT_PATH.resolve())
    print("Files:", len(pivoted))
    print("\nMostra:")
    print(pivoted.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
