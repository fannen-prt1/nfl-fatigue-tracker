"""
Metrics Utilities

Common metric calculations.
"""

import numpy as np
from typing import Dict


def calculate_metrics(y_true: np.ndarray,
                     y_pred: np.ndarray,
                     metrics: list = None) -> Dict:
    """
    Calculate multiple metrics at once.

    Args:
        y_true: Ground truth
        y_pred: Predictions
        metrics: List of metric names to calculate

    Returns:
        Dictionary of calculated metrics
    """
    # TODO: Implement metric calculations
    pass


def mean_absolute_percentage_error(y_true: np.ndarray,
                                  y_pred: np.ndarray) -> float:
    """
    Calculate MAPE.

    Args:
        y_true: Ground truth
        y_pred: Predictions

    Returns:
        MAPE value
    """
    # TODO: Implement MAPE
    pass


def root_mean_squared_error(y_true: np.ndarray,
                           y_pred: np.ndarray) -> float:
    """
    Calculate RMSE.

    Args:
        y_true: Ground truth
        y_pred: Predictions

    Returns:
        RMSE value
    """
    # TODO: Implement RMSE
    pass