"""
scripts/evaluate_burnout.py

Evalúa el pipeline entrenado (burnout_pipeline.pkl) sobre un CSV
que contiene tanto los features como la columna real de burnout_risk.

Métricas generadas:
  - Accuracy, Precision, Recall, F1-Score (weighted)
  - ROC-AUC (OvR weighted para multiclase)
  - Reporte de clasificación completo por clase
  - Matriz de confusión
  - Panel de visualizaciones guardado en PNG

Uso CLI:
  # Evaluación completa
  python -m scripts.evaluate_burnout --csv data/training/training_dataset.csv

  # Evaluación con set de prueba guardado (X_test, y_test)
  python -m scripts.evaluate_burnout --test-pkl ai-service/models/burnout_test_set.pkl
"""

import argparse
import logging
import warnings
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    f1_score, precision_score, recall_score, roc_auc_score,
)

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Configuración
MODELS_DIR = Path(__file__).resolve().parent.parent.parent / \
    "ai-service" / "models"

TARGET = "burnout_risk"

FEATURES = [
    # Datos laborales
    "assigned_tasks", "completed_tasks", "absences",
    "employee_calls", "completion_rate", "seniority_years",
    # Datos personales
    "age", "gender_enc",
    # Modalidad y sede
    "worker_type_enc", "location_enc",
    # Encuesta MBI-GS
    "avg_agotamiento", "avg_despersonalizacion", "eficacia_invertida"
]

# Metas de desempeño (SLAs)
SLA_PRECISION_PCT = 90.0    # % mínimo de aciertos

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
    labels_path = models_dir / "burnout_labels.pkl"
    encoder_path = models_dir / "burnout_encoder.pkl"

    for p in (pipeline_path, labels_path, encoder_path):
        if not p.exists():
            raise FileNotFoundError(
                f"Artefacto no encontrado: {p}\n"
                "Ejecuta train_burnout.py primero para generar los modelos."
            )

    pipeline = joblib.load(pipeline_path)
    class_names = joblib.load(labels_path)
    le = joblib.load(encoder_path)
    logger.info("Carga de artefactos en : %s", models_dir)

    return pipeline, class_names, le


# Carga del CSV de evaluación
def load_csv(csv_path: Path, le) -> tuple[np.ndarray, np.ndarray]:
    """
    Carga el CSV de evaluación y encodea el target al mismo orden
    que el modelo fue entrenado.

    Args:
        csv_path:    ruta al CSV con FEATURES + TARGET.
        class_names: lista ordenada de clases del modelo entrenado.

    Returns:
        X (np.ndarray), y_enc (np.ndarray int), y_raw (Series str)

    Raises:
        FileNotFoundError: si el archivo no existe.
        ValueError: si faltan columnas requeridas o si hay columnas con datos vacíos.
    """

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV no encontrado: {csv_path}")

    with open(csv_path, encoding="utf-8-sig") as f:
        sample = f.read(2048)
    sep = ";" if sample.count(";") > sample.count(",") else ","

    df = pd.read_csv(csv_path, sep=sep, encoding="utf-8-sig")
    logger.info("CSV cargado: %d filas × %d columnas", *df.shape)

    required = set(FEATURES + [TARGET])
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Columnas faltantes en el CSV: {sorted(missing)}")

    # Manejo de nulos: Si no se imputa, se eliminan las filas con nulos
    initial_rows = len(df)
    df.dropna(subset=FEATURES + [TARGET], inplace=True)
    if len(df) < initial_rows:
        logger.warning(
            f"Se eliminaron {initial_rows - len(df)} filas con valores nulos en el set de evaluación.")

    X_df = df[FEATURES].astype(float)
    y_raw = df[TARGET].astype(str).str.strip()

    # Encodear usando el mismo orden de class_names del modelo entrenado
    # Usar el LabelEncoder cargado para asegurar consistencia
    try:
        y_enc = le.transform(y_raw).astype(int)
    except ValueError as e:
        raise ValueError(
            f"Error al codificar el target: {e}. Asegúrate de que todas las clases en el CSV de evaluación fueron vistas durante el entrenamiento.")

    logger.info(
        "Distribución real:\n%s",
        y_raw.value_counts().sort_index().to_string(),
    )
    return X_df, y_enc, y_raw


# Cálculo de métricas
def compute_metrics(
    pipeline, class_names: list, X_eval: pd.DataFrame,
    y_eval: np.ndarray, y_raw: pd.Series,
) -> dict:
    """
    Calcula métricas completas de evaluación.

    Args:
        pipeline:    pipeline entrenado.
        class_names: lista ordenada de nombres de clase.
        le:          label encoder.
        X:           features del set de evaluación.
        y_enc:       target encodeado (int).
        y_raw:       target original (str), para el reporte legible.

    Returns:
        dict con accuracy, precision, recall, f1, roc_auc,
        y_pred, y_proba, y_pred_labels.
    """
    y_pred = pipeline.predict(X_eval)
    y_proba = pipeline.predict_proba(X_eval)

    acc = accuracy_score(y_eval, y_pred)
    prec = precision_score(y_eval, y_pred, average="weighted", zero_division=0)
    rec = recall_score(y_eval, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_eval, y_pred, average="weighted", zero_division=0)

    n_classes = len(class_names)
    if n_classes == 2:
        auc = roc_auc_score(y_eval, y_proba[:, 1])
    else:
        auc = roc_auc_score(
            y_eval, y_proba, multi_class="ovr", average="weighted"
        )

    # Reporte legible con nombres de clase originales
    y_pred_labels = [class_names[p] for p in y_pred]

    logger.info("─" * 45)
    logger.info("Accuracy  : %.4f  (%.2f%%)", acc, acc * 100)
    logger.info("Precision : %.4f", prec)
    logger.info("Recall    : %.4f", rec)
    logger.info("F1-Score  : %.4f", f1)
    logger.info("ROC-AUC   : %.4f", auc)
    logger.info("─" * 45)
    logger.info(
        "Reporte de clasificación:\n%s",
        classification_report(
            y_raw, y_pred_labels,
            target_names=class_names,
            zero_division=0,
        ),
    )

    return {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "roc_auc": auc,
        "y_pred": y_pred,
        "y_proba": y_proba,
        "y_pred_labels": y_pred_labels,
    }


def compute_additional_ml_metrics(
    metrics: dict, class_names: list, y_enc: np.ndarray,
    y_raw: pd.Series,
) -> dict:
    """
    Calcula métricas adicionales que no fueron incluidas en compute_metrics().

    Incluye:
    - Macro precision/recall/f1
    - Métricas por clase
    - Matriz de confusión

    Args:
        metrics: resultado retornado por compute_metrics().
        class_names: nombres de clase ordenados.
        y_enc: target encodeado real.
        y_raw: target original real.

    Returns:
        dict con métricas adicionales.
    """

    y_pred = metrics["y_pred"]
    y_pred_labels = metrics["y_pred_labels"]

    # Macro metrics
    macro_precision = precision_score(
        y_enc, y_pred, average="macro", zero_division=0)
    macro_recall = recall_score(
        y_enc, y_pred, average="macro", zero_division=0)
    macro_f1 = f1_score(y_enc, y_pred, average="macro", zero_division=0)

    # Métricas por clase
    per_class = classification_report(
        y_raw,
        y_pred_labels,
        target_names=class_names,
        output_dict=True,
        zero_division=0,
    )

    # Matriz de confusión
    cm = confusion_matrix(y_raw, y_pred_labels, labels=class_names)
    confusion = {
        true_label: {
            pred_label: int(cm[i][j])
            for j, pred_label in enumerate(class_names)
        }
        for i, true_label in enumerate(class_names)
    }

    return {
        "macro_precision": round(macro_precision, 4),
        "macro_recall": round(macro_recall, 4),
        "macro_f1": round(macro_f1, 4),
        "per_class": per_class,
        "confusion_matrix": confusion,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Evalúa un pipeline de burnout entrenado."
    )
    parser.add_argument(
        "--csv",
        type=Path,
        help="Ruta al archivo CSV con los datos de evaluación.",
    )
    parser.add_argument(
        "--test-pkl",
        type=Path,
        help="Ruta al archivo .pkl del set de prueba (X_test, y_test)."
    )
    parser.add_argument(
        "--models-dir",
        type=Path,
        default=MODELS_DIR,
        help="Directorio donde se encuentran los artefactos del modelo (.pkl).",
    )
    args = parser.parse_args()

    try:
        # 1. Cargar modelos
        pipeline, class_names, le = load_artifacts(args.models_dir)

        # 2. Cargar datos de evaluación
        if args.test_pkl:
            logger.info(f"Evaluando con test set PKL: {args.test_pkl}")
            X_eval, y_eval = joblib.load(args.test_pkl)
            y_raw = pd.Series(le.inverse_transform(y_eval), name=TARGET)
        elif args.csv:
            logger.info(f"Evaluando con CSV: {args.csv}")
            X_eval, y_eval, y_raw = load_csv(args.csv, le)
        else:
            # Intentar cargar el test set por defecto si no se provee nada
            default_test_pkl = Path(args.models_dir) / "burnout_test_set.pkl"
            if default_test_pkl.exists():
                logger.info(
                    f"Usando set de prueba por defecto: {default_test_pkl}")
                X_eval, y_eval = joblib.load(default_test_pkl)
                y_raw = pd.Series(le.inverse_transform(y_eval), name=TARGET)
            else:
                raise ValueError(
                    "Debes proporcionar --csv o --test-pkl, o asegurar que data/models/burnout_test_set.pkl exista.")

        # 3. Calcular métricas
        metrics = compute_metrics(pipeline, class_names, X_eval, y_eval, y_raw)
        additional = compute_additional_ml_metrics(
            metrics, class_names, y_eval, y_raw)

        # Log métricas adicionales
        logger.info("Macro Precision : %.4f", additional["macro_precision"])
        logger.info("Macro Recall    : %.4f", additional["macro_recall"])
        logger.info("Macro F1        : %.4f", additional["macro_f1"])

        # Verificar SLA
        if metrics["precision"] * 100 < SLA_PRECISION_PCT:
            logger.warning(
                "¡ADVERTENCIA! La precision (%.2f%%) está por debajo del SLA (%.2f%%).",
                metrics["precision"] * 100, SLA_PRECISION_PCT
            )
        else:
            logger.info(
                "SLA cumplido: precision %.2f%% >= %.2f%%",
                metrics["precision"] * 100, SLA_PRECISION_PCT,
            )

    except FileNotFoundError as e:
        logger.error("Error de archivo: %s", e)
        exit(1)
    except ValueError as e:
        logger.error("Error de datos: %s", e)
        exit(1)
    except Exception as e:
        logger.error("Ocurrió un error inesperado: %s", e)
        exit(1)


if __name__ == "__main__":
    main()
