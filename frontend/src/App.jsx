import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import PlayerList from './pages/PlayerList';
import PlayerDetail from './pages/PlayerDetail';
import Matches from './pages/Matches';

function App() {
  return (
    <AppProvider>
      <Router>
        <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-main)' }}>
          <Sidebar />
          <main style={{
            flex: 1, padding: '2rem 2.5rem', overflowY: 'auto', maxHeight: '100vh',
          }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/players" element={<PlayerList />} />
              <Route path="/players/:id" element={<PlayerDetail />} />
              <Route path="/matches" element={<Matches />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AppProvider>
  );
}

export default App;
