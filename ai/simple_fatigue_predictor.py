"""
Simplified Fatigue Predictor

This module provides a simple interface for predicting fatigue levels
from raw sensor data. Users only need to provide basic sensor readings,
and the system automatically computes all 33 features required by the model.
"""

import numpy as np
import joblib
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class SimpleFatiguePredictor:
    """
    Simplified fatigue predictor that auto-computes features from raw sensor data.

    Users only need to provide raw sensor samples:
    - ECG voltage readings
    - Heart rate BPM and RR intervals
    - IMU accelerometer samples (x, y, z)
    - IMU gyroscope samples (x, y, z)
    - Magnetometer samples (x, y, z)
    """

    LABELS = {
        0: 'Low',
        1: 'Moderate',
        2: 'High',
        3: 'Critical'
    }

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the predictor.

        Args:
            model_path: Path to trained model file (auto-detects latest if None)
        """
        self.model = None
        self.scaler_params = {}
        self.feature_names = []

        if model_path:
            self.load_model(model_path)
        else:
            # Auto-detect latest model
            script_dir = Path(__file__).parent
            model_dir = script_dir / 'models'
            model_files = list(model_dir.glob("fatigue_model_*.pkl"))

            if model_files:
                model_path = sorted(model_files)[-1]
                self.load_model(str(model_path))
            else:
                print("WARNING: No trained model found!")

    def load_model(self, model_path: str):
        """Load the trained model."""
        print(f"Loading model from: {model_path}")
        model_data = joblib.load(model_path)

        self.model = model_data['model']
        self.scaler_params = model_data['scaler_params']
        self.feature_names = model_data['feature_names']

        print(f"Model loaded: {len(self.feature_names)} features")
        print(f"Labels: {self.LABELS}")

    def extract_features(self,
                        ecg_samples: Optional[List[float]] = None,
                        heart_rate_bpm: Optional[float] = None,
                        rr_intervals: Optional[List[float]] = None,
                        accel_samples: Optional[List[Dict[str, float]]] = None,
                        gyro_samples: Optional[List[Dict[str, float]]] = None,
                        magn_samples: Optional[List[Dict[str, float]]] = None) -> Dict[str, float]:
        """
        Extract all 33 features from raw sensor samples.

        Args:
            ecg_samples: List of ECG voltage readings (e.g., [-52.3, -51.2, ...])
            heart_rate_bpm: Heart rate in beats per minute (e.g., 95.5)
            rr_intervals: List of RR interval durations in ms (e.g., [620, 610, 605])
            accel_samples: List of accelerometer samples with x, y, z values
                          (e.g., [{"x": 1.2, "y": 0.3, "z": 9.8}, ...])
            gyro_samples: List of gyroscope samples with x, y, z values
                         (e.g., [{"x": 0.1, "y": 0.2, "z": 0.05}, ...])
            magn_samples: List of magnetometer samples with x, y, z values
                         (e.g., [{"x": 0.1, "y": 0.2, "z": 0.3}, ...])

        Returns:
            Dictionary of extracted features (33 features)
        """
        features = {}

        # ========================================================================
        # HEART RATE & ECG FEATURES (11 features)
        # ========================================================================

        # HR and RR features (5 features)
        features['heart_rate_bpm'] = heart_rate_bpm if heart_rate_bpm is not None else 75.0

        if rr_intervals and len(rr_intervals) > 0:
            rr_arr = np.array(rr_intervals)
            features['rr_interval_ms'] = float(np.mean(rr_arr))
            features['rr_std_ms'] = float(np.std(rr_arr)) if len(rr_arr) > 1 else 0.0

            # RMSSD (Root Mean Square of Successive Differences)
            if len(rr_arr) > 1:
                successive_diffs = np.diff(rr_arr)
                features['rmssd_ms'] = float(np.sqrt(np.mean(successive_diffs ** 2)))
            else:
                features['rmssd_ms'] = 0.0
            features['rr_count'] = len(rr_intervals)
        else:
            features['rr_interval_ms'] = 800.0
            features['rr_std_ms'] = 50.0
            features['rmssd_ms'] = 30.0
            features['rr_count'] = 10

        # ECG features (6 features)
        if ecg_samples and len(ecg_samples) > 0:
            ecg_arr = np.array(ecg_samples)
            features['ecg_mean'] = float(np.mean(ecg_arr))
            features['ecg_std'] = float(np.std(ecg_arr))
            features['ecg_min'] = float(np.min(ecg_arr))
            features['ecg_max'] = float(np.max(ecg_arr))
            features['ecg_range'] = float(np.max(ecg_arr) - np.min(ecg_arr))
            features['ecg_rms'] = float(np.sqrt(np.mean(ecg_arr ** 2)))
        else:
            features['ecg_mean'] = 0.0
            features['ecg_std'] = 100.0
            features['ecg_min'] = -100.0
            features['ecg_max'] = 100.0
            features['ecg_range'] = 200.0
            features['ecg_rms'] = 70.7

        # ========================================================================
        # ACCELEROMETER FEATURES (8 features)
        # ========================================================================
        if accel_samples and len(accel_samples) > 0:
            accel_x = [s.get('x', 0) for s in accel_samples]
            accel_y = [s.get('y', 0) for s in accel_samples]
            accel_z = [s.get('z', 0) for s in accel_samples]

            features['accel_x_mean'] = float(np.mean(accel_x))
            features['accel_y_mean'] = float(np.mean(accel_y))
            features['accel_z_mean'] = float(np.mean(accel_z))
            features['accel_x_std'] = float(np.std(accel_x))
            features['accel_y_std'] = float(np.std(accel_y))
            features['accel_z_std'] = float(np.std(accel_z))

            # Magnitude
            accel_mag = np.sqrt(np.array(accel_x)**2 + np.array(accel_y)**2 + np.array(accel_z)**2)
            features['accel_magnitude_mean'] = float(np.mean(accel_mag))
            features['accel_magnitude_std'] = float(np.std(accel_mag))
        else:
            features['accel_x_mean'] = 0.0
            features['accel_y_mean'] = 0.0
            features['accel_z_mean'] = 9.8  # Gravity
            features['accel_x_std'] = 0.5
            features['accel_y_std'] = 0.5
            features['accel_z_std'] = 0.5
            features['accel_magnitude_mean'] = 9.8
            features['accel_magnitude_std'] = 0.5

        # ========================================================================
        # GYROSCOPE FEATURES (8 features)
        # ========================================================================
        if gyro_samples and len(gyro_samples) > 0:
            gyro_x = [s.get('x', 0) for s in gyro_samples]
            gyro_y = [s.get('y', 0) for s in gyro_samples]
            gyro_z = [s.get('z', 0) for s in gyro_samples]

            features['gyro_x_mean'] = float(np.mean(gyro_x))
            features['gyro_y_mean'] = float(np.mean(gyro_y))
            features['gyro_z_mean'] = float(np.mean(gyro_z))
            features['gyro_x_std'] = float(np.std(gyro_x))
            features['gyro_y_std'] = float(np.std(gyro_y))
            features['gyro_z_std'] = float(np.std(gyro_z))

            # Magnitude
            gyro_mag = np.sqrt(np.array(gyro_x)**2 + np.array(gyro_y)**2 + np.array(gyro_z)**2)
            features['gyro_magnitude_mean'] = float(np.mean(gyro_mag))
            features['gyro_magnitude_std'] = float(np.std(gyro_mag))
        else:
            features['gyro_x_mean'] = 0.0
            features['gyro_y_mean'] = 0.0
            features['gyro_z_mean'] = 0.0
            features['gyro_x_std'] = 1.0
            features['gyro_y_std'] = 1.0
            features['gyro_z_std'] = 1.0
            features['gyro_magnitude_mean'] = 1.0
            features['gyro_magnitude_std'] = 1.0

        # ========================================================================
        # MAGNETOMETER FEATURES (6 features)
        # ========================================================================
        if magn_samples and len(magn_samples) > 0:
            magn_x = [s.get('x', 0) for s in magn_samples]
            magn_y = [s.get('y', 0) for s in magn_samples]
            magn_z = [s.get('z', 0) for s in magn_samples]

            features['magn_x_mean'] = float(np.mean(magn_x))
            features['magn_y_mean'] = float(np.mean(magn_y))
            features['magn_z_mean'] = float(np.mean(magn_z))
            features['magn_x_std'] = float(np.std(magn_x))
            features['magn_y_std'] = float(np.std(magn_y))
            features['magn_z_std'] = float(np.std(magn_z))
        else:
            features['magn_x_mean'] = 0.0
            features['magn_y_mean'] = 0.0
            features['magn_z_mean'] = 0.0
            features['magn_x_std'] = 0.1
            features['magn_y_std'] = 0.1
            features['magn_z_std'] = 0.1

        return features

    def normalize_features(self, features: Dict[str, float]) -> np.ndarray:
        """
        Normalize features using the scaler parameters from training.

        Args:
            features: Dictionary of raw features

        Returns:
            Normalized feature vector
        """
        normalized = []

        for fname in self.feature_names:
            if fname in features:
                val = features[fname]

                # Apply StandardScaler normalization
                if fname in self.scaler_params:
                    mean_val = self.scaler_params[fname]['mean']
                    std_val = self.scaler_params[fname]['std']

                    if std_val > 0:
                        normalized_val = (val - mean_val) / std_val
                    else:
                        normalized_val = 0
                else:
                    normalized_val = val

                normalized.append(normalized_val)
            else:
                # Missing feature - use 0
                normalized.append(0.0)

        return np.array(normalized).reshape(1, -1)

    def predict(self,
               ecg_samples: Optional[List[float]] = None,
               heart_rate_bpm: Optional[float] = None,
               rr_intervals: Optional[List[float]] = None,
               accel_samples: Optional[List[Dict[str, float]]] = None,
               gyro_samples: Optional[List[Dict[str, float]]] = None,
               magn_samples: Optional[List[Dict[str, float]]] = None) -> Dict:
        """
        Predict fatigue level from raw sensor samples.

        Args:
            ecg_samples: ECG voltage readings
            heart_rate_bpm: Heart rate in BPM
            rr_intervals: RR interval durations
            accel_samples: Accelerometer samples
            gyro_samples: Gyroscope samples
            magn_samples: Magnetometer samples

        Returns:
            Prediction results dictionary
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        # Extract features from raw samples
        features = self.extract_features(
            ecg_samples=ecg_samples,
            heart_rate_bpm=heart_rate_bpm,
            rr_intervals=rr_intervals,
            accel_samples=accel_samples,
            gyro_samples=gyro_samples,
            magn_samples=magn_samples
        )

        # Normalize features
        X = self.normalize_features(features)

        # Make prediction
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]

        # Format result
        result = {
            'level': int(prediction),
            'label': self.LABELS.get(prediction, 'Unknown'),
            'confidence': float(np.max(probabilities)),
            'probabilities': {
                self.LABELS[i]: float(prob) for i, prob in enumerate(probabilities)
            }
        }

        return result

    def predict_batch(self, samples: List[Dict]) -> List[Dict]:
        """
        Predict fatigue for multiple samples.

        Args:
            samples: List of sample dictionaries with raw sensor data

        Returns:
            List of prediction results
        """
        results = []
        for i, sample in enumerate(samples):
            result = self.predict(**sample)
            result['sample_id'] = i
            results.append(result)
        return results

    def print_prediction(self, result: Dict):
        """Pretty print a prediction result."""
        print("\n" + "="*60)
        print("FATIGUE PREDICTION")
        print("="*60)
        print(f"Fatigue Level: {result['level']} ({result['label']})")
        print(f"Confidence: {result['confidence']*100:.1f}%")
        print("\nProbabilities:")
        for label, prob in result['probabilities'].items():
            bar = '=' * int(prob * 20)
            print(f"  {label:10s}: {prob*100:5.1f}% {bar}")
        print("="*60)


def main():
    """Demo of the simplified predictor."""
    print("="*60)
    print("SIMPLIFIED FATIGUE PREDICTOR - DEMO")
    print("="*60)

    # Initialize predictor
    predictor = SimpleFatiguePredictor()

    # Example 1: Minimal input (just heart rate)
    print("\n--- Example 1: Minimal Input (Heart Rate Only) ---")
    result1 = predictor.predict(heart_rate_bpm=110)
    predictor.print_prediction(result1)

    # Example 2: Full sensor input
    print("\n--- Example 2: Full Sensor Input ---")

    # Simulated raw sensor data (what you'd get from a wearable)
    ecg_data = [-50 + np.random.randn()*10 for _ in range(100)]
    rr_data = [600 + np.random.randn()*30 for _ in range(10)]
    accel_data = [
        {"x": 1.0 + np.random.randn()*0.5, "y": 0.2 + np.random.randn()*0.3, "z": 9.8 + np.random.randn()*0.2}
        for _ in range(50)
    ]
    gyro_data = [
        {"x": 0.1 + np.random.randn()*0.1, "y": 0.2 + np.random.randn()*0.1, "z": 0.05 + np.random.randn()*0.1}
        for _ in range(50)
    ]
    magn_data = [
        {"x": 0.1 + np.random.randn()*0.05, "y": 0.2 + np.random.randn()*0.05, "z": 0.3 + np.random.randn()*0.05}
        for _ in range(50)
    ]

    result2 = predictor.predict(
        ecg_samples=ecg_data,
        heart_rate_bpm=95.5,
        rr_intervals=rr_data,
        accel_samples=accel_data,
        gyro_samples=gyro_data,
        magn_samples=magn_data
    )
    predictor.print_prediction(result2)

    # Example 3: High intensity activity
    print("\n--- Example 3: High Intensity Activity ---")

    active_accel = [
        {"x": np.random.randn()*3, "y": np.random.randn()*3, "z": 9.8 + np.random.randn()*3}
        for _ in range(100)
    ]
    active_gyro = [
        {"x": np.random.randn()*5, "y": np.random.randn()*5, "z": np.random.randn()*5}
        for _ in range(100)
    ]

    result3 = predictor.predict(
        heart_rate_bpm=145,
        rr_intervals=[550 + np.random.randn()*20 for _ in range(10)],
        accel_samples=active_accel,
        gyro_samples=active_gyro
    )
    predictor.print_prediction(result3)

    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("\nFor real use, provide actual sensor data:")
    print("  - ecg_samples: List[float] - ECG voltage readings")
    print("  - heart_rate_bpm: float - Current heart rate")
    print("  - rr_intervals: List[float] - RR interval durations (ms)")
    print("  - accel_samples: List[Dict] - Accelerometer x,y,z readings")
    print("  - gyro_samples: List[Dict] - Gyroscope x,y,z readings")
    print("  - magn_samples: List[Dict] - Magnetometer x,y,z readings")


if __name__ == "__main__":
    main()