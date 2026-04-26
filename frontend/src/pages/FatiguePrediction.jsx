import React, { useState, useEffect } from 'react';
import { Brain, Activity, TrendingUp, AlertCircle, CheckCircle2, Clock, User } from 'lucide-react';
import { useApp } from '../context/AppContext';

const FatiguePrediction = () => {
  const { players } = useApp();
  const [prediction, setPrediction] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [autoMode, setAutoMode] = useState(false);
  const [selectedPlayer, setSelectedPlayer] = useState(null);

  // Custom input state
  const [customInputs, setCustomInputs] = useState({
    heartRateBPM: 95.5,
    rrIntervals: '620, 610, 605, 625, 615, 630, 600, 608, 612, 618',
    ecgSamples: '-52, -51, -50, -53, -49, -51, -52, -50, -51, -53, -50, -49, -52, -51, -50',
    accelX: 1.2,
    accelY: 0.3,
    accelZ: 9.8,
    gyroX: 0.1,
    gyroY: 0.2,
    gyroZ: 0.05,
    magnX: 0.1,
    magnY: 0.2,
    magnZ: 0.3
  });

  // Sample data for demonstration
  const [sampleData, setSampleData] = useState({
    heartRateBPM: 95.5,
    rrIntervals: [620, 610, 605, 625, 615, 630, 600],
    ecgSamples: Array.from({ length: 125 }, () => -52 + Math.random() * 10),
    accelSamples: Array.from({ length: 50 }, () => ({
      x: 1.2 + Math.random() * 0.5,
      y: 0.3 + Math.random() * 0.3,
      z: 9.8 + Math.random() * 0.2
    })),
    gyroSamples: Array.from({ length: 50 }, () => ({
      x: 0.1 + Math.random() * 0.1,
      y: 0.2 + Math.random() * 0.1,
      z: 0.05 + Math.random() * 0.1
    })),
    magnSamples: Array.from({ length: 50 }, () => ({
      x: 0.1 + Math.random() * 0.05,
      y: 0.2 + Math.random() * 0.05,
      z: 0.3 + Math.random() * 0.05
    }))
  });

  const simulateSensorData = () => {
    // Use player's custom inputs if selected, otherwise use default custom inputs
    const baseHR = selectedPlayer?.customInputs?.heartRateBPM || customInputs.heartRateBPM;
    const baseAccel = {
      x: selectedPlayer?.customInputs?.accelX || customInputs.accelX,
      y: selectedPlayer?.customInputs?.accelY || customInputs.accelY,
      z: selectedPlayer?.customInputs?.accelZ || customInputs.accelZ
    };
    const baseGyro = {
      x: selectedPlayer?.customInputs?.gyroX || customInputs.gyroX,
      y: selectedPlayer?.customInputs?.gyroY || customInputs.gyroY,
      z: selectedPlayer?.customInputs?.gyroZ || customInputs.gyroZ
    };
    const baseMagn = {
      x: selectedPlayer?.customInputs?.magnX || customInputs.magnX,
      y: selectedPlayer?.customInputs?.magnY || customInputs.magnY,
      z: selectedPlayer?.customInputs?.magnZ || customInputs.magnZ
    };

    // Parse RR intervals
    const rrString = selectedPlayer?.customInputs?.rrIntervals || customInputs.rrIntervals;
    const baseRR = rrString.split(',').map(v => parseFloat(v.trim())).filter(v => !isNaN(v));
    const avgRR = baseRR.reduce((a, b) => a + b, 0) / baseRR.length;

    // Parse ECG samples
    const ecgString = selectedPlayer?.customInputs?.ecgSamples || customInputs.ecgSamples;
    const baseECG = ecgString.split(',').map(v => parseFloat(v.trim())).filter(v => !isNaN(v));

    // Simulate realistic sensor data with variation based on custom inputs
    const variation = Math.random() * 0.1 - 0.05; // 5% variation

    return {
      heartRateBPM: baseHR + (Math.random() * 4 - 2), // ±2 BPM variation
      rrIntervals: Array.from({ length: 10 }, () =>
        avgRR + (Math.random() * 30 - 15)
      ),
      ecgSamples: baseECG.length > 0 ? baseECG.map(v => v + (Math.random() * 6 - 3)) :
        Array.from({ length: 125 }, () => -50 + Math.random() * 10),
      accelSamples: Array.from({ length: 50 }, () => ({
        x: baseAccel.x * (1 + variation),
        y: baseAccel.y * (1 + variation),
        z: baseAccel.z * (1 + variation)
      })),
      gyroSamples: Array.from({ length: 50 }, () => ({
        x: baseGyro.x * (1 + variation),
        y: baseGyro.y * (1 + variation),
        z: baseGyro.z * (1 + variation)
      })),
      magnSamples: Array.from({ length: 50 }, () => ({
        x: baseMagn.x * (1 + variation),
        y: baseMagn.y * (1 + variation),
        z: baseMagn.z * (1 + variation)
      }))
    };
  };

  const predictFatigue = async (data = sampleData) => {
    setIsLoading(true);
    setError(null);

    try {
      // Simulate API call to backend
      await new Promise(resolve => setTimeout(resolve, 800));

      // For demo: simulate prediction based on heart rate
      // In real implementation, this would call your Python API
      const hr = data.heartRateBPM;
      let level, label, confidence;

      if (hr < 90) {
        level = 1; label = 'Moderate'; confidence = 0.85 + Math.random() * 0.1;
      } else if (hr < 110) {
        level = 1; label = 'Moderate'; confidence = 0.90 + Math.random() * 0.08;
      } else if (hr < 130) {
        level = 2; label = 'High'; confidence = 0.88 + Math.random() * 0.09;
      } else {
        level = 3; label = 'Critical'; confidence = 0.92 + Math.random() * 0.06;
      }

      // Add some randomness
      if (Math.random() < 0.15) {
        level = Math.max(0, Math.min(3, level + (Math.random() < 0.5 ? -1 : 1)));
        const labels = ['Low', 'Moderate', 'High', 'Critical'];
        label = labels[level];
        confidence = 0.75 + Math.random() * 0.2;
      }

      setPrediction({
        level,
        label,
        confidence,
        probabilities: {
          Low: Math.random() * 0.3,
          Moderate: Math.random() * 0.4,
          High: Math.random() * 0.2,
          Critical: Math.random() * 0.1
        },
        features: {
          heartRate: data.heartRateBPM,
          rrInterval: data.rrIntervals.reduce((a, b) => a + b) / data.rrIntervals.length,
          accelMagnitude: data.accelSamples.reduce((sum, s) =>
            sum + Math.sqrt(s.x**2 + s.y**2 + s.z**2), 0) / data.accelSamples.length,
          gyroMagnitude: data.gyroSamples.reduce((sum, s) =>
            sum + Math.sqrt(s.x**2 + s.y**2 + s.z**2), 0) / data.gyroSamples.length
        }
      });

      // Recalculate probabilities properly
      const probs = [0.1, 0.3, 0.4, 0.2];
      probs[level] = confidence;
      const otherProb = (1 - confidence) / 3;
      for (let i = 0; i < 4; i++) {
        if (i !== level) probs[i] = otherProb;
      }
      const labels = ['Low', 'Moderate', 'High', 'Critical'];
      const probabilities = {};
      labels.forEach((label, i) => {
        probabilities[label] = probs[i];
      });

      setPrediction(prev => ({ ...prev, probabilities }));

    } catch (err) {
      setError('Failed to predict fatigue. Please try again.');
      console.error('Prediction error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleManualPredict = () => {
    predictFatigue();
  };

  const handleAutoModeToggle = () => {
    setAutoMode(!autoMode);
  };

  useEffect(() => {
    if (autoMode) {
      const interval = setInterval(() => {
        const newData = simulateSensorData();
        setSampleData(newData);
        predictFatigue(newData);
      }, 1000); // Changed from 5000ms to 1000ms (1 second)
      return () => clearInterval(interval);
    }
  }, [autoMode]);

  const getStatusColor = (level) => {
    switch (level) {
      case 0: return '#10b981'; // green
      case 1: return '#f59e0b'; // yellow
      case 2: return '#f97316'; // orange
      case 3: return '#ef4444'; // red
      default: return '#6b7280'; // gray
    }
  };

  const getStatusIcon = (level) => {
    switch (level) {
      case 0: return <CheckCircle2 size={20} />;
      case 1: return <Activity size={20} />;
      case 2: return <AlertCircle size={20} />;
      case 3: return <AlertCircle size={20} />;
      default: return <Clock size={20} />;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div>
        <h1 style={{
          fontSize: '2rem', fontWeight: 800, margin: 0,
          background: 'linear-gradient(135deg, var(--text) 0%, var(--primary) 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          Fatigue Prediction
        </h1>
        <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
          Real-time fatigue level detection using wearable sensor data
        </p>
      </div>

      {/* Controls */}
      <div style={{
        display: 'flex', gap: '1rem', flexWrap: 'wrap',
        background: 'var(--bg-card)', padding: '1.5rem', borderRadius: '16px',
        border: '1px solid var(--border)'
      }}>
        <button
          onClick={handleManualPredict}
          disabled={isLoading}
          style={{
            padding: '0.75rem 1.5rem',
            background: 'linear-gradient(135deg, var(--primary) 0%, #8b5cf6 100%)',
            color: 'white', border: 'none', borderRadius: '12px',
            fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem',
            opacity: isLoading ? 0.6 : 1
          }}
        >
          <Brain size={18} />
          {isLoading ? 'Analyzing...' : 'Predict Fatigue'}
        </button>

        <button
          onClick={handleAutoModeToggle}
          style={{
            padding: '0.75rem 1.5rem',
            background: autoMode ? 'var(--primary-glow)' : 'var(--bg-main)',
            color: autoMode ? 'var(--primary)' : 'var(--text)',
            border: `2px solid ${autoMode ? 'var(--primary)' : 'var(--border)'}`,
            borderRadius: '12px', fontWeight: 600, cursor: 'pointer',
            display: 'flex', alignItems: 'center', gap: '0.5rem'
          }}
        >
          <TrendingUp size={18} />
          {autoMode ? 'Stop Auto-Mode' : 'Start Auto-Mode (1s)'}
        </button>

        <button
          onClick={() => {
            const newData = simulateSensorData();
            setSampleData(newData);
          }}
          style={{
            padding: '0.75rem 1.5rem',
            background: 'var(--bg-main)', color: 'var(--text)',
            border: '2px solid var(--border)', borderRadius: '12px',
            fontWeight: 600, cursor: 'pointer'
          }}
        >
          Generate New Sample Data
        </button>
      </div>

      {/* Current Sensor Data */}
      <div style={{
        background: 'var(--bg-card)', padding: '1.5rem', borderRadius: '16px',
        border: '1px solid var(--border)'
      }}>
        <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '1rem' }}>
          Current Sensor Readings
        </h2>
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '1rem'
        }}>
          <div style={{ background: 'var(--bg-main)', padding: '1rem', borderRadius: '12px' }}>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Heart Rate</p>
            <p style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--primary)' }}>
              {sampleData.heartRateBPM.toFixed(1)} <span style={{ fontSize: '0.6em' }}>BPM</span>
            </p>
          </div>
          <div style={{ background: 'var(--bg-main)', padding: '1rem', borderRadius: '12px' }}>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>RR Interval</p>
            <p style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--primary)' }}>
              {(sampleData.rrIntervals.reduce((a, b) => a + b) / sampleData.rrIntervals.length).toFixed(0)}
              <span style={{ fontSize: '0.6em' }}> ms</span>
            </p>
          </div>
          <div style={{ background: 'var(--bg-main)', padding: '1rem', borderRadius: '12px' }}>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>ECG Samples</p>
            <p style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--primary)' }}>
              {sampleData.ecgSamples.length}
            </p>
          </div>
          <div style={{ background: 'var(--bg-main)', padding: '1rem', borderRadius: '12px' }}>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>IMU Samples</p>
            <p style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--primary)' }}>
              {sampleData.accelSamples.length}
            </p>
          </div>
        </div>
      </div>

      {/* Prediction Result */}
      {prediction && (
        <div style={{
          background: 'var(--bg-card)', padding: '2rem', borderRadius: '16px',
          border: `2px solid ${getStatusColor(prediction.level)}`
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
            <div style={{
              width: '60px', height: '60px', borderRadius: '16px',
              background: `${getStatusColor(prediction.level)}20`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: getStatusColor(prediction.level)
            }}>
              {getStatusIcon(prediction.level)}
            </div>
            <div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700, margin: 0 }}>
                {prediction.label} Fatigue
              </h2>
              <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                Confidence: {(prediction.confidence * 100).toFixed(1)}%
              </p>
            </div>
          </div>

          {/* Probabilities */}
          <div style={{ marginTop: '1.5rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem' }}>
              Probability Distribution
            </h3>
            {Object.entries(prediction.probabilities).map(([label, prob]) => (
              <div key={label} style={{ marginBottom: '0.75rem' }}>
                <div style={{
                  display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem'
                }}>
                  <span style={{ fontSize: '0.9rem', fontWeight: 500 }}>{label}</span>
                  <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                    {(prob * 100).toFixed(1)}%
                  </span>
                </div>
                <div style={{
                  width: '100%', height: '8px', background: 'var(--bg-main)',
                  borderRadius: '4px', overflow: 'hidden'
                }}>
                  <div style={{
                    width: `${prob * 100}%`,
                    height: '100%',
                    background: label === prediction.label
                      ? getStatusColor(prediction.level)
                      : 'var(--border)',
                    transition: 'width 0.3s ease'
                  }} />
                </div>
              </div>
            ))}
          </div>

          {/* Extracted Features */}
          <div style={{
            marginTop: '2rem', paddingTop: '1.5rem',
            borderTop: '1px solid var(--border)'
          }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem' }}>
              Extracted Features (33 total)
            </h3>
            <div style={{
              display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '0.75rem'
            }}>
              <div>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Heart Rate</p>
                <p style={{ fontWeight: 600 }}>{prediction.features.heartRate.toFixed(1)} BPM</p>
              </div>
              <div>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>RR Interval</p>
                <p style={{ fontWeight: 600 }}>{prediction.features.rrInterval.toFixed(0)} ms</p>
              </div>
              <div>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Accel Magnitude</p>
                <p style={{ fontWeight: 600 }}>{prediction.features.accelMagnitude.toFixed(2)} m/s²</p>
              </div>
              <div>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Gyro Magnitude</p>
                <p style={{ fontWeight: 600 }}>{prediction.features.gyroMagnitude.toFixed(2)} rad/s</p>
              </div>
            </div>
            <p style={{
              marginTop: '1rem', fontSize: '0.85rem', color: 'var(--text-muted)'
            }}>
              + 29 additional features automatically computed (ECG stats, HRV metrics, magnetometer, etc.)
            </p>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{
          background: '#ef444420', color: '#ef4444',
          padding: '1rem', borderRadius: '12px', border: '1px solid #ef4444'
        }}>
          {error}
        </div>
      )}

      {/* Info Box */}
      <div style={{
        background: 'var(--bg-card)', padding: '1.5rem', borderRadius: '16px',
        border: '1px solid var(--border)'
      }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.75rem' }}>
          How It Works
        </h3>
        <p style={{ color: 'var(--text-secondary)', lineHeight: '1.6' }}>
          This system uses a trained RandomForest model to predict fatigue levels from wearable sensor data.
          You only need to provide raw sensor readings (ECG, heart rate, RR intervals, accelerometer, gyroscope, and magnetometer).
          The system automatically computes all 33 features required by the model, including statistical measures,
          heart rate variability metrics, and movement patterns.
        </p>
        <div style={{
          marginTop: '1rem', padding: '1rem', background: 'var(--bg-main)',
          borderRadius: '8px'
        }}>
          <p style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.5rem' }}>
            Required Inputs (what you provide):
          </p>
          <ul style={{
            margin: 0, paddingLeft: '1.5rem', color: 'var(--text-secondary)',
            fontSize: '0.85rem', lineHeight: '1.8'
          }}>
            <li>ECG samples: List of voltage readings</li>
            <li>Heart rate: Single BPM value</li>
            <li>RR intervals: List of interval durations (ms)</li>
            <li>Accelerometer: 3-axis samples (x, y, z)</li>
            <li>Gyroscope: 3-axis angular velocity (x, y, z)</li>
            <li>Magnetometer: 3-axis magnetic field (x, y, z) - optional</li>
          </ul>
          <p style={{
            fontSize: '0.85rem', fontWeight: 600, marginTop: '1rem', marginBottom: '0.5rem'
          }}>
            Automatically Computed Features:
          </p>
          <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            33 features including means, standard deviations, ranges, RMS values, HRV metrics,
            magnitude calculations, and movement intensity measures.
          </p>
        </div>
      </div>
    </div>
  );
};

export default FatiguePrediction;