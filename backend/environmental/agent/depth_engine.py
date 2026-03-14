# backend/environmental/agent/depth_engine.py

from typing import Dict, Any
import numpy as np

from backend.environmental.agent.schemas import DepthEstimationResult
from backend.environmental.agent.loaders import load_depth_model, PredictModel


class DepthEngine:
    def __init__(self):
        self.model: PredictModel | None = load_depth_model()

    def is_available(self) -> bool:
        return self.model is not None

    def build_feature_vector(
        self,
        weather_features: Dict[str, Any],
        satellite_features: Dict[str, Any],
        social_features: Dict[str, Any],
    ) -> np.ndarray:
        rainfall_score = float(weather_features.get("rainfall_score", 0.0))
        river_score = float(weather_features.get("river_score", 0.0))
        satellite_score = float(satellite_features.get("satellite_score", 0.0))
        extent_score = float(satellite_features.get("water_extent_score", 0.0))
        social_score = float(social_features.get("social_score", 0.0))

        return np.array(
            [[rainfall_score, river_score, satellite_score, extent_score, social_score]],
            dtype=np.float32
        )

    def predict_depth(
        self,
        weather_features: Dict[str, Any],
        satellite_features: Dict[str, Any],
        social_features: Dict[str, Any],
    ) -> DepthEstimationResult:
        if self.model is None:
            return DepthEstimationResult(
                estimated_depth_m=None,
                depth_model_used=False,
                confidence=0.0
            )

        try:
            feature_vector = self.build_feature_vector(
                weather_features,
                satellite_features,
                social_features
            )

            prediction = self.model.predict(feature_vector, verbose=0)
            depth_value = float(prediction[0][0])

            return DepthEstimationResult(
                estimated_depth_m=round(depth_value, 3),
                depth_model_used=True,
                confidence=0.75
            )
        except Exception:
            return DepthEstimationResult(
                estimated_depth_m=None,
                depth_model_used=False,
                confidence=0.0
            )