import React from 'react';
import './Dashboard.css';

const Dashboard = () => {
  return (
    <div className="dashboard-app">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <span className="logo-icon">C</span>
          <span className="logo-text">Civix AI</span>
        </div>
        <nav className="sidebar-nav">
          <div className="nav-item active">📊 Overview</div>
          <div className="nav-item">🛡️ Booth Risk Analysis</div>
          <div className="nav-item">🌐 Cluster Intelligence</div>
          <div className="nav-item">📈 Temporal Trends</div>
          <div className="nav-item">💡 Recommendations</div>
          <div className="nav-item">⚙️ Settings</div>
        </nav>
      </aside>

      {/* MAIN VIEWPORT */}
      <main className="main-viewport">
        {/* HEADER SLAB */}
        <header className="header-slab">
          <h1>Booth Civic Intelligence</h1>
          <div className="header-controls">
            <button className="btn-refresh">🔄 Refresh</button>
            <div className="admin-profile">
              <div className="avatar-circle">AD</div>
              <span>Admin ▾</span>
            </div>
          </div>
        </header>

        {/* CONTENT AREA */}
        <div className="scroll-container">
          <div className="stats-row">
            <div className="stat-card">
              <label>Total Booths</label>
              <div className="stat-value">124</div>
            </div>
            <div className="stat-card">
              <label>High Risk Booths</label>
              <div className="stat-value">17 <span>▲</span></div>
            </div>
            <div className="stat-card">
              <label>Avg Civic Score</label>
              <div className="stat-value">72.4</div>
            </div>
            <div className="stat-card">
              <label>Complaint Growth</label>
              <div className="stat-value">+18% <span className="green-text">▲</span></div>
            </div>
          </div>

          <div className="main-grid">
            <div className="left-panel">
              <div className="card">
                <h3 className="card-title">Booth Risk Analysis</h3>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Booth</th>
                      <th>Risk Level</th>
                      <th>Civic Score</th>
                      <th>Growth</th>
                      <th>Top Issue</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Booth 23</td>
                      <td><span className="badge badge-high">High</span></td>
                      <td>64</td>
                      <td className="growth-up">▲ 34%</td>
                      <td>Water</td>
                    </tr>
                    <tr>
                      <td>Booth 15</td>
                      <td><span className="badge badge-med">Medium</span></td>
                      <td>75</td>
                      <td className="growth-up">▲ 20%</td>
                      <td>Power</td>
                    </tr>
                    <tr>
                      <td>Booth 8</td>
                      <td><span className="badge badge-low">Low</span></td>
                      <td>82</td>
                      <td className="growth-down">▼ 5%</td>
                      <td>Sanitation</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div className="card">
                <h3 className="card-title">Cluster Insights</h3>
                <div className="cluster-body">
                  <div className="circle-node-mock"></div>
                  <div className="cluster-info">
                    <p><strong>Top Issues:</strong> 1. Water &nbsp; 2. Power</p>
                    <p><strong>Central Booths:</strong> Booth 12, Booth 31</p>
                    <p className="alert-text"><strong>Spread Alerts:</strong> Rapid Complaints in Cluster 4</p>
                  </div>
                </div>
              </div>

              <div className="charts-row">
                <div className="card">
                  <h3 className="card-title">Complaint Growth</h3>
                  <div className="chart-mock blue-wave"></div>
                </div>
                <div className="card">
                  <h3 className="card-title">Sentiment Trend</h3>
                  <div className="chart-mock green-wave"></div>
                </div>
              </div>
            </div>

            <div className="right-panel">
              <div className="card side-card">
                <h3 className="card-title">Top Issues:</h3>
                <ol className="simple-list">
                  <li>Water</li>
                  <li>Power</li>
                </ol>
              </div>
              <div className="card side-card">
                <h3 className="card-title">AI Recommendations</h3>
                <div className="rec-row">
                  <span className="tag-high">Booth 23</span>
                  <p>Deploy water inspection team</p>
                </div>
                <div className="rec-row">
                  <span className="tag-med">Booth 7</span>
                  <p>Increase security patrols</p>
                </div>
                <div className="rec-row">
                  <span className="tag-low">Booth 15</span>
                  <p>Organize power supply check</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;