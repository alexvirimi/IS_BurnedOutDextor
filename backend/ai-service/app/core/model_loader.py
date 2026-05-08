# app/core/model_loader.py
import joblib
import os

BASE = os.path.join(os.path.dirname(__file__), "../../models")


class ModelLoader:
    _pipeline = None
    _labels = None
    _encoder = None

    @classmethod
    def load(cls):
        cls._pipeline = joblib.load(f"{BASE}/burnout_pipeline.pkl")
        cls._labels = joblib.load(f"{BASE}/burnout_labels.pkl")
        cls._encoder = joblib.load(f"{BASE}/burnout_encoder.pkl")
        print("Modelos cargados correctamente")

    @classmethod
    def get_pipeline(cls): return cls._pipeline

    @classmethod
    def get_labels(cls): return cls._labels

    @classmethod
    def get_encoder(cls): return cls._encoder
