const API_BASE = 'http://localhost:8000/api';

async function request(url, options = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'API Error');
  }
  return res.json();
}

// ─── Players ──────────────────────────────────────────────────────────────────

export const getPlayers = () => request('/players');

export const addPlayer = (player) =>
  request('/players', { method: 'POST', body: JSON.stringify(player) });

export const updatePlayer = (id, data) =>
  request(`/players/${id}`, { method: 'PUT', body: JSON.stringify(data) });

export const deletePlayer = (id) =>
  request(`/players/${id}`, { method: 'DELETE' });

export const clearAllPlayers = () =>
  request('/players', { method: 'DELETE' });

export const generatePlayers = (config) =>
  request('/players/generate', { method: 'POST', body: JSON.stringify(config) });

export const uploadPhoto = async (playerId, file) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/players/${playerId}/photo`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Upload failed');
  return res.json();
};

// ─── Matches ──────────────────────────────────────────────────────────────────

export const getPlayerMatches = (playerId) =>
  request(`/players/${playerId}/matches`);

export const addMatch = (playerId, match) =>
  request(`/players/${playerId}/matches`, { method: 'POST', body: JSON.stringify(match) });

export const updateMatch = (playerId, matchNum, data) =>
  request(`/players/${playerId}/matches/${matchNum}`, { method: 'PUT', body: JSON.stringify(data) });

export const deleteMatch = (playerId, matchNum) =>
  request(`/players/${playerId}/matches/${matchNum}`, { method: 'DELETE' });

export const clearPlayerMatches = (playerId) =>
  request(`/players/${playerId}/matches`, { method: 'DELETE' });

export const getAllMatches = () => request('/matches');

export const getMatchOverview = () => request('/matches/overview');

export const getPerformanceTrends = () => request('/matches/trends');

// ─── Lineup & Reports ─────────────────────────────────────────────────────────

export const optimizeLineup = (maxFatigue = 80) =>
  request(`/lineup/optimize?max_fatigue=${maxFatigue}`);

export const getTeamReport = () => request('/team/report');
