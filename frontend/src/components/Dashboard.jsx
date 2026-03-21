import React, { useState, useEffect } from 'react';
import AskPanel from './AskPanel';
import UploadPanel from './UploadPanel';

const API_BASE = 'http://localhost:8000/api/v1/admin';

const Dashboard = ({ tab, setTab }) => {
  const [overview, setOverview] = useState(null);
  const [booths, setBooths] = useState([]);
  const [recommendations, setRecommendations] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [o, b, r] = await Promise.all([
        fetch(`${API_BASE}/overview`).then(res => res.json()),
        fetch(`${API_BASE}/booths`).then(res => res.json()),
        fetch(`${API_BASE}/recommendations`).then(res => res.json()),
      ]);
      setOverview(o);
      setBooths(b);
      setRecommendations(r);
    } catch (e) {
      console.error(e);
      setError('Failed to load dashboard data. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const badge = (level) => {
    const cls = level === 'High' ? 'badge-high' : level === 'Medium' ? 'badge-med' : 'badge-low';
    return <span className={`badge ${cls}`}>{level}</span>;
  };

  /* ── Upload Tab ── */
  if (tab === 'upload') return <UploadPanel />;

  /* ── Ask AI Tab ── */
  if (tab === 'ask') return <AskPanel />;

  /* ── Settings Tab ── */
  if (tab === 'settings') {
    return (
      <div className="fade-in">
        <div className="card" style={{ maxWidth: 520 }}>
          <h3>Settings</h3>
          <p style={{ fontSize: 14, color: 'var(--gray-500)', lineHeight: 1.6 }}>
            Configuration options will appear here in future updates.
          </p>
        </div>
      </div>
    );
  }

  /* ── Overview Tab ── */
  const hasComplaints = overview?.total_complaints > 0;
  const resolutionRate = hasComplaints 
    ? ((1 - (overview.avg_open_ratio ?? 0)) * 100).toFixed(0) 
    : '—';

  return (
    <div className="fade-in">
      {/* ── Stat Cards ── */}
      <div className="stats-grid">
        <StatCard
          color="var(--blue-500)"
          bgColor="var(--blue-50)"
          label="Total Booths"
          value={overview?.total_booths ?? '—'}
          icon={
            <svg viewBox="0 0 24 24" fill="none" stroke="var(--blue-500)" strokeWidth="2">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              <polyline points="9 22 9 12 15 12 15 22" />
            </svg>
          }
        />
        <StatCard
          color="var(--amber-500)"
          bgColor="var(--amber-50)"
          label="Total Complaints"
          value={overview?.total_complaints ?? '—'}
          icon={
            <svg viewBox="0 0 24 24" fill="none" stroke="var(--amber-500)" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
            </svg>
          }
        />
        <StatCard
          color="var(--green-500)"
          bgColor="var(--green-50)"
          label="Resolved"
          value={overview?.total_resolved_complaints ?? '—'}
          icon={
            <svg viewBox="0 0 24 24" fill="none" stroke="var(--green-500)" strokeWidth="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
          }
        />
        <StatCard
          color="var(--red-500)"
          bgColor="var(--red-50)"
          label="Open"
          value={overview?.total_open_complaints ?? '—'}
          icon={
            <svg viewBox="0 0 24 24" fill="none" stroke="var(--red-500)" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          }
        />
      </div>

      {/* ── Error Banner ── */}
      {error && <div className="error-msg">{error}</div>}

      {/* ── Loading ── */}
      {loading ? (
        <div className="loading-state">
          <div className="spinner" />
          Loading data...
        </div>
      ) : (
        <>
          <div className="grid-2col">
            {/* ── Booth Risk Table ── */}
            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 18 }}>
                <h3 style={{ margin: 0 }}>Booth Risk Analysis</h3>
                <button className="btn" onClick={fetchData} style={{ fontSize: 12 }}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ width: 13, height: 13 }}>
                    <polyline points="23 4 23 10 17 10" />
                    <polyline points="1 20 1 14 7 14" />
                    <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
                  </svg>
                  Refresh
                </button>
              </div>
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
                    <tr>
                      <td colSpan="5">
                        <div className="empty-state" style={{ height: 120 }}>
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                            <rect x="3" y="3" width="7" height="7" rx="1.5" />
                            <rect x="14" y="3" width="7" height="7" rx="1.5" />
                            <rect x="14" y="14" width="7" height="7" rx="1.5" />
                            <rect x="3" y="14" width="7" height="7" rx="1.5" />
                          </svg>
                          <p>No booth data yet</p>
                        </div>
                      </td>
                    </tr>
                  ) : (
                    booths.map(b => (
                      <tr key={b.booth_id}>
                        <td style={{ fontWeight: 700, color: 'var(--gray-900)' }}>Booth {b.booth_id}</td>
                        <td>{badge(b.risk_level)}</td>
                        <td>{b.complaint_count}</td>
                        <td>{b.open_count}</td>
                        <td>{b.resolved_count}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* ── Right Column ── */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              {/* Resolution Rate */}
              <div className="card">
                <h3>Resolution Rate</h3>
                <div className="rate-value">{resolutionRate}{hasComplaints ? '%' : ''}</div>
                <div className="rate-label">complaints resolved</div>
                <div className="progress-bar" style={{ marginTop: 14 }}>
                  <div className="fill" style={{ width: hasComplaints ? `${resolutionRate}%` : '0%' }} />
                </div>
              </div>

              {/* Quick Stats */}
              <div className="card" style={{ flex: 1 }}>
                <h3>Data Summary</h3>
                <div className="summary-stats">
                  <div className="summary-row">
                    <span className="summary-label">High-risk booths</span>
                    <span className="summary-value badge badge-high">
                      {booths.filter(b => b.risk_level === 'High').length}
                    </span>
                  </div>
                  <div className="summary-row">
                    <span className="summary-label">Medium-risk booths</span>
                    <span className="summary-value badge badge-med">
                      {booths.filter(b => b.risk_level === 'Medium').length}
                    </span>
                  </div>
                  <div className="summary-row">
                    <span className="summary-label">Active recommendations</span>
                    <span className="summary-value badge" style={{ background: 'var(--gray-100)', color: 'var(--gray-800)' }}>
                      {recommendations.length}
                    </span>
                  </div>

                </div>
              </div>
            </div>
          </div>

          {/* ── Full-Width Recommendations Section ── */}
          <div className="section-full" style={{ marginTop: 24 }}>
            <div className="card">
              <div className="section-header">
                <div className="section-title-group">
                  <div className="section-icon" style={{ background: 'var(--amber-50)' }}>
                    <svg viewBox="0 0 24 24" fill="none" stroke="var(--amber-500)" strokeWidth="2">
                      <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <div>
                    <h3 style={{ margin: 0 }}>Booth Recommendations</h3>
                    <p className="section-subtitle">Action items generated by risk analysis</p>
                  </div>
                </div>
                <span className="section-count">{recommendations.length} active</span>
              </div>

              {recommendations.length === 0 ? (
                <div className="empty-state" style={{ height: 140 }}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                    <polyline points="22 4 12 14.01 9 11.01" />
                  </svg>
                  <p>All clear — no action needed</p>
                </div>
              ) : (
                <div className="rec-grid">
                  {recommendations.map((r, i) => (
                    <div className="rec-card" key={i}>
                      <div className="rec-card-header">
                        <span className="rec-booth">Booth {r.booth_id}</span>
                        {badge(r.risk_level)}
                      </div>
                      <p className="rec-text">{r.recommendation}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>


        </>
      )}
    </div>
  );
};

/* ── Stat Card Helper ── */
function StatCard({ label, value, icon, bgColor }) {
  return (
    <div className="stat-card">
      <div className="stat-icon" style={{ background: bgColor }}>
        {icon}
      </div>
      <div>
        <p className="label">{label}</p>
        <p className="value">{value}</p>
      </div>
    </div>
  );
}

export default Dashboard;