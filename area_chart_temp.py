import pandas as pd
from pathlib import Path

# ---------- CONFIG ----------
INPUT_PATH = Path("Dataset") / "produccio_vs_fertilitzant_ajustada.csv"
OUTPUT_PATH = Path("Dataset") / "mean_yield_per_ha_by_temp.csv"

TEMP_COL = "temp_mitjana_4_periodes"
NURSERY_COL = "Nursery"
YIELD_PER_HA_COL = "YeldPerHectarea"
# ----------------------------


def to_numeric(s: pd.Series) -> pd.Series:
    if s.dtype == object:
        s = s.astype(str).str.strip().str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce")


def main():
    df = pd.read_csv(INPUT_PATH)

    # Validacions
    needed = [TEMP_COL, NURSERY_COL, YIELD_PER_HA_COL]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(
            f"Falten columnes requerides: {missing}\n"
            f"Columnes disponibles: {list(df.columns)}"
        )

    # Preparació de dades
    df[TEMP_COL] = to_numeric(df[TEMP_COL])
    df[YIELD_PER_HA_COL] = to_numeric(df[YIELD_PER_HA_COL])
    df[NURSERY_COL] = df[NURSERY_COL].astype(str).str.strip().str.lower()

    # Filtrar només dry / wet i dades vàlides
    df = df[df[NURSERY_COL].isin(["dry", "wet"])]
    df = df.dropna(subset=[TEMP_COL, YIELD_PER_HA_COL])

    # Mitjana per temperatura i regadiu
    grouped = (
        df.groupby([TEMP_COL, NURSERY_COL])[YIELD_PER_HA_COL]
        .mean()
        .reset_index()
    )

    # Rotació de columnes segons regadiu
    pivoted = (
        grouped.pivot(index=TEMP_COL, columns=NURSERY_COL, values=YIELD_PER_HA_COL)
        .reset_index()
        .rename(columns={
            "dry": "meanYeld_Dry",
            "wet": "meanYeld_Wet",
            TEMP_COL: TEMP_COL
        })
        .sort_values(by=TEMP_COL)
    )

    # Guardar CSV
    pivoted.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    print("CSV creat:", OUTPUT_PATH.resolve())
    print("Files:", len(pivoted))
    print("\nMostra:")
    print(pivoted.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
