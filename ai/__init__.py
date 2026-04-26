"""
AI Module for NFL Fatigue Tracker

This module provides machine learning capabilities for:
- Fatigue prediction using time-series and physiological data
- Injury risk assessment
- Player performance forecasting
- Optimal lineup recommendations
"""

from .predictor import FatiguePredictor
from .injury_risk import InjuryRiskAssessor
from .lineup_optimizer import LineupOptimizer
from .performance_forecaster import PerformanceForecaster

__all__ = [
    "FatiguePredictor",
    "InjuryRiskAssessor",
    "LineupOptimizer",
    "PerformanceForecaster",
]