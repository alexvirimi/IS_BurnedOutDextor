# COPIE Y PEGUE DOS CODIGOS DIFERENTES, NO LOS HE REVISADO, LO HAGO MAÑANA, ES DECIR, HOY
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

  # Solo métricas, sin guardar gráfico
  python -m scripts.evaluate_burnout --csv data/test.csv --no-plot

  # Especificar carpetas
  python -m scripts.evaluate_burnout --csv data/test.csv --models-dir data/models --output-dir outputs
"""

import argparse
import logging
import os
import warnings
from pathlib import Path

import joblib
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    f1_score, precision_score, recall_score, roc_auc_score, roc_curve,
)
from sklearn.preprocessing import label_binarize

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Configuración
MODELS_DIR = Path(__file__).resolve().parent[1] / "data" / "models"
OUTPUT_DIR = Path(__file__).resolve().parent[2] / "outputs"

TARGET = "burnout_risk"

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
        models_dir: carpeta con los .pkl generados por train_burnout.py.

    Returns:
        pipeline, class_names

    Raises:
        FileNotFoundError: si alguno de los .pkl no existe.
    """
    pipeline_path = models_dir / "burnout_pipeline.pkl"
    labels_path   = models_dir / "burnout_labels.pkl"

    for p in (pipeline_path, labels_path):
        if not p.exists():
            raise FileNotFoundError(
                f"Artefacto no encontrado: {p}\n"
                "Ejecuta train_burnout.py primero."
            )

    pipeline    = joblib.load(pipeline_path)
    class_names = joblib.load(labels_path)
    logger.info("Pipeline cargado desde: %s", pipeline_path)
    logger.info("Clases: %s", class_names)
    return pipeline, class_names


# ── Carga del CSV de evaluación ────────────────────────────────────────────────

def load_eval_csv(csv_path: Path, class_names: list) -> tuple[np.ndarray, np.ndarray, pd.Series]:
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
        ValueError: si faltan columnas requeridas.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV no encontrado: {csv_path}")

    with open(csv_path, encoding="utf-8-sig") as f:
        sample = f.read(2048)
    sep = ";" if sample.count(";") > sample.count(",") else ","

    df = pd.read_csv(csv_path, sep=sep, encoding="utf-8-sig")
    logger.info("CSV cargado: %d filas × %d columnas", *df.shape)

    required = set(FEATURES + [TARGET])
    missing  = required - set(df.columns)
    if missing:
        raise ValueError(f"Columnas faltantes en el CSV: {sorted(missing)}")

    # Imputar nulos
    null_counts = df[FEATURES].isnull().sum()
    null_cols   = null_counts[null_counts > 0]
    if not null_cols.empty:
        logger.warning("Nulos detectados — imputando con mediana:\n%s", null_cols.to_string())
        df[FEATURES] = df[FEATURES].fillna(df[FEATURES].median(numeric_only=True))

    X     = df[FEATURES].astype(float).values
    y_raw = df[TARGET].astype(str).str.strip()

    # Encodear usando el mismo orden de class_names del modelo entrenado
    class_map = {name: i for i, name in enumerate(class_names)}
    unknown   = set(y_raw.unique()) - set(class_names)
    if unknown:
        raise ValueError(
            f"Valores desconocidos en '{TARGET}': {unknown}\n"
            f"Clases conocidas por el modelo: {class_names}"
        )
    y_enc = y_raw.map(class_map).astype(int).values

    logger.info(
        "Distribución real:\n%s",
        y_raw.value_counts().sort_index().to_string(),
    )
    return X, y_enc, y_raw


# ── Cálculo de métricas ────────────────────────────────────────────────────────

def compute_metrics(
    pipeline,
    class_names: list,
    X: np.ndarray,
    y_enc: np.ndarray,
    y_raw: pd.Series,
) -> dict:
    """
    Calcula métricas completas de evaluación.

    Args:
        pipeline:    pipeline entrenado.
        class_names: lista ordenada de nombres de clase.
        X:           features del set de evaluación.
        y_enc:       target encodeado (int).
        y_raw:       target original (str), para el reporte legible.

    Returns:
        dict con accuracy, precision, recall, f1, roc_auc,
        y_pred, y_proba, y_pred_labels.
    """
    y_pred  = pipeline.predict(X)
    y_proba = pipeline.predict_proba(X)

    acc  = accuracy_score(y_enc, y_pred)
    prec = precision_score(y_enc, y_pred, average="weighted", zero_division=0)
    rec  = recall_score(y_enc, y_pred, average="weighted", zero_division=0)
    f1   = f1_score(y_enc, y_pred, average="weighted", zero_division=0)

    n_classes = len(class_names)
    if n_classes == 2:
        auc = roc_auc_score(y_enc, y_proba[:, 1])
    else:
        auc = roc_auc_score(
            y_enc, y_proba, multi_class="ovr", average="weighted"
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
        "accuracy"     : acc,
        "precision"    : prec,
        "recall"       : rec,
        "f1"           : f1,
        "roc_auc"      : auc,
        "y_pred"       : y_pred,
        "y_proba"      : y_proba,
        "y_pred_labels": y_pred_labels,
    }


# ── Visualizaciones ────────────────────────────────────────────────────────────

def plot_evaluation(
    metrics: dict,
    class_names: list,
    y_enc: np.ndarray,
    output_dir: Path,
) -> None:
    """
    Genera y guarda el panel de visualizaciones de evaluación.

    Paneles:
      - Métricas resumen
      - Matriz de confusión
      - Curva ROC (una por clase en multiclase)
      - Distribución de probabilidades predichas (violinplot)

    Args:
        metrics:     dict retornado por compute_metrics().
        class_names: lista ordenada de nombres de clase.
        y_enc:       target encodeado real.
        output_dir:  carpeta donde se guarda el PNG.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    DARK_BG = "#0f1117"
    CARD_BG = "#1a1d27"
    TEXT    = "#e8eaf0"
    MUTED   = "#7c8099"
    ACCENT  = "#4c8bf5"
    GREEN   = "#2de08b"
    AMBER   = "#f5a623"
    PALETTE = ["#4c8bf5", "#2de08b", "#f5a623", "#ff5a5f", "#c77dff"]

    y_pred  = metrics["y_pred"]
    y_proba = metrics["y_proba"]
    n_cls   = len(class_names)

    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor(DARK_BG)
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.42, wspace=0.35)

    def styled_ax(ax, title=""):
        ax.set_facecolor(CARD_BG)
        for sp in ax.spines.values():
            sp.set_edgecolor("#2c2f3e")
        ax.tick_params(colors=MUTED, labelsize=9)
        ax.xaxis.label.set_color(MUTED)
        ax.yaxis.label.set_color(MUTED)
        if title:
            ax.set_title(title, color=TEXT, fontsize=11, pad=10, fontweight="bold")

    fig.text(0.5, 0.97, "GaussianNB — Evaluación del modelo",
             ha="center", va="top", fontsize=15, color=TEXT, fontweight="bold")

    # ── Panel 1: Métricas
    ax0 = fig.add_subplot(gs[0, 0])
    ax0.set_facecolor(CARD_BG)
    ax0.axis("off")
    ax0.set_title("Métricas", color=TEXT, fontsize=11, pad=10, fontweight="bold")
    for sp in ax0.spines.values():
        sp.set_edgecolor("#2c2f3e")
    for i, (lbl, val, col) in enumerate([
        ("Accuracy",  f"{metrics['accuracy']*100:.2f}%",  GREEN),
        ("Precision", f"{metrics['precision']*100:.2f}%", ACCENT),
        ("Recall",    f"{metrics['recall']*100:.2f}%",    AMBER),
        ("F1-Score",  f"{metrics['f1']*100:.2f}%",        ACCENT),
        ("ROC-AUC",   f"{metrics['roc_auc']:.4f}",        "#c77dff"),
    ]):
        y_pos = 0.85 - i * 0.17
        ax0.text(0.05, y_pos, lbl, transform=ax0.transAxes, color=MUTED, fontsize=9)
        ax0.text(0.95, y_pos, val, transform=ax0.transAxes, color=col,
                 fontsize=13, fontweight="bold", ha="right")

    # ── Panel 2: Matriz de confusión
    ax1 = fig.add_subplot(gs[0, 1])
    styled_ax(ax1, "Matriz de confusión")
    cm = confusion_matrix(y_enc, y_pred)
    sns.heatmap(
        cm, annot=True, fmt="d", ax=ax1, cmap="Blues",
        xticklabels=class_names, yticklabels=class_names,
        linewidths=0.5, linecolor="#2c2f3e", cbar_kws={"shrink": 0.8},
    )
    ax1.set_xlabel("Predicho", color=MUTED)
    ax1.set_ylabel("Real", color=MUTED)
    ax1.tick_params(colors=MUTED, labelsize=8)

    # ── Panel 3: Curva ROC
    ax2 = fig.add_subplot(gs[0, 2])
    styled_ax(ax2, "Curva ROC")
    if n_cls == 2:
        fpr, tpr, _ = roc_curve(y_enc, y_proba[:, 1])
        ax2.plot(fpr, tpr, color=ACCENT, lw=2,
                 label=f"AUC = {metrics['roc_auc']:.3f}")
        ax2.fill_between(fpr, tpr, alpha=0.12, color=ACCENT)
    else:
        y_bin = label_binarize(y_enc, classes=list(range(n_cls)))
        for i in range(n_cls):
            fpr, tpr, _ = roc_curve(y_bin[:, i], y_proba[:, i])
            auc_i = roc_auc_score(y_bin[:, i], y_proba[:, i])
            ax2.plot(fpr, tpr, color=PALETTE[i % len(PALETTE)], lw=1.8,
                     label=f"{class_names[i]} ({auc_i:.2f})")
    ax2.plot([0, 1], [0, 1], color=MUTED, linestyle="--", lw=1, alpha=0.5)
    ax2.set_xlabel("FPR", color=MUTED)
    ax2.set_ylabel("TPR", color=MUTED)
    ax2.legend(fontsize=8, facecolor=CARD_BG, labelcolor=TEXT, edgecolor="#2c2f3e")

    # ── Panel 4: Violinplot de probabilidades predichas
    ax3 = fig.add_subplot(gs[1, 0])
    styled_ax(ax3, "Probabilidades predichas por clase")
    parts = ax3.violinplot(
        [y_proba[:, i] for i in range(n_cls)],
        positions=range(n_cls), showmedians=True,
    )
    for i, pc in enumerate(parts["bodies"]):
        pc.set_facecolor(PALETTE[i % len(PALETTE)])
        pc.set_alpha(0.75)
    for key in ("cmedians", "cbars", "cmins", "cmaxes"):
        parts[key].set_colors(DARK_BG if key == "cmedians" else MUTED)
    ax3.set_xticks(range(n_cls))
    ax3.set_xticklabels(class_names, color=MUTED, fontsize=8)
    ax3.set_ylabel("Probabilidad", color=MUTED)

    # ── Panel 5: Barras de predicciones por clase
    ax4 = fig.add_subplot(gs[1, 1])
    styled_ax(ax4, "Distribución de predicciones")
    from collections import Counter
    pred_counts = Counter(metrics["y_pred_labels"])
    cls_vals    = [pred_counts.get(c, 0) for c in class_names]
    bars = ax4.bar(class_names, cls_vals, color=PALETTE[:n_cls],
                   alpha=0.85, edgecolor="#2c2f3e")
    for bar, val in zip(bars, cls_vals):
        ax4.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                 str(val), ha="center", va="bottom", color=TEXT, fontsize=9)
    ax4.set_xlabel("Clase predicha", color=MUTED)
    ax4.set_ylabel("Cantidad", color=MUTED)

    # ── Panel 6: Real vs Predicho (heatmap normalizado)
    ax5 = fig.add_subplot(gs[1, 2])
    styled_ax(ax5, "Matriz de confusión normalizada")
    cm_norm = confusion_matrix(y_enc, y_pred, normalize="true")
    sns.heatmap(
        cm_norm, annot=True, fmt=".2f", ax=ax5, cmap="Blues",
        xticklabels=class_names, yticklabels=class_names,
        linewidths=0.5, linecolor="#2c2f3e", cbar_kws={"shrink": 0.8},
        vmin=0, vmax=1,
    )
    ax5.set_xlabel("Predicho", color=MUTED)
    ax5.set_ylabel("Real", color=MUTED)
    ax5.tick_params(colors=MUTED, labelsize=8)

    out_path = output_dir / "gnb_burnout_evaluation.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
    plt.close()
    logger.info("Visualización guardada: %s", out_path)


# ── Función pública ────────────────────────────────────────────────────────────

def evaluate(
    csv_path: str | Path,
    models_dir: Path = MODELS_DIR,
    output_dir: Path = OUTPUT_DIR,
    save_plot: bool = True,
) -> dict:
    """
    Pipeline completo de evaluación:
      1. Carga pipeline y labels.
      2. Carga y prepara el CSV con y_real.
      3. Calcula métricas completas.
      4. Genera y guarda el panel de visualizaciones (opcional).

    Args:
        csv_path:   ruta al CSV con FEATURES + TARGET (burnout_risk real).
        models_dir: carpeta con los .pkl del modelo.
        output_dir: carpeta donde se guarda el PNG.
        save_plot:  si False, omite la generación del gráfico.

    Returns:
        dict con accuracy, precision, recall, f1 y roc_auc.
    """
    logger.info("=== Iniciando evaluación BurnoutClassifier ===")

    pipeline, class_names = load_artifacts(models_dir)
    X, y_enc, y_raw       = load_eval_csv(Path(csv_path), class_names)
    metrics               = compute_metrics(pipeline, class_names, X, y_enc, y_raw)

    if save_plot:
        plot_evaluation(metrics, class_names, y_enc, output_dir)

    logger.info("=== Evaluación finalizada ===")

    return {
        "accuracy" : metrics["accuracy"],
        "precision": metrics["precision"],
        "recall"   : metrics["recall"],
        "f1"       : metrics["f1"],
        "roc_auc"  : metrics["roc_auc"],
    }


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluador de BurnoutClassifier")
    parser.add_argument(
        "--csv", required=True,
        help="Ruta al CSV con features + columna burnout_risk real.",
    )
    parser.add_argument(
        "--models-dir", type=Path, default=MODELS_DIR,
        help=f"Carpeta con los .pkl del modelo (default: {MODELS_DIR}).",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=OUTPUT_DIR,
        help=f"Carpeta donde se guarda el PNG (default: {OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--no-plot", action="store_true",
        help="Omite la generación del gráfico.",
    )
    args = parser.parse_args()

    evaluate(
        csv_path   = args.csv,
        models_dir = args.models_dir,
        output_dir = args.output_dir,
        save_plot  = not args.no_plot,
    )

"""
scripts/evaluate_burnout.py

Evalúa el pipeline entrenado de BurnoutClassifier contra un CSV
con ground truth (columna burnout_risk real).

Flujo de evaluación:
  1. Valida el CSV de entrada             (modo validate)
  2. Carga pipeline + labels              (artefactos de train_burnout.py)
  3. Predice sobre cada fila del CSV
  4. Compara predicción vs ground truth
  5. Calcula métricas ML completas
  6. Imprime reporte con badges SLA
  7. Persiste resultados en JSON          (eval_results.json)

Métricas evaluadas:
  - Accuracy, Precision, Recall, F1-Score (macro y weighted)
  - Matriz de confusión por clase
  - SLA: precisión ≥ 70%

Modos:
  validate   → Valida el CSV sin predecir
  batch      → Predice y evalúa todo el CSV
  report     → Reporte consolidado de resultados guardados

Uso:
  # Validar CSV primero
  python -m ai.scripts.evaluate_burnout --mode validate --csv data/test.csv

  # Evaluación completa
  python -m ai.scripts.evaluate_burnout --mode batch --csv data/test.csv

  # Reporte consolidado
  python -m ai.scripts.evaluate_burnout --mode report

  # Especificar carpeta de modelos
  python -m ai.scripts.evaluate_burnout --mode batch --csv data/test.csv --models-dir data/models
"""

import argparse
import json
import statistics
import sys
import warnings
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import joblib
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ── Configuración ──────────────────────────────────────────────────────────────

MODELS_DIR   = Path(__file__).parent.parent / "data" / "models"
EVAL_DIR     = Path(__file__).parent.parent / "data" / "evaluation"
RESULTS_FILE = EVAL_DIR / "eval_results.json"

TARGET = "burnout_risk"

FEATURES = [
    "assigned_tasks", "completed_tasks", "absences",
    "employee_calls", "completion_rate", "seniority_years",
    "rank_index", "group_index",
    "age", "gender_enc",
    "work_mode_enc", "location_enc",
    "avg_agotamiento", "avg_despersonalizacion", "eficacia_invertida",
]

CLASS_ORDER = {
    "Muy Bajo" : 0,
    "Bajo"     : 1,
    "Medio"    : 2,
    "Moderado" : 3,
    "Alto"     : 4,
}

# SLAs
SLA_ACCURACY_PCT = 70.0   # % mínimo de accuracy global

# ── Paleta terminal ────────────────────────────────────────────────────────────

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"
CHECK  = "✓"
CROSS  = "✗"


# ── Helpers ────────────────────────────────────────────────────────────────────

def banner():
    print(f"""
{BOLD}{CYAN}╔══════════════════════════════════════════════════════════╗
║        EVALUADOR BurnoutClassifier — GaussianNB          ║
╚══════════════════════════════════════════════════════════╝{RESET}
""")


def sla_badge(value: float, threshold: float, higher_is_better: bool = True) -> str:
    ok    = (value >= threshold) if higher_is_better else (value <= threshold)
    icon  = CHECK if ok else CROSS
    color = GREEN if ok else RED
    return f"{color}{BOLD}[{icon} SLA]{RESET}"


# ── Estructuras de datos ───────────────────────────────────────────────────────

@dataclass
class RowResult:
    """Resultado de predicción para una fila del CSV."""
    row_idx          : int
    predicted        : Optional[str]  = None
    ground_truth     : Optional[str]  = None
    correct          : Optional[bool] = None
    confidence       : Optional[float]= None
    probabilities    : dict           = field(default_factory=dict)
    error            : Optional[str]  = None
    timestamp        : str            = field(default_factory=lambda: datetime.now().isoformat())


# ── Carga de artefactos ────────────────────────────────────────────────────────

def load_artifacts(models_dir: Path) -> tuple:
    """
    Carga pipeline, labels y encoder desde models_dir.

    Returns:
        pipeline, class_names, le

    Raises:
        FileNotFoundError: si algún .pkl no existe.
    """
    files = {
        "pipeline": models_dir / "burnout_pipeline.pkl",
        "labels"  : models_dir / "burnout_labels.pkl",
        "encoder" : models_dir / "burnout_encoder.pkl",
    }
    for name, path in files.items():
        if not path.exists():
            raise FileNotFoundError(
                f"Artefacto '{name}' no encontrado: {path}\n"
                "Ejecuta train_burnout.py primero."
            )

    pipeline    = joblib.load(files["pipeline"])
    class_names = joblib.load(files["labels"])
    le          = joblib.load(files["encoder"])
    return pipeline, class_names, le


# ── Carga y validación del CSV ─────────────────────────────────────────────────

def load_csv(csv_path: Path) -> tuple[pd.DataFrame, pd.Series]:
    """
    Carga el CSV de evaluación.

    Requiere columnas de FEATURES + TARGET (burnout_risk).

    Returns:
        X (DataFrame), y_raw (Series str)

    Raises:
        FileNotFoundError, ValueError
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV no encontrado: {csv_path}")

    with open(csv_path, encoding="utf-8-sig") as f:
        sample = f.read(2048)
    sep = ";" if sample.count(";") > sample.count(",") else ","

    df = pd.read_csv(csv_path, sep=sep, encoding="utf-8-sig")

    required = set(FEATURES + [TARGET])
    missing  = required - set(df.columns)
    if missing:
        raise ValueError(f"Columnas faltantes en el CSV: {sorted(missing)}")

    df = df.dropna(subset=[TARGET])
    if df.empty:
        raise ValueError("El CSV no tiene filas válidas con target.")

    null_counts = df[FEATURES].isnull().sum()
    null_cols   = null_counts[null_counts > 0]
    if not null_cols.empty:
        df[FEATURES] = df[FEATURES].fillna(df[FEATURES].median(numeric_only=True))

    X     = df[FEATURES].astype(float)
    y_raw = df[TARGET].astype(str).str.strip()

    return X, y_raw


def validate_csv(csv_path: Path) -> tuple[bool, list[str]]:
    """
    Valida el CSV sin predecir.

    Returns:
        (es_válido, lista_de_errores)
    """
    errors = []

    if not csv_path.exists():
        return False, [f"Archivo no encontrado: {csv_path}"]

    with open(csv_path, encoding="utf-8-sig") as f:
        sample = f.read(2048)
    sep = ";" if sample.count(";") > sample.count(",") else ","

    try:
        df = pd.read_csv(csv_path, sep=sep, encoding="utf-8-sig")
    except Exception as e:
        return False, [f"Error al leer CSV: {e}"]

    # Columnas requeridas
    required = set(FEATURES + [TARGET])
    missing  = required - set(df.columns)
    if missing:
        errors.append(f"Columnas faltantes: {sorted(missing)}")

    if TARGET in df.columns:
        # Valores válidos del target
        valid_classes = set(CLASS_ORDER.keys())
        found_classes = set(df[TARGET].astype(str).str.strip().unique())
        unknown       = found_classes - valid_classes
        if unknown:
            errors.append(
                f"Valores desconocidos en '{TARGET}': {unknown}\n"
                f"  Clases válidas: {sorted(valid_classes)}"
            )

        # Nulos en target
        null_target = df[TARGET].isnull().sum()
        if null_target > 0:
            errors.append(f"Nulos en '{TARGET}': {null_target} filas")

    # Nulos en features
    if not missing:
        null_counts = df[FEATURES].isnull().sum()
        null_cols   = null_counts[null_counts > 0]
        if not null_cols.empty:
            errors.append(
                f"Nulos en features (se imputarán con mediana):\n"
                + "\n".join(f"    {col}: {cnt}" for col, cnt in null_cols.items())
            )

    return len(errors) == 0, errors


# ── Métricas ML ────────────────────────────────────────────────────────────────

def compute_ml_metrics(results: list[dict]) -> dict:
    """
    Calcula métricas ML completas (multiclase) sin sklearn.

    Returns:
        dict con accuracy, macro/weighted precision/recall/f1,
        per_class, confusion_matrix y labels.
    """
    validated = [r for r in results if r.get("correct") is not None]
    if not validated:
        return {}

    y_true = [str(r["ground_truth"]).strip() for r in validated]
    y_pred = [str(r["predicted"]).strip()    for r in validated]
    labels = sorted(set(y_true) | set(y_pred), key=lambda x: CLASS_ORDER.get(x, 99))
    n      = len(validated)

    # Matriz de confusión cm[true][pred]
    cm: dict[str, dict[str, int]] = {
        lbl: {l: 0 for l in labels} for lbl in labels
    }
    for yt, yp in zip(y_true, y_pred):
        if yt not in cm:
            cm[yt] = {l: 0 for l in labels}
        cm[yt][yp] = cm[yt].get(yp, 0) + 1

    # Métricas por clase
    per_class: dict[str, dict] = {}
    for lbl in labels:
        tp      = cm.get(lbl, {}).get(lbl, 0)
        fp      = sum(cm.get(o, {}).get(lbl, 0) for o in labels if o != lbl)
        fn      = sum(cm.get(lbl, {}).get(o, 0) for o in labels if o != lbl)
        support = tp + fn

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1        = (2 * precision * recall / (precision + recall)
                     if (precision + recall) > 0 else 0.0)
        per_class[lbl] = {
            "precision": round(precision, 4),
            "recall"   : round(recall,    4),
            "f1"       : round(f1,        4),
            "support"  : support,
        }

    accuracy          = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp) / n
    total_support     = sum(per_class[l]["support"] for l in labels) or 1
    macro_precision   = sum(per_class[l]["precision"] for l in labels) / len(labels)
    macro_recall      = sum(per_class[l]["recall"]    for l in labels) / len(labels)
    macro_f1          = sum(per_class[l]["f1"]        for l in labels) / len(labels)
    weighted_precision= sum(per_class[l]["precision"] * per_class[l]["support"] for l in labels) / total_support
    weighted_recall   = sum(per_class[l]["recall"]    * per_class[l]["support"] for l in labels) / total_support
    weighted_f1       = sum(per_class[l]["f1"]        * per_class[l]["support"] for l in labels) / total_support

    return {
        "accuracy"          : round(accuracy,           4),
        "macro_precision"   : round(macro_precision,    4),
        "macro_recall"      : round(macro_recall,       4),
        "macro_f1"          : round(macro_f1,           4),
        "weighted_precision": round(weighted_precision, 4),
        "weighted_recall"   : round(weighted_recall,    4),
        "weighted_f1"       : round(weighted_f1,        4),
        "per_class"         : per_class,
        "labels"            : labels,
        "n_samples"         : n,
        "_cm_raw"           : cm,
    }


# ── Impresión de métricas ──────────────────────────────────────────────────────

def print_ml_metrics(ml: dict):
    """Imprime métricas ML con tabla por clase y matriz de confusión."""
    if not ml:
        print(f"  {YELLOW}Sin datos para métricas ML.{RESET}\n")
        return

    acc  = ml["accuracy"]
    mp   = ml["macro_precision"]
    mr   = ml["macro_recall"]
    mf1  = ml["macro_f1"]
    wp   = ml["weighted_precision"]
    wr   = ml["weighted_recall"]
    wf1  = ml["weighted_f1"]
    n    = ml["n_samples"]
    badge_acc = sla_badge(acc * 100, SLA_ACCURACY_PCT)

    print(f"""
  {BOLD}MÉTRICAS ML{RESET}
  ┌────────────────────────────────────────────────────────────────────┐
  │  Muestras evaluadas : {n}
  │
  │  {BOLD}Métricas globales:{RESET}
  │    Accuracy                       : {GREEN if acc >= 0.7 else RED}{acc*100:>6.1f}%{RESET}  {badge_acc}
  │
  │    ── Macro (promedio no ponderado) ──────────────────────
  │    Precision  (macro)             : {mp*100:>6.1f}%
  │    Recall     (macro / TPR)       : {mr*100:>6.1f}%
  │    F1-Score   (macro)             : {mf1*100:>6.1f}%
  │
  │    ── Weighted (ponderado por soporte) ───────────────────
  │    Precision  (weighted)          : {wp*100:>6.1f}%
  │    Recall     (weighted / TPR)    : {wr*100:>6.1f}%
  │    F1-Score   (weighted)          : {wf1*100:>6.1f}%
  └────────────────────────────────────────────────────────────────────┘""")

    # Tabla por clase
    per_class = ml.get("per_class", {})
    labels    = ml.get("labels", [])
    if per_class:
        col_w = max((len(l) for l in labels), default=10)
        col_w = max(col_w, 10)
        print(f"\n  {BOLD}Detalle por clase:{RESET}")
        print(f"  {'Clase':>{col_w}}  {'Precision':>10}  {'Recall':>8}  {'F1':>8}  {'Soporte':>8}")
        print(f"  {'─'*col_w}  {'─'*10}  {'─'*8}  {'─'*8}  {'─'*8}")
        for lbl in labels:
            s   = per_class.get(lbl, {})
            p   = s.get("precision", 0)
            r   = s.get("recall",    0)
            f1  = s.get("f1",        0)
            sup = s.get("support",   0)
            p_c = GREEN if p  >= 0.7 else (YELLOW if p  >= 0.5 else RED)
            r_c = GREEN if r  >= 0.7 else (YELLOW if r  >= 0.5 else RED)
            f_c = GREEN if f1 >= 0.7 else (YELLOW if f1 >= 0.5 else RED)
            print(
                f"  {lbl:>{col_w}}  "
                f"{p_c}{p*100:>9.1f}%{RESET}  "
                f"{r_c}{r*100:>7.1f}%{RESET}  "
                f"{f_c}{f1*100:>7.1f}%{RESET}  "
                f"{sup:>8}"
            )

    # Matriz de confusión
    cm_raw = ml.get("_cm_raw", {})
    if cm_raw and labels:
        col_w2 = max((len(l) for l in labels), default=8)
        col_w2 = max(col_w2, 8)
        print(f"\n  {BOLD}Matriz de Confusión (filas=real, columnas=predicho):{RESET}")
        print(f"  {' '*col_w2}  " + "  ".join(f"{l[:col_w2]:>{col_w2}}" for l in labels))
        print(f"  {'─'*(col_w2 + (col_w2+2)*len(labels))}")
        for true_lbl in labels:
            row = []
            for pred_lbl in labels:
                cnt = cm_raw.get(true_lbl, {}).get(pred_lbl, 0)
                if true_lbl == pred_lbl:
                    cell = f"{GREEN}{cnt:>{col_w2}}{RESET}"
                elif cnt > 0:
                    cell = f"{RED}{cnt:>{col_w2}}{RESET}"
                else:
                    cell = f"{' '*col_w2}"
                row.append(cell)
            print(f"  {true_lbl:>{col_w2}}  " + "  ".join(row))
        print()

    all_ok = ml["accuracy"] * 100 >= SLA_ACCURACY_PCT
    status_color = GREEN if all_ok else RED
    print(f"""
  {BOLD}ESTADO GENERAL : {status_color}{'✓ MODELO CUMPLE META SLA' if all_ok else '✗ REVISAR — SLA INCUMPLIDO'}{RESET}
""")


# ── Persistencia ───────────────────────────────────────────────────────────────

def load_results() -> list[dict]:
    if RESULTS_FILE.exists():
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_results(results: list[dict]):
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


# ── MODO: validate ─────────────────────────────────────────────────────────────

def run_validate(csv_path: Path):
    """Valida el CSV sin predecir."""
    banner()
    print(f"{BOLD}Modo: Validación — {csv_path}{RESET}\n")

    is_valid, errors = validate_csv(csv_path)

    # Intentar cargar para estadísticas
    try:
        with open(csv_path, encoding="utf-8-sig") as f:
            sample = f.read(2048)
        sep = ";" if sample.count(";") > sample.count(",") else ","
        df  = pd.read_csv(csv_path, sep=sep, encoding="utf-8-sig")
        print(f"  Filas        : {len(df)}")
        print(f"  Columnas     : {len(df.columns)}")
        if TARGET in df.columns:
            dist = df[TARGET].astype(str).str.strip().value_counts().sort_index()
            print(f"\n  {BOLD}Distribución de '{TARGET}':{RESET}")
            for cls, cnt in dist.items():
                bar = "█" * int(cnt / len(df) * 40)
                print(f"    {cls:>10}: {cnt:>5}  ({cnt/len(df)*100:.1f}%)  {bar}")
    except Exception:
        pass

    print()
    if errors:
        print(f"{BOLD}{RED}Problemas encontrados:{RESET}")
        for e in errors:
            print(f"  {RED}✗{RESET} {e}")
        print()
    else:
        print(f"{GREEN}{BOLD}✓ CSV válido — listo para evaluación.{RESET}\n")
        print(f"{DIM}  Siguiente paso:{RESET}")
        print(f"  python -m ai.scripts.evaluate_burnout --mode batch --csv {csv_path}\n")


# ── MODO: batch ────────────────────────────────────────────────────────────────

def run_batch(csv_path: Path, models_dir: Path):
    """Predice y evalúa todas las filas del CSV."""
    banner()
    print(f"{BOLD}Modo: Evaluación Batch — {csv_path}{RESET}\n")

    # Validar antes de predecir
    is_valid, val_errors = validate_csv(csv_path)
    if not is_valid:
        print(f"{YELLOW}⚠  Advertencias en el CSV:{RESET}")
        for e in val_errors:
            print(f"  {YELLOW}→{RESET} {e}")
        print()

    # Cargar artefactos
    try:
        pipeline, class_names, le = load_artifacts(models_dir)
    except FileNotFoundError as e:
        print(f"{RED}ERROR: {e}{RESET}")
        sys.exit(1)

    # Cargar CSV
    try:
        X, y_raw = load_csv(csv_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"{RED}ERROR: {e}{RESET}")
        sys.exit(1)

    print(f"  Empleados a evaluar : {len(X)}")
    print(f"  Clases del modelo   : {class_names}\n")

    # Predicción por lotes
    y_pred  = pipeline.predict(X.values)
    y_proba = pipeline.predict_proba(X.values)

    print(f"  {'#':>5}  {'Predicho':>10}  {'Real':>10}  {'Conf':>6}  Veredicto")
    print(f"  {'─'*5}  {'─'*10}  {'─'*10}  {'─'*6}  {'─'*10}")

    row_results = []
    for i, (pred, proba, truth) in enumerate(zip(y_pred, y_proba, y_raw)):
        pred_idx  = int(np.argmax(proba))
        pred_name = class_names[pred_idx]
        truth_str = str(truth).strip()
        correct   = pred_name == truth_str
        conf      = round(float(proba[pred_idx]), 4)

        verdict_str = f"{GREEN}✓{RESET}" if correct else f"{RED}✗{RESET}"
        print(
            f"  {i+1:>5}  {pred_name:>10}  {truth_str:>10}  "
            f"{conf:>6.2f}  {verdict_str}"
        )

        row_results.append(RowResult(
            row_idx      = i,
            predicted    = pred_name,
            ground_truth = truth_str,
            correct      = correct,
            confidence   = conf,
            probabilities= {class_names[j]: round(float(p), 4) for j, p in enumerate(proba)},
        ))

    # Métricas
    results_dicts = [asdict(r) for r in row_results]
    ml = compute_ml_metrics(results_dicts)

    print(f"\n{BOLD}{CYAN}{'═'*60}")
    print(f"  RESULTADOS BATCH ({len(row_results)} empleados)")
    print(f"{'═'*60}{RESET}")
    print_ml_metrics(ml)

    # Persistir
    all_results = load_results()
    batch_entry = {
        "_type"    : "batch",
        "timestamp": datetime.now().isoformat(),
        "csv"      : str(csv_path),
        "metrics"  : {k: v for k, v in ml.items() if k != "_cm_raw"},
        "rows"     : results_dicts,
    }
    all_results.append(batch_entry)
    save_results(all_results)
    print(f"{DIM}Guardado en: {RESULTS_FILE.absolute()}{RESET}\n")


# ── MODO: report ───────────────────────────────────────────────────────────────

def run_report():
    """Reporte consolidado de todas las evaluaciones guardadas."""
    banner()
    print(f"{BOLD}Modo: Reporte Consolidado — {RESULTS_FILE}{RESET}\n")

    all_results = load_results()
    batches     = [r for r in all_results if r.get("_type") == "batch"]

    if not batches:
        print(f"{YELLOW}No hay evaluaciones guardadas aún.")
        print(f"Ejecuta primero:{RESET}")
        print(f"  python -m ai.scripts.evaluate_burnout --mode batch --csv <archivo.csv>\n")
        return

    print(f"  {BOLD}Historial de evaluaciones ({len(batches)} ejecuciones):{RESET}")
    print(f"\n  {'#':>3}  {'Fecha':>22}  {'CSV':>30}  {'N':>5}  {'Accuracy':>9}  {'F1-W':>7}")
    print(f"  {'─'*3}  {'─'*22}  {'─'*30}  {'─'*5}  {'─'*9}  {'─'*7}")

    for i, b in enumerate(batches, 1):
        ts  = b.get("timestamp", "?")[:19]
        csv = Path(b.get("csv", "?")).name[:30]
        m   = b.get("metrics", {})
        n   = m.get("n_samples", "?")
        acc = m.get("accuracy", 0) * 100
        wf1 = m.get("weighted_f1", 0) * 100
        acc_c = GREEN if acc >= SLA_ACCURACY_PCT else RED
        print(
            f"  {i:>3}  {ts:>22}  {csv:>30}  {n:>5}  "
            f"{acc_c}{acc:>8.1f}%{RESET}  {wf1:>6.1f}%"
        )

    # Última evaluación en detalle
    last = batches[-1]
    print(f"\n{BOLD}{CYAN}{'═'*60}")
    print(f"  ÚLTIMA EVALUACIÓN — {Path(last['csv']).name}")
    print(f"{'═'*60}{RESET}")

    # Reconstruir _cm_raw para imprimir
    rows = last.get("rows", [])
    ml   = compute_ml_metrics(rows)
    print_ml_metrics(ml)

    # Distribución de predicciones
    preds  = [r["predicted"]    for r in rows if r.get("predicted")]
    truths = [r["ground_truth"] for r in rows if r.get("ground_truth")]

    if preds:
        pred_dist  = Counter(preds)
        truth_dist = Counter(truths)
        labels     = sorted(set(preds) | set(truths), key=lambda x: CLASS_ORDER.get(x, 99))

        print(f"  {BOLD}Distribución predicho vs real:{RESET}")
        print(f"  {'Clase':>10}  {'Predicho':>10}  {'Real':>10}")
        print(f"  {'─'*10}  {'─'*10}  {'─'*10}")
        for lbl in labels:
            print(
                f"  {lbl:>10}  "
                f"{pred_dist.get(lbl, 0):>10}  "
                f"{truth_dist.get(lbl, 0):>10}"
            )
        print()


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluador de BurnoutClassifier (GaussianNB)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modos:
  validate   Valida el CSV sin predecir (recomendado primero)
  batch      Predice y evalúa todas las filas del CSV
  report     Reporte consolidado de evaluaciones guardadas

Flujo recomendado:
  1. python -m ai.scripts.evaluate_burnout --mode validate --csv data/test.csv
  2. python -m ai.scripts.evaluate_burnout --mode batch    --csv data/test.csv
  3. python -m ai.scripts.evaluate_burnout --mode report
        """
    )
    parser.add_argument(
        "--mode", choices=["validate", "batch", "report"],
        default="batch",
        help="Modo de ejecución (default: batch).",
    )
    parser.add_argument(
        "--csv", type=Path,
        help="Ruta al CSV con FEATURES + burnout_risk real.",
    )
    parser.add_argument(
        "--models-dir", type=Path, default=MODELS_DIR,
        help=f"Carpeta con los .pkl del modelo (default: {MODELS_DIR}).",
    )
    args = parser.parse_args()

    if args.mode == "validate":
        if not args.csv:
            parser.error("--csv es requerido para el modo validate.")
        run_validate(args.csv)

    elif args.mode == "batch":
        if not args.csv:
            parser.error("--csv es requerido para el modo batch.")
        run_batch(args.csv, args.models_dir)

    elif args.mode == "report":
        run_report()