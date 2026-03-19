import React, { useState, useRef, useEffect } from 'react';
import { Network } from 'vis-network';
import { DataSet } from 'vis-data';

const API_URL = 'http://localhost:8000/api/v1/ask';

const COLORS = {
  Voter:     { bg: '#dbeafe', border: '#3b82f6' },
  Booth:     { bg: '#fef2f2', border: '#ef4444' },
  House:     { bg: '#f0fdf4', border: '#22c55e' },
  Complaint: { bg: '#fffbeb', border: '#f59e0b' },
  Issue:     { bg: '#faf5ff', border: '#a855f7' },
  Default:   { bg: '#f4f4f5', border: '#71717a' },
};

const AskPanel = () => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const graphRef = useRef(null);
  const networkRef = useRef(null);

  useEffect(() => {
    if (!result?.graph || !graphRef.current) return;
    const { nodes, edges } = result.graph;
    if (!nodes.length && !edges.length) return;

    if (networkRef.current) { networkRef.current.destroy(); networkRef.current = null; }

    const visNodes = new DataSet(nodes.map(n => {
      const c = COLORS[n.group] || COLORS.Default;
      return {
        id: n.id,
        label: n.properties?.name || n.properties?.voter_id?.toString() || n.properties?.booth_id?.toString() || n.properties?.complaint_id?.toString() || n.label,
        title: n.title,
        color: { background: c.bg, border: c.border, highlight: { background: c.bg, border: c.border } },
        font: { color: '#18181b', size: 13, face: 'Inter, sans-serif' },
        shape: 'dot', size: 16, borderWidth: 2,
      };
    }));

    const visEdges = new DataSet(edges.map((e, i) => ({
      id: `e-${i}`, from: e.from, to: e.to, label: e.label,
      arrows: 'to',
      color: { color: '#d4d4d8', highlight: '#3b82f6' },
      font: { size: 10, color: '#a1a1aa', face: 'Inter, sans-serif' },
      smooth: { type: 'continuous' },
    })));

    networkRef.current = new Network(graphRef.current, { nodes: visNodes, edges: visEdges }, {
      physics: { forceAtlas2Based: { gravitationalConstant: -30, springLength: 140, springConstant: 0.04 }, solver: 'forceAtlas2Based', stabilization: { iterations: 100 } },
      interaction: { hover: true, tooltipDelay: 200 },
      edges: { width: 1.5 },
      nodes: { borderWidth: 2 },
    });

    return () => { if (networkRef.current) { networkRef.current.destroy(); networkRef.current = null; } };
  }, [result]);

  const handleAsk = async () => {
    if (!question.trim()) return;
    setLoading(true); setError(null); setResult(null);
    try {
      const res = await fetch(API_URL, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question: question.trim() }) });
      if (!res.ok) { const e = await res.json().catch(() => ({})); throw new Error(e.detail || `Error ${res.status}`); }
      setResult(await res.json());
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  const columns = result?.data?.length ? Object.keys(result.data[0]) : [];

  return (
    <div>
      {/* Search */}
      <div className="ask-search">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input
          type="text"
          placeholder="Ask a question about your civic data..."
          value={question}
          onChange={e => setQuestion(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') handleAsk(); }}
          disabled={loading}
        />
        <button className="btn-primary btn" onClick={handleAsk} disabled={loading || !question.trim()}>
          {loading ? 'Thinking...' : 'Ask'}
        </button>
      </div>

      {loading && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--gray-500)', padding: '40px 0', justifyContent: 'center' }}>
          <div className="spinner" /> Querying knowledge graph...
        </div>
      )}

      {error && <div className="error-msg">{error}</div>}

      {result && (
        <>
          {/* Answer */}
          <div className="answer-card">
            <h4>Answer</h4>
            <p>{result.answer}</p>
          </div>

          <div className="grid-2col" style={{ marginBottom: 24 }}>
            {/* Left: Graph */}
            <div>
              <div className="cypher-block">
                <h4>Cypher Query</h4>
                <pre>{result.cypher}</pre>
              </div>
              {result.graph?.nodes?.length > 0 ? (
                <div className="graph-container" ref={graphRef} />
              ) : (
                <div className="card" style={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--gray-400)' }}>
                  No graph data for this query
                </div>
              )}
            </div>

            {/* Right: Data table */}
            {result.data?.length > 0 && (
              <div className="card">
                <h3>Results ({result.data.length} rows)</h3>
                <div style={{ overflowX: 'auto' }}>
                  <table>
                    <thead>
                      <tr>{columns.map(c => <th key={c}>{c}</th>)}</tr>
                    </thead>
                    <tbody>
                      {result.data.map((row, i) => (
                        <tr key={i}>
                          {columns.map(c => (
                            <td key={c}>{typeof row[c] === 'object' ? JSON.stringify(row[c]) : String(row[c] ?? '')}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default AskPanel;
