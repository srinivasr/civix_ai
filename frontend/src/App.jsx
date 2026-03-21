import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
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
];

const SETTINGS_ITEM = {
  id: 'settings',
  label: 'Settings',
  icon: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
    </svg>
  ),
};

const PAGE_TITLES = {
  overview: 'Overview',
  ask: 'Ask AI',
  upload: 'Upload Data',
  settings: 'Settings',
};

function App() {
  const [tab, setTab] = useState('overview');

  return (
    <div className="app">
      {/* ── Expanding Sidebar ── */}
      <aside className="sidebar">
        <div className="sidebar-top">
          <div className="sidebar-brand">
            <div className="logo">C</div>
            <span className="brand-name">Civix AI</span>
          </div>
          <nav className="sidebar-nav">
            {NAV_ITEMS.map(item => (
              <div
                key={item.id}
                className={`nav-item ${tab === item.id ? 'active' : ''}`}
                onClick={() => setTab(item.id)}
                title={item.label}
              >
                {item.icon}
                {item.label}
              </div>
            ))}
          </nav>
        </div>
        <div className="sidebar-bottom">
          <nav className="sidebar-nav">
            <div
              className={`nav-item ${tab === 'settings' ? 'active' : ''}`}
              onClick={() => setTab('settings')}
              title="Settings"
            >
              {SETTINGS_ITEM.icon}
              {SETTINGS_ITEM.label}
            </div>
          </nav>
        </div>
      </aside>

      {/* ── Main ── */}
      <div className="main">
        <header className="header">
          <h1>{PAGE_TITLES[tab]}</h1>
          <div className="header-right">
            <div className="avatar">A</div>
          </div>
        </header>
        <div className="content">
          <Dashboard tab={tab} setTab={setTab} />
        </div>
      </div>
    </div>
  );
}

export default App;