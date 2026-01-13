import pandas as pd
from pathlib import Path

INPUT_PATH = Path("Dataset") / "paddydataset_fert_normalitzat.csv"
OUTPUT_PATH = Path("Dataset") / "produccio_vs_fertilitzant.csv"

YIELD_COL = "Paddy yield(in Kg)"
HECTARES_COL = "Hectares"
YIELD_PER_HA_COL = "YeldPerHectarea"
FERT_COL = "fertilitzant_normalitzat"

# Columnes addicionals per identificar files
ID_CANDIDATES = ["Variety", "Soil Types"]

EXTRA_KEEP_COLS = [
    "Nursery",
    "Nursery area (Cents)",
    "temp_mitjana_4_periodes",
    "rh_mitjana_4_periodes",
    "vent_mitja_4_periodes",
]
# ----------------------------

#Converió a valor numèric
def to_numeric(series: pd.Series) -> pd.Series:
    if series.dtype == object:
        series = series.astype(str).str.strip().str.replace(",", ".", regex=False)
    return pd.to_numeric(series, errors="coerce")

# Crear YeldPerHectarea si no existeix
def ensure_yield_per_ha(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if YIELD_PER_HA_COL in df.columns:
        return df

    if YIELD_COL not in df.columns or HECTARES_COL not in df.columns:
        return df

    df[YIELD_COL] = to_numeric(df[YIELD_COL])
    df[HECTARES_COL] = to_numeric(df[HECTARES_COL])

    ha = df[HECTARES_COL].where(df[HECTARES_COL] != 0)
    df[YIELD_PER_HA_COL] = df[YIELD_COL] / ha
    return df


def existing_cols(df: pd.DataFrame, candidates: list[str]) -> list[str]:
    return [c for c in candidates if c in df.columns]

#Agafa totes les columnes de temperatura i humitat segons els noms del dataset.
def get_temperature_and_humidity_cols(df: pd.DataFrame) -> list[str]:
    temp_cols = [c for c in df.columns if c.startswith("Min temp_") or c.startswith("Max temp_")]
    hum_cols = [c for c in df.columns if c.startswith("Relative Humidity_")]

    return sorted(temp_cols) + sorted(hum_cols)


def main():
    df = pd.read_csv(INPUT_PATH)
    missing = [c for c in [YIELD_COL, FERT_COL] if c not in df.columns]
    if missing:
        raise ValueError(
            f"Falten columnes requerides al fitxer d'entrada: {missing}\n"
            f"Columnes disponibles: {list(df.columns)}"
        )

    df[YIELD_COL] = to_numeric(df[YIELD_COL])
    df[FERT_COL] = to_numeric(df[FERT_COL])

    df = ensure_yield_per_ha(df)

    id_cols = existing_cols(df, ID_CANDIDATES)
    if HECTARES_COL in df.columns:
        id_cols.append(HECTARES_COL)

    extra_cols = [YIELD_PER_HA_COL] if YIELD_PER_HA_COL in df.columns else []

    # Afegir totes les columnes de temperatura i humitat
    env_cols = get_temperature_and_humidity_cols(df)

    # Conservar les columnes addicionals
    keep_cols = existing_cols(df, EXTRA_KEEP_COLS)

    # Subset final de columnes
    cols = id_cols + keep_cols + [YIELD_COL] + extra_cols + [FERT_COL] + env_cols

    # Eliminar duplicats mantenint ordre
    seen = set()
    cols = [c for c in cols if c in df.columns and not (c in seen or seen.add(c))]

    out = df[cols].copy()

    # Eliminar files sense dades
    base_required = [YIELD_COL, FERT_COL]
    if YIELD_PER_HA_COL in out.columns:
        base_required.append(YIELD_PER_HA_COL)

    out = out.dropna(subset=base_required)

    # Guardar
    out.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    print("CSV generat:", OUTPUT_PATH.resolve())
    print("Files:", len(out), "| Columnes:", len(out.columns))
    print("Columnes temperatura/humitat afegides:", len(env_cols))
    print("Columnes extra conservades:", keep_cols)


if __name__ == "__main__":
    main()
