import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search, Filter, UserPlus, MoreHorizontal, Trash2, Dice5, Download, X, ChevronDown
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { motion, AnimatePresence } from 'framer-motion';

const POSITIONS = ['QB', 'RB', 'WR', 'TE', 'OL', 'DL', 'LB', 'CB', 'S', 'K', 'P', 'DE', 'DT'];
const STATUSES = ['active', 'benched', 'practice squad', 'injured'];

const getFatigueColor = (f) => f > 80 ? '#ff3d00' : f > 60 ? '#ffd600' : '#00c853';
const statusStyle = (s) => ({
  background: s === 'active' ? 'rgba(0,200,83,0.1)' : s === 'injured' ? 'rgba(255,61,0,0.1)' : 'rgba(255,214,0,0.1)',
  color: s === 'active' ? 'var(--success)' : s === 'injured' ? 'var(--danger)' : 'var(--warning)',
});

const inputStyle = {
  width: '100%', padding: '0.7rem 1rem', borderRadius: '10px', border: '1px solid var(--border)',
  background: 'var(--bg-elevated)', color: 'white', fontSize: '0.9rem', outline: 'none',
};

const selectStyle = { ...inputStyle, cursor: 'pointer' };

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

const PlayerList = () => {
  const { players, addPlayer, deletePlayer, clearAllPlayers, generatePlayers, loading } = useApp();
  const navigate = useNavigate();

  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [positionFilter, setPositionFilter] = useState('All');
  const [sortBy, setSortBy] = useState('fatigue-desc');
  const [showAddModal, setShowAddModal] = useState(false);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [confirmClear, setConfirmClear] = useState(false);

  // Add player form
  const [form, setForm] = useState({
    name: '', number: 1, position: 'QB', team: '', avg_bpm: 75, rr_ms: 800,
    avg_speed: 5, acceleration: 3.5, status: 'active',
  });

  // Generate form
  const [genForm, setGenForm] = useState({
    count: 5, team_name: 'Random Team',
    position_distribution: 'Balanced NFL Roster', quality_level: 'Average Team',
  });

  const [submitError, setSubmitError] = useState('');

  // Filtering & sorting
  let filtered = [...players];
  if (searchTerm) {
    const q = searchTerm.toLowerCase();
    filtered = filtered.filter(p =>
      p.name.toLowerCase().includes(q) || p.team.toLowerCase().includes(q) ||
      p.position.toLowerCase().includes(q) || String(p.number).includes(q));
  }
  if (statusFilter !== 'All') filtered = filtered.filter(p => p.status === statusFilter);
  if (positionFilter !== 'All') filtered = filtered.filter(p => p.position === positionFilter);

  filtered.sort((a, b) => {
    switch (sortBy) {
      case 'fatigue-desc': return b.fatigue_prediction - a.fatigue_prediction;
      case 'fatigue-asc': return a.fatigue_prediction - b.fatigue_prediction;
      case 'name-asc': return a.name.localeCompare(b.name);
      case 'name-desc': return b.name.localeCompare(a.name);
      case 'number': return a.number - b.number;
      default: return 0;
    }
  });

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!form.name || !form.team) { setSubmitError('Name and Team are required'); return; }
    try {
      await addPlayer(form);
      setShowAddModal(false);
      setForm({ name: '', number: 1, position: 'QB', team: '', avg_bpm: 75, rr_ms: 800, avg_speed: 5, acceleration: 3.5, status: 'active' });
      setSubmitError('');
    } catch (err) {
      setSubmitError(err.message);
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    try {
      await generatePlayers(genForm);
      setShowGenerateModal(false);
    } catch (err) {
      setSubmitError(err.message);
    }
  };

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (window.confirm('Remove this player?')) {
      await deletePlayer(id);
    }
  };

  const handleClearAll = async () => {
    await clearAllPlayers();
    setConfirmClear(false);
  };

  const exportCSV = () => {
    if (!players.length) return;
    const headers = ['Name', 'Number', 'Position', 'Team', 'Status', 'BPM', 'RR_MS', 'Speed', 'Acceleration', 'Fatigue'];
    const rows = players.map(p => [p.name, p.number, p.position, p.team, p.status, p.avg_bpm, p.rr_ms, p.avg_speed, p.acceleration, p.fatigue_prediction]);
    const csv = [headers, ...rows].map(r => r.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'players_data.csv'; a.click();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <h3 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Roster Management</h3>
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <button onClick={() => setShowGenerateModal(true)} style={{
            background: 'var(--bg-elevated)', color: 'var(--text-secondary)', padding: '0.7rem 1.2rem',
            borderRadius: '12px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem',
            border: '1px solid var(--border)',
          }}><Dice5 size={18} /> Generate</button>
          <button onClick={exportCSV} style={{
            background: 'var(--bg-elevated)', color: 'var(--text-secondary)', padding: '0.7rem 1.2rem',
            borderRadius: '12px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem',
            border: '1px solid var(--border)',
          }}><Download size={18} /> Export CSV</button>
          {players.length > 0 && (
            <button onClick={() => setConfirmClear(true)} style={{
              background: 'rgba(255,61,0,0.1)', color: 'var(--danger)', padding: '0.7rem 1.2rem',
              borderRadius: '12px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem',
              border: '1px solid rgba(255,61,0,0.2)',
            }}><Trash2 size={18} /> Clear All</button>
          )}
          <button onClick={() => setShowAddModal(true)} style={{
            background: 'var(--primary)', color: 'white', padding: '0.7rem 1.5rem', borderRadius: '12px',
            fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem',
            boxShadow: '0 0 20px var(--primary-glow)',
          }}><UserPlus size={18} /> Add Player</button>
        </div>
      </div>

      {/* Search & Filters */}
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        <div className="glass" style={{
          flex: 1, minWidth: '250px', display: 'flex', alignItems: 'center', gap: '1rem',
          padding: '0.7rem 1.25rem', borderRadius: '14px', border: '1px solid var(--border)',
        }}>
          <Search size={20} color="var(--text-muted)" />
          <input type="text" placeholder="Search by name, team, position..." value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            style={{ background: 'none', border: 'none', outline: 'none', color: 'white', width: '100%', fontSize: '0.95rem' }} />
        </div>
        <button onClick={() => setShowFilters(!showFilters)} className="glass" style={{
          padding: '0.7rem 1.25rem', borderRadius: '14px', display: 'flex', alignItems: 'center', gap: '0.5rem',
          color: 'var(--text-secondary)', fontWeight: 600, border: '1px solid var(--border)',
        }}><Filter size={18} /> Filters <ChevronDown size={14} /></button>
      </div>

      <AnimatePresence>
        {showFilters && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}
            style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', overflow: 'hidden' }}>
            <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)} style={selectStyle}>
              <option value="All">All Statuses</option>
              {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            <select value={positionFilter} onChange={e => setPositionFilter(e.target.value)} style={selectStyle}>
              <option value="All">All Positions</option>
              {POSITIONS.map(p => <option key={p} value={p}>{p}</option>)}
            </select>
            <select value={sortBy} onChange={e => setSortBy(e.target.value)} style={selectStyle}>
              <option value="fatigue-desc">Fatigue (High → Low)</option>
              <option value="fatigue-asc">Fatigue (Low → High)</option>
              <option value="name-asc">Name (A → Z)</option>
              <option value="name-desc">Name (Z → A)</option>
              <option value="number">Jersey Number</option>
            </select>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Player count */}
      <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
        Showing {filtered.length} of {players.length} players
      </p>

      {/* Table */}
      {loading ? (
        <p style={{ color: 'var(--text-muted)', padding: '2rem', textAlign: 'center' }}>Loading...</p>
      ) : filtered.length === 0 ? (
        <div className="glass" style={{ padding: '3rem', textAlign: 'center', borderRadius: '20px', border: '1px solid var(--border)' }}>
          <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem' }}>
            {players.length === 0 ? 'No players yet. Add or generate players to get started.' : 'No players match your filters.'}
          </p>
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: '0 0.6rem' }}>
            <thead>
              <tr style={{ color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 700, textAlign: 'left' }}>
                <th style={{ padding: '0 1.5rem 0.5rem' }}>PLAYER</th>
                <th style={{ padding: '0 1rem 0.5rem' }}>POS</th>
                <th style={{ padding: '0 1rem 0.5rem' }}>TEAM</th>
                <th style={{ padding: '0 1rem 0.5rem' }}>BPM</th>
                <th style={{ padding: '0 1rem 0.5rem' }}>HRV</th>
                <th style={{ padding: '0 1rem 0.5rem' }}>SPEED</th>
                <th style={{ padding: '0 1rem 0.5rem' }}>FATIGUE</th>
                <th style={{ padding: '0 1rem 0.5rem' }}>STATUS</th>
                <th style={{ padding: '0 1.5rem 0.5rem', textAlign: 'right' }}>ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((player) => (
                <motion.tr key={player.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                  className="glass" style={{ borderRadius: '15px', cursor: 'pointer' }}
                  onClick={() => navigate(`/players/${player.id}`)}>
                  <td style={{ padding: '0.875rem 1.5rem', borderTopLeftRadius: '15px', borderBottomLeftRadius: '15px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.875rem' }}>
                      <div style={{
                        width: '42px', height: '42px', borderRadius: '12px', background: 'var(--bg-elevated)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: '1rem', fontWeight: 700, color: 'var(--primary)', overflow: 'hidden', flexShrink: 0,
                      }}>
                        {player.photo_url
                          ? <img src={`http://localhost:8000${player.photo_url}`} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                          : player.name.charAt(0)}
                      </div>
                      <div>
                        <h4 style={{ fontSize: '0.95rem', fontWeight: 700 }}>{player.name}</h4>
                        <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>#{player.number}</p>
                      </div>
                    </div>
                  </td>
                  <td style={{ padding: '0.875rem 1rem' }}>
                    <span className="glass" style={{ padding: '0.3rem 0.7rem', borderRadius: '8px', fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)' }}>
                      {player.position}
                    </span>
                  </td>
                  <td style={{ padding: '0.875rem 1rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{player.team}</td>
                  <td style={{ padding: '0.875rem 1rem', fontWeight: 600, fontSize: '0.9rem' }}>{player.avg_bpm}</td>
                  <td style={{ padding: '0.875rem 1rem', fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-secondary)' }}>{player.rr_ms}</td>
                  <td style={{ padding: '0.875rem 1rem', fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-secondary)' }}>{player.avg_speed}</td>
                  <td style={{ padding: '0.875rem 1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <div style={{ flex: 1, height: '6px', background: 'var(--bg-elevated)', borderRadius: '10px', width: '70px', overflow: 'hidden' }}>
                        <div style={{
                          height: '100%', width: `${player.fatigue_prediction}%`,
                          background: getFatigueColor(player.fatigue_prediction),
                          boxShadow: `0 0 8px ${getFatigueColor(player.fatigue_prediction)}50`,
                        }} />
                      </div>
                      <span style={{ fontSize: '0.85rem', fontWeight: 700, color: getFatigueColor(player.fatigue_prediction) }}>
                        {player.fatigue_prediction}%
                      </span>
                    </div>
                  </td>
                  <td style={{ padding: '0.875rem 1rem' }}>
                    <div style={{
                      display: 'inline-flex', alignItems: 'center', gap: '0.4rem', padding: '0.3rem 0.7rem',
                      borderRadius: '20px', fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase',
                      ...statusStyle(player.status),
                    }}>
                      <div style={{ width: '5px', height: '5px', borderRadius: '50%', background: 'currentColor' }} />
                      {player.status}
                    </div>
                  </td>
                  <td style={{ padding: '0.875rem 1.5rem', textAlign: 'right', borderTopRightRadius: '15px', borderBottomRightRadius: '15px' }}>
                    <button onClick={(e) => handleDelete(e, player.id)} style={{ color: 'var(--text-muted)', padding: '0.3rem' }}
                      title="Remove player">
                      <Trash2 size={16} />
                    </button>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Add Player Modal */}
      <AnimatePresence>
        {showAddModal && (
          <Modal title="Add New Player" onClose={() => { setShowAddModal(false); setSubmitError(''); }}>
            <form onSubmit={handleAdd} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Player Name *</label>
                  <input style={inputStyle} placeholder="e.g., Tom Brady" value={form.name}
                    onChange={e => setForm({ ...form, name: e.target.value })} />
                </div>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Jersey Number *</label>
                  <input type="number" style={inputStyle} min="1" max="99" value={form.number}
                    onChange={e => setForm({ ...form, number: parseInt(e.target.value) || 1 })} />
                </div>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Position *</label>
                  <select style={selectStyle} value={form.position} onChange={e => setForm({ ...form, position: e.target.value })}>
                    {POSITIONS.map(p => <option key={p} value={p}>{p}</option>)}
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Team *</label>
                  <input style={inputStyle} placeholder="e.g., Tampa Bay" value={form.team}
                    onChange={e => setForm({ ...form, team: e.target.value })} />
                </div>
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Status</label>
                <select style={selectStyle} value={form.status} onChange={e => setForm({ ...form, status: e.target.value })}>
                  {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-secondary)', marginTop: '0.5rem' }}>Performance Metrics</h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Avg BPM</label>
                  <input type="number" step="0.1" style={inputStyle} value={form.avg_bpm}
                    onChange={e => setForm({ ...form, avg_bpm: parseFloat(e.target.value) || 75 })} />
                </div>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>RR_MS (HRV)</label>
                  <input type="number" step="1" style={inputStyle} value={form.rr_ms}
                    onChange={e => setForm({ ...form, rr_ms: parseFloat(e.target.value) || 800 })} />
                </div>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Avg Speed (yd/s)</label>
                  <input type="number" step="0.1" style={inputStyle} value={form.avg_speed}
                    onChange={e => setForm({ ...form, avg_speed: parseFloat(e.target.value) || 5 })} />
                </div>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Acceleration (yd/s²)</label>
                  <input type="number" step="0.1" style={inputStyle} value={form.acceleration}
                    onChange={e => setForm({ ...form, acceleration: parseFloat(e.target.value) || 3.5 })} />
                </div>
              </div>
              {submitError && <p style={{ color: 'var(--danger)', fontSize: '0.85rem' }}>{submitError}</p>}
              <button type="submit" style={{
                background: 'var(--primary)', color: 'white', padding: '0.875rem', borderRadius: '12px',
                fontWeight: 700, fontSize: '1rem', marginTop: '0.5rem',
              }}>Add Player</button>
            </form>
          </Modal>
        )}
      </AnimatePresence>

      {/* Generate Players Modal */}
      <AnimatePresence>
        {showGenerateModal && (
          <Modal title="Generate Random Players" onClose={() => setShowGenerateModal(false)}>
            <form onSubmit={handleGenerate} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Number of Players</label>
                  <input type="number" style={inputStyle} min="1" max="50" value={genForm.count}
                    onChange={e => setGenForm({ ...genForm, count: parseInt(e.target.value) || 5 })} />
                </div>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Team Name</label>
                  <input style={inputStyle} value={genForm.team_name}
                    onChange={e => setGenForm({ ...genForm, team_name: e.target.value })} />
                </div>
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Position Distribution</label>
                <select style={selectStyle} value={genForm.position_distribution}
                  onChange={e => setGenForm({ ...genForm, position_distribution: e.target.value })}>
                  <option>Balanced NFL Roster</option>
                  <option>Defensive Focus</option>
                  <option>Offensive Focus</option>
                  <option>Random Mix</option>
                </select>
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', display: 'block' }}>Quality Level</label>
                <select style={selectStyle} value={genForm.quality_level}
                  onChange={e => setGenForm({ ...genForm, quality_level: e.target.value })}>
                  <option>Elite Team</option>
                  <option>Good Team</option>
                  <option>Average Team</option>
                  <option>Mixed Quality</option>
                  <option>Random</option>
                </select>
              </div>
              <button type="submit" style={{
                background: 'var(--primary)', color: 'white', padding: '0.875rem', borderRadius: '12px',
                fontWeight: 700, fontSize: '1rem',
              }}>Generate Players</button>
            </form>
          </Modal>
        )}
      </AnimatePresence>

      {/* Clear All Confirmation */}
      <AnimatePresence>
        {confirmClear && (
          <Modal title="Clear All Players" onClose={() => setConfirmClear(false)}>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
              This will permanently remove <strong>all {players.length} players</strong> and their match history. This action cannot be undone.
            </p>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <button onClick={() => setConfirmClear(false)} style={{
                flex: 1, padding: '0.8rem', borderRadius: '12px', fontWeight: 700,
                background: 'var(--bg-elevated)', color: 'var(--text-secondary)', border: '1px solid var(--border)',
              }}>Cancel</button>
              <button onClick={handleClearAll} style={{
                flex: 1, padding: '0.8rem', borderRadius: '12px', fontWeight: 700,
                background: 'var(--danger)', color: 'white',
              }}>Clear All</button>
            </div>
          </Modal>
        )}
      </AnimatePresence>
    </div>
  );
};

export default PlayerList;
