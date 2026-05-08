"""
scripts/predict_model.py

Carga el pipeline entrenado (burnout_pipeline.pkl + burnout_labels.pkl)
y realiza predicciones de riesgo de burnout.

Acepta dos modos de entrada:
  - Un solo empleado : dict o JSON con los valores de cada feature.
  - Múltiples empleados: CSV con las mismas columnas de FEATURES.

Retorna por cada muestra:
  - burnout_risk     : clase predicha  (ej: "high")
  - confidence       : probabilidad de la clase predicha
  - probabilities    : probabilidad de cada clase

Uso CLI: (si estas desde backend/ai/)
  # Predecir desde CSV
  python -m scripts.predict_burnout --csv data/new_employees.csv

  # Predecir un empleado desde JSON
  python -m scripts.predict_burnout --json '{"assigned_tasks": 10, "completed_tasks": 7, ...}'

  # Especificar carpeta de modelos
  python -m scripts.predict_burnout --csv data/new_employees.csv --models-dir data/models
"""

import argparse
import json
import logging
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Configuración
MODELS_DIR = Path(__file__).resolve().parents[2] / "ai-service" / "models"

FEATURES = [
    # Datos laborales
    "assigned_tasks", "completed_tasks", "absences",
    "employee_calls", "completion_rate", "seniority_years",
    "rank_index", "group_index",
    # Datos personales
    "age", "gender_enc",
    # Modalidad y sede
    "work_mode_enc", "location_enc",
    # Encuesta MBI-GS
    "avg_agotamiento", "avg_despersonalizacion", "eficacia_invertida",
]


# Carga de artefactos 
def load_artifacts(models_dir: Path) -> tuple:
    """
    Carga el pipeline entrenado y las etiquetas de clase.

    Args:
        models_dir: carpeta donde están los .pkl generados por train_burnout.py.

    Returns:
        pipeline, class_names, le

    Raises:
        FileNotFoundError: si alguno de los .pkl no existe.
    """
    pipeline_path = models_dir / "burnout_pipeline.pkl"
    labels_path   = models_dir / "burnout_labels.pkl"
    encoder_path  = models_dir / "burnout_encoder.pkl"

    for p in (pipeline_path, labels_path, encoder_path):
        if not p.exists():
            raise FileNotFoundError(
                f"Artefacto no encontrado: {p}\n"
                "Ejecuta train_burnout.py primero para generar los modelos."
            )

    pipeline    = joblib.load(pipeline_path)
    class_names = joblib.load(labels_path)
    le          = joblib.load(encoder_path)

    logger.info("Carga de artefactos en : %s", models_dir)

    return pipeline, class_names, le


# Preparación de datos
def prepare_from_dict(employee: dict) -> pd.DataFrame:
    """
    Convierte un dict de un empleado a DataFrame listo para predecir.

    Args:
        employee: dict con al menos las claves de FEATURES.

    Returns:
        DataFrame de una fila con las columnas de FEATURES.

    Raises:
        ValueError: si faltan features requeridos.
    """
    missing = [f for f in FEATURES if f not in employee]
    if missing:
        raise ValueError(f"Features faltantes en el dict: {missing}")

    return pd.DataFrame([employee])[FEATURES].astype(float)


def prepare_from_csv(csv_path: Path) -> pd.DataFrame:
    """
    Carga un CSV con múltiples empleados y lo prepara para predecir.

    Args:
        csv_path: ruta al CSV. Debe contener las columnas de FEATURES.

    Returns:
        DataFrame con las columnas de FEATURES.

    Raises:
        FileNotFoundError: si el archivo no existe.
        ValueError: si faltan columnas requeridas.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV no encontrado: {csv_path}")

    # Detectar separador
    with open(csv_path, encoding="utf-8-sig") as f:
        sample = f.read(2048)
    sep = ";" if sample.count(";") > sample.count(",") else ","

    df = pd.read_csv(csv_path, sep=sep, encoding="utf-8-sig")
    logger.info("CSV cargado: %d filas × %d columnas", *df.shape)

    missing = [f for f in FEATURES if f not in df.columns]
    if missing:
        raise ValueError(f"Columnas faltantes en el CSV: {missing}")

    # Verificar nulos en columnas requeridas
    null_counts = df[FEATURES].isnull().sum()
    null_cols = null_counts[null_counts > 0]
    if not null_cols.empty:
        error_msg = (
            "El archivo contiene valores nulos en columnas requeridas:\n"
            f"{null_cols.to_string()}"
        )

        logger.error(error_msg)
        raise ValueError(error_msg)

    return df[FEATURES].astype(float)


# Predicción
def predict(
    pipeline, class_names: list,
    le: LabelEncoder, X: pd.DataFrame,
) -> list[dict]:
    """
    Realiza predicciones sobre un DataFrame de features.

    Args:
        pipeline: pipeline entrenado (scaler + GaussianNB).
        class_names (list): lista ordenada de nombres de clase.
        le (LabelEncoder): encoder para decodificar las clases predichas.
        X (pd.DataFrame): Con las columnas de FEATURES.

    Returns:
        results (list[dict]): Lista de diccionarios, uno por muestra,
        con keys: burnout_risk, confidence, probabilities. 
    """
    y_pred  = pipeline.predict(X.values)
    y_proba = pipeline.predict_proba(X.values)

    # DEBUG — quitar después
    gnb = pipeline.named_steps["gnb"]
    logger.info("Clases del modelo : %s", gnb.classes_)
    logger.info("class_names cargado: %s", class_names)
    logger.info("y_pred raw: %s", y_pred)
    logger.info("y_proba: %s", y_proba)

    results = []
    for pred, proba in zip(y_pred, y_proba):
        pred_idx = int(np.argmax(proba))          # índice de mayor probabilidad
        cls_name = class_names[pred_idx]   
        results.append({
            "burnout_risk" : cls_name,
            "confidence"   : round(float(proba[pred]), 4),
            "probabilities": {
                class_names[i]: round(float(p), 4)
                for i, p in enumerate(proba)
            },
        })

    return results


# Predicción para empleado(s)
def predict_employee(employee: dict, models_dir: Path = MODELS_DIR) -> dict:
    """
    Predice el riesgo de burnout de un solo empleado.

    Args:
        employee (dict): diccionario con los valores de cada feature.
        models_dir (Path): carpeta con los .pkl del modelo.

    Returns:
        Dict con burnout_risk, confidence y probabilities.
    """
    pipeline, class_names, le = load_artifacts(models_dir)
    X = prepare_from_dict(employee)
    return predict(pipeline, class_names, le, X)[0] # Retorna el dict del primer (y único) empleado


def predict_from_csv(csv_path: str | Path, models_dir: Path = MODELS_DIR) -> list[dict]:
    """
    Predice el riesgo de burnout para todos los empleados de un CSV.

    Args:
        csv_path:   ruta al CSV con columnas de FEATURES.
        models_dir: carpeta con los .pkl del modelo.

    Returns:
        results (list[dict]): Lista de dicts con burnout_risk, confidence y probabilities.
    """
    pipeline, class_names, le = load_artifacts(models_dir)
    X = prepare_from_csv(Path(csv_path))
    results = predict(pipeline, class_names, le, X)
    logger.info("Predicciones completadas: %d muestras", len(results))
    return results


# CLI
if __name__ == "__main__":
    print (MODELS_DIR)
    # Permite leer argumentos desde la terminal para predecir desde CSV o JSON
    parser = argparse.ArgumentParser(description="Predictor de riesgo de burnout")
    # Solo se puede usar alguno de los dos (CSV o JSON)
    group  = parser.add_mutually_exclusive_group(required=True)
    # Definición de parámetros y textos mostrados en --help
    group.add_argument(
        "--csv",
        help="Ruta al CSV con múltiples empleados.",
    )
    group.add_argument(
        "--json",
        help='JSON de un empleado. Ej: \'{"assigned_tasks": 10, ...}\'',
    )
    group.add_argument(
        "--json-file",
        help="Ruta a un archivo .json con los datos del empleado.",
    )
    # Opcional: carpeta de modelos
    parser.add_argument(
        "--models-dir", type=Path, default=MODELS_DIR,
        help=f"Carpeta con los .pkl del modelo (default: {MODELS_DIR}).",
    )
    # Leer lo escrito en la terminal
    args = parser.parse_args()

    # Si se proporcionó un CSV, predecir para cada empleado en el archivo
    if args.csv:
        results = predict_from_csv(args.csv, models_dir=args.models_dir)
        for i, r in enumerate(results):
            logger.info(
                "Empleado %d → %s (conf: %.2f) | probs: %s",
                i, r["burnout_risk"], r["confidence"], r["probabilities"],
            )
    # Sino se proporcionó un CSV, se asumió que se dio un JSON de un solo empleado
    elif args.json_file:
        with open(args.json_file, encoding="utf-8") as f:
            employee = json.load(f)
        result = predict_employee(employee, models_dir=args.models_dir)
        logger.info("Resultado → %s (conf: %.2f) | probs: %s",
                    result["burnout_risk"], result["confidence"], result["probabilities"])
    else:
        employee = json.loads(args.json)
        result   = predict_employee(employee, models_dir=args.models_dir)
        logger.info("Resultado → %s (conf: %.2f) | probs: %s",
                    result["burnout_risk"], result["confidence"], result["probabilities"])
        