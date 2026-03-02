import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { Activity, LayoutDashboard, Users, Calendar } from 'lucide-react';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/players', label: 'Players', icon: Users },
  { path: '/matches', label: 'Matches', icon: Calendar },
];

const Sidebar = () => {
  const location = useLocation();

  return (
    <aside style={{
      width: '260px', background: 'var(--bg-card)', borderRight: '1px solid var(--border)',
      display: 'flex', flexDirection: 'column', padding: '2rem 1rem', minHeight: '100vh', flexShrink: 0,
    }}>
      {/* Logo */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0 0.75rem', marginBottom: '2.5rem',
      }}>
        <div style={{
          width: '40px', height: '40px', borderRadius: '12px', background: 'var(--primary-glow)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <Activity size={22} color="var(--primary)" />
        </div>
        <div>
          <p style={{ fontSize: '0.95rem', fontWeight: 800, letterSpacing: '-0.025em' }}>
            NFL FATIGUE
          </p>
          <p style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--primary)', letterSpacing: '0.1em' }}>
            TRACKER PRO
          </p>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', flex: 1 }}>
        {navItems.map(({ path, label, icon: Icon }) => {
          const isActive = path === '/' ? location.pathname === '/' : location.pathname.startsWith(path);
          return (
            <NavLink key={path} to={path} style={{
              display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.75rem 1rem',
              borderRadius: '12px', fontWeight: 600, fontSize: '0.9rem', textDecoration: 'none',
              transition: 'all 0.2s',
              background: isActive ? 'var(--primary-glow)' : 'transparent',
              color: isActive ? 'var(--primary)' : 'var(--text-secondary)',
            }}>
              <Icon size={18} />
              {label}
            </NavLink>
          );
        })}
      </nav>

      {/* Footer */}
      <div style={{
        padding: '1rem', borderRadius: '16px', background: 'rgba(255,255,255,0.02)',
        border: '1px solid var(--border)', marginTop: 'auto', textAlign: 'center',
      }}>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          NFL Fatigue Tracker v2.0
        </p>
        <p style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
          React + FastAPI
        </p>
      </div>
    </aside>
  );
};

export default Sidebar;
