from fastapi import FastAPI, HTTPException
from app.schemas.burnout_scheme import WorkerInput, BurnoutPredictionResponse
from app.core.model_loader import ml_loader
from app.core.explanation import explain_burnout_reasons
import uvicorn

app = FastAPI(
    title="Burnout AI Service",
    description="Servicio de predicción de riesgo de burnout",
    version="1.0.0"
)


@app.get("/health")
def health_check():
    return {
        "status"      : "healthy",
        "model_loaded": ml_loader.pipeline is not None,
    }


@app.post("/predict", response_model=BurnoutPredictionResponse)
async def predict(input_data: WorkerInput):
    try:
        # 1. Extraer features — excluir IDs, el modelo no los usa
        features_dict = input_data.model_dump(
            exclude={"worker_id", "survey_id"}
        )

        # 2. Predecir
        burnout_class, confidence, prob_map = ml_loader.predict(features_dict)

        # 3. Explicar razones
        reasons = explain_burnout_reasons(features_dict, burnout_class)

        # 4. Retornar — solo predice y explica, nada más
        return BurnoutPredictionResponse(
            worker_id          = input_data.worker_id,
            burnout_class      = burnout_class,
            burnout_confidence = round(confidence, 4),
            probabilities      = {k: round(v, 4) for k, v in prob_map.items()},
            reasons            = reasons,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en la predicción: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)