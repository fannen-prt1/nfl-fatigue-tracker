import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft, Heart, Gauge, TrendingUp, Zap, Plus, Edit3, Trash2, X, Upload, AlertTriangle, CheckCircle
} from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Cell, ReferenceLine, Area, AreaChart
} from 'recharts';
import { useApp } from '../context/AppContext';
import { getPlayerMatches, addMatch, updateMatch, deleteMatch, clearPlayerMatches, uploadPhoto } from '../utils/api';
import { motion, AnimatePresence } from 'framer-motion';

const getFatigueColor = (f) => f > 80 ? '#ff3d00' : f > 60 ? '#ffd600' : '#00c853';
const getFatigueLabel = (f) => f > 80 ? 'HIGH' : f > 60 ? 'MEDIUM' : 'LOW';

const inputStyle = {
  width: '100%', padding: '0.7rem 1rem', borderRadius: '10px', border: '1px solid var(--border)',
  background: 'var(--bg-elevated)', color: 'white', fontSize: '0.9rem', outline: 'none',
};

const PlayerDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { players, updatePlayer, deletePlayer, fetchPlayers } = useApp();
  const [matches, setMatches] = useState([]);
  const [loadingMatches, setLoadingMatches] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [showAddMatch, setShowAddMatch] = useState(false);
  const [showEditMatch, setShowEditMatch] = useState(null);
  const [showEditPlayer, setShowEditPlayer] = useState(false);
  const [matchForm, setMatchForm] = useState({
    avg_bpm: 75, rr_ms: 800, speed: 5, acceleration: 3.5, date: '', opponent: '', notes: '',
  });
  const [editForm, setEditForm] = useState({});
  const [error, setError] = useState('');

  const playerId = parseInt(id);
  const player = players.find(p => p.id === playerId);

  const loadMatches = async () => {
    try {
      setLoadingMatches(true);
      const data = await getPlayerMatches(playerId);
      setMatches(data);
    } catch { setMatches([]); }
    finally { setLoadingMatches(false); }
  };

  useEffect(() => {
    if (player) loadMatches();
  }, [playerId, player]);

  if (!player) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center' }}>
        <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem', marginBottom: '1rem' }}>Player not found.</p>
        <button onClick={() => navigate('/players')} style={{
          background: 'var(--primary)', color: 'white', padding: '0.75rem 1.5rem',
          borderRadius: '12px', fontWeight: 700,
        }}>Back to Players</button>
      </div>
    );
  }

  const handleAddMatch = async (e) => {
    e.preventDefault();
    try {
      await addMatch(playerId, matchForm);
      setShowAddMatch(false);
      setMatchForm({ avg_bpm: 75, rr_ms: 800, speed: 5, acceleration: 3.5, date: '', opponent: '', notes: '' });
      loadMatches();
    } catch (err) { setError(err.message); }
  };

  const handleEditMatch = async (e) => {
    e.preventDefault();
    try {
      await updateMatch(playerId, showEditMatch.match_number, {
        avg_bpm: showEditMatch.avg_bpm,
        rr_ms: showEditMatch.rr_ms,
        speed: showEditMatch.speed,
        acceleration: showEditMatch.acceleration,
        opponent: showEditMatch.opponent,
        notes: showEditMatch.notes,
      });
      setShowEditMatch(null);
      loadMatches();
    } catch (err) { setError(err.message); }
  };

  const handleDeleteMatch = async (matchNum) => {
    if (!window.confirm(`Delete Match ${matchNum}?`)) return;
    await deleteMatch(playerId, matchNum);
    loadMatches();
  };

  const handleClearMatches = async () => {
    if (!window.confirm('Clear ALL matches for this player?')) return;
    await clearPlayerMatches(playerId);
    loadMatches();
  };

  const handleUpdatePlayer = async (e) => {
    e.preventDefault();
    try {
      await updatePlayer(playerId, editForm);
      setShowEditPlayer(false);
      setError('');
    } catch (err) { setError(err.message); }
  };

  const handleRemovePlayer = async () => {
    if (!window.confirm(`Remove ${player.name} permanently?`)) return;
    await deletePlayer(playerId);
    navigate('/players');
  };

  const handlePhotoUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      await uploadPhoto(playerId, file);
      await fetchPlayers();
    } catch (err) { setError('Photo upload failed'); }
  };

  const analysis = player.fatigue_analysis || { high: [], moderate: [], good: [] };
  const suggestions = player.suggestions || [];

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'matches', label: `Matches (${matches.length})` },
    { id: 'charts', label: 'Performance Charts' },
    { id: 'manage', label: 'Management' },
  ];

  const Modal = ({ title, onClose, children }) => (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.7)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
    }} onClick={onClose}>
      <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
        style={{
          background: 'var(--bg-card)', borderRadius: '24px', padding: '2rem', width: '500px',
          maxHeight: '85vh', overflowY: 'auto', border: '1px solid var(--border)',
        }} onClick={e => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>{title}</h3>
          <button onClick={onClose} style={{ color: 'var(--text-muted)' }}><X size={20} /></button>
        </div>
        {children}
      </motion.div>
    </div>
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Back + Header */}
      <div>
        <button onClick={() => navigate('/players')} style={{
          display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)',
          fontWeight: 600, marginBottom: '1.5rem', fontSize: '0.9rem',
        }}><ArrowLeft size={18} /> Back to Roster</button>

        <div className="glass" style={{
          padding: '2rem', borderRadius: '24px', border: '1px solid var(--border)',
          display: 'flex', gap: '2rem', alignItems: 'center', flexWrap: 'wrap',
        }}>
          {/* Photo */}
          <div style={{ position: 'relative' }}>
            <div style={{
              width: '100px', height: '100px', borderRadius: '20px', background: 'var(--bg-elevated)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '2.5rem', fontWeight: 800, color: 'var(--primary)', overflow: 'hidden',
              border: '2px solid var(--border)',
            }}>
              {player.photo_url
                ? <img src={`http://localhost:8000${player.photo_url}`} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                : player.name.charAt(0)}
            </div>
            <label style={{
              position: 'absolute', bottom: -4, right: -4, width: '28px', height: '28px',
              borderRadius: '8px', background: 'var(--primary)', display: 'flex', alignItems: 'center',
              justifyContent: 'center', cursor: 'pointer', boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
            }}>
              <Upload size={14} color="white" />
              <input type="file" accept="image/*" onChange={handlePhotoUpload} style={{ display: 'none' }} />
            </label>
          </div>

          {/* Info */}
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
              <h2 style={{ fontSize: '1.75rem', fontWeight: 800 }}>{player.name}</h2>
              <span style={{
                padding: '0.3rem 0.7rem', borderRadius: '20px', fontSize: '0.7rem', fontWeight: 700,
                textTransform: 'uppercase',
                background: player.status === 'active' ? 'rgba(0,200,83,0.1)' : player.status === 'injured' ? 'rgba(255,61,0,0.1)' : 'rgba(255,214,0,0.1)',
                color: player.status === 'active' ? 'var(--success)' : player.status === 'injured' ? 'var(--danger)' : 'var(--warning)',
              }}>{player.status}</span>
            </div>
            <p style={{ color: 'var(--text-secondary)' }}>#{player.number} · {player.position} · {player.team}</p>
          </div>

          {/* Fatigue Ring */}
          <div style={{ textAlign: 'center' }}>
            <div style={{
              width: '90px', height: '90px', borderRadius: '50%', display: 'flex', alignItems: 'center',
              justifyContent: 'center', flexDirection: 'column',
              border: `4px solid ${getFatigueColor(player.fatigue_prediction)}`,
              boxShadow: `0 0 20px ${getFatigueColor(player.fatigue_prediction)}30`,
            }}>
              <span style={{ fontSize: '1.5rem', fontWeight: 800, color: getFatigueColor(player.fatigue_prediction) }}>
                {player.fatigue_prediction}%
              </span>
            </div>
            <p style={{ fontSize: '0.75rem', fontWeight: 700, color: getFatigueColor(player.fatigue_prediction), marginTop: '0.5rem' }}>
              {getFatigueLabel(player.fatigue_prediction)} FATIGUE
            </p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid var(--border)', paddingBottom: '0' }}>
        {tabs.map(tab => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{
            padding: '0.75rem 1.25rem', fontWeight: 700, fontSize: '0.9rem',
            color: activeTab === tab.id ? 'var(--primary)' : 'var(--text-secondary)',
            borderBottom: activeTab === tab.id ? '2px solid var(--primary)' : '2px solid transparent',
            transition: 'all 0.2s',
          }}>{tab.label}</button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* Metrics Row */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.25rem' }}>
            {[
              { label: 'Heart Rate', value: `${player.avg_bpm} BPM`, icon: Heart, color: '#e60000' },
              { label: 'HRV (RR_MS)', value: `${player.rr_ms} ms`, icon: Gauge, color: '#2196f3' },
              { label: 'Speed', value: `${player.avg_speed} yd/s`, icon: TrendingUp, color: '#00c853' },
              { label: 'Acceleration', value: `${player.acceleration} yd/s²`, icon: Zap, color: '#ffd600' },
            ].map(({ label, value, icon: Icon, color }) => (
              <div key={label} className="glass" style={{
                padding: '1.5rem', borderRadius: '20px', border: '1px solid var(--border)',
              }}>
                <div style={{
                  width: '40px', height: '40px', borderRadius: '12px', background: `${color}15`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '0.75rem',
                }}>
                  <Icon size={20} color={color} />
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>{label}</p>
                <p style={{ fontSize: '1.3rem', fontWeight: 800 }}>{value}</p>
              </div>
            ))}
          </div>

          {/* Analysis + Suggestions */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
            <div className="glass" style={{ padding: '2rem', borderRadius: '24px', border: '1px solid var(--border)' }}>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1.25rem' }}>Fatigue Analysis</h3>
              {analysis.high.length > 0 && (
                <div style={{ marginBottom: '1rem' }}>
                  <p style={{ fontSize: '0.8rem', fontWeight: 700, color: '#ff3d00', marginBottom: '0.5rem' }}>HIGH STRESS</p>
                  {analysis.high.map((r, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.3rem 0' }}>
                      <AlertTriangle size={14} color="#ff3d00" /><span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{r}</span>
                    </div>
                  ))}
                </div>
              )}
              {analysis.moderate.length > 0 && (
                <div style={{ marginBottom: '1rem' }}>
                  <p style={{ fontSize: '0.8rem', fontWeight: 700, color: '#ffd600', marginBottom: '0.5rem' }}>MODERATE</p>
                  {analysis.moderate.map((r, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.3rem 0' }}>
                      <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#ffd600' }} /><span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{r}</span>
                    </div>
                  ))}
                </div>
              )}
              {analysis.good.length > 0 && (
                <div>
                  <p style={{ fontSize: '0.8rem', fontWeight: 700, color: '#00c853', marginBottom: '0.5rem' }}>GOOD</p>
                  {analysis.good.map((r, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.3rem 0' }}>
                      <CheckCircle size={14} color="#00c853" /><span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{r}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="glass" style={{ padding: '2rem', borderRadius: '24px', border: '1px solid var(--border)' }}>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1.25rem' }}>Recommendations</h3>
              {suggestions.length === 0 ? (
                <p style={{ color: 'var(--text-muted)' }}>No specific recommendations at this time.</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {suggestions.map((s, i) => (
                    <div key={i} style={{
                      display: 'flex', alignItems: 'flex-start', gap: '0.75rem', padding: '0.75rem',
                      borderRadius: '12px', background: 'rgba(255,255,255,0.02)',
                    }}>
                      <div style={{
                        width: '24px', height: '24px', borderRadius: '8px', background: 'var(--primary-glow)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                        fontSize: '0.75rem', fontWeight: 700, color: 'var(--primary)',
                      }}>{i + 1}</div>
                      <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', lineHeight: 1.5 }}>{s}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'matches' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Match History</h3>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              {matches.length > 0 && (
                <button onClick={handleClearMatches} style={{
                  background: 'rgba(255,61,0,0.1)', color: 'var(--danger)', padding: '0.6rem 1.1rem',
                  borderRadius: '10px', fontWeight: 600, fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.4rem',
                  border: '1px solid rgba(255,61,0,0.2)',
                }}><Trash2 size={15} /> Clear All</button>
              )}
              <button onClick={() => setShowAddMatch(true)} style={{
                background: 'var(--primary)', color: 'white', padding: '0.6rem 1.1rem',
                borderRadius: '10px', fontWeight: 700, fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.4rem',
              }}><Plus size={15} /> Add Match</button>
            </div>
          </div>

          {loadingMatches ? (
            <p style={{ color: 'var(--text-muted)' }}>Loading matches...</p>
          ) : matches.length === 0 ? (
            <div className="glass" style={{ padding: '3rem', textAlign: 'center', borderRadius: '20px', border: '1px solid var(--border)' }}>
              <p style={{ color: 'var(--text-muted)' }}>No matches recorded. Add a match to start tracking performance.</p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: '0 0.5rem' }}>
                <thead>
                  <tr style={{ color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 700, textAlign: 'left' }}>
                    <th style={{ padding: '0 1rem 0.5rem' }}>#</th>
                    <th style={{ padding: '0 1rem 0.5rem' }}>DATE</th>
                    <th style={{ padding: '0 1rem 0.5rem' }}>OPPONENT</th>
                    <th style={{ padding: '0 1rem 0.5rem' }}>BPM</th>
                    <th style={{ padding: '0 1rem 0.5rem' }}>HRV</th>
                    <th style={{ padding: '0 1rem 0.5rem' }}>SPEED</th>
                    <th style={{ padding: '0 1rem 0.5rem' }}>ACCEL</th>
                    <th style={{ padding: '0 1rem 0.5rem' }}>FATIGUE</th>
                    <th style={{ padding: '0 1rem 0.5rem', textAlign: 'right' }}>ACTIONS</th>
                  </tr>
                </thead>
                <tbody>
                  {matches.map(m => (
                    <tr key={m.match_number} className="glass" style={{ borderRadius: '12px' }}>
                      <td style={{ padding: '0.75rem 1rem', borderTopLeftRadius: '12px', borderBottomLeftRadius: '12px', fontWeight: 700 }}>{m.match_number}</td>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{m.date || '—'}</td>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{m.opponent || '—'}</td>
                      <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>{m.avg_bpm}</td>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--text-secondary)' }}>{m.rr_ms}</td>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--text-secondary)' }}>{m.speed}</td>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--text-secondary)' }}>{m.acceleration}</td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <span style={{ fontWeight: 700, color: getFatigueColor(m.fatigue) }}>{m.fatigue}%</span>
                      </td>
                      <td style={{ padding: '0.75rem 1rem', textAlign: 'right', borderTopRightRadius: '12px', borderBottomRightRadius: '12px' }}>
                        <button onClick={() => setShowEditMatch({ ...m })} style={{ color: 'var(--text-muted)', marginRight: '0.5rem' }}><Edit3 size={15} /></button>
                        <button onClick={() => handleDeleteMatch(m.match_number)} style={{ color: 'var(--text-muted)' }}><Trash2 size={15} /></button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Match Summary Stats */}
          {matches.length > 0 && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
              {[
                { label: 'Avg Match BPM', value: (matches.reduce((s, m) => s + m.avg_bpm, 0) / matches.length).toFixed(1) },
                { label: 'Avg Match Fatigue', value: `${(matches.reduce((s, m) => s + m.fatigue, 0) / matches.length).toFixed(1)}%` },
                { label: 'Avg Match Speed', value: `${(matches.reduce((s, m) => s + m.speed, 0) / matches.length).toFixed(1)} yd/s` },
                { label: 'Total Matches', value: matches.length },
              ].map(({ label, value }) => (
                <div key={label} className="glass" style={{ padding: '1.25rem', borderRadius: '16px', border: '1px solid var(--border)' }}>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.3rem' }}>{label}</p>
                  <p style={{ fontSize: '1.3rem', fontWeight: 800 }}>{value}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'charts' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {matches.length < 2 ? (
            <div className="glass" style={{ padding: '3rem', textAlign: 'center', borderRadius: '20px', border: '1px solid var(--border)' }}>
              <p style={{ color: 'var(--text-muted)' }}>Need at least 2 matches to display charts.</p>
            </div>
          ) : (
            <>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                {/* Heart Metrics */}
                <div className="glass" style={{ padding: '2rem', borderRadius: '24px', border: '1px solid var(--border)' }}>
                  <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem' }}>Heart Rate & HRV Over Matches</h4>
                  <div style={{ height: '280px' }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={matches}>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                        <XAxis dataKey="match" stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                        <YAxis yAxisId="left" stroke="#e60000" fontSize={11} tickLine={false} axisLine={false} />
                        <YAxis yAxisId="right" orientation="right" stroke="#2196f3" fontSize={11} tickLine={false} axisLine={false} />
                        <Tooltip contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: '10px', color: '#fff' }} />
                        <Line yAxisId="left" type="monotone" dataKey="avg_bpm" stroke="#e60000" strokeWidth={2} dot={{ r: 4 }} name="BPM" />
                        <Line yAxisId="right" type="monotone" dataKey="rr_ms" stroke="#2196f3" strokeWidth={2} dot={{ r: 4 }} name="HRV (ms)" />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Fatigue */}
                <div className="glass" style={{ padding: '2rem', borderRadius: '24px', border: '1px solid var(--border)' }}>
                  <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem' }}>Fatigue Level Over Matches</h4>
                  <div style={{ height: '280px' }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={matches}>
                        <defs>
                          <linearGradient id="fatigueGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#9c27b0" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#9c27b0" stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                        <XAxis dataKey="match" stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                        <YAxis domain={[0, 100]} stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                        <Tooltip contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: '10px', color: '#fff' }} />
                        <ReferenceLine y={60} stroke="#ffd600" strokeDasharray="5 5" />
                        <ReferenceLine y={80} stroke="#ff3d00" strokeDasharray="5 5" />
                        <Area type="monotone" dataKey="fatigue" stroke="#9c27b0" strokeWidth={2} fillOpacity={1} fill="url(#fatigueGrad)" name="Fatigue %" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Speed */}
                <div className="glass" style={{ padding: '2rem', borderRadius: '24px', border: '1px solid var(--border)' }}>
                  <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem' }}>Speed Over Matches</h4>
                  <div style={{ height: '280px' }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={matches}>
                        <defs>
                          <linearGradient id="speedGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#00c853" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#00c853" stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                        <XAxis dataKey="match" stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                        <YAxis stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                        <Tooltip contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: '10px', color: '#fff' }} />
                        <Area type="monotone" dataKey="speed" stroke="#00c853" strokeWidth={2} fillOpacity={1} fill="url(#speedGrad)" name="Speed (yd/s)" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Acceleration */}
                <div className="glass" style={{ padding: '2rem', borderRadius: '24px', border: '1px solid var(--border)' }}>
                  <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem' }}>Acceleration Over Matches</h4>
                  <div style={{ height: '280px' }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={matches}>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                        <XAxis dataKey="match" stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                        <YAxis stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                        <Tooltip contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: '10px', color: '#fff' }} />
                        <Bar dataKey="acceleration" name="Acceleration (yd/s²)" radius={[6, 6, 0, 0]}>
                          {matches.map((_, i) => <Cell key={i} fill="#64b5f6" />)}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {activeTab === 'manage' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          <div className="glass" style={{ padding: '2rem', borderRadius: '24px', border: '1px solid var(--border)' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1.5rem' }}>Edit Player Details</h3>
            <form onSubmit={(e) => {
              e.preventDefault();
              handleUpdatePlayer(e);
            }} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Avg BPM</label>
                  <input type="number" step="0.1" style={inputStyle} defaultValue={player.avg_bpm}
                    onChange={e => setEditForm(f => ({ ...f, avg_bpm: parseFloat(e.target.value) }))} />
                </div>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>RR_MS (HRV)</label>
                  <input type="number" step="1" style={inputStyle} defaultValue={player.rr_ms}
                    onChange={e => setEditForm(f => ({ ...f, rr_ms: parseFloat(e.target.value) }))} />
                </div>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Avg Speed</label>
                  <input type="number" step="0.1" style={inputStyle} defaultValue={player.avg_speed}
                    onChange={e => setEditForm(f => ({ ...f, avg_speed: parseFloat(e.target.value) }))} />
                </div>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Acceleration</label>
                  <input type="number" step="0.1" style={inputStyle} defaultValue={player.acceleration}
                    onChange={e => setEditForm(f => ({ ...f, acceleration: parseFloat(e.target.value) }))} />
                </div>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Status</label>
                  <select style={{ ...inputStyle, cursor: 'pointer' }} defaultValue={player.status}
                    onChange={e => setEditForm(f => ({ ...f, status: e.target.value }))}>
                    <option value="active">Active</option>
                    <option value="benched">Benched</option>
                    <option value="practice squad">Practice Squad</option>
                    <option value="injured">Injured</option>
                  </select>
                </div>
              </div>
              {error && <p style={{ color: 'var(--danger)', fontSize: '0.85rem' }}>{error}</p>}
              <button type="submit" style={{
                background: 'var(--primary)', color: 'white', padding: '0.875rem', borderRadius: '12px',
                fontWeight: 700, alignSelf: 'flex-start', paddingInline: '2rem',
              }}>Update Player</button>
            </form>
          </div>

          <div className="glass" style={{ padding: '2rem', borderRadius: '24px', border: '1px solid rgba(255,61,0,0.2)' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.75rem', color: 'var(--danger)' }}>Danger Zone</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.25rem' }}>
              Permanently remove this player and all their match history.
            </p>
            <button onClick={handleRemovePlayer} style={{
              background: 'rgba(255,61,0,0.15)', color: 'var(--danger)', padding: '0.75rem 1.5rem',
              borderRadius: '12px', fontWeight: 700, border: '1px solid rgba(255,61,0,0.3)',
            }}>Remove Player</button>
          </div>
        </div>
      )}

      {/* Add Match Modal */}
      <AnimatePresence>
        {showAddMatch && (
          <Modal title="Add New Match" onClose={() => setShowAddMatch(false)}>
            <form onSubmit={handleAddMatch} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Avg BPM</label>
                  <input type="number" step="0.1" style={inputStyle} value={matchForm.avg_bpm}
                    onChange={e => setMatchForm(f => ({ ...f, avg_bpm: parseFloat(e.target.value) || 75 }))} />
                </div>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>RR_MS (HRV)</label>
                  <input type="number" step="1" style={inputStyle} value={matchForm.rr_ms}
                    onChange={e => setMatchForm(f => ({ ...f, rr_ms: parseFloat(e.target.value) || 800 }))} />
                </div>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Speed (yd/s)</label>
                  <input type="number" step="0.1" style={inputStyle} value={matchForm.speed}
                    onChange={e => setMatchForm(f => ({ ...f, speed: parseFloat(e.target.value) || 5 }))} />
                </div>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Acceleration (yd/s²)</label>
                  <input type="number" step="0.1" style={inputStyle} value={matchForm.acceleration}
                    onChange={e => setMatchForm(f => ({ ...f, acceleration: parseFloat(e.target.value) || 3.5 }))} />
                </div>
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Date</label>
                <input type="date" style={inputStyle} value={matchForm.date}
                  onChange={e => setMatchForm(f => ({ ...f, date: e.target.value }))} />
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Opponent</label>
                <input style={inputStyle} placeholder="e.g., Dallas Cowboys" value={matchForm.opponent}
                  onChange={e => setMatchForm(f => ({ ...f, opponent: e.target.value }))} />
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Notes</label>
                <textarea style={{ ...inputStyle, minHeight: '60px', resize: 'vertical' }} value={matchForm.notes}
                  onChange={e => setMatchForm(f => ({ ...f, notes: e.target.value }))} />
              </div>
              {error && <p style={{ color: 'var(--danger)', fontSize: '0.85rem' }}>{error}</p>}
              <button type="submit" style={{
                background: 'var(--primary)', color: 'white', padding: '0.875rem', borderRadius: '12px', fontWeight: 700,
              }}>Add Match</button>
            </form>
          </Modal>
        )}
      </AnimatePresence>

      {/* Edit Match Modal */}
      <AnimatePresence>
        {showEditMatch && (
          <Modal title={`Edit Match ${showEditMatch.match_number}`} onClose={() => setShowEditMatch(null)}>
            <form onSubmit={handleEditMatch} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Avg BPM</label>
                  <input type="number" step="0.1" style={inputStyle} value={showEditMatch.avg_bpm}
                    onChange={e => setShowEditMatch(m => ({ ...m, avg_bpm: parseFloat(e.target.value) }))} />
                </div>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>RR_MS</label>
                  <input type="number" step="1" style={inputStyle} value={showEditMatch.rr_ms}
                    onChange={e => setShowEditMatch(m => ({ ...m, rr_ms: parseFloat(e.target.value) }))} />
                </div>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Speed</label>
                  <input type="number" step="0.1" style={inputStyle} value={showEditMatch.speed}
                    onChange={e => setShowEditMatch(m => ({ ...m, speed: parseFloat(e.target.value) }))} />
                </div>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Acceleration</label>
                  <input type="number" step="0.1" style={inputStyle} value={showEditMatch.acceleration}
                    onChange={e => setShowEditMatch(m => ({ ...m, acceleration: parseFloat(e.target.value) }))} />
                </div>
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Opponent</label>
                <input style={inputStyle} value={showEditMatch.opponent || ''}
                  onChange={e => setShowEditMatch(m => ({ ...m, opponent: e.target.value }))} />
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Notes</label>
                <textarea style={{ ...inputStyle, minHeight: '60px', resize: 'vertical' }} value={showEditMatch.notes || ''}
                  onChange={e => setShowEditMatch(m => ({ ...m, notes: e.target.value }))} />
              </div>
              {error && <p style={{ color: 'var(--danger)', fontSize: '0.85rem' }}>{error}</p>}
              <button type="submit" style={{
                background: 'var(--primary)', color: 'white', padding: '0.875rem', borderRadius: '12px', fontWeight: 700,
              }}>Update Match</button>
            </form>
          </Modal>
        )}
      </AnimatePresence>
    </div>
  );
};

export default PlayerDetail;
