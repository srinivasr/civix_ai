import React, { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:8000/api/v1';

// Stitch Design Tokens
const tokens = {
    colors: {
        background: '#f3faff',
        surface: '#ffffff',
        surfaceLow: '#e6f6ff',
        surfaceHigh: '#d5ecf8',
        surfaceHighest: '#cfe6f2',
        primary: '#000666',
        primaryContainer: '#1a237e',
        onSurface: '#071e27',
        onSurfaceVariant: '#454652',
        outlineVariant: 'rgba(198, 197, 212, 0.15)',
        success: '#22c55e',
        successBg: '#f0fdf4',
        warning: '#d97706',
        warningBg: '#fffbeb',
    },
    shadows: {
        ambient: '0 8px 24px rgba(7, 30, 39, 0.05)',
    },
    fonts: {
        main: '"Inter", sans-serif',
    }
};

const ComplaintsPanel = () => {
    const [complaints, setComplaints] = useState([]);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null);
    const [expandedRows, setExpandedRows] = useState(new Set());
    const [searchQuery, setSearchQuery] = useState('');

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
            const res = await fetch(`${API_BASE}/complaints/resolve/${id}`, { method: 'POST' });
            if (res.ok) {
                setMessage({ type: 'success', text: `COMPLAINT #${id} RESOLVED & VOTER NOTIFIED.` });
                setComplaints(prev => prev.map(c => 
                    c.complaint_id === id ? { ...c, status: 'Resolved', Status: 'Resolved' } : c
                ));
            } else {
                setMessage({ type: 'error', text: 'FAILED TO RESOLVE COMPLAINT.' });
            }
        } catch (e) {
            setMessage({ type: 'error', text: 'SYSTEM ERROR: UNABLE TO REACH REGISTRY.' });
        }
    };

    const toggleRowExpansion = (id) => {
        const newExpandedRows = new Set(expandedRows);
        if (newExpandedRows.has(id)) newExpandedRows.delete(id);
        else newExpandedRows.add(id);
        setExpandedRows(newExpandedRows);
    };

    // Calculate Stats
    const totalComplaints = complaints.length;
    const openComplaints = complaints.filter(c => (c.status || c.Status) === 'Open').length;
    const resolvedComplaints = complaints.filter(c => (c.status || c.Status) === 'Resolved').length;

    // Filter logic
    const filteredComplaints = complaints.filter(c => {
        if (!searchQuery) return true;
        const q = searchQuery.toLowerCase();
        const idMatch = String(c.complaint_id).toLowerCase().includes(q);
        const epicMatch = String(c.voter_epic || c.epic || c.EPIC || '').toLowerCase().includes(q);
        const boothMatch = String(c.booth_id || '').toLowerCase().includes(q);
        const typeMatch = String(c.issue_type || c.Issue_Type || '').toLowerCase().includes(q);
        return idMatch || epicMatch || boothMatch || typeMatch;
    });

    return (
        <div style={{ backgroundColor: tokens.colors.background, minHeight: '100%', fontFamily: tokens.fonts.main, color: tokens.colors.onSurface, padding: '48px' }}>
            <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '40px' }}>
                
                {/* Header Section */}
                <header>
                    <h2 style={{ fontSize: '11px', fontWeight: '700', color: tokens.colors.onSurfaceVariant, letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: '8px' }}>
                        The Sovereign Ledger
                    </h2>
                    <h1 style={{ fontSize: '36px', fontWeight: '800', color: tokens.colors.primaryContainer, letterSpacing: '-0.02em', margin: 0 }}>
                        Voter Complaints Management
                    </h1>
                </header>

                {/* Notifications */}
                {message && (
                    <div style={{ 
                        padding: '16px 24px', 
                        backgroundColor: message.type === 'success' ? tokens.colors.successBg : tokens.colors.warningBg,
                        borderLeft: `4px solid ${message.type === 'success' ? tokens.colors.success : tokens.colors.warning}`,
                        color: message.type === 'success' ? '#166534' : '#991b1b',
                        fontSize: '13px', fontWeight: '600', borderRadius: '4px',
                        boxShadow: tokens.shadows.ambient
                    }}>
                        {message.text}
                    </div>
                )}

                {/* Stat Cards */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
                    
                    <div style={{ backgroundColor: tokens.colors.surface, padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.ambient, borderLeft: `3px solid ${tokens.colors.primaryContainer}` }}>
                        <div style={{ fontSize: '12px', fontWeight: '700', color: tokens.colors.onSurfaceVariant, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>Total Complaints</div>
                        <div style={{ fontSize: '40px', fontWeight: '800', color: tokens.colors.onSurface, letterSpacing: '-0.02em' }}>{totalComplaints}</div>
                    </div>

                    <div style={{ backgroundColor: tokens.colors.surface, padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.ambient, borderLeft: `3px solid ${tokens.colors.warning}` }}>
                        <div style={{ fontSize: '12px', fontWeight: '700', color: tokens.colors.onSurfaceVariant, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>Open Complaints</div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <div style={{ fontSize: '40px', fontWeight: '800', color: tokens.colors.onSurface, letterSpacing: '-0.02em' }}>{openComplaints}</div>
                            <span style={{ backgroundColor: tokens.colors.warningBg, color: tokens.colors.warning, padding: '6px 12px', borderRadius: '9999px', fontSize: '12px', fontWeight: '700' }}>Requires Attention</span>
                        </div>
                    </div>

                    <div style={{ backgroundColor: tokens.colors.surface, padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.ambient, borderLeft: `3px solid ${tokens.colors.success}` }}>
                        <div style={{ fontSize: '12px', fontWeight: '700', color: tokens.colors.onSurfaceVariant, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>Resolved Complaints</div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <div style={{ fontSize: '40px', fontWeight: '800', color: tokens.colors.onSurface, letterSpacing: '-0.02em' }}>{resolvedComplaints}</div>
                            <span style={{ backgroundColor: tokens.colors.successBg, color: tokens.colors.success, padding: '6px 12px', borderRadius: '9999px', fontSize: '12px', fontWeight: '700' }}>Resolved</span>
                        </div>
                    </div>

                </div>

                {/* Search Bar */}
                <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                    <div style={{ flex: 1, position: 'relative' }}>
                        <input 
                            type="text" 
                            placeholder="Search by Complaint ID, EPIC Number or Booth ID..." 
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            style={{ 
                                width: '100%', padding: '16px 24px', fontSize: '15px', 
                                backgroundColor: tokens.colors.surface, border: 'none', 
                                borderRadius: '8px', boxShadow: tokens.shadows.ambient, 
                                color: tokens.colors.onSurface, outline: 'none', transition: 'all 0.2s ease',
                                boxSizing: 'border-box'
                            }}
                            onFocus={(e) => e.target.style.boxShadow = `0 0 0 2px ${tokens.colors.primaryContainer}30`}
                            onBlur={(e) => e.target.style.boxShadow = tokens.shadows.ambient}
                        />
                    </div>
                </div>

                {/* Data Table */}
                <div style={{ backgroundColor: tokens.colors.surface, borderRadius: '16px', boxShadow: tokens.shadows.ambient, overflow: 'hidden' }}>
                    <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                            <thead style={{ backgroundColor: tokens.colors.surfaceLow }}>
                                <tr>
                                    <th style={{ padding: '20px 24px', color: tokens.colors.onSurfaceVariant, fontWeight: '700', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>ID</th>
                                    <th style={{ padding: '20px 24px', color: tokens.colors.onSurfaceVariant, fontWeight: '700', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Date</th>
                                    <th style={{ padding: '20px 24px', color: tokens.colors.onSurfaceVariant, fontWeight: '700', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Booth ID</th>
                                    <th style={{ padding: '20px 24px', color: tokens.colors.onSurfaceVariant, fontWeight: '700', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Voter EPIC</th>
                                    <th style={{ padding: '20px 24px', color: tokens.colors.onSurfaceVariant, fontWeight: '700', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Contact</th>
                                    <th style={{ padding: '20px 24px', color: tokens.colors.onSurfaceVariant, fontWeight: '700', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Issue Type</th>
                                    <th style={{ padding: '20px 24px', color: tokens.colors.onSurfaceVariant, fontWeight: '700', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Status</th>
                                    <th style={{ padding: '20px 24px', color: tokens.colors.onSurfaceVariant, fontWeight: '700', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {loading ? (
                                    <tr><td colSpan="8" style={{ padding: '60px', textAlign: 'center', color: tokens.colors.onSurfaceVariant }}>Synchronizing with registry...</td></tr>
                                ) : filteredComplaints.length === 0 ? (
                                    <tr><td colSpan="8" style={{ padding: '60px', textAlign: 'center', color: tokens.colors.onSurfaceVariant, fontStyle: 'italic' }}>No complaints match your criteria.</td></tr>
                                ) : (
                                    filteredComplaints.map((c, i) => {
                                        const isExpanded = expandedRows.has(c.complaint_id);
                                        const isOpen = (c.status || c.Status) === 'Open';
                                        return (
                                            <React.Fragment key={c.complaint_id}>
                                                <tr style={{ 
                                                    backgroundColor: i % 2 === 0 ? 'transparent' : tokens.colors.surfaceLow,
                                                    transition: 'background-color 0.2s',
                                                    borderBottom: isExpanded ? 'none' : `1px solid ${tokens.colors.outlineVariant}`
                                                }}>
                                                    <td style={{ padding: '20px 24px', fontWeight: '800', color: tokens.colors.primaryContainer, fontSize: '14px' }}>#{c.complaint_id}</td>
                                                    <td style={{ padding: '20px 24px', color: tokens.colors.onSurfaceVariant, fontSize: '13px' }}>{new Date(c.timestamp).toLocaleDateString()}</td>
                                                    <td style={{ padding: '20px 24px', fontWeight: '700', color: tokens.colors.primaryContainer, fontSize: '13px' }}>{c.booth_id || 'UNKNOWN'}</td>
                                                    <td style={{ padding: '20px 24px', fontWeight: '600', color: tokens.colors.onSurface, fontFamily: 'monospace', fontSize: '14px' }}>{c.voter_epic || c.epic || c.EPIC}</td>
                                                    <td style={{ padding: '20px 24px', color: tokens.colors.onSurfaceVariant, fontSize: '13px' }}>{c.phone_number || c.Contact_no || 'N/A'}</td>
                                                    <td style={{ padding: '20px 24px' }}>
                                                        <span style={{ 
                                                            fontSize: '11px', fontWeight: '700', padding: '6px 12px', backgroundColor: tokens.colors.surfaceHighest,
                                                            color: tokens.colors.primaryContainer, borderRadius: '6px'
                                                        }}>
                                                            {c.issue_type || c.Issue_Type}
                                                        </span>
                                                    </td>
                                                    <td style={{ padding: '20px 24px' }}>
                                                        <span style={{ 
                                                            fontSize: '11px', fontWeight: '800', padding: '6px 12px', borderRadius: '9999px',
                                                            backgroundColor: isOpen ? tokens.colors.warningBg : tokens.colors.successBg,
                                                            color: isOpen ? tokens.colors.warning : tokens.colors.success,
                                                            display: 'inline-flex', alignItems: 'center', gap: '6px'
                                                        }}>
                                                            <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: isOpen ? tokens.colors.warning : tokens.colors.success }} />
                                                            {(c.status || c.Status || '').toUpperCase()}
                                                        </span>
                                                    </td>
                                                    <td style={{ padding: '20px 24px' }}>
                                                        <button 
                                                            onClick={() => toggleRowExpansion(c.complaint_id)}
                                                            style={{ 
                                                                backgroundColor: tokens.colors.surfaceLow, color: tokens.colors.primaryContainer, 
                                                                padding: '8px 16px', border: 'none', borderRadius: '6px',
                                                                fontSize: '12px', fontWeight: '700', cursor: 'pointer',
                                                                transition: 'all 0.2s', boxShadow: '0 2px 4px rgba(0,0,0,0.02)'
                                                            }}
                                                            onMouseOver={(e) => e.target.style.backgroundColor = tokens.colors.surfaceHigh}
                                                            onMouseOut={(e) => e.target.style.backgroundColor = tokens.colors.surfaceLow}
                                                        >
                                                            {isExpanded ? 'Hide' : 'Details'}
                                                        </button>
                                                    </td>
                                                </tr>
                                                {isExpanded && (
                                                    <tr style={{ backgroundColor: i % 2 === 0 ? 'transparent' : tokens.colors.surfaceLow, borderBottom: `1px solid ${tokens.colors.outlineVariant}` }}>
                                                        <td colSpan="8" style={{ padding: '0 24px 32px 24px' }}>
                                                            <div style={{ 
                                                                backgroundColor: tokens.colors.surface, padding: '24px', borderRadius: '12px',
                                                                boxShadow: tokens.shadows.ambient, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '32px'
                                                            }}>
                                                                <div style={{ flex: 1 }}>
                                                                    <div style={{ fontSize: '11px', fontWeight: '700', color: tokens.colors.onSurfaceVariant, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>
                                                                        Detailed Description
                                                                    </div>
                                                                    <div style={{ color: tokens.colors.onSurface, fontSize: '15px', lineHeight: '1.6' }}>
                                                                        {/* Support both Description and subject field names */}
                                                                        {c.description || c.Description || c.subject || 'No description available for this record.'}
                                                                    </div>
                                                                </div>
                                                                {isOpen && (
                                                                    <button 
                                                                        onClick={() => handleResolve(c.complaint_id)}
                                                                        style={{ 
                                                                            background: `linear-gradient(135deg, ${tokens.colors.primary}, ${tokens.colors.primaryContainer})`, 
                                                                            color: '#fff', padding: '14px 28px', border: 'none', borderRadius: '8px',
                                                                            fontSize: '13px', fontWeight: '800', cursor: 'pointer',
                                                                            boxShadow: '0 4px 12px rgba(26, 35, 126, 0.2)', transition: 'all 0.2s transform'
                                                                        }}
                                                                        onMouseOver={(e) => e.target.style.transform = 'translateY(-1px)'}
                                                                        onMouseOut={(e) => e.target.style.transform = 'translateY(0)'}
                                                                    >
                                                                        Mark as Resolved
                                                                    </button>
                                                                )}
                                                            </div>
                                                        </td>
                                                    </tr>
                                                )}
                                            </React.Fragment>
                                        );
                                    })
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
