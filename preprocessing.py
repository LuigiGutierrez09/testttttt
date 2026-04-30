"""Módulo de preprocesamiento de datos."""

from pathlib import Path

import pandas as pd


TARGET_COL = "target"
ID_COL = "key_value"
PROB_COL = "prob_value"
MONTO_COL = "monto"
GROUP_SOURCE_COL = "grp_camptottlv06m"


def load_data(path: str | Path) -> pd.DataFrame:
    """Carga el dataset desde la ruta indicada."""
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {path}")

    return pd.read_csv(path, low_memory=False)


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Crea nombres estándar usados por las siguientes etapas del pipeline."""
    df = df.copy()

    # El Word pide usar monto, contactabilidad y grp_campana en el postproceso.
    # En el dataset real, la columna de grupo viene como grp_camptottlv06m.
    if GROUP_SOURCE_COL in df.columns and "grp_campana" not in df.columns:
        df["grp_campana"] = df[GROUP_SOURCE_COL]

    # El dataset real trae prob_value; la usamos como contactabilidad base.
    if PROB_COL in df.columns and "contactabilidad" not in df.columns:
        df["contactabilidad"] = df[PROB_COL]

    return df


def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Imputa valores nulos con reglas simples y entendibles."""
    df = df.copy()

    numeric_cols = df.select_dtypes(include="number").columns
    object_cols = df.select_dtypes(include="object").columns

    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())

    for col in object_cols:
        mode_value = df[col].mode(dropna=True)
        fill_value = mode_value.iloc[0] if not mode_value.empty else "desconocido"
        df[col] = df[col].fillna(fill_value)

    return df


def encode_features(df: pd.DataFrame) -> pd.DataFrame:
    """Codifica variables categóricas usando one-hot encoding."""
    df = df.copy()

    # Se conservan columnas de ID y grupo porque se usan o se reportan después.
    protected_cols = [ID_COL, "grp_campana", GROUP_SOURCE_COL]
    categorical_cols = [
        col for col in df.select_dtypes(include="object").columns
        if col not in protected_cols
    ]

    if categorical_cols:
        df = pd.get_dummies(df, columns=categorical_cols, drop_first=False)

    return df


def scale_features(df: pd.DataFrame) -> pd.DataFrame:
    """Escala columnas numéricas con min-max simple."""
    df = df.copy()

    # Estas columnas se mantienen en escala original porque se usan en training/post.
    exclude_cols = [
        TARGET_COL,
        MONTO_COL,
        PROB_COL,
        "contactabilidad",
        "p_codmes",
    ]

    numeric_cols = [
        col for col in df.select_dtypes(include="number").columns
        if col not in exclude_cols
    ]

    for col in numeric_cols:
        min_value = df[col].min()
        max_value = df[col].max()

        if max_value != min_value:
            df[col] = (df[col] - min_value) / (max_value - min_value)
        else:
            df[col] = 0

    return df


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Ejecuta el pipeline completo de preprocesamiento."""
    df = standardize_columns(df)
    df = handle_missing(df)
    df = encode_features(df)
    df = scale_features(df)
    return df
