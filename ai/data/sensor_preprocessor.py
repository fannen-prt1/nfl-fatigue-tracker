"""
Sensor Data Preprocessor

Loads, cleans, aligns, and prepares wearable sensor data for AI model training.
Supports: ECG, Heart Rate, IMU (Accelerometer + Gyroscope), Magnetometer data.
"""

import json
import os
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class SensorDataPreprocessor:
    """
    Preprocesses raw wearable sensor data into ML-ready format.
    """

    def __init__(self, data_dir: str = None):
        """
        Initialize preprocessor.

        Args:
            data_dir: Directory containing sensor JSON files
        """
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent
        self.raw_data = {}
        self.processed_data = {}
        self.time_aligned_data = None

    def load_raw_data(self, session_prefix: str = None) -> Dict:
        """
        Load all sensor data files.

        Args:
            session_prefix: Optional prefix to filter files (e.g., '20251112T223140Z_253330006143')

        Returns:
            Dictionary of raw sensor data
        """
        if session_prefix is None:
            # Find the session folder
            data_files = list(self.data_dir.glob("*_heartRate_stream.json"))
            if not data_files:
                data_files = list(self.data_dir.glob("*.json"))
            if not data_files:
                raise FileNotFoundError("No JSON files found in data directory")

            # Extract prefix (everything before _heartRate_stream.json)
            session_prefix = data_files[0].name.replace('_heartRate_stream.json', '')
            print(f"Detected session prefix: {session_prefix}")

        print(f"Loading sensor data: {session_prefix}")

        # File mappings to readable names
        file_map = {
            'heartRate_stream': 'heart_rate',
            'ecg_stream': 'ecg',
            'imu_stream': 'imu',
            'gyro_stream': 'gyro',
            'magn_stream': 'magnetometer'
        }

        for suffix, name in file_map.items():
            filename = f"{session_prefix}_{suffix}.json"
            filepath = self.data_dir / filename

            if filepath.exists():
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    self.raw_data[name] = data.get('data', [])
                    print(f"  Loaded {name}: {len(self.raw_data[name])} records")
            else:
                print(f"  Warning: {filename} not found")

        return self.raw_data

    def process_heart_rate(self) -> pd.DataFrame:
        """
        Process heart rate data into features.

        Returns:
            DataFrame with HR features
        """
        records = self.raw_data.get('heart_rate', [])
        processed = []

        for i, record in enumerate(records):
            hr = record.get('heartRate', {})
            rr_data = hr.get('rrData', [])

            # Calculate HRV metrics
            if len(rr_data) > 0:
                rr_mean = np.mean(rr_data)
                rr_std = np.std(rr_data) if len(rr_data) > 1 else 0

                # RMSSD (root mean square of successive differences)
                if len(rr_data) > 1:
                    successive_diffs = np.diff(rr_data)
                    rmssd = np.sqrt(np.mean(successive_diffs ** 2))
                else:
                    rmssd = 0

                processed.append({
                    'timestamp_idx': i,
                    'heart_rate_bpm': hr.get('average', 0),
                    'rr_interval_ms': rr_mean,
                    'rr_std_ms': rr_std,
                    'rmssd_ms': rmssd,
                    'rr_count': len(rr_data)
                })

        df = pd.DataFrame(processed)
        print(f"Heart Rate: {len(df)} samples, {df.columns.tolist()}")
        return df

    def process_ecg(self) -> pd.DataFrame:
        """
        Process ECG data into features.

        Returns:
            DataFrame with ECG features
        """
        records = self.raw_data.get('ecg', [])
        processed = []

        for i, record in enumerate(records):
            ecg = record.get('ecg', {})
            samples = ecg.get('Samples', [])
            timestamp = ecg.get('Timestamp', 0)

            if len(samples) > 0:
                processed.append({
                    'timestamp_idx': i,
                    'timestamp_us': timestamp,
                    'ecg_mean': np.mean(samples),
                    'ecg_std': np.std(samples),
                    'ecg_min': np.min(samples),
                    'ecg_max': np.max(samples),
                    'ecg_range': np.max(samples) - np.min(samples),
                    'ecg_median': np.median(samples),
                    'ecg_skew': self._skewness(samples),
                    'ecg_kurtosis': self._kurtosis(samples),
                    'ecg_rms': np.sqrt(np.mean(np.array(samples) ** 2)),
                    'ecg_samples': [samples]  # Keep raw for advanced features
                })

        df = pd.DataFrame(processed)
        print(f"ECG: {len(df)} samples")
        return df

    def process_imu(self) -> pd.DataFrame:
        """
        Process IMU (Accelerometer + Gyroscope) data.

        Returns:
            DataFrame with IMU features
        """
        records = self.raw_data.get('imu', [])
        processed = []

        for i, record in enumerate(records):
            imu = record.get('imu', {})
            timestamp = imu.get('Timestamp', 0)
            accel_samples = imu.get('ArrayAcc', [])
            gyro_samples = imu.get('ArrayGyro', [])

            # Process accelerometer
            accel_x = [s.get('x', 0) for s in accel_samples]
            accel_y = [s.get('y', 0) for s in accel_samples]
            accel_z = [s.get('z', 0) for s in accel_samples]

            # Process gyroscope
            gyro_x = [s.get('x', 0) for s in gyro_samples]
            gyro_y = [s.get('y', 0) for s in gyro_samples]
            gyro_z = [s.get('z', 0) for s in gyro_samples]

            # Calculate magnitude
            accel_mag = np.sqrt(np.array(accel_x)**2 + np.array(accel_y)**2 + np.array(accel_z)**2)
            gyro_mag = np.sqrt(np.array(gyro_x)**2 + np.array(gyro_y)**2 + np.array(gyro_z)**2)

            processed.append({
                'timestamp_idx': i,
                'timestamp_us': timestamp,
                # Accelerometer stats
                'accel_x_mean': np.mean(accel_x),
                'accel_y_mean': np.mean(accel_y),
                'accel_z_mean': np.mean(accel_z),
                'accel_x_std': np.std(accel_x),
                'accel_y_std': np.std(accel_y),
                'accel_z_std': np.std(accel_z),
                'accel_magnitude_mean': np.mean(accel_mag),
                'accel_magnitude_std': np.std(accel_mag),
                # Gyroscope stats
                'gyro_x_mean': np.mean(gyro_x),
                'gyro_y_mean': np.mean(gyro_y),
                'gyro_z_mean': np.mean(gyro_z),
                'gyro_x_std': np.std(gyro_x),
                'gyro_y_std': np.std(gyro_y),
                'gyro_z_std': np.std(gyro_z),
                'gyro_magnitude_mean': np.mean(gyro_mag),
                'gyro_magnitude_std': np.std(gyro_mag),
            })

        df = pd.DataFrame(processed)
        print(f"IMU: {len(df)} samples")
        return df

    def process_gyro(self) -> pd.DataFrame:
        """
        Process standalone gyroscope data.

        Returns:
            DataFrame with gyroscope features
        """
        records = self.raw_data.get('gyro', [])
        processed = []

        for i, record in enumerate(records):
            gyro_data = record.get('gyro', {})
            timestamp = gyro_data.get('Timestamp', 0)
            samples = gyro_data.get('ArrayGyro', [])

            if samples:
                x_vals = [s.get('x', 0) for s in samples]
                y_vals = [s.get('y', 0) for s in samples]
                z_vals = [s.get('z', 0) for s in samples]

                processed.append({
                    'timestamp_idx': i,
                    'timestamp_us': timestamp,
                    'gyro_standalone_x_mean': np.mean(x_vals),
                    'gyro_standalone_y_mean': np.mean(y_vals),
                    'gyro_standalone_z_mean': np.mean(z_vals),
                    'gyro_standalone_x_std': np.std(x_vals),
                    'gyro_standalone_y_std': np.std(y_vals),
                    'gyro_standalone_z_std': np.std(z_vals),
                })

        df = pd.DataFrame(processed)
        print(f"Gyroscope: {len(df)} samples")
        return df

    def process_magnetometer(self) -> pd.DataFrame:
        """
        Process magnetometer data.

        Returns:
            DataFrame with magnetometer features
        """
        records = self.raw_data.get('magnetometer', [])
        processed = []

        for i, record in enumerate(records):
            magn_data = record.get('magn', {})
            timestamp = magn_data.get('Timestamp', 0)
            samples = magn_data.get('ArrayMagn', [])

            if samples:
                x_vals = [s.get('x', 0) for s in samples]
                y_vals = [s.get('y', 0) for s in samples]
                z_vals = [s.get('z', 0) for s in samples]

                processed.append({
                    'timestamp_idx': i,
                    'timestamp_us': timestamp,
                    'magn_x_mean': np.mean(x_vals),
                    'magn_y_mean': np.mean(y_vals),
                    'magn_z_mean': np.mean(z_vals),
                    'magn_x_std': np.std(x_vals),
                    'magn_y_std': np.std(y_vals),
                    'magn_z_std': np.std(z_vals),
                })

        df = pd.DataFrame(processed)
        print(f"Magnetometer: {len(df)} samples")
        return df

    def align_and_merge(self) -> pd.DataFrame:
        """
        Align all sensor data by timestamp and merge into single DataFrame.

        Returns:
            Merged DataFrame with all features
        """
        print("\nAligning and merging sensor data...")

        # Process each sensor type
        hr_df = self.process_heart_rate()
        ecg_df = self.process_ecg()
        imu_df = self.process_imu()
        gyro_df = self.process_gyro()
        magn_df = self.process_magnetometer()

        # Start with HR data as base (lowest sampling rate)
        merged = hr_df.copy()

        # Merge ECG (approximate alignment by index ratio)
        if len(ecg_df) > 0 and len(hr_df) > 0:
            ratio = len(ecg_df) / len(hr_df)
            ecg_df['hr_idx'] = (ecg_df['timestamp_idx'] / ratio).astype(int)
            ecg_agg = ecg_df.groupby('hr_idx').agg({
                'ecg_mean': 'mean',
                'ecg_std': 'mean',
                'ecg_min': 'min',
                'ecg_max': 'max',
                'ecg_range': 'mean',
                'ecg_rms': 'mean'
            }).reset_index(drop=True)
            merged = pd.concat([merged, ecg_agg], axis=1)

        # Merge IMU
        if len(imu_df) > 0 and len(hr_df) > 0:
            ratio = len(imu_df) / len(hr_df)
            imu_df['hr_idx'] = (imu_df['timestamp_idx'] / ratio).astype(int)
            imu_agg = imu_df.groupby('hr_idx').agg({
                'accel_x_mean': 'mean', 'accel_y_mean': 'mean', 'accel_z_mean': 'mean',
                'accel_x_std': 'mean', 'accel_y_std': 'mean', 'accel_z_std': 'mean',
                'accel_magnitude_mean': 'mean', 'accel_magnitude_std': 'mean',
                'gyro_x_mean': 'mean', 'gyro_y_mean': 'mean', 'gyro_z_mean': 'mean',
                'gyro_x_std': 'mean', 'gyro_y_std': 'mean', 'gyro_z_std': 'mean',
                'gyro_magnitude_mean': 'mean', 'gyro_magnitude_std': 'mean',
            }).reset_index(drop=True)
            merged = pd.concat([merged, imu_agg], axis=1)

        # Merge Magnetometer
        if len(magn_df) > 0 and len(hr_df) > 0:
            ratio = len(magn_df) / len(hr_df)
            magn_df['hr_idx'] = (magn_df['timestamp_idx'] / ratio).astype(int)
            magn_agg = magn_df.groupby('hr_idx').agg({
                'magn_x_mean': 'mean', 'magn_y_mean': 'mean', 'magn_z_mean': 'mean',
                'magn_x_std': 'mean', 'magn_y_std': 'mean', 'magn_z_std': 'mean',
            }).reset_index(drop=True)
            merged = pd.concat([merged, magn_agg], axis=1)

        self.time_aligned_data = merged
        print(f"\nMerged dataset: {len(merged)} rows x {len(merged.columns)} columns")
        return merged

    def handle_missing_values(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Handle missing values in the dataset.

        Args:
            df: DataFrame to process (uses time_aligned_data if None)

        Returns:
            DataFrame with missing values handled
        """
        if df is None:
            df = self.time_aligned_data

        print(f"\nHandling missing values...")
        print(f"  Before: {df.isnull().sum().sum()} missing values")

        # Fill with forward fill then backward fill
        df = df.ffill().bfill()

        # Fill any remaining with column means
        df = df.fillna(df.mean())

        print(f"  After: {df.isnull().sum().sum()} missing values")
        return df

    def calculate_fatigue_score(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Calculate fatigue score using heart rate and HRV features.

        This formula is adapted for wearable sensor data:
        - Heart Rate: Higher BPM = more fatigue
        - HRV (RR interval): Lower RR = less recovery = more fatigue
        - Activity: Higher acceleration/gyro = more exertion

        Args:
            df: DataFrame with sensor features

        Returns:
            DataFrame with fatigue_score column added
        """
        if df is None:
            df = self.time_aligned_data

        print("\nCalculating fatigue scores...")

        # Heart Rate Component (0-100)
        # Normal resting HR is 60-100 BPM
        # <60 = very low fatigue, >120 = very high
        hr_normalized = (df['heart_rate_bpm'] - 60) / 60  # 60 BPM = 0, 120 BPM = 1
        hr_component = np.clip(hr_normalized, 0, 1) * 30  # Max 30 points

        # HRV Component (0-100) - inverse relationship
        # Higher RR interval = lower HR = less fatigue
        # Normal RR: 600-1200ms
        hrv_normalized = 1 - ((df['rr_interval_ms'] - 400) / 800)  # 1200ms = 0 fatigue, 400ms = max
        hrv_component = np.clip(hrv_normalized, 0, 1) * 30  # Max 30 points

        # Activity Component from Accelerometer (0-100)
        # Deviation from gravity (9.8) indicates movement
        activity_from_accel = np.abs(df['accel_magnitude_mean'] - 9.8) / 9.8
        activity_component = np.clip(activity_from_accel, 0, 1) * 20  # Max 20 points

        # Activity from Gyroscope (0-100)
        activity_from_gyro = df['gyro_magnitude_mean'] / 10  # normalize
        gyro_component = np.clip(activity_from_gyro, 0, 1) * 20  # Max 20 points

        # Calculate total fatigue score (0-100)
        fatigue_score = hr_component + hrv_component + activity_component + gyro_component

        # Clamp to 0-100
        fatigue_score = fatigue_score.clip(0, 100)

        df['fatigue_score'] = fatigue_score

        print(f"  Fatigue score range: {fatigue_score.min():.2f} - {fatigue_score.max():.2f}")
        print(f"  HR component range: {hr_component.min():.2f} - {hr_component.max():.2f}")
        print(f"  HRV component range: {hrv_component.min():.2f} - {hrv_component.max():.2f}")
        print(f"  Activity component range: {(activity_component + gyro_component).min():.2f} - {(activity_component + gyro_component).max():.2f}")
        return df

    def create_fatigue_labels(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Create fatigue level labels (0-3) from fatigue scores.

        Levels:
        - 0 (Low):      fatigue_score <= 25
        - 1 (Moderate): fatigue_score <= 50
        - 2 (High):     fatigue_score <= 75
        - 3 (Critical): fatigue_score > 75

        Args:
            df: DataFrame with fatigue_score

        Returns:
            DataFrame with fatigue_level label column
        """
        if df is None:
            df = self.time_aligned_data

        if 'fatigue_score' not in df.columns:
            df = self.calculate_fatigue_score(df)

        print("\nCreating fatigue level labels...")

        # Bin into 4 levels
        conditions = [
            df['fatigue_score'] <= 25,
            (df['fatigue_score'] > 25) & (df['fatigue_score'] <= 50),
            (df['fatigue_score'] > 50) & (df['fatigue_score'] <= 75),
            df['fatigue_score'] > 75
        ]
        choices = [0, 1, 2, 3]

        df['fatigue_level'] = np.select(conditions, choices, default=0)

        # Print distribution
        label_counts = df['fatigue_level'].value_counts().sort_index()
        label_names = {0: 'Low', 1: 'Moderate', 2: 'High', 3: 'Critical'}

        print("  Label distribution:")
        for level, count in label_counts.items():
            pct = count / len(df) * 100
            print(f"    {level} ({label_names[level]}): {count} samples ({pct:.1f}%)")

        return df

    def normalize_features(self, df: pd.DataFrame = None,
                           fit: bool = True) -> Tuple[pd.DataFrame, Dict]:
        """
        Normalize numerical features using StandardScaler.

        Args:
            df: DataFrame to normalize
            fit: Whether to fit the scaler (True for training)

        Returns:
            Tuple of (normalized DataFrame, scaler parameters)
        """
        if df is None:
            df = self.time_aligned_data

        print("\nNormalizing features...")

        # Identify numeric columns (exclude timestamp_idx and target columns)
        exclude_cols = ['timestamp_idx', 'fatigue_score', 'fatigue_level']
        numeric_cols = [col for col in df.select_dtypes(include=[np.number]).columns
                       if col not in exclude_cols]

        scaler_params = {}

        # StandardScaler: (x - mean) / std
        for col in numeric_cols:
            mean_val = df[col].mean()
            std_val = df[col].std()

            if std_val > 0:
                df[col] = (df[col] - mean_val) / std_val
                scaler_params[col] = {'mean': mean_val, 'std': std_val}
            else:
                df[col] = 0
                scaler_params[col] = {'mean': mean_val, 'std': 1}

        print(f"  Normalized {len(numeric_cols)} features")
        return df, scaler_params

    def get_feature_matrix(self, df: pd.DataFrame = None) -> Tuple[np.ndarray, List[str]]:
        """
        Get feature matrix for ML training.

        Args:
            df: DataFrame to convert

        Returns:
            Tuple of (feature matrix, feature names)
        """
        if df is None:
            df = self.time_aligned_data

        # Select only numeric columns, exclude targets
        exclude_cols = ['timestamp_idx', 'fatigue_score', 'fatigue_level']
        feature_cols = [col for col in df.select_dtypes(include=[np.number]).columns
                       if col not in exclude_cols]

        X = df[feature_cols].values
        return X, feature_cols

    def get_labels(self, df: pd.DataFrame = None) -> np.ndarray:
        """
        Get fatigue level labels.

        Args:
            df: DataFrame

        Returns:
            Label array
        """
        if df is None:
            df = self.time_aligned_data

        return df['fatigue_level'].values

    def save_processed_data(self, output_dir: str = None,
                           format: str = 'csv') -> str:
        """
        Save processed data to disk.

        Args:
            output_dir: Output directory (defaults to data/processed)
            format: Output format ('csv', 'json', 'numpy')

        Returns:
            Path to saved file
        """
        if self.time_aligned_data is None:
            raise ValueError("No processed data to save. Run align_and_merge first.")

        if output_dir is None:
            output_dir = self.data_dir / 'processed'
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if format == 'csv':
            output_path = output_dir / f'sensor_features_{timestamp}.csv'
            self.time_aligned_data.to_csv(output_path, index=False)
        elif format == 'json':
            output_path = output_dir / f'sensor_features_{timestamp}.json'
            self.time_aligned_data.to_json(output_path, orient='records', indent=2)
        elif format == 'numpy':
            output_path = output_dir / f'sensor_features_{timestamp}.npy'
            X = self.get_feature_matrix()
            np.save(output_path, X)

        print(f"\nSaved processed data to: {output_path}")
        return str(output_path)

    @staticmethod
    def _skewness(data: List[float]) -> float:
        """Calculate skewness of data."""
        if len(data) < 3:
            return 0
        n = len(data)
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0
        return np.sum(((np.array(data) - mean) / std) ** 3) / n

    @staticmethod
    def _kurtosis(data: List[float]) -> float:
        """Calculate kurtosis of data."""
        if len(data) < 4:
            return 0
        n = len(data)
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0
        return np.sum(((np.array(data) - mean) / std) ** 4) / n - 3


def main():
    """Run preprocessing pipeline."""
    # Initialize preprocessor
    preprocessor = SensorDataPreprocessor()

    # Load raw sensor data
    preprocessor.load_raw_data()

    # Process and merge all sensors
    merged_df = preprocessor.align_and_merge()

    # Handle missing values
    merged_df = preprocessor.handle_missing_values(merged_df)

    # Calculate fatigue scores
    merged_df = preprocessor.calculate_fatigue_score(merged_df)

    # Create fatigue level labels
    merged_df = preprocessor.create_fatigue_labels(merged_df)

    # Store in preprocessor for saving
    preprocessor.time_aligned_data = merged_df

    # Save processed data (with labels, before normalization)
    # This is important - we want raw labels saved, not normalized
    output_path = preprocessor.save_processed_data(format='csv')

    # Create a copy for normalization (for ML training - modifies in place)
    normalized_df = merged_df.copy()
    normalized_df, scaler_params = preprocessor.normalize_features(normalized_df)

    # Get feature matrix and labels for ML
    X, feature_names = preprocessor.get_feature_matrix(normalized_df)
    y = preprocessor.get_labels(normalized_df)

    print("\n" + "="*60)
    print("PREPROCESSING COMPLETE")
    print("="*60)
    print(f"Feature matrix: {X.shape}")
    print(f"Labels: {y.shape}")
    print(f"Output file: {output_path}")
    print("\nReady for AI model training!")

    return preprocessor


if __name__ == "__main__":
    main()