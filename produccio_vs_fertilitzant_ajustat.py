import pandas as pd
from pathlib import Path

# ---------- CONFIG ----------
INPUT_PATH = Path("Dataset") / "produccio_vs_fertilitzant.csv"
OUTPUT_PATH = Path("Dataset") / "produccio_vs_fertilitzant_ajustada.csv"

YIELD_PER_HA_COL = "YeldPerHectarea"
FERT_COL = "fertilitzant_normalitzat"
ADJUSTED_COL = "YeldPerHa_ajustada"

TOTAL_EFFECT = 0.05      # 5% d'increment total (0 -> 4)
STEP_FACTOR = 0.25       # cada pas de fertilitzant aporta un 25%

# Columnes que volem conservar
EXTRA_KEEP_COLS = [
    "Nursery",
    "Nursery area (Cents)",
    "temp_mitjana_4_periodes",
    "rh_mitjana_4_periodes",
    "vent_mitja_4_periodes",
]
# ----------------------------


def to_numeric(series: pd.Series) -> pd.Series:
    if series.dtype == object:
        series = (
            series.astype(str)
            .str.strip()
            .str.replace(",", ".", regex=False)
        )
    return pd.to_numeric(series, errors="coerce")


def get_temperature_and_humidity_cols(df: pd.DataFrame) -> list[str]:
    temp_cols = [c for c in df.columns if c.startswith("Min temp_") or c.startswith("Max temp_")]
    hum_cols = [c for c in df.columns if c.startswith("Relative Humidity_")]
    return sorted(temp_cols) + sorted(hum_cols)


def existing_cols(df: pd.DataFrame, candidates: list[str]) -> list[str]:
    return [c for c in candidates if c in df.columns]


def main():
    df = pd.read_csv(INPUT_PATH)

    # Validacions bàsiques
    missing = [c for c in [YIELD_PER_HA_COL, FERT_COL] if c not in df.columns]
    if missing:
        raise ValueError(
            f"Falten columnes requerides al CSV d'entrada: {missing}\n"
            f"Columnes disponibles: {list(df.columns)}"
        )

    df[YIELD_PER_HA_COL] = to_numeric(df[YIELD_PER_HA_COL])
    df[FERT_COL] = to_numeric(df[FERT_COL])

    # Eliminar files amb valors nuls
    df = df.dropna(subset=[YIELD_PER_HA_COL, FERT_COL]).reset_index(drop=True)

    # Afegir columna ID per numerar files
    df.insert(0, "id", df.index + 1)

    # Aplicar la fórmula d'ajust
    df[ADJUSTED_COL] = (
        df[YIELD_PER_HA_COL] - (df[YIELD_PER_HA_COL] * TOTAL_EFFECT * df[FERT_COL] * STEP_FACTOR)
    )

    # Informatiu
    env_cols = get_temperature_and_humidity_cols(df)
    kept_extra = existing_cols(df, EXTRA_KEEP_COLS)

    # Guardar CSV
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    print("Columna creada:", ADJUSTED_COL)
    print("Afegida columna ID per numerar les files.")
    print("Fitxer guardat a:", OUTPUT_PATH.resolve())
    print("Columnes extra conservades:", kept_extra)
    print("Columnes de temperatura + humitat conservades:", len(env_cols))
    print("\nMostra de valors:")
    print(df[["id", YIELD_PER_HA_COL, FERT_COL, ADJUSTED_COL]].head())


if __name__ == "__main__":
    main()
