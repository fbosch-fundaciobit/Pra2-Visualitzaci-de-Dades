import pandas as pd
from pathlib import Path

INPUT_PATH = Path("Dataset") / "produccio_vs_fertilitzant_ajustada.csv"
OUTPUT_PATH = Path("Dataset") / "yeld_temp_by_variety.csv"

GROUP_COL = "Variety"
YIELD_ADJ_COL = "YeldPerHa_ajustada"

# Columnes de temperatura per als 4 periodes
MIN_EARLY_COL = "Min temp_D1_D30"
MAX_EARLY_COL = "Max temp_D1_D30"
MIN_LATE_COL  = "Min temp_D91_D120"
MAX_LATE_COL  = "Max temp_D91_D120"

# Valors minims i maxims objectiu
TARGETS = {
    "Mean_YeldPerHa_adj_min_early_18C": (MIN_EARLY_COL, 18),
    "Mean_YeldPerHa_adj_max_early_35C": (MAX_EARLY_COL, 35),
    "Mean_YeldPerHa_adj_min_late_15C":  (MIN_LATE_COL, 15),
    "Mean_YeldPerHa_adj_max_late_35C":  (MAX_LATE_COL, 35),
}
# ----------------------------


def to_numeric(s: pd.Series) -> pd.Series:
    if s.dtype == object:
        s = s.astype(str).str.strip().str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce")


def mean_by_variety_on_temp(df: pd.DataFrame, temp_col: str, temp_value: float) -> pd.DataFrame:
    d = df[[GROUP_COL, YIELD_ADJ_COL, temp_col]].copy()
    d[YIELD_ADJ_COL] = to_numeric(d[YIELD_ADJ_COL])
    d[temp_col] = to_numeric(d[temp_col])
    d = d.dropna(subset=[GROUP_COL, YIELD_ADJ_COL, temp_col])
    d = d[d[temp_col] == temp_value]
    return d.groupby(GROUP_COL, as_index=False)[YIELD_ADJ_COL].mean()


def main():
    df = pd.read_csv(INPUT_PATH)

    needed = [GROUP_COL, YIELD_ADJ_COL, MIN_EARLY_COL, MAX_EARLY_COL, MIN_LATE_COL, MAX_LATE_COL]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"Falten columnes requerides: {missing}")

    # Mitjana global de producció ajustada
    base = df[[GROUP_COL, YIELD_ADJ_COL]].copy()
    base[YIELD_ADJ_COL] = to_numeric(base[YIELD_ADJ_COL])
    base = base.dropna(subset=[GROUP_COL, YIELD_ADJ_COL])
    result = (
        base.groupby(GROUP_COL, as_index=False)[YIELD_ADJ_COL]
        .mean()
        .rename(columns={YIELD_ADJ_COL: "Mean_YeldPerHa_ajustada_all"})
    )

    # Mitjanes condicionades segons temperatura exacta
    for out_col, (temp_col, target) in TARGETS.items():
        m = mean_by_variety_on_temp(df, temp_col, target).rename(columns={YIELD_ADJ_COL: out_col})
        result = result.merge(m, on=GROUP_COL, how="left")

    # Ordenar per mitjana global
    result = result.sort_values("Mean_YeldPerHa_ajustada_all", ascending=False).reset_index(drop=True)

    # Guardar
    result.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    print("CSV creat:", OUTPUT_PATH.resolve())
    print("Files:", len(result))
    print(result.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
