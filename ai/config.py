"""
AI Module Configuration

Central configuration for all AI models and training parameters.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ModelConfig:
    """Configuration for a single model."""
    name: str
    model_type: str
    hyperparameters: Dict
    features: List[str]
    target: str
    output_path: str


@dataclass
class TrainingConfig:
    """Training configuration."""
    batch_size: int = 32
    epochs: int = 100
    learning_rate: float = 0.001
    validation_split: float = 0.2
    early_stopping_patience: int = 10
    random_seed: int = 42


# Default configurations
FATIGUE_PREDICTOR_CONFIG = ModelConfig(
    name="fatigue_predictor",
    model_type="xgboost",
    hyperparameters={
        "n_estimators": 200,
        "max_depth": 6,
        "learning_rate": 0.1,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": 42
    },
    features=[
        "avg_bpm",
        "rr_ms",
        "avg_speed",
        "acceleration",
        "matches_last_7_days",
        "avg_fatigue_last_3",
        "position_encoded",
        "days_since_last_match"
    ],
    target="fatigue_prediction",
    output_path="ai/models/fatigue_predictor.pkl"
)

INJURY_RISK_CONFIG = ModelConfig(
    name="injury_risk",
    model_type="random_forest",
    hyperparameters={
        "n_estimators": 150,
        "max_depth": 10,
        "min_samples_split": 5,
        "random_state": 42,
        "class_weight": "balanced"
    },
    features=[
        "avg_bpm",
        "rr_ms",
        "fatigue_level",
        "matches_per_week",
        "fatigue_trend",
        "rest_days",
        "position_encoded",
        "age_group"
    ],
    target="injury_occurred",
    output_path="ai/models/injury_risk.pkl"
)

PERFORMANCE_FORECASTER_CONFIG = ModelConfig(
    name="performance_forecaster",
    model_type="prophet",
    hyperparameters={
        "seasonality_mode": "additive",
        "yearly_seasonality": False,
        "weekly_seasonality": True,
        "daily_seasonality": False,
        "interval_width": 0.95
    },
    features=["ds", "y", "bpm", "speed", "acceleration"],
    target="fatigue",
    output_path="ai/models/performance_forecaster.pkl"
)

# Feature engineering settings
FEATURE_CONFIG = {
    "window_sizes": [3, 7, 14],
    "fatigue_thresholds": {
        "low": 40,
        "moderate": 60,
        "high": 80,
        "critical": 90
    },
    "position_mapping": {
        "QB": 0, "RB": 1, "WR": 2, "TE": 3, "OL": 4,
        "DL": 5, "LB": 6, "CB": 7, "S": 8, "K": 9, "P": 10
    }
}

# Data paths
DATA_PATHS = {
    "players_file": "players_data.json",
    "matches_dir": "matches_history",
    "models_dir": "ai/models",
    "logs_dir": "ai/logs",
    "cache_dir": "ai/cache"
}