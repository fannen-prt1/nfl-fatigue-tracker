import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Users, Activity, TrendingUp, AlertTriangle, Heart, Zap, Gauge, Shield
} from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar
} from 'recharts';
import { useApp } from '../context/AppContext';
import { getMatchOverview, getTeamReport } from '../utils/api';
import { motion } from 'framer-motion';

const COLORS = ['#00c853', '#ffd600', '#ff3d00', '#2196f3'];

const StatCard = ({ title, value, icon: Icon, delta, color }) => (
  <motion.div
    whileHover={{ y: -4, boxShadow: `0 8px 30px ${color}25` }}
    className="glass"
    style={{
      padding: '1.5rem', borderRadius: '20px', flex: 1, minWidth: '220px',
      border: '1px solid var(--border)', cursor: 'default',
    }}
  >
    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
      <div style={{
        width: '48px', height: '48px', borderRadius: '14px',
        background: `${color}15`, display: 'flex', alignItems: 'center',
        justifyContent: 'center', color,
      }}>
        <Icon size={24} />
      </div>
      {delta !== undefined && delta !== null && (
        <span style={{
          fontSize: '0.85rem', fontWeight: 700,
          color: String(delta).startsWith('+') ? 'var(--danger)' : 'var(--success)',
          padding: '0.25rem 0.5rem', borderRadius: '20px',
          background: String(delta).startsWith('+') ? 'rgba(230,0,0,0.1)' : 'rgba(0,200,83,0.1)',
        }}>{delta}</span>
      )}
    </div>
    <h3 style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', fontWeight: 600, marginBottom: '0.25rem' }}>{title}</h3>
    <p style={{ fontSize: '1.75rem', fontWeight: 800 }}>{value}</p>
  </motion.div>
);

const getFatigueColor = (f) => f > 80 ? '#ff3d00' : f > 60 ? '#ffd600' : '#00c853';

const Dashboard = () => {
  const { players, loading } = useApp();
  const navigate = useNavigate();
  const [overview, setOverview] = useState(null);
  const [report, setReport] = useState(null);

  useEffect(() => {
    getMatchOverview().then(setOverview).catch(() => {});
    getTeamReport().then(setReport).catch(() => {});
  }, [players]);

  if (loading) return <div style={{ padding: '2rem', color: 'var(--text-secondary)' }}>Loading dashboard...</div>;

  const activePlayers = players.filter(p => p.status === 'active');
  const avgFatigue = players.length > 0
    ? (players.reduce((s, p) => s + p.fatigue_prediction, 0) / players.length).toFixed(1)
    : 0;
  const highFatiguePlayers = players.filter(p => p.fatigue_prediction > 75);

  // Fatigue distribution
  const fatigueDist = [
    { name: 'Low (0-60%)', value: players.filter(p => p.fatigue_prediction < 60).length, color: '#00c853' },
    { name: 'Medium (60-80%)', value: players.filter(p => p.fatigue_prediction >= 60 && p.fatigue_prediction <= 80).length, color: '#ffd600' },
    { name: 'High (80-100%)', value: players.filter(p => p.fatigue_prediction > 80).length, color: '#ff3d00' },
  ].filter(d => d.value > 0);

  // Status distribution
  const statusDist = {};
  players.forEach(p => { statusDist[p.status || 'active'] = (statusDist[p.status || 'active'] || 0) + 1; });
  const statusData = Object.entries(statusDist).map(([name, value]) => ({ name, value }));

  // Team avg metrics
  const avgBpm = players.length ? (players.reduce((s, p) => s + p.avg_bpm, 0) / players.length) : 0;
  const avgRr = players.length ? (players.reduce((s, p) => s + p.rr_ms, 0) / players.length) : 0;
  const avgSpeed = players.length ? (players.reduce((s, p) => s + p.avg_speed, 0) / players.length) : 0;
  const avgAccel = players.length ? (players.reduce((s, p) => s + p.acceleration, 0) / players.length) : 0;

  const metricsBarData = [
    { name: 'BPM', value: Math.round(avgBpm), fill: '#e60000' },
    { name: 'HRV', value: Math.round(avgRr), fill: '#2196f3' },
    { name: 'Spd×10', value: Math.round(avgSpeed * 10), fill: '#00c853' },
    { name: 'Acc×10', value: Math.round(avgAccel * 10), fill: '#ffd600' },
    { name: 'Fatigue', value: Math.round(Number(avgFatigue)), fill: '#9c27b0' },
  ];

  const timeline = overview?.timeline?.slice().reverse().map(t => ({
    match: t.date || t.game,
    fatigue: t.avg_fatigue,
  })) || [];

  const sortedByFatigue = [...players].sort((a, b) => b.fatigue_prediction - a.fatigue_prediction);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Stat Cards */}
      <div style={{ display: 'flex', gap: '1.25rem', flexWrap: 'wrap' }}>
        <StatCard title="Total Players" value={players.length} icon={Users} color="var(--primary)" />
        <StatCard title="Average Fatigue" value={`${avgFatigue}%`} icon={Activity}
          delta={report ? (report.risk_level === 'HIGH' ? '+HIGH' : report.risk_level === 'MODERATE' ? '~MOD' : '-LOW') : null}
          color="#007bff" />
        <StatCard title="Active Players" value={activePlayers.length} icon={Shield} color="var(--success)" />
        <StatCard title="At Risk" value={highFatiguePlayers.length} icon={AlertTriangle}
          delta={highFatiguePlayers.length > 0 ? `+${highFatiguePlayers.length}` : null} color="var(--warning)" />
      </div>

      {/* Main Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
        {/* Fatigue Timeline */}
        <div className="glass" style={{ padding: '2rem', borderRadius: '24px', border: '1px solid var(--border)' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1.5rem' }}>Team Fatigue Trend</h3>
          {timeline.length > 0 ? (
            <div style={{ height: '300px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={timeline}>
                  <defs>
                    <linearGradient id="colorFatigue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="var(--primary)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                  <XAxis dataKey="match" stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} unit="%" />
                  <Tooltip contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: '12px', color: '#fff' }} />
                  <Area type="monotone" dataKey="fatigue" stroke="var(--primary)" strokeWidth={3} fillOpacity={1} fill="url(#colorFatigue)" name="Fatigue %" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
              No match data yet. Add matches through the Players page.
            </div>
          )}
        </div>

        {/* High Fatigue Alert */}
        <div className="glass" style={{ padding: '2rem', borderRadius: '24px', border: '1px solid var(--border)', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1.5rem' }}>High Fatigue Alert</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', flex: 1, overflowY: 'auto' }}>
            {highFatiguePlayers.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem 0' }}>All players in optimal range.</p>
            ) : (
              highFatiguePlayers.slice(0, 6).map((player) => (
                <div key={player.id} className="glass card-hover" style={{
                  padding: '0.875rem', borderRadius: '14px', display: 'flex', alignItems: 'center',
                  gap: '0.75rem', border: '1px solid rgba(230,0,0,0.2)', cursor: 'pointer',
                }} onClick={() => navigate(`/players/${player.id}`)}>
                  <div style={{
                    width: '40px', height: '40px', borderRadius: '10px', background: 'var(--bg-elevated)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '1.1rem', fontWeight: 700, color: 'var(--primary)', overflow: 'hidden',
                  }}>
                    {player.photo_url
                      ? <img src={`http://localhost:8000${player.photo_url}`} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                      : player.name.charAt(0)}
                  </div>
                  <div style={{ flex: 1 }}>
                    <h4 style={{ fontSize: '0.9rem', fontWeight: 700 }}>{player.name}</h4>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>#{player.number} · {player.position}</p>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <p style={{ color: 'var(--danger)', fontWeight: 800, fontSize: '0.95rem' }}>{player.fatigue_prediction}%</p>
                  </div>
                </div>
              ))
            )}
          </div>
          <button onClick={() => navigate('/players')} className="glass" style={{
            width: '100%', marginTop: '1rem', padding: '0.875rem', borderRadius: '12px',
            fontWeight: 700, color: 'var(--primary)', border: '1px solid var(--primary-glow)', cursor: 'pointer',
          }}>View All Players</button>
        </div>
      </div>

      {/* Charts Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '2rem' }}>
        <div className="glass" style={{ padding: '2rem', borderRadius: '24px', border: '1px solid var(--border)' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem' }}>Fatigue Distribution</h3>
          {fatigueDist.length > 0 ? (
            <div style={{ height: '220px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={fatigueDist} dataKey="value" nameKey="name" cx="50%" cy="50%"
                    outerRadius={80} innerRadius={45} paddingAngle={3}
                    label={({ x, y, name, value }) => (
                      <text x={x} y={y} fill="#ffffff" fontSize={12} fontWeight={600} textAnchor="middle" dominantBaseline="central">{value}</text>
                    )}
                    labelLine={{ stroke: '#888' }}
                    >
                    {fatigueDist.map((e, i) => <Cell key={i} fill={e.color} />)}
                  </Pie>
                  <Tooltip contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: '10px', color: '#fff' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : <p style={{ color: 'var(--text-muted)', textAlign: 'center' }}>No players</p>}
        </div>

        <div className="glass" style={{ padding: '2rem', borderRadius: '24px', border: '1px solid var(--border)' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem' }}>Status Distribution</h3>
          {statusData.length > 0 ? (
            <div style={{ height: '220px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={statusData} dataKey="value" nameKey="name" cx="50%" cy="50%"
                    outerRadius={80} innerRadius={45} paddingAngle={3}
                    label={({ x, y, name, value }) => (
                      <text x={x} y={y} fill="#ffffff" fontSize={11} fontWeight={600} textAnchor="middle" dominantBaseline="central">{name}: {value}</text>
                    )}
                    labelLine={{ stroke: '#888' }}
                    >
                    {statusData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: '10px', color: '#fff' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : <p style={{ color: 'var(--text-muted)', textAlign: 'center' }}>No players</p>}
        </div>

        <div className="glass" style={{ padding: '2rem', borderRadius: '24px', border: '1px solid var(--border)' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem' }}>Team Metrics</h3>
          {players.length > 0 ? (
            <div style={{ height: '220px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={metricsBarData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                  <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={10} tickLine={false} />
                  <YAxis stroke="var(--text-muted)" fontSize={10} tickLine={false} axisLine={false} />
                  <Tooltip contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: '10px', color: '#fff' }} />
                  <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                    {metricsBarData.map((e, i) => <Cell key={i} fill={e.fill} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : <p style={{ color: 'var(--text-muted)', textAlign: 'center' }}>No data</p>}
        </div>
      </div>

      {/* Team Report */}
      {report && report.total > 0 && (
        <div className="glass" style={{ padding: '2rem', borderRadius: '24px', border: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Team Report</h3>
            <span style={{
              padding: '0.4rem 1rem', borderRadius: '20px', fontWeight: 800, fontSize: '0.85rem',
              background: report.risk_level === 'HIGH' ? 'rgba(255,61,0,0.15)' : report.risk_level === 'MODERATE' ? 'rgba(255,214,0,0.15)' : 'rgba(0,200,83,0.15)',
              color: report.risk_level === 'HIGH' ? '#ff3d00' : report.risk_level === 'MODERATE' ? '#ffd600' : '#00c853',
            }}>{report.risk_level} RISK</span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.5rem', marginBottom: '1.5rem' }}>
            <div><p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>Total Players</p><p style={{ fontSize: '1.4rem', fontWeight: 800 }}>{report.total}</p></div>
            <div><p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>Avg Fatigue</p><p style={{ fontSize: '1.4rem', fontWeight: 800 }}>{report.avg_fatigue}%</p></div>
            <div><p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>Active</p><p style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--success)' }}>{report.active}</p></div>
            <div><p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>Injured</p><p style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--danger)' }}>{report.injured}</p></div>
          </div>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '0.75rem', color: 'var(--text-secondary)' }}>Recommendations</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {report.recommendations.map((r, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.5rem 0' }}>
                <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--primary)', flexShrink: 0 }} />
                <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{r}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Player Cards */}
      {players.length > 0 && (
        <div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1.25rem' }}>Player Overview</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1.25rem' }}>
            {sortedByFatigue.slice(0, 8).map((player) => (
              <motion.div key={player.id} whileHover={{ y: -4 }} className="glass card-hover"
                style={{ padding: '1.5rem', borderRadius: '20px', border: '1px solid var(--border)', cursor: 'pointer' }}
                onClick={() => navigate(`/players/${player.id}`)}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                  <div style={{
                    width: '50px', height: '50px', borderRadius: '14px', background: 'var(--bg-elevated)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '1.2rem', fontWeight: 800, color: 'var(--primary)', overflow: 'hidden',
                  }}>
                    {player.photo_url
                      ? <img src={`http://localhost:8000${player.photo_url}`} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                      : player.name.charAt(0)}
                  </div>
                  <div style={{ flex: 1 }}>
                    <h4 style={{ fontSize: '1rem', fontWeight: 700 }}>{player.name}</h4>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>#{player.number} · {player.position} · {player.team}</p>
                  </div>
                </div>
                <div style={{ marginBottom: '0.75rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Fatigue</span>
                    <span style={{ fontSize: '0.85rem', fontWeight: 800, color: getFatigueColor(player.fatigue_prediction) }}>{player.fatigue_prediction}%</span>
                  </div>
                  <div style={{ height: '6px', background: 'var(--bg-elevated)', borderRadius: '10px', overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: `${player.fatigue_prediction}%`, background: getFatigueColor(player.fatigue_prediction), borderRadius: '10px', transition: 'width 0.5s ease' }} />
                  </div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <Heart size={13} color="#e60000" /><span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{player.avg_bpm} BPM</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <Gauge size={13} color="#2196f3" /><span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{player.rr_ms} ms</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <TrendingUp size={13} color="#00c853" /><span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{player.avg_speed} yd/s</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <Zap size={13} color="#ffd600" /><span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{player.acceleration} yd/s²</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
