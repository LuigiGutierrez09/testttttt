# Proyecto ML Básico — Pre · Dummy · Post

Este proyecto implementa una estructura base de Machine Learning siguiendo el enunciado del Word:

1. Preprocesamiento
2. Entrenamiento Dummy
3. Posprocesamiento

El objetivo es tener un pipeline reproducible, modular y fácil de ejecutar en local.

---

## Estructura del proyecto

```text
proyecto_ml_word_actual/
├── README.md
├── requirements.txt
├── pyproject.toml
├── conda.yml
├── main.py
├── preprocessing.py
├── training.py
├── postprocessing.py
├── data/
│   └── Data_CU_venta.csv
├── outputs/
│   └── resultados.csv        # Se genera al ejecutar el pipeline
└── notebooks/
    └── 1_Preprocessing_ventas.ipynb
```

---

## Dataset usado

El dataset usado es:

```text
data/Data_CU_venta.csv
```

Columnas principales usadas por el pipeline:

- `target`: variable objetivo.
- `monto`: valor usado para la puntuación.
- `prob_value`: probabilidad usada en el scoring final.
- `grp_camptottlv06m`: grupo de campaña original.
- `key_value`: identificador del cliente.

Durante el preprocesamiento se crean columnas estándar para cumplir con el Word:

- `grp_campana` desde `grp_camptottlv06m`.
- `contactabilidad` desde `prob_value`.

---

## Instalación con pip

Crear entorno virtual:

```bash
python -m venv .venv
```

Activar entorno en Windows:

```bash
.venv\Scripts\activate
```

Activar entorno en Linux/macOS:

```bash
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

---

## Instalación con conda

```bash
conda env create -f conda.yml
conda activate proyecto_ml_basico
```

---

## Ejecución

Desde la carpeta del proyecto ejecutar:

```bash
python main.py
```

El pipeline realiza lo siguiente:

1. Lee `data/Data_CU_venta.csv`.
2. Estandariza columnas necesarias para el pipeline.
3. Imputa valores nulos.
4. Codifica variables categóricas.
5. Escala variables numéricas.
6. Entrena un modelo dummy.
7. Calcula una puntuación de prioridad.
8. Exporta resultados en `outputs/resultados.csv`.

---

## Fórmula de posprocesamiento

```text
puntuacion = prob * contactabilidad * log(monto + 1) * frescura
```

Donde:

- `prob`: se toma de `prob_value` del dataset.
- `contactabilidad`: se crea desde `prob_value`.
- `monto`: valor potencial del cliente.
- `frescura`: factor asociado al grupo de campaña.

---

## Archivos principales

### `main.py`

Orquesta todo el flujo. Importa los módulos y ejecuta las etapas en orden.

### `preprocessing.py`

Carga datos, estandariza columnas, trata nulos, codifica categóricas y escala variables numéricas.

### `training.py`

Entrena un modelo dummy que predice siempre la clase mayoritaria.

### `postprocessing.py`

Calcula el score final, asigna grupos de prioridad y exporta los resultados.

---

## Nota

El modelo dummy no busca ser el mejor modelo. Sirve como baseline para validar que el pipeline completo funciona de inicio a fin.
