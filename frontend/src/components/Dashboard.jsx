import React, { useState, useEffect } from 'react';
import AskPanel from './AskPanel';
import UploadPanel from './UploadPanel';

const API_BASE = 'http://localhost:8000/api/v1/admin';

const Dashboard = () => {
  const [tab, setTab] = useState('overview');
  const [overview, setOverview] = useState(null);
  const [booths, setBooths] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [o, b, r] = await Promise.all([
        fetch(`${API_BASE}/overview`).then(r => r.json()),
        fetch(`${API_BASE}/booths`).then(r => r.json()),
        fetch(`${API_BASE}/recommendations`).then(r => r.json()),
      ]);
      setOverview(o);
      setBooths(b);
      setRecommendations(r);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const badge = (level) => {
    const cls = level === 'High' ? 'badge-high' : level === 'Medium' ? 'badge-med' : 'badge-low';
    return <span className={`badge ${cls}`}>{level}</span>;
  };

  const navItems = [
    { id: 'overview', label: 'Overview', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/></svg> },
    { id: 'ask', label: 'Ask AI', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg> },
    { id: 'upload', label: 'Upload', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg> },
  ];

  return (
    <div className="app">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="logo">C</div>
          <span>Civix AI</span>
        </div>
        <nav className="sidebar-nav">
          {navItems.map(item => (
            <div
              key={item.id}
              className={`nav-item ${tab === item.id ? 'active' : ''}`}
              onClick={() => setTab(item.id)}
            >
              {item.icon}
              {item.label}
            </div>
          ))}
        </nav>
      </aside>

      {/* Main */}
      <div className="main">
        <header className="header">
          <h1>{tab === 'ask' ? 'Ask AI' : tab === 'upload' ? 'Upload PDF' : 'Overview'}</h1>
          <div className="header-right">
            <button className="btn" onClick={fetchData}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{width:14,height:14}}><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
              Refresh
            </button>
            <div className="avatar">A</div>
          </div>
        </header>

        <div className="content">
          {tab === 'upload' ? (
            <UploadPanel />
          ) : tab === 'ask' ? (
            <AskPanel />
          ) : loading ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '200px', gap: 8, color: 'var(--gray-500)' }}>
              <div className="spinner" />
              Loading...
            </div>
          ) : (
            <>
              {/* Stats */}
              <div className="stats-grid">
                {[
                  { label: 'Total Booths', value: overview?.total_booths },
                  { label: 'Total Complaints', value: overview?.total_complaints },
                  { label: 'Open', value: overview?.total_open_complaints },
                  { label: 'Resolved', value: overview?.total_resolved_complaints },
                ].map((s, i) => (
                  <div className="stat-card" key={i}>
                    <div className="label">{s.label}</div>
                    <div className="value">{s.value ?? '—'}</div>
                  </div>
                ))}
              </div>

              {/* Grid */}
              <div className="grid-2col">
                {/* Table */}
                <div className="card">
                  <h3>Booth Risk Analysis</h3>
                  <table>
                    <thead>
                      <tr>
                        <th>Booth</th>
                        <th>Risk</th>
                        <th>Complaints</th>
                        <th>Open</th>
                        <th>Resolved</th>
                      </tr>
                    </thead>
                    <tbody>
                      {booths.length === 0 ? (
                        <tr><td colSpan="5" style={{ textAlign: 'center', color: 'var(--gray-400)', padding: 24 }}>No data</td></tr>
                      ) : booths.map(b => (
                        <tr key={b.booth_id}>
                          <td style={{ fontWeight: 600, color: 'var(--gray-900)' }}>Booth {b.booth_id}</td>
                          <td>{badge(b.risk_level)}</td>
                          <td>{b.complaint_count}</td>
                          <td>{b.open_count}</td>
                          <td>{b.resolved_count}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Right column */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                  {/* Resolution rate */}
                  <div className="card">
                    <h3>Resolution Rate</h3>
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
                      <span style={{ fontSize: 28, fontWeight: 700, color: 'var(--gray-900)' }}>
                        {((1 - (overview?.avg_open_ratio ?? 0)) * 100).toFixed(0)}%
                      </span>
                      <span style={{ fontSize: 13, color: 'var(--gray-500)' }}>complaints resolved</span>
                    </div>
                    <div className="progress-bar">
                      <div className="fill" style={{ width: `${(1 - (overview?.avg_open_ratio ?? 0)) * 100}%` }} />
                    </div>
                  </div>

                  {/* Recommendations */}
                  <div className="card" style={{ flex: 1 }}>
                    <h3>Recommendations</h3>
                    {recommendations.length === 0 ? (
                      <p style={{ color: 'var(--gray-400)', fontSize: 14 }}>All clear — no action needed.</p>
                    ) : recommendations.map((r, i) => (
                      <div className="rec-item" key={i}>
                        <div className="rec-label">Booth {r.booth_id} · {badge(r.risk_level)}</div>
                        <p>{r.recommendation}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;