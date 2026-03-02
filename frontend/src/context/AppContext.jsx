import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import * as api from '../utils/api';

const AppContext = createContext(null);

export const useApp = () => {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
};

export const AppProvider = ({ children }) => {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchPlayers = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.getPlayers();
      setPlayers(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPlayers();
  }, [fetchPlayers]);

  const addPlayer = async (player) => {
    const res = await api.addPlayer(player);
    await fetchPlayers();
    return res;
  };

  const updatePlayer = async (id, data) => {
    const res = await api.updatePlayer(id, data);
    await fetchPlayers();
    return res;
  };

  const deletePlayer = async (id) => {
    const res = await api.deletePlayer(id);
    await fetchPlayers();
    return res;
  };

  const clearAllPlayers = async () => {
    const res = await api.clearAllPlayers();
    await fetchPlayers();
    return res;
  };

  const generatePlayers = async (config) => {
    const res = await api.generatePlayers(config);
    await fetchPlayers();
    return res;
  };

  const uploadPhoto = async (id, file) => {
    const res = await api.uploadPhoto(id, file);
    await fetchPlayers();
    return res;
  };

  const value = {
    players,
    loading,
    error,
    fetchPlayers,
    addPlayer,
    updatePlayer,
    deletePlayer,
    clearAllPlayers,
    generatePlayers,
    uploadPhoto,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};
