"""Módulo de entrenamiento dummy."""

import pandas as pd


TARGET_COL = "target"
ID_COL = "key_value"


def split_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Separa variables explicativas X y variable objetivo y."""
    if TARGET_COL not in df.columns:
        raise ValueError(f"La columna objetivo '{TARGET_COL}' no existe en el dataset.")

    drop_cols = [TARGET_COL]
    if ID_COL in df.columns:
        drop_cols.append(ID_COL)

    X = df.drop(columns=drop_cols)
    y = df[TARGET_COL]
    return X, y


def build_dummy_model(y: pd.Series) -> int | float | str:
    """Obtiene la clase más frecuente para usarla como predicción constante."""
    return y.mode().iloc[0]


def train_dummy(df: pd.DataFrame) -> tuple[int | float | str, pd.Series]:
    """
    Entrena un modelo dummy.

    Este modelo no aprende patrones reales: siempre predice la clase mayoritaria.
    Sirve como baseline para validar que el pipeline corra de inicio a fin.
    """
    X, y = split_data(df)
    model = build_dummy_model(y)

    predictions = pd.Series([model] * len(X), index=X.index, name="y_pred_dummy")

    accuracy = (predictions == y).mean()
    print(f"Modelo dummy: predice siempre -> {model}")
    print(f"Total predicciones: {len(predictions)}")
    print(f"Accuracy dummy: {accuracy:.4f}")

    return model, predictions
