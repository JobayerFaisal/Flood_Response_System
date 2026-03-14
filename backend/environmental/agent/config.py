# backend/environmental/agent/config.py

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"
DEPTH_MODEL_PATH = MODEL_DIR / "flood_depth_model.h5"

DEFAULT_TREND = "rising"

# Risk scoring weights
WEATHER_WEIGHT = 0.35
SATELLITE_WEIGHT = 0.40
SOCIAL_WEIGHT = 0.25

# Detection thresholds
FLOOD_DETECTION_THRESHOLD = 0.65
SEVERITY_LOW_THRESHOLD = 0.35
SEVERITY_MEDIUM_THRESHOLD = 0.55
SEVERITY_HIGH_THRESHOLD = 0.75
SEVERITY_CRITICAL_THRESHOLD = 0.90