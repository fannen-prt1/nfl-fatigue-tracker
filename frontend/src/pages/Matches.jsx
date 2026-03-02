import React, { useEffect, useState } from 'react';
import {
  Activity, Users, TrendingUp, Calendar, Shield, Sliders, BarChart3, AlertTriangle, ChevronDown
} from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Cell, LineChart, Line, PieChart, Pie, Legend
} from 'recharts';
import { useApp } from '../context/AppContext';
import { getMatchOverview, optimizeLineup, getPerformanceTrends, getAllMatches } from '../utils/api';
import { motion } from 'framer-motion';

const getFatigueColor = (f) => f > 80 ? '#ff3d00' : f > 60 ? '#ffd600' : '#00c853';
const tabs = [
  { id: 'overview', label: 'Match Overview', icon: BarChart3 },
  { id: 'lineup', label: 'Lineup Optimizer', icon: Shield },
  { id: 'trends', label: 'Performance Trends', icon: TrendingUp },
];

const Matches = () => {
  const { players } = useApp();
  const [activeTab, setActiveTab] = useState('overview');
  const [overview, setOverview] = useState(null);
  const [lineup, setLineup] = useState(null);
  const [trends, setTrends] = useState(null);
  const [allMatches, setAllMatches] = useState([]);
  const [maxFatigue, setMaxFatigue] = useState(80);
  const [loading, setLoading] = useState({ overview: true, lineup: false, trends: true });

  useEffect(() => {
    loadOverview();
    loadTrends();
    loadAllMatches();
  }, []);

  const loadOverview = async () => {
    setLoading(l => ({ ...l, overview: true }));
    try { setOverview(await getMatchOverview()); } catch { }
    setLoading(l => ({ ...l, overview: false }));
  };

  const loadTrends = async () => {
    setLoading(l => ({ ...l, trends: true }));
    try { setTrends(await getPerformanceTrends()); } catch { }
    setLoading(l => ({ ...l, trends: false }));
  };

  const loadAllMatches = async () => {
    try { setAllMatches(await getAllMatches()); } catch { }
  };

  const loadLineup = async (fatigue) => {
    setLoading(l => ({ ...l, lineup: true }));
    try { setLineup(await optimizeLineup(fatigue)); } catch { }
    setLoading(l => ({ ...l, lineup: false }));
  };

  useEffect(() => { loadLineup(maxFatigue); }, [maxFatigue]);

  const positionGroupConfig = {
    'Defensive Line': { color: '#e60000', icon: '🛡️' },
    'Linebackers': { color: '#ff6d00', icon: '⚡' },
    'Defensive Backs': { color: '#2196f3', icon: '🏃' },
    'Quarterbacks': { color: '#9c27b0', icon: '🎯' },
    'Running Backs': { color: '#00c853', icon: '💨' },
    'Wide Receivers': { color: '#ffd600', icon: '📡' },
    'Tight Ends': { color: '#00bcd4', icon: '🔗' },
    'Offensive Line': { color: '#795548', icon: '🧱' },
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '0.5rem' }}>Matches & Analysis</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Match data, lineup optimization, and performance trends</p>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
        {tabs.map(tab => {
          const Icon = tab.icon;
          return (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{
              display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem 1.25rem',
              borderRadius: '12px', fontWeight: 700, fontSize: '0.9rem', transition: 'all 0.2s',
              background: activeTab === tab.id ? 'var(--primary-glow)' : 'rgba(255,255,255,0.03)',
              color: activeTab === tab.id ? 'var(--primary)' : 'var(--text-secondary)',
              border: activeTab === tab.id ? '1px solid var(--primary)' : '1px solid var(--border)',
            }}>
              <Icon size={16} />{tab.label}
            </button>
          );
        })}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <>
          {loading.overview ? <p style={{ color: 'var(--text-muted)' }}>Loading match overview...</p> : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
              {/* Stats */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.25rem' }}>
                {[
                  { label: 'Total Matches', value: overview?.total_matches || 0, icon: Calendar, color: '#2196f3' },
                  { label: 'Avg Match Fatigue', value: `${(overview?.avg_fatigue || 0).toFixed(1)}%`, icon: Activity, color: '#ff6d00' },
                  { label: 'High Fatigue Matches', value: overview?.high_fatigue_count || 0, icon: AlertTriangle, color: '#ff3d00' },
                  { label: 'Active Players', value: overview?.active_players || 0, icon: Users, color: '#00c853' },
                ].map(({ label, value, icon: Icon, color }) => (
                  <motion.div key={label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                    className="glass" style={{ padding: '1.5rem', borderRadius: '20px', border: '1px solid var(--border)' }}>
                    <div style={{
                      width: '40px', height: '40px', borderRadius: '12px', background: `${color}15`,
                      display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '0.75rem',
                    }}><Icon size={20} color={color} /></div>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>{label}</p>
                    <p style={{ fontSize: '1.5rem', fontWeight: 800 }}>{value}</p>
                  </motion.div>
                ))}
              </div>

              {/* Recent Matches Chart */}
              {overview?.recent_matches && overview.recent_matches.length > 0 && (
                <div className="glass" style={{ padding: '2rem', borderRadius: '24px', border: '1px solid var(--border)' }}>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1.5rem' }}>Recent Match Fatigue Timeline</h3>
                  <div style={{ height: '300px' }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={overview.recent_matches}>
                        <defs>
                          <linearGradient id="matchFatigueGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="var(--primary)" stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                        <XAxis dataKey="player" stroke="var(--text-muted)" fontSize={10} tickLine={false} angle={-20} textAnchor="end" height={50} />
                        <YAxis domain={[0, 100]} stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                        <Tooltip contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: '10px', color: '#fff' }} />
                        <Area type="monotone" dataKey="fatigue" stroke="var(--primary)" strokeWidth={2} fillOpacity={1} fill="url(#matchFatigueGrad)" name="Fatigue %" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              {/* All Matches List */}
              {allMatches.length > 0 && (
                <div className="glass" style={{ padding: '2rem', borderRadius: '24px', border: '1px solid var(--border)' }}>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1.5rem' }}>All Match Records ({allMatches.length})</h3>
                  <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: '0 0.5rem' }}>
                      <thead>
                        <tr style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 700, textAlign: 'left' }}>
                          <th style={{ padding: '0 0.75rem 0.5rem' }}>PLAYER</th>
                          <th style={{ padding: '0 0.75rem 0.5rem' }}>MATCH</th>
                          <th style={{ padding: '0 0.75rem 0.5rem' }}>DATE</th>
                          <th style={{ padding: '0 0.75rem 0.5rem' }}>OPPONENT</th>
                          <th style={{ padding: '0 0.75rem 0.5rem' }}>FATIGUE</th>
                          <th style={{ padding: '0 0.75rem 0.5rem' }}>BPM</th>
                          <th style={{ padding: '0 0.75rem 0.5rem' }}>SPEED</th>
                        </tr>
                      </thead>
                      <tbody>
                        {allMatches.slice(0, 30).map((m, i) => (
                          <tr key={i} style={{ background: 'rgba(255,255,255,0.02)', borderRadius: '10px' }}>
                            <td style={{ padding: '0.6rem 0.75rem', fontWeight: 600, fontSize: '0.85rem' }}>{m.player_name}</td>
                            <td style={{ padding: '0.6rem 0.75rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>#{m.match_number}</td>
                            <td style={{ padding: '0.6rem 0.75rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{m.date || '—'}</td>
                            <td style={{ padding: '0.6rem 0.75rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{m.opponent || '—'}</td>
                            <td style={{ padding: '0.6rem 0.75rem' }}>
                              <span style={{ fontWeight: 700, color: getFatigueColor(m.fatigue) }}>{m.fatigue}%</span>
                            </td>
                            <td style={{ padding: '0.6rem 0.75rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{m.avg_bpm}</td>
                            <td style={{ padding: '0.6rem 0.75rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{m.speed}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {allMatches.length > 30 && (
                      <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', padding: '0.75rem', textAlign: 'center' }}>
                        Showing 30 of {allMatches.length} match records
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* Lineup Optimizer Tab */}
      {activeTab === 'lineup' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* Fatigue Slider */}
          <div className="glass" style={{ padding: '2rem', borderRadius: '24px', border: '1px solid var(--border)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <div>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Max Fatigue Threshold</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Players above this fatigue level will be excluded</p>
              </div>
              <span style={{
                fontSize: '1.5rem', fontWeight: 800, color: getFatigueColor(maxFatigue),
                padding: '0.5rem 1rem', borderRadius: '12px', background: `${getFatigueColor(maxFatigue)}10`,
              }}>{maxFatigue}%</span>
            </div>
            <input type="range" min="30" max="100" value={maxFatigue}
              onChange={e => setMaxFatigue(parseInt(e.target.value))}
              style={{
                width: '100%', height: '6px', borderRadius: '3px',
                appearance: 'none', background: `linear-gradient(to right, #00c853, #ffd600, #ff3d00)`,
                cursor: 'pointer',
              }} />
            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: '0.5rem' }}>
              <span>30%</span><span>100%</span>
            </div>
          </div>

          {loading.lineup ? <p style={{ color: 'var(--text-muted)' }}>Optimizing lineup...</p> : lineup && (
            <>
              {/* Lineup Stats */}
              {lineup.stats && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.25rem' }}>
                  {[
                    { label: 'Avg Fatigue', value: `${lineup.stats.avg_fatigue?.toFixed(1) || 0}%`, color: '#ff6d00' },
                    { label: 'Avg Heart Rate', value: `${lineup.stats.avg_bpm?.toFixed(1) || 0} BPM`, color: '#e60000' },
                    { label: 'Avg Speed', value: `${lineup.stats.avg_speed?.toFixed(1) || 0} yd/s`, color: '#00c853' },
                    { label: 'Lineup Size', value: lineup.stats.total_players || 0, color: '#2196f3' },
                  ].map(({ label, value, color }) => (
                    <div key={label} className="glass" style={{ padding: '1.25rem', borderRadius: '16px', border: '1px solid var(--border)' }}>
                      <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>{label}</p>
                      <p style={{ fontSize: '1.25rem', fontWeight: 800, color }}>{value}</p>
                    </div>
                  ))}
                </div>
              )}

              {/* Position Groups */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem' }}>
                {lineup.groups && Object.entries(lineup.groups).map(([group, groupPlayers]) => {
                  const cfg = positionGroupConfig[group] || { color: '#9e9e9e', icon: '🏈' };
                  return (
                    <div key={group} className="glass" style={{
                      padding: '1.5rem', borderRadius: '20px', border: `1px solid ${cfg.color}30`,
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                        <span style={{ fontSize: '1.25rem' }}>{cfg.icon}</span>
                        <h4 style={{ fontWeight: 700, fontSize: '0.95rem' }}>{group}</h4>
                        <span style={{
                          marginLeft: 'auto', fontSize: '0.75rem', fontWeight: 700, color: cfg.color,
                          background: `${cfg.color}15`, padding: '0.2rem 0.5rem', borderRadius: '6px',
                        }}>{groupPlayers.length}</span>
                      </div>
                      {groupPlayers.length === 0 ? (
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No eligible players</p>
                      ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                          {groupPlayers.map((p, i) => (
                            <div key={i} style={{
                              display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.5rem 0.75rem',
                              borderRadius: '10px', background: 'rgba(255,255,255,0.02)',
                            }}>
                              <span style={{
                                width: '24px', height: '24px', borderRadius: '6px', background: `${cfg.color}20`,
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                fontSize: '0.7rem', fontWeight: 700, color: cfg.color,
                              }}>{i + 1}</span>
                              <div style={{ flex: 1 }}>
                                <p style={{ fontSize: '0.85rem', fontWeight: 600 }}>{p.name}</p>
                                <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>#{p.number} · {p.position}</p>
                              </div>
                              <div style={{ textAlign: 'right' }}>
                                <span style={{
                                  fontWeight: 700, fontSize: '0.85rem', color: getFatigueColor(p.fatigue),
                                }}>{p.fatigue}%</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Excluded Players */}
              {lineup.excluded && lineup.excluded.length > 0 && (
                <div className="glass" style={{ padding: '2rem', borderRadius: '24px', border: '1px solid rgba(255,61,0,0.15)' }}>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--danger)' }}>
                    <AlertTriangle size={18} style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} />
                    Excluded – High Fatigue ({lineup.excluded.length})
                  </h3>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
                    {lineup.excluded.map((p, i) => (
                      <div key={i} style={{
                        display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem',
                        borderRadius: '10px', background: 'rgba(255,61,0,0.06)', border: '1px solid rgba(255,61,0,0.15)',
                      }}>
                        <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>{p.name}</span>
                        <span style={{ fontWeight: 700, color: '#ff3d00', fontSize: '0.85rem' }}>{p.fatigue}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* Trends Tab */}
      {activeTab === 'trends' && (
        <>
          {loading.trends ? <p style={{ color: 'var(--text-muted)' }}>Loading performance trends...</p> : trends ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
              {/* Multi-metric Chart */}
              {trends.trend_data && trends.trend_data.length > 1 && (
                <div className="glass" style={{ padding: '2rem', borderRadius: '24px', border: '1px solid var(--border)' }}>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1.5rem' }}>Team Performance Trends</h3>
                  <div style={{ height: '320px' }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={trends.trend_data}>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                        <XAxis dataKey="match" stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                        <YAxis yAxisId="left" stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                        <YAxis yAxisId="right" orientation="right" stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                        <Tooltip contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: '10px', color: '#fff' }} />
                        <Legend />
                        <Line yAxisId="left" type="monotone" dataKey="avg_fatigue" stroke="#ff6d00" strokeWidth={2} dot={{ r: 3 }} name="Avg Fatigue %" />
                        <Line yAxisId="right" type="monotone" dataKey="avg_bpm" stroke="#e60000" strokeWidth={2} dot={{ r: 3 }} name="Avg BPM" />
                        <Line yAxisId="left" type="monotone" dataKey="avg_speed" stroke="#00c853" strokeWidth={2} dot={{ r: 3 }} name="Avg Speed" />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              {/* Correlation */}
              {trends.correlations && (
                <div className="glass" style={{ padding: '2rem', borderRadius: '24px', border: '1px solid var(--border)' }}>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1.5rem' }}>Performance Correlations</h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.25rem' }}>
                    {Object.entries(trends.correlations).map(([key, val]) => {
                      const label = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
                      const absV = Math.abs(val);
                      const corrColor = val > 0.5 ? '#ff3d00' : val > 0 ? '#ffd600' : '#00c853';
                      return (
                        <div key={key} style={{
                          padding: '1.25rem', borderRadius: '16px', background: `${corrColor}08`,
                          border: `1px solid ${corrColor}20`,
                        }}>
                          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>{label}</p>
                          <p style={{ fontSize: '1.5rem', fontWeight: 800, color: corrColor }}>{val.toFixed(3)}</p>
                          <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.3rem' }}>
                            {absV > 0.7 ? 'Strong' : absV > 0.4 ? 'Moderate' : 'Weak'} {val >= 0 ? 'positive' : 'negative'}
                          </p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Insights */}
              {trends.insights && trends.insights.length > 0 && (
                <div className="glass" style={{ padding: '2rem', borderRadius: '24px', border: '1px solid var(--border)' }}>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1.25rem' }}>Performance Insights</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {trends.insights.map((insight, i) => (
                      <div key={i} style={{
                        display: 'flex', alignItems: 'flex-start', gap: '0.75rem', padding: '0.75rem 1rem',
                        borderRadius: '12px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border)',
                      }}>
                        <TrendingUp size={16} color="var(--primary)" style={{ flexShrink: 0, marginTop: '2px' }} />
                        <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.5 }}>{insight}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {(!trends.trend_data || trends.trend_data.length < 2) && !trends.correlations && !trends.insights && (
                <div className="glass" style={{ padding: '3rem', textAlign: 'center', borderRadius: '24px', border: '1px solid var(--border)' }}>
                  <p style={{ color: 'var(--text-muted)' }}>Not enough match data for trend analysis. Add matches to players first.</p>
                </div>
              )}
            </div>
          ) : (
            <div className="glass" style={{ padding: '3rem', textAlign: 'center', borderRadius: '24px', border: '1px solid var(--border)' }}>
              <p style={{ color: 'var(--text-muted)' }}>Unable to load performance trends.</p>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default Matches;
