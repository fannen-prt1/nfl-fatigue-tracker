"""
Fatigue Prediction Inference Script

Loads the trained model and makes predictions on new sensor data.
"""

import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
import joblib


class FatiguePredictor:
    """
    Makes fatigue level predictions using trained model.
    """

    LABELS = {
        0: 'Low',
        1: 'Moderate',
        2: 'High',
        3: 'Critical'
    }

    def __init__(self, model_path: str = None):
        """
        Initialize predictor with trained model.

        Args:
            model_path: Path to saved model file
        """
        self.model = None
        self.feature_names = None
        self.scaler_params = {}

        if model_path:
            self.load_model(model_path)

    def load_model(self, filepath: str):
        """Load trained model from disk."""
        print(f"Loading model from: {filepath}")
        model_data = joblib.load(filepath)

        self.model = model_data['model']
        self.feature_names = model_data['feature_names']
        self.scaler_params = model_data['scaler_params']
        self.LABELS = model_data['labels']

        print(f"Model loaded successfully!")
        print(f"Features: {len(self.feature_names)}")
        print(f"Labels: {self.LABELS}")

    def preprocess_raw_data(self, raw_data_path: str) -> pd.DataFrame:
        """
        Preprocess raw sensor data using the preprocessor.

        Args:
            raw_data_path: Path to raw sensor JSON files directory

        Returns:
            DataFrame with processed features
        """
        # Import preprocessor
        sys.path.insert(0, str(Path(__file__).parent.parent / 'data'))
        from sensor_preprocessor import SensorDataPreprocessor

        print(f"\nPreprocessing raw data from: {raw_data_path}")

        preprocessor = SensorDataPreprocessor(raw_data_path)
        preprocessor.load_raw_data()
        df = preprocessor.align_and_merge()
        df = preprocessor.handle_missing_values(df)

        # Don't calculate labels - just normalize features
        df = preprocessor.calculate_fatigue_score(df)
        normalized_df, _ = preprocessor.normalize_features(df)

        # Get feature matrix
        X, feature_names = preprocessor.get_feature_matrix(normalized_df)

        # Create DataFrame with correct column names
        df_features = pd.DataFrame(X, columns=feature_names)

        return df_features

    def preprocess_single_sample(self, sample_data: dict) -> np.ndarray:
        """
        Preprocess a single sample for prediction.

        Args:
            sample_data: Dictionary with sensor values

        Returns:
            Feature vector
        """
        # Map input to expected features
        features = []

        for fname in self.feature_names:
            if fname in sample_data:
                val = sample_data[fname]
            elif fname in self.scaler_params:
                # Normalize using saved params
                params = self.scaler_params[fname]
                if fname in sample_data:
                    val = (sample_data[fname] - params['mean']) / params['std']
                else:
                    val = 0
            else:
                val = 0

            features.append(val)

        return np.array(features).reshape(1, -1)

    def predict(self, X: np.ndarray) -> dict:
        """
        Predict fatigue levels.

        Args:
            X: Feature matrix (samples x features)

        Returns:
            Dictionary with predictions
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        # Make predictions
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)

        results = []
        for i, pred in enumerate(predictions):
            result = {
                'sample': i,
                'level': int(pred),
                'label': self.LABELS.get(pred, 'Unknown'),
                'confidence': float(np.max(probabilities[i])),
                'probabilities': {}
            }

            # Map probabilities to labels
            for j, prob in enumerate(probabilities[i]):
                label = self.LABELS.get(j, f'Class_{j}')
                result['probabilities'][label] = float(prob)

            results.append(result)

        return {
            'predictions': results,
            'summary': {
                'total_samples': len(predictions),
                'level_counts': {
                    self.LABELS.get(i, f'Class_{i}'): int(np.sum(predictions == i))
                    for i in np.unique(predictions)
                }
            }
        }

    def predict_from_csv(self, csv_path: str) -> dict:
        """
        Predict fatigue levels from processed CSV data.

        Args:
            csv_path: Path to CSV with features

        Returns:
            Prediction results
        """
        print(f"Loading data from: {csv_path}")

        df = pd.read_csv(csv_path)

        # Exclude non-feature columns
        exclude_cols = ['timestamp_idx', 'fatigue_score', 'fatigue_level']
        feature_cols = [col for col in df.columns if col not in exclude_cols]

        X = df[feature_cols].values

        return self.predict(X)

    def print_predictions(self, results: dict):
        """Pretty print prediction results."""
        print("\n" + "="*60)
        print("PREDICTION RESULTS")
        print("="*60)

        for pred in results['predictions']:
            print(f"\nSample {pred['sample']}:")
            print(f"  Fatigue Level: {pred['level']} ({pred['label']})")
            print(f"  Confidence: {pred['confidence']*100:.1f}%")
            print("  Probabilities:")
            for label, prob in pred['probabilities'].items():
                bar = '=' * int(prob * 20)
                print(f"    {label:10s}: {prob*100:5.1f}% {bar}")

        print("\n" + "-"*40)
        print("Summary:")
        for label, count in results['summary']['level_counts'].items():
            print(f"  {label}: {count} samples")


def main():
    """Main inference pipeline."""
    # Paths
    script_dir = Path(__file__).parent
    model_dir = script_dir  # Models are in the same directory
    data_dir = script_dir.parent / 'data'
    processed_dir = data_dir / 'processed'

    # Find latest model
    model_files = list(model_dir.glob("fatigue_model_*.pkl"))
    if not model_files:
        print("No trained model found!")
        return

    model_path = sorted(model_files)[-1]

    # Initialize predictor
    predictor = FatiguePredictor(str(model_path))

    # Option 1: Predict from existing CSV
    csv_files = list(processed_dir.glob("sensor_features_*.csv"))
    if csv_files:
        csv_path = sorted(csv_files)[-1]
        results = predictor.predict_from_csv(str(csv_path))
        predictor.print_predictions(results)

    print("\n" + "="*60)
    print("HOW TO USE FOR NEW DATA")
    print("="*60)
    print("""
# Option 1: From CSV
predictor = FatiguePredictor('path/to/model.pkl')
results = predictor.predict_from_csv('path/to/features.csv')

# Option 2: From raw sensor data
predictor = FatiguePredictor('path/to/model.pkl')
df_features = predictor.preprocess_raw_data('path/to/sensor/files/')
# Need to add method to predict from DataFrame

# Option 3: Single prediction
sample = {
    'heart_rate_bpm': 95,
    'rr_interval_ms': 600,
    'accel_magnitude_mean': 10.5,
    'gyro_magnitude_mean': 3.2,
    # ... other features
}
X = predictor.preprocess_single_sample(sample)
results = predictor.predict(X)
""")


if __name__ == "__main__":
    main()