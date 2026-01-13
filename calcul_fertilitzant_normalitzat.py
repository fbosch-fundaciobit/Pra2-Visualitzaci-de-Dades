import pandas as pd
from pathlib import Path

INPUT_PATH = Path("Dataset") / "paddydataset.csv"
OUTPUT_PATH = Path("Dataset") / "paddydataset_fert_normalitzat.csv"

# Columnes de fertilitzants
FERTILIZER_COLS = [
    "Urea_40Days",
    "DAP_20days",
    "Potassh_50Days",
    "Micronutrients_70Days"
]

# Columnes que vols assegurar que queden al resultat
REQUIRED_COLS = [
    "Nursery",
    "Nursery area (Cents)"
]

# Columnes per calcular mitjanes per període
TEMP_MIN_COLS = ["Min temp_D1_D30", "Min temp_D31_D60", "Min temp_D61_D90", "Min temp_D91_D120"]
TEMP_MAX_COLS = ["Max temp_D1_D30", "Max temp_D31_D60", "Max temp_D61_D90", "Max temp_D91_D120"]

RH_COLS = [
    "Relative Humidity_D1_D30",
    "Relative Humidity_D31_D60",
    "Relative Humidity_D61_D90",
    "Relative Humidity_D91_D120",
]

WIND_COLS = [
    "Inst Wind Speed_D1_D30(in Knots)",
    "Inst Wind Speed_D31_D60(in Knots)",
    "Inst Wind Speed_D61_D90(in Knots)",
    "Inst Wind Speed_D91_D120(in Knots)",
]

NORMALIZED_COL = "fertilitzant_normalitzat"

NEW_COL_TEMP = "temp_mitjana_4_periodes"
NEW_COL_RH = "rh_mitjana_4_periodes"
NEW_COL_WIND = "vent_mitja_4_periodes"
# ----------------------------


def to_numeric(series: pd.Series) -> pd.Series:
    if series.dtype == object:
        series = (
            series.astype(str)
            .str.strip()
            .str.replace(",", ".", regex=False)
        )
    return pd.to_numeric(series, errors="coerce")

#Normalitzacio segons valors min-max
def min_max_normalize(series: pd.Series) -> pd.Series:
    min_val = series.min()
    max_val = series.max()

    if pd.isna(min_val) or pd.isna(max_val) or min_val == max_val:
        return pd.Series(0.0, index=series.index)

    return (series - min_val) / (max_val - min_val)


def main():
    df = pd.read_csv(INPUT_PATH)

    missing_required = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing_required:
        raise ValueError(
            "Falten columnes requerides al dataset:\n"
            f"{missing_required}\n"
            f"Columnes disponibles: {list(df.columns)}"
        )

    # Verificar de columnes
    fert_cols = [c for c in FERTILIZER_COLS if c in df.columns]
    if not fert_cols:
        raise ValueError(
            "No s'ha trobat cap columna de fertilitzant esperada.\n"
            f"Columnes disponibles: {list(df.columns)}"
        )

    for col in fert_cols:
        df[col] = to_numeric(df[col])

    for col in (TEMP_MIN_COLS + TEMP_MAX_COLS + RH_COLS + WIND_COLS):
        if col in df.columns:
            df[col] = to_numeric(df[col])

    # Normalitzar fertilitzants
    normalized_ferts = []
    for col in fert_cols:
        norm_col = f"{col}_norm"
        df[norm_col] = min_max_normalize(df[col])
        normalized_ferts.append(norm_col)

    # Sumar fertilitzants normalitzats
    df[NORMALIZED_COL] = df[normalized_ferts].sum(axis=1)

    # Eliminar columnes intermèdies *_norm
    df.drop(columns=normalized_ferts, inplace=True)

    
    # Afegir columnes amb mitjana de temperatura dels 4 periodes.
    if all(c in df.columns for c in TEMP_MIN_COLS + TEMP_MAX_COLS):
        period_means = []
        for min_c, max_c in zip(TEMP_MIN_COLS, TEMP_MAX_COLS):
            period_means.append((df[min_c] + df[max_c]) / 2)
        df[NEW_COL_TEMP] = pd.concat(period_means, axis=1).mean(axis=1)
    else:
        df[NEW_COL_TEMP] = pd.NA

    # Humitat relativa mitjana
    if all(c in df.columns for c in RH_COLS):
        df[NEW_COL_RH] = df[RH_COLS].mean(axis=1)
    else:
        df[NEW_COL_RH] = pd.NA

    # Vent mitjà
    if all(c in df.columns for c in WIND_COLS):
        df[NEW_COL_WIND] = df[WIND_COLS].mean(axis=1)
    else:
        df[NEW_COL_WIND] = pd.NA

    # Guardar nou CSV (df ja conté Nursery i Nursery area perquè no hem filtrat columnes)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    # Resum
    print("Nova columna afegida:", NORMALIZED_COL)
    print("Columnes climàtiques afegides:", [NEW_COL_TEMP, NEW_COL_RH, NEW_COL_WIND])
    print("S'asseguren al resultat:", REQUIRED_COLS)
    print("Fertilitzants utilitzats:", fert_cols)
    print("Fitxer guardat a:", OUTPUT_PATH.resolve())

    print("\nEstadístiques bàsiques del fertilitzant normalitzat:")
    print(df[NORMALIZED_COL].describe())


if __name__ == "__main__":
    main()
