

from pathlib import Path

import postprocessing as post
import preprocessing as pp
import training as tr


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "Data_CU_venta.csv"
OUTPUT_PATH = BASE_DIR / "outputs" / "resultados.csv"


def main() -> None:
    """Ejecuta el pipeline completo de Machine Learning básico."""
    # 1. Cargar y preprocesar datos
    df_raw = pp.load_data(DATA_PATH)
    df_processed = pp.preprocess(df_raw)

    # 2. Entrenar modelo dummy
    model, predictions = tr.train_dummy(df_processed)

    # 3. Posprocesar resultados y exportar archivo final
    results = post.postprocess(df_processed, predictions)
    post.export_results(results, OUTPUT_PATH)

    print("\nPipeline finalizado correctamente.")
    print(f"Modelo dummy usado: {model}")
    print(f"Archivo generado: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
