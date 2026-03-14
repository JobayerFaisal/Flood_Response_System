# backend/environmental/agent/loaders.py

from pathlib import Path
from typing import Optional, Protocol, Any

from backend.environmental.agent.config import DEPTH_MODEL_PATH


class PredictModel(Protocol):
    def predict(self, x: Any, verbose: int = 0) -> Any:
        ...


def load_depth_model() -> Optional[PredictModel]:
    """
    Safely load the flood depth model.
    Returns None if loading fails.
    """
    if not Path(DEPTH_MODEL_PATH).exists():
        return None

    try:
        import tensorflow as tf
        model = tf.keras.models.load_model(DEPTH_MODEL_PATH)
        return model
    except Exception:
        return None