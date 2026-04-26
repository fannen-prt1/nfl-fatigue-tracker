"""
Fatigue Prediction Model Training

Trains a Random Forest classifier to predict fatigue levels (0-3) from sensor data.
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, Any
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    f1_score, precision_score, recall_score
)
import joblib
from datetime import datetime


class FatigueModel:
    """
    Fatigue level prediction model using Random Forest.
    """

    # Class labels
    LABELS = {
        0: 'Low',
        1: 'Moderate',
        2: 'High',
        3: 'Critical'
    }

    def __init__(self):
        self.model = None
        self.feature_names = None
        self.scaler_params = {}
        self.label_distribution = {}
        self.is_trained = False

    def preprocess_data(self, data_dir: str = None) -> Tuple[np.ndarray, np.ndarray, list]:
        """
        Preprocess sensor data and prepare for training.

        Args:
            data_dir: Path to processed data directory

        Returns:
            Tuple of (X, y, feature_names)
        """
        print("="*60)
        print("STEP 1: DATA PREPROCESSING")
        print("="*60)

        if data_dir is None:
            script_dir = Path(__file__).parent
            data_dir = script_dir.parent / 'data'

        # Initialize preprocessor
        preprocessor = SensorDataPreprocessor(data_dir)

        # Load and process raw data
        preprocessor.load_raw_data()
        df = preprocessor.align_and_merge()
        df = preprocessor.handle_missing_values(df)

        # Calculate fatigue scores and create labels
        df = preprocessor.calculate_fatigue_score(df)
        df = preprocessor.create_fatigue_labels(df)

        # Normalize features (save params for inference)
        df, self.scaler_params = preprocessor.normalize_features(df)

        # Get feature matrix and labels
        X, feature_names = preprocessor.get_feature_matrix(df)
        y = preprocessor.get_labels(df)

        # Store feature names
        self.feature_names = feature_names

        print(f"\nData Summary:")
        print(f"  Samples: {X.shape[0]}")
        print(f"  Features: {X.shape[1]}")
        print(f"  Label distribution:")

        unique, counts = np.unique(y, return_counts=True)
        for label, count in zip(unique, counts):
            pct = count / len(y) * 100
            self.label_distribution[int(label)] = int(count)
            print(f"    {label} ({self.LABELS[label]}): {count} ({pct:.1f}%)")

        return X, y, feature_names

    def load_processed_data(self, csv_path: str) -> Tuple[np.ndarray, np.ndarray, list]:
        """
        Load preprocessed data from CSV.

        Args:
            csv_path: Path to CSV file

        Returns:
            Tuple of (X, y, feature_names)
        """
        print(f"Loading data from: {csv_path}")

        df = pd.read_csv(csv_path)

        print(f"DataFrame columns: {df.columns.tolist()}")

        # Exclude target columns from features
        exclude_cols = ['timestamp_idx', 'fatigue_score', 'fatigue_level']
        feature_cols = [col for col in df.columns if col not in exclude_cols]

        X = df[feature_cols].values
        y = df['fatigue_level'].values

        self.feature_names = feature_cols

        # Print label distribution
        print("\nLabel distribution:")
        unique, counts = np.unique(y, return_counts=True)
        for label, count in zip(unique, counts):
            pct = count / len(y) * 100
            print(f"  {label} ({self.LABELS.get(label, 'Unknown')}): {count} ({pct:.1f}%)")

        return X, y, feature_cols

    def train(self, X: np.ndarray, y: np.ndarray,
              model_type: str = 'random_forest',
              test_size: float = 0.2,
              random_state: int = 42) -> Dict[str, Any]:
        """
        Train the fatigue prediction model.

        Args:
            X: Feature matrix
            y: Labels
            model_type: 'random_forest' or 'gradient_boosting'
            test_size: Proportion for test set
            random_state: Random seed

        Returns:
            Training results dictionary
        """
        print("\n" + "="*60)
        print("STEP 2: MODEL TRAINING")
        print("="*60)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state,
            stratify=y  # Maintain class distribution
        )

        print(f"\nTrain/Test Split:")
        print(f"  Training samples: {len(X_train)}")
        print(f"  Test samples: {len(X_test)}")

        # Initialize model
        if model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                class_weight='balanced',  # Handle class imbalance
                random_state=random_state,
                n_jobs=-1
            )
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=random_state
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        # Train
        print(f"\nTraining {model_type} model...")
        self.model.fit(X_train, y_train)

        # Cross-validation
        print("\nCross-validation (5-fold)...")
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=cv, scoring='accuracy')
        print(f"  CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")

        # Evaluate on test set
        y_pred = self.model.predict(X_test)

        # Get unique labels in the data
        unique_labels = sorted(np.unique(np.concatenate([y_test, y_pred])))
        target_names = [self.LABELS[i] for i in unique_labels]

        results = {
            'accuracy': accuracy_score(y_test, y_pred),
            'f1_macro': f1_score(y_test, y_pred, average='macro', zero_division=0),
            'f1_weighted': f1_score(y_test, y_pred, average='weighted', zero_division=0),
            'precision_macro': precision_score(y_test, y_pred, average='macro', zero_division=0),
            'recall_macro': recall_score(y_test, y_pred, average='macro', zero_division=0),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'classification_report': classification_report(
                y_test, y_pred,
                target_names=target_names,
                zero_division=0
            )
        }

        print(f"\nTest Set Evaluation:")
        print(f"  Accuracy:  {results['accuracy']:.4f}")
        print(f"  F1 (macro): {results['f1_macro']:.4f}")
        print(f"  Precision: {results['precision_macro']:.4f}")
        print(f"  Recall:    {results['recall_macro']:.4f}")

        print("\nClassification Report:")
        print(results['classification_report'])

        print("\nConfusion Matrix:")
        cm = confusion_matrix(y_test, y_pred, labels=unique_labels)
        label_names = [self.LABELS[i] for i in unique_labels]

        label_width = max(len(name) for name in label_names)
        cell_width = max(5, label_width + 2)
        left_pad = len("Actual ") + label_width + 1

        print(" " * left_pad + "Predicted")
        print(" " * (len("Actual ") + label_width + 1) + "".join(f"{name:>{cell_width}}" for name in label_names))
        for r, row_name in enumerate(label_names):
            row_cells = "".join(f"{cm[r, c]:>{cell_width}d}" for c in range(len(label_names)))
            print(f"Actual {row_name:<{label_width}} {row_cells}")

        # Feature importance
        self._print_feature_importance(X)

        self.is_trained = True

        return results

    def _print_feature_importance(self, X: np.ndarray, top_n: int = 10):
        """Print top feature importances."""
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            indices = np.argsort(importances)[::-1]

            print(f"\nTop {top_n} Feature Importances:")
            for i in range(min(top_n, len(indices))):
                idx = indices[i]
                name = self.feature_names[idx] if self.feature_names else f"feature_{idx}"
                print(f"  {i+1}. {name}: {importances[idx]:.4f}")

    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict fatigue levels for new data.

        Args:
            X: Feature matrix (samples x features)

        Returns:
            Tuple of (predicted_labels, prediction_probabilities)
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")

        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)

        return predictions, probabilities

    def predict_level(self, X: np.ndarray) -> list:
        """
        Predict fatigue levels with human-readable labels.

        Args:
            X: Feature matrix

        Returns:
            List of dictionaries with prediction details
        """
        predictions, probabilities = self.predict(X)

        results = []
        for i, pred in enumerate(predictions):
            results.append({
                'level': int(pred),
                'label': self.LABELS[pred],
                'confidence': float(np.max(probabilities[i])),
                'probabilities': {
                    self.LABELS[j]: float(prob) for j, prob in enumerate(probabilities[i])
                }
            })

        return results

    def save(self, filepath: str):
        """Save model to disk."""
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names,
            'scaler_params': self.scaler_params,
            'label_distribution': self.label_distribution,
            'labels': self.LABELS,
            'is_trained': self.is_trained
        }
        joblib.dump(model_data, filepath)
        print(f"\nModel saved to: {filepath}")

    def load(self, filepath: str):
        """Load model from disk."""
        model_data = joblib.load(filepath)
        self.model = model_data['model']
        self.feature_names = model_data['feature_names']
        self.scaler_params = model_data['scaler_params']
        self.label_distribution = model_data['label_distribution']
        self.LABELS = model_data['labels']
        self.is_trained = model_data['is_trained']
        print(f"Model loaded from: {filepath}")


def main():
    """Main training pipeline."""
    # Paths
    script_dir = Path(__file__).parent
    ai_dir = script_dir.parent  # Go up from models/ to ai/
    data_dir = ai_dir / 'data'
    processed_dir = data_dir / 'processed'
    model_dir = script_dir
    model_dir.mkdir(exist_ok=True)

    # Initialize model
    fatigue_model = FatigueModel()

    # Check for existing processed data
    processed_files = list(processed_dir.glob("sensor_features_*.csv"))

    if processed_files:
        # Use most recent processed file
        csv_path = sorted(processed_files)[-1]
        print(f"Using existing processed data: {csv_path}")
        X, y, feature_names = fatigue_model.load_processed_data(str(csv_path))
    else:
        print("No processed data found. Please run sensor_preprocessor.py first.")
        return None

    # Train model
    results = fatigue_model.train(X, y, model_type='random_forest')

    # Save model
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_path = model_dir / f'fatigue_model_{timestamp}.pkl'
    fatigue_model.save(str(model_path))

    print("\n" + "="*60)
    print("TRAINING COMPLETE")
    print("="*60)
    print(f"Model: Random Forest Classifier")
    print(f"Features: {len(feature_names)}")
    print(f"Accuracy: {results['accuracy']:.4f}")
    print(f"Model saved: {model_path}")

    return fatigue_model


if __name__ == "__main__":
    main()