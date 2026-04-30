"""Módulo de posprocesamiento: scoring y segmentación."""

from pathlib import Path

import numpy as np
import pandas as pd


# Factor de frescura según grupo de campaña.
FRESCURA_MAP = {
    "G1": 0.066,
    "G2": 0.028,
    "G3": 0.022,
    "G4": 0.008,
}
FRESCURA_DEFAULT = 0.004
OUTPUT_PATH = Path("outputs") / "resultados.csv"


def assign_frescura(df: pd.DataFrame, col: str = "grp_campana") -> pd.Series:
    """Mapea el grupo de campaña al factor de frescura."""
    if col not in df.columns:
        raise ValueError(f"Falta la columna requerida: {col}")

    return df[col].map(FRESCURA_MAP).fillna(FRESCURA_DEFAULT)


def get_probability(df: pd.DataFrame, predictions: pd.Series) -> pd.Series:
    """Obtiene la probabilidad usada para el score final."""
    if "prob_value" in df.columns:
        return df["prob_value"].astype(float).clip(0, 1)

    # Si no existe prob_value, se usa la salida del dummy como probabilidad simple.
    return predictions.astype(float).clip(0, 1)


def compute_score(df: pd.DataFrame, prob: pd.Series) -> pd.Series:
    """
    Calcula la puntuación compuesta.

    Fórmula:
        puntuacion = prob * contactabilidad * log(monto + 1) * frescura
    """
    required_cols = ["contactabilidad", "monto", "grp_campana"]
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise ValueError(f"Faltan columnas para posprocesamiento: {missing_cols}")

    frescura = assign_frescura(df)
    contactabilidad = df["contactabilidad"].astype(float).fillna(0.000001).clip(0, 1)
    monto = df["monto"].astype(float).clip(lower=0)

    puntuacion = prob * contactabilidad * np.log(monto + 1) * frescura
    return puntuacion


def segment_groups(puntuacion: pd.Series, n_groups: int = 5) -> pd.Series:
    """Segmenta la puntuación en grupos de prioridad. 1 es mayor prioridad."""
    ranking = puntuacion.rank(method="first")
    labels = list(range(n_groups, 0, -1))

    return pd.qcut(ranking, q=n_groups, labels=labels)


def postprocess(df: pd.DataFrame, predictions: pd.Series) -> pd.DataFrame:
    """Ejecuta el pipeline completo de posprocesamiento."""
    result = df.copy()

    # Se conserva la salida del modelo dummy para evidenciar la etapa de entrenamiento.
    result["y_pred_dummy"] = predictions.values

    # El dataset real trae prob_value; esa probabilidad alimenta la fórmula del Word.
    result["prob"] = get_probability(result, predictions)
    result["puntuacion"] = compute_score(result, result["prob"])
    result["grupo_prioridad"] = segment_groups(result["puntuacion"])
    result = result.sort_values("puntuacion", ascending=False)

    print("Distribución de grupos de prioridad:")
    print(result["grupo_prioridad"].value_counts().sort_index())

    return result


def export_results(results: pd.DataFrame, path: str | Path = OUTPUT_PATH) -> None:
    """Exporta el resultado final del pipeline a un archivo CSV."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    results.to_csv(path, index=False)
    print(f"Resultados exportados a: {path}")
