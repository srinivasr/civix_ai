import React, { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:8000/api/v1';

const ComplaintsPanel = () => {
    const [complaints, setComplaints] = useState([]);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null);

    // Design Tokens - Institutional Palette
    const navy = "#04122e";
    const surface = "#f8f9fb";
    const surfaceDeep = "#edeef0";
    const white = "#ffffff";
    const gray400 = "#94a3b8";
    const gray600 = "#475569";
    const amber = "#D4A843";

    useEffect(() => {
        fetchComplaints();
    }, []);

    const fetchComplaints = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/complaints/`);
            const data = await res.json();
            setComplaints(data);
        } catch (e) {
            console.error("Failed to fetch complaints:", e);
        } finally {
            setLoading(false);
        }
    };

    const handleResolve = async (id) => {
        try {
            const res = await fetch(`${API_BASE}/complaints/resolve/${id}`, {
                method: 'POST'
            });
            if (res.ok) {
                setMessage({ type: 'success', text: `COMPLAINT #${id} RESOLVED & VOTER NOTIFIED.` });
                fetchComplaints(); // Refresh
            } else {
                setMessage({ type: 'error', text: 'FAILED TO RESOLVE COMPLAINT.' });
            }
        } catch (e) {
            setMessage({ type: 'error', text: 'SYSTEM ERROR: UNABLE TO REACH REGISTRY.' });
        }
    };

    return (
        <div style={{ padding: '40px', backgroundColor: surface, minHeight: '100%', fontFamily: '"Public Sans", "Inter", sans-serif' }}>
            <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '32px' }}>
                
                <header style={{ borderLeft: `6px solid ${navy}`, paddingLeft: '24px', marginBottom: '8px' }}>
                    <h2 style={{ fontSize: '10px', fontWeight: '900', color: gray400, letterSpacing: '0.4em', textTransform: 'uppercase', marginBottom: '8px' }}>
                        Intelligence Registry
                    </h2>
                    <h1 style={{ fontSize: '24px', fontWeight: '900', color: navy, letterSpacing: '-0.02em', textTransform: 'uppercase' }}>
                        Voter Complaints Management
                    </h1>
                </header>

                {message && (
                    <div style={{ 
                        padding: '16px 24px', 
                        backgroundColor: message.type === 'success' ? '#f0fdf4' : '#fef2f2',
                        borderLeft: `4px solid ${message.type === 'success' ? '#22c55e' : '#ef4444'}`,
                        color: message.type === 'success' ? '#166534' : '#991b1b',
                        fontSize: '12px', fontWeight: '800'
                    }}>
                        {message.text}
                    </div>
                )}

                <div style={{ backgroundColor: white, border: `1px solid ${surfaceDeep}`, padding: '0' }}>
                    <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                            <thead>
                                <tr style={{ borderBottom: `2px solid ${navy}`, textAlign: 'left' }}>
                                    <th style={{ padding: '20px', color: gray400, fontWeight: '900', textTransform: 'uppercase' }}>ID</th>
                                    <th style={{ padding: '20px', color: gray400, fontWeight: '900', textTransform: 'uppercase' }}>Voter EPIC</th>
                                    <th style={{ padding: '20px', color: gray400, fontWeight: '900', textTransform: 'uppercase' }}>Contact</th>
                                    <th style={{ padding: '20px', color: gray400, fontWeight: '900', textTransform: 'uppercase' }}>Issue Type</th>
                                    <th style={{ padding: '20px', color: gray400, fontWeight: '900', textTransform: 'uppercase' }}>Status</th>
                                    <th style={{ padding: '20px', color: gray400, fontWeight: '900', textTransform: 'uppercase' }}>Subject</th>
                                    <th style={{ padding: '20px', color: gray400, fontWeight: '900', textTransform: 'uppercase' }}>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {loading ? (
                                    <tr><td colSpan="7" style={{ padding: '40px', textAlign: 'center' }}>Synchronizing with registry...</td></tr>
                                ) : complaints.length === 0 ? (
                                    <tr><td colSpan="7" style={{ padding: '40px', textAlign: 'center', color: gray400, fontStyle: 'italic' }}>No registered complaints found.</td></tr>
                                ) : (
                                    complaints.map((c, i) => (
                                        <tr key={c.complaint_id} style={{ borderBottom: `1px solid ${surfaceDeep}`, backgroundColor: i % 2 === 0 ? 'transparent' : surface }}>
                                            <td style={{ padding: '20px', fontWeight: '900', color: navy }}>#{c.complaint_id}</td>
                                            <td style={{ padding: '20px', fontWeight: '700', color: gray600, fontFamily: 'monospace' }}>{c.voter_epic || c.epic}</td>
                                            <td style={{ padding: '20px', fontWeight: '700', color: gray600 }}>{c.phone_number || 'N/A'}</td>
                                            <td style={{ padding: '20px' }}>
                                                <span style={{ 
                                                    fontSize: '9px', fontWeight: '900', padding: '4px 8px', backgroundColor: '#f0f9ff',
                                                    color: '#0369a1', border: `1px solid #bae6fd`, textTransform: 'uppercase'
                                                }}>
                                                    {c.issue_type}
                                                </span>
                                            </td>
                                            <td style={{ padding: '20px' }}>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: c.status === 'Open' ? amber : '#22c55e', fontWeight: '900', fontSize: '10px' }}>
                                                    <div style={{ width: '6px', height: '6px', backgroundColor: c.status === 'Open' ? amber : '#22c55e' }} />
                                                    {c.status.toUpperCase()}
                                                </div>
                                            </td>
                                            <td style={{ padding: '20px', color: gray600, fontWeight: '500' }}>{c.subject}</td>
                                            <td style={{ padding: '20px' }}>
                                                {c.status === 'Open' && (
                                                    <button 
                                                        onClick={() => handleResolve(c.complaint_id)}
                                                        style={{ 
                                                            backgroundColor: navy, color: white, padding: '8px 16px', border: 'none', 
                                                            fontSize: '10px', fontWeight: '900', textTransform: 'uppercase', cursor: 'pointer',
                                                            letterSpacing: '0.1em'
                                                        }}
                                                    >
                                                        Resolve
                                                    </button>
                                                )}
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ComplaintsPanel;
