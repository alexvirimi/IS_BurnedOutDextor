import joblib
import pandas as pd
import logging
from pathlib import Path
from typing import Tuple, Dict

logger = logging.getLogger(__name__)

class ModelLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized: return
        
        # Ruta a los modelos (ajustable por variable de entorno)
        self.base_path = Path(__file__).resolve().parent.parent.parent / "models"
        self._load_artifacts()
        self._initialized = True

    def _load_artifacts(self):
        try:
            self.pipeline = joblib.load(self.base_path / "burnout_pipeline.pkl")
            self.class_names = joblib.load(self.base_path / "burnout_labels.pkl")
            logger.info("Modelos de Burnout cargados correctamente.")
        except Exception as e:
            logger.error(f"Error cargando modelos: {e}")
            raise RuntimeError(e)

    def predict(self, data: dict) -> Tuple[str, float, Dict[str, float]]:
        # Convertimos el diccionario a DataFrame para el pipeline
        df = pd.DataFrame([data])
        
        # Obtenemos predicción y probabilidades (predict_burnout.py)
        proba = self.pipeline.predict_proba(df)[0]
        max_idx = proba.argmax()
        
        predicted_class = self.class_names[max_idx]
        confidence = float(proba[max_idx])
        
        # Mapa de probabilidades por clase
        prob_map = {self.class_names[i]: float(proba[i]) for i in range(len(self.class_names))}
        
        return predicted_class, confidence, prob_map

# Instancia única para toda la aplicación
ml_loader = ModelLoader()
