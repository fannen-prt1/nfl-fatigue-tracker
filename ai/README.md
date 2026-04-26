# AI Module

Machine learning components for the NFL Fatigue Tracker.

## Overview

This module provides ML-powered enhancements:

1. **Fatigue Prediction** - ML models that predict player fatigue beyond the rule-based calculation
2. **Injury Risk Assessment** - Classification models to identify players at risk
3. **Lineup Optimization** - ML-enhanced lineup selection considering predictions
4. **Performance Forecasting** - Time-series models for trend prediction

## Structure

```
ai/
├── __init__.py              # Main module exports
├── config.py                # Model configurations
├── api_integration.py       # FastAPI endpoints for AI features
├── requirements.txt         # AI-specific dependencies
│
├── predictor.py            # Fatigue prediction model
├── injury_risk.py          # Injury risk assessment
├── lineup_optimizer.py     # ML lineup optimization
├── performance_forecaster.py # Time-series forecasting
│
├── data/                   # Data handling
│   ├── __init__.py
│   ├── preprocessor.py     # Data preprocessing
│   └── loader.py           # Data loading utilities
│
├── features/               # Feature engineering
│   ├── __init__.py
│   ├── engineer.py         # Feature engineering pipeline
│   └── extractor.py        # Feature extractors
│
├── training/               # Model training
│   ├── __init__.py
│   ├── trainer.py          # Model trainer
│   ├── evaluator.py          # Model evaluation
│   └── pipeline.py         # Training pipeline
│
├── utils/                  # Utilities
│   ├── __init__.py
│   ├── metrics.py            # Metric calculations
│   ├── visualization.py      # Plotting functions
│   └── logger.py             # Logging setup
│
├── models/                 # Saved model files (gitignored)
├── logs/                   # Training logs (gitignored)
└── cache/                  # Cached data (gitignored)
```

## Installation

```bash
# From project root with venv activated
pip install -r ai/requirements.txt
```

## Usage

### Training Models

```python
from ai.training.pipeline import TrainingPipeline

pipeline = TrainingPipeline()
pipeline.run()
```

### Making Predictions

```python
from ai import FatiguePredictor

predictor = FatiguePredictor("ai/models/fatigue_predictor.pkl")
fatigue = predictor.predict_single(player_data)
```

### API Endpoints

The AI module adds these FastAPI endpoints:

- `POST /api/ai/predict/fatigue` - Predict fatigue
- `POST /api/ai/assess/injury-risk` - Assess injury risk
- `POST /api/ai/optimize/lineup` - ML lineup optimization
- `POST /api/ai/forecast/performance` - Performance forecasting

## Models

| Model | Type | Purpose |
|-------|------|---------|
| Fatigue Predictor | XGBoost | Predict fatigue scores |
| Injury Risk | Random Forest | Classify injury risk |
| Performance Forecaster | Prophet | Time-series forecasting |
| Lineup Optimizer | Genetic Algorithm | Optimal lineup selection |

## Features

The models use these features:

- **Physiological**: BPM, HRV (RR interval)
- **Performance**: Speed, Acceleration
- **Temporal**: Days since last match, day of week
- **Aggregates**: Rolling averages (3, 7, 14 day windows)
- **Context**: Position, opponent

## Training Data

Models are trained on:
- Player baseline metrics from `players_data.json`
- Match history from `matches_history/`
- Calculated fatigue scores from current algorithm

## Development Status

This is a placeholder structure. Implementation needed:

- [ ] `FatiguePredictor.train()`
- [ ] `InjuryRiskAssessor.train()`
- [ ] `PerformanceForecaster.train()`
- [ ] Feature engineering implementation
- [ ] API endpoint implementations
- [ ] Model persistence (save/load)
- [ ] Training pipeline complete workflow
- [ ] Integration with existing `api.py`