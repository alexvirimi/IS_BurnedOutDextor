"""
  GaussianNB - Pipeline completo de entrenamiento ML
  Modelo: GaussianNB(priors=None, var_smoothing=1e-09)
  Incluye: auto_balance, evaluación, visualización y guardado
"""
import logging
import os
import warnings
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

#  1. Configuración global
CONFIG = {
    "var_smoothing": 1e-9,          # Hiperparámetro principal de GaussianNB
    "priors": None,                  # None → estima automáticamente del dataset
    "test_size": 0.2,               # 20% para test
    "random_state": 42,
    "cv_folds": 5,                  # Cross-validation folds
    "auto_balance": True,           # Activar balanceo automático
    "balance_strategy": "resample",  # Opciones: "resample", "undersample", "weight"
    "dataset": "../data/training_data/training_dataset.csv",
    "output_dir": "./backend/ai-service/models",
    "save_model": True,
}

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

CLASS_ORDER = {
    "Muy Bajo": 0,
    "Bajo": 1,
    "Medio": 2,
    "Moderado": 3,
    "Alto": 4,
}

#  2. Carga de Datos


def load_dataset(csv_path: str) -> tuple[pd.DataFrame, pd.Series, list, LabelEncoder]:
    """
    Carga el dataset desde CSV.

    Args:
        csv_path: ruta relativa al script O absoluta.
    Returns:
        X (DataFrame), y (Series), class_names (list ordenada), le (LabelEncoder ajustado)
    Raises:
        FileNotFoundError: si el archivo no existe.
    """

    # Resuelve ruta absoluta
    if not os.path.isabs(csv_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_dir, csv_path)

    # Verifica existencia
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encontró el archivo: {csv_path}")

    # Cargar con pandas
    df = pd.read_csv(csv_path)

    # Manejo de nulos: Se eliminan las filas con nulos en features o target debido a que GaussianNB no maneja nulos. Se registra cuántas filas se eliminaron.
    # Además, si se rellenan los valores nulos con la media o la moda, se corre el riesgo de una predicción incorrecta
    initial_rows = len(df)
    df.dropna(subset=FEATURES + [TARGET], inplace=True)
    if len(df) < initial_rows:
        logger.warning(
            f"Se eliminaron {initial_rows - len(df)} filas con valores nulos en features o target.")

    X = df[FEATURES]
    y_raw = df[TARGET]

    class_names = ["Muy Bajo", "Bajo", "Medio", "Moderado", "Alto"]
    y = y_raw.map(CLASS_ORDER)

    le = LabelEncoder()
    le.classes_ = np.array(class_names)

    return X, y, class_names, le


#  3. Análisis de balance de clases
def check_balance(y: pd.Series) -> dict:
    """
    Analiza la distribución de clases y detecta desbalance.

    Returns:
        dict con conteos, proporciones, ratio de desbalance e indicador booleano
         de si el dataset se considera desbalanceado (>1.5) o no.
    """

    # Contar clases y calcular proporciones
    counts = Counter(y)
    total = len(y)
    ratios = {cls: counts[cls] / total for cls in counts}
    min_ratio = min(ratios.values())
    max_ratio = max(ratios.values())
    imbalance_ratio = max_ratio / min_ratio

    # Imprimir distribución de clases
    logger.info("Distribución de clases:")
    for cls, cnt in sorted(counts.items(), key=lambda x: str(x[0])):
        logger.info("  %-20s %5d  (%.1f%%) ", cls, cnt, ratios[cls] * 100)

    # Evaluar desbalance
    is_imbalanced = imbalance_ratio > 1.5
    status = "DESBALANCEADO" if is_imbalanced else "BALANCEADO"
    logger.info("Ratio de desbalance: %.2fx  -  %s", imbalance_ratio, status)

    return {
        "counts": counts,
        "ratios": ratios,
        "imbalance_ratio": imbalance_ratio,
        "is_imbalanced": is_imbalanced,
    }

#  4. Autobalance de clases


def auto_balance(
    X_train: np.ndarray, y_train: np.ndarray, strategy: str
) -> tuple[np.ndarray, np.ndarray, list | None]:
    """
    Aplica balanceo automático de clases según la estrategia elegida.

    Estrategias:
      - "resample"    : Oversampling de la clase minoritaria con ruido gaussiano
      - "undersample" : Reducir la clase mayoritaria al tamaño de la minoritaria
      - "weight"      : Calcula priors ajustados para pasarle al modelo

    Returns:
        X_train_balanced (np.ndarray): Características del set de entrenamiento balanceado.
        y_train_balanced (np.ndarray): Etiquetas del set de entrenamiento balanceado.
        priors (list | None): Priors calculados para el modelo, si aplica.
    """
    counts = Counter(y_train)
    print(f"\n Auto Balance activado — estrategia: '{strategy}'")
    print(f"  Distribución antes: {dict(counts)}")

    if strategy == "resample":
        # Oversampling con ruido gaussiano
        # Encontrar clase mayoritaria
        max_count = max(counts.values())
        # Arrays a listas
        X_bal, y_bal = list(X_train), list(y_train)

        np.random.seed(CONFIG["random_state"])
        for cls, cnt in counts.items():
            # Solo balancear si la clase es minoritaria
            if cnt < max_count:
                # Cuantas clases faltan para igualar a la mayoritaria
                deficit = max_count - cnt
                # Busca índices de esta clase en el set de entrenamiento y elige aleatoriamente con reemplazo
                idx = np.where(y_train == cls)[0]
                chosen = np.random.choice(idx, deficit, replace=True)
                noise = np.random.normal(0, 0.01, (deficit, X_train.shape[1]))
                X_bal.extend(X_train[chosen] + noise)
                y_bal.extend([cls] * deficit)

        # Convertir de nuevo a arrays
        X_train = np.array(X_bal)
        y_train = np.array(y_bal)
        priors = None  # deja que el modelo estime

    elif strategy == "undersample":
        # Reducir todas las clases al tamaño de la minoritaria
        # Escoger mínimo y preparar listas para balancear
        min_count = min(counts.values())
        np.random.seed(CONFIG["random_state"])
        X_bal, y_bal = [], []

        for cls in counts:
            # Obtener índices de esta clase y elegir aleatoriamente sin reemplazo ni repetición
            idx = np.where(y_train == cls)[0]
            chosen = np.random.choice(idx, min_count, replace=False)
            # Guardar muestras seleccionadas
            X_bal.append(X_train[chosen])
            y_bal.extend([cls] * min_count)

        # Convertir a arrays de cada clase
        X_train = np.vstack(X_bal)
        y_train = np.array(y_bal)
        priors = None

    elif strategy == "weight":
        # Calcula priors inversamente proporcionales al tamaño de clase
        total = sum(counts.values())
        n_classes = len(counts)
        # Invertir los pesos, mientras más pequeña la clase, mayor el peso
        raw_weights = {cls: total / (n_classes * cnt)
                       for cls, cnt in counts.items()}
        weight_sum = sum(raw_weights.values())
        # Convierte pesos para que sumen 1 (probabilidades)
        priors = [raw_weights[cls] /
                  weight_sum for cls in sorted(counts.keys())]
        print(f"  Priors calculados: {[round(p, 4) for p in priors]}")

    else:
        raise ValueError(f"Estrategia '{strategy}' no reconocida.")

    # Contar distribución después del balanceo
    counts_after = Counter(y_train)
    print(f"  Distribución después: {dict(counts_after)}")

    # Solo "weight" cambia priors; las demás lo dejan en None
    priors_out = priors if strategy == "weight" else None

    return X_train, y_train, priors_out


#  5. Construcción del Pipeline
def build_pipeline(var_smoothing: float, priors) -> Pipeline:
    """
    Construye el pipeline de entrenamiento: StandardScaler → GaussianNB.

    Args:
        var_smoothing (float): Parámetro de suavizado de varianza para GaussianNB.
        priors (list | None): Priors para GaussianNB.

    Returns:
        Pipeline: Pipeline de entrenamiento configurado.
    """
    # Construir modelo con hiperparámetros configurados
    model = GaussianNB(
        priors=priors,
        var_smoothing=var_smoothing
    )

    # Automatiza la normalización de características y el entrenamiento del modelo en un solo pipeline
    pipeline = Pipeline([
        # Normaliza los datos para mejorar el rendimiento de GaussianNB
        ("scaler", StandardScaler()),
        # Agrega el modelo GaussianNB con los hiperparámetros configurados
        ("gnb", model),
    ])
    return pipeline


#  6. Entrenamiento
def train_nb(
        pipeline: Pipeline, X_train: np.ndarray,
        y_train: np.ndarray, var_smoothing: float
) -> Pipeline:
    """
    Ajusta el pipeline sobre los datos de entrenamientos

    Args:
        pipeline (Pipeline): Pipeline de entrenamiento configurado con build_pipeline().
        X_train (np.ndarray): Características del set de entrenamiento.
        y_train (np.ndarray): Etiquetas del set de entrenamiento.
        var_smoothing (float): Parámetro de suavizado de varianza para GaussianNB.

    Returns:
        Pipeline: Pipeline entrenado listo para predicciones.
    """
    # Registrar eventos del programa para seguimiento y debugging
    logger.info(
        "Entrenando GaussianNB — muestras: %d | features: %d | var_smoothing: %s",
        len(X_train), X_train.shape[1], var_smoothing,
    )

    # Entrenamiento del pipeline completo (incluye escalado y GaussianNB)
    pipeline.fit(X_train, y_train)
    # Acceder al modelo entrenado dentro del pipeline para mostrar clases aprendidas y priors
    gnb = pipeline.named_steps["gnb"]
    logger.info(
        "Clases aprendidas: %s | priors: %s",
        gnb.classes_,
        np.round(gnb.class_prior_, 4),
    )
    # Devolver el pipeline completo, que incluye el modelo entrenado y el escalador
    return pipeline

#  7. Guardar modelo entrenado, etiquetas de clase y LabelEncoder para uso en predicción


def save_artifacts(
    pipeline: Pipeline, class_names: list,
    le: LabelEncoder, output_dir: Path,
) -> None:
    """
    Serializa el pipeline entrenado con jobliby las etiquetas de clase en output_dir.

    Archivos generados:
      burnout_pipeline.pkl  → Pipeline completo (scaler + GaussianNB)
      burnout_labels.pkl    → Lista ordenada de class_names

    Args:
        pipeline:    pipeline entrenado.
        class_names: lista de nombres de clase en el orden del LabelEncoder.
        le:          LabelEncoder utilizado para transformar las etiquetas.
        output_dir:  directorio destino.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(pipeline, output_dir / "burnout_pipeline.pkl")
    joblib.dump(class_names, output_dir / "burnout_labels.pkl")
    joblib.dump(le, output_dir / "burnout_encoder.pkl")

    logger.info("Artefactos guardados en: %s", output_dir)

#  8. Main: Ejecución completa del pipeline


def main():
    logger.info("GaussianNB — Pipeline de Entrenamiento")
    logger.info("Modelo: GaussianNB(priors=None, var_smoothing=1e-9)")

    # Carga
    X, y, class_names, le = load_dataset(CONFIG["dataset"])

    # Split inicial (estratificado)
    X_train, X_test, y_train, y_test = train_test_split(
        X.values, y.values,
        test_size=CONFIG["test_size"],
        random_state=CONFIG["random_state"],
        stratify=y.values
    )

    # Análisis de balance
    balance_info = check_balance(y_train)
    logger.info("Split → train: %d | test: %d", len(X_train), len(X_test))

    # Auto Balance (solo en train)
    priors_override = CONFIG["priors"]   # None por defecto

    if CONFIG["auto_balance"] and balance_info["is_imbalanced"]:
        X_train, y_train, priors_computed = auto_balance(X_train, y_train, CONFIG["balance_strategy"])
        if priors_computed is not None:
            priors_override = priors_computed
    elif CONFIG["auto_balance"] and not balance_info["is_imbalanced"]:
        print("\n Auto_balance activado pero el dataset ya está balanceado — no se aplica.")

    # Construir pipeline
    pipeline = build_pipeline(CONFIG["var_smoothing"], priors_override)
    # Entrenamiento final
    train_nb(pipeline, X_train, y_train, CONFIG["var_smoothing"])

    # Guardar modelo
    if CONFIG["save_model"]:
        output_path = Path(CONFIG["output_dir"])
        save_artifacts(pipeline, class_names, le, output_path)

        # Guardamos el set de prueba para la evaluación posterior
        test_set_path = output_path / "burnout_test_set.pkl"
        joblib.dump((X_test, y_test), test_set_path)
        logger.info(f"Set de prueba guardado en: {test_set_path}")

    logger.info(" Entrenamiento finalizado")
    return pipeline


if __name__ == "__main__":
    pipeline = main()
