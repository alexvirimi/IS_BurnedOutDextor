from fastapi import FastAPI, HTTPException
from app.schemas.burnout_scheme import WorkerInput, BurnoutPredictionResult
from app.core.model_loader import ml_loader
import uvicorn

app = FastAPI(
    title="Burnout AI Service",
    description="Servicio de predicción de riesgo de burnout para trabajadores",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": ml_loader.pipeline is not None}

@app.post("/predict", response_model=BurnoutPredictionResult)
def predict(input_data: WorkerInput):
    try:
        # 1. Extraee los datos validados por Pydantic (excepto el worker_id)
        # Convertir a dict y quitar worker_id porque el modelo no lo usa
        features_dict = input_data.model_dump(exclude={"worker_id"})
        
        # 2. Realizar la predicción
        label, confidence, prob_map = ml_loader.predict(features_dict)
        
        # 3. Retornar el resultado según el esquema
        return BurnoutPredictionResult(
            worker_id=input_data.worker_id,
            burnout_class=label,
            burnout_score=confidence, # Usar la confianza como score principal
            probabilities=prob_map
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la predicción: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
