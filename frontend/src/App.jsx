import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import LodgeComplaintPanel from './components/LodgeComplaintPanel';
import LoginPage from './components/LoginPage';
import './index.css';

const NAV_ITEMS = [
  {
    id: 'upload',
    label: 'Upload',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
        <polyline points="17 8 12 3 7 8" />
        <line x1="12" y1="3" x2="12" y2="15" />
      </svg>
    ),
  },
  {
    id: 'overview',
    label: 'Overview',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <rect x="3" y="3" width="7" height="7" rx="1.5" />
        <rect x="14" y="3" width="7" height="7" rx="1.5" />
        <rect x="14" y="14" width="7" height="7" rx="1.5" />
        <rect x="3" y="14" width="7" height="7" rx="1.5" />
      </svg>
    ),
  },
  {
    id: 'ask',
    label: 'Ask AI',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      </svg>
    ),
  },
  {
    id: 'intelligence',
    label: 'Network',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="18" cy="5" r="3" />
        <circle cx="6" cy="12" r="3" />
        <circle cx="18" cy="19" r="3" />
        <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
        <line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
      </svg>
    ),
  },
  {
    id: 'drives',
    label: 'Drives',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
      </svg>
    ),
  },
];

const ABOUT_ITEM = {
  id: 'about',
  label: 'About',
  icon: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="16" x2="12" y2="12" />
      <line x1="12" y1="8" x2="12.01" y2="8" />
    </svg>
  ),
};

const SETTINGS_ITEM = {
  id: 'settings',
  label: 'Settings',
  icon: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51-1z" />
    </svg>
  ),
};

const PAGE_TITLES = {
  overview: 'Overview',
  intelligence: 'Threat Intelligence Network',
  ask: 'Ask AI',
  upload: 'Upload Data',
  drives: 'Drive Management',
  about: 'About System',
  settings: 'Settings',
  lodge_complaint: 'Voter Complaint Portal',
};

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [tab, setTab] = useState('overview');
  const [userRole, setUserRole] = useState('official'); // 'official' or 'voter'
  const [boothId, setBoothId] = useState(null);
  const [expanded] = useState(true);

  const handleLogin = (type, bId) => {
    setIsLoggedIn(true);
    setUserRole(type === 'booth' ? 'voter' : 'official');
    setBoothId(bId);
    setTab('overview');
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setTab('overview');
    setBoothId(null);
  };

  if (!isLoggedIn) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <div className="app">
      {/* ── Sidebar (Only for Officials) ── */}
      {userRole === 'official' && (
        <div className={`sidebar ${expanded ? 'expanded' : ''}`}>
          <div className="sidebar-top">
            <div className="sidebar-brand">
              <div className="logo">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ width: 18, height: 18 }}>
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                </svg>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <span className="brand-name" style={{ letterSpacing: '1px' }}>CIVIX AI</span>
                <span style={{ fontSize: 9, color: 'var(--blue-100)', fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase' }}>National Intelligence</span>
              </div>
            </div>

            <nav className="sidebar-nav">
              {NAV_ITEMS.map((item) => (
                <div
                  key={item.id}
                  className={`nav-item ${tab === item.id ? 'active' : ''}`}
                  onClick={() => setTab(item.id)}
                >
                  {item.icon}
                  <span>{item.label}</span>
                </div>
              ))}
            </nav>
          </div>

          <div className="sidebar-bottom">
            <div className="sidebar-nav" style={{ marginBottom: 12 }}>
              <div
                className={`nav-item ${tab === ABOUT_ITEM.id ? 'active' : ''}`}
                onClick={() => setTab(ABOUT_ITEM.id)}
              >
                {ABOUT_ITEM.icon}
                <span>{ABOUT_ITEM.label}</span>
              </div>
              <div
                className={`nav-item ${tab === SETTINGS_ITEM.id ? 'active' : ''}`}
                onClick={() => setTab(SETTINGS_ITEM.id)}
              >
                {SETTINGS_ITEM.icon}
                <span>{SETTINGS_ITEM.label}</span>
              </div>
              {/* Logout Button */}
              <div className="nav-item" onClick={handleLogout} style={{ marginTop: 'auto', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '12px' }}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ width: 18, height: 18 }}>
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                  <polyline points="16 17 21 12 16 7" />
                  <line x1="21" y1="12" x2="9" y2="12" />
                </svg>
                <span>Logout</span>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 24px', background: 'var(--blue-700)', borderTop: '1px solid rgba(255,255,255,0.05)', margin: '0 -12px' }}>
              <div style={{ width: 8, height: 8, background: 'var(--amber-500)', borderRadius: 0 }} />
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontSize: 9, fontWeight: 800, color: 'var(--white)', letterSpacing: '0.08em' }}>OFFICIAL_04</span>
                <span style={{ fontSize: 8, color: 'var(--blue-100)', letterSpacing: '0.1em', opacity: 0.8 }}>AUTHORIZED ACCESS</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Main ── */}
      <div className="main" style={{
        marginLeft: userRole === 'official' ? '' : '0',
        width: userRole === 'official' ? '' : '100%',
        background: userRole === 'voter' ? 'var(--bg)' : 'white'
      }}>
        {userRole === 'official' && (
          <header className="header">
            <h1>{PAGE_TITLES[tab]}</h1>
            <div className="header-right">
              <div style={{ marginRight: 15, textAlign: 'right', display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontSize: 10, fontWeight: 800, opacity: 0.7 }}>ADMIN_PORTAL</span>
                <span style={{ fontSize: 9, opacity: 0.5 }}>OFFICIAL_ACCESS</span>
              </div>
              <div className="avatar">A</div>
            </div>
          </header>
        )}

        {/* Voter Header with Logout */}
        {userRole === 'voter' && (
          <div style={{
            padding: '12px 40px',
            background: 'white',
            borderBottom: '1px solid var(--gray-100)',
            display: 'flex',
            justifyContent: 'flex-end'
          }}>
            <button
              onClick={handleLogout}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--gray-500)',
                fontSize: '11px',
                fontWeight: '800',
                textTransform: 'uppercase',
                letterSpacing: '0.1em',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              Terminate Session <div style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--red-500)' }} />
            </button>
          </div>
        )}

        <div className="content" style={{ padding: userRole === 'voter' ? '0' : '28px 32px' }}>
          {userRole === 'official' ? (
            <Dashboard tab={tab} setTab={setTab} />
          ) : (
            <LodgeComplaintPanel boothId={boothId} />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;