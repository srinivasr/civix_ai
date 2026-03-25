import React, { useState, useRef, useEffect } from 'react';
import { Network } from 'vis-network';
import { DataSet } from 'vis-data';

const API_URL = 'http://localhost:8000/api/v1/ask';


const COLORS = {
  Person: { bg: '#d9d9d9', border: '#8c8c8c' },
  Booth: { bg: '#ff4d4f', border: '#cf1322' },
  House: { bg: '#52c41a', border: '#389e0d' },
  Area: { bg: '#fa8c16', border: '#d46b08' },
  Issue: { bg: '#722ed1', border: '#531dab' },
  Default: { bg: '#999', border: '#666' },
};



const getColor = (label) => {
  switch (label) {
    case "Booth": return { background: "#ff4d4f", border: "#cf1322" };
    case "Area": return { background: "#fa8c16", border: "#d46b08" };
    case "House": return { background: "#52c41a", border: "#389e0d" };
    case "Family": return { background: "#13c2c2", border: "#08979c" };
    case "Person": return { background: "#d9d9d9", border: "#8c8c8c" };
    case "Issue": return { background: "#722ed1", border: "#531dab" };
    default: return { background: "#999", border: "#666" };
  }
};
const AskPanel = () => {
  const [selectedNode, setSelectedNode] = useState(null);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isFullScreen, setIsFullScreen] = useState(false);
  const graphRef = useRef(null);
  const networkRef = useRef(null);

  const toggleFullScreen = () => {
    setIsFullScreen(!isFullScreen);
  };

  useEffect(() => {
    // When fullscreen toggles, give a small delay for DOM to update then resize
    const timer = setTimeout(() => {
      if (networkRef.current) {
        networkRef.current.setSize('100%', '100%');
        networkRef.current.redraw();
        networkRef.current.fit();
      }
    }, 100);
    return () => clearTimeout(timer);
  }, [isFullScreen]);

  useEffect(() => {
    if (!result?.graph || !graphRef.current) return;
    const { nodes, edges } = result.graph;
    if (!nodes.length && !edges.length) return;

    if (networkRef.current) {
      networkRef.current.destroy();
      networkRef.current = null;
    }

    const visNodes = new DataSet(
nodes.map(n => {
  const nodeType = n.label;
  const c = getColor(nodeType);

return {
  id: n.id,
  label:
    n.properties?.name ||
    n.properties?.epic?.toString() ||
    (n.properties?.house_no ? `House ${n.properties.house_no}` : null) ||
    n.properties?.booth_id?.toString() ||
    n.properties?.complaint_id?.toString() ||
    nodeType,

  color: c,
  raw: n, // 🔥 ADD THIS
  font: { color: '#18181b', size: 13 },
  shape: 'dot',
  size: 16,
  borderWidth: 2,
};
}))
    ;

    const visEdges = new DataSet(
      edges.map((e, i) => ({
        id: `e-${i}`,
        from: e.from,
        to: e.to,
        label: e.label,
        arrows: 'to',
        color: { color: '#d4d4d8', highlight: '#3b82f6' },
        font: { size: 10, color: '#a1a1aa', face: 'Inter, sans-serif' },
        smooth: { type: 'continuous' },
      }))
    );

    networkRef.current = new Network(
      graphRef.current,
      { nodes: visNodes, edges: visEdges },
      {
physics: {
  enabled: true,
  solver: 'forceAtlas2Based',
  forceAtlas2Based: {
    gravitationalConstant: -50,
    centralGravity: 0.01,
    springLength: 100,
    springConstant: 0.08
  },
  stabilization: { iterations: 150 }
},
        interaction: { hover: true, tooltipDelay: 200 },
        edges: { width: 1.5 },
        nodes: { borderWidth: 2 },
      }
    );
  networkRef.current.on("click", function (params) {
  if (params.nodes.length > 0) {
    const nodeId = params.nodes[0];
    const node = visNodes.get(nodeId);

    setSelectedNode(node.raw);
  }
});

    return () => {
      if (networkRef.current) {
        networkRef.current.destroy();
        networkRef.current = null;
      }
    };
  }, [result]);

  const handleAsk = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
           question: question.trim(),
           shortcut: null
           }),
      });
      if (!res.ok) {
        const e = await res.json().catch(() => ({}));
        throw new Error(e.detail || `Error ${res.status}`);
      }
      setResult(await res.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };
  const handleQuickQuery = async (shortcut) => {
  setLoading(true);
  setError(null);
  setResult(null);

  try {
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question:null,
        shortcut:shortcut

         }), 
    });

    if (!res.ok) throw new Error("Error");

    setResult(await res.json());
  } catch (e) {
    setError(e.message);
  } finally {
    setLoading(false);
  }
};

  const columns = result?.data?.length ? Object.keys(result.data[0]) : [];

  return (
    <div className={isFullScreen ? '' : 'fade-in'}>
      {/* ── Search Bar ── */}
      <div className="ask-search">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input
          type="text"
          placeholder="Ask a question about your civic data..."
          value={question}
          onChange={e => setQuestion(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') handleAsk(); }}
          disabled={loading}
        />
        <button
          className="btn btn-primary"
          onClick={handleAsk}
          disabled={loading || !question.trim()}
          style={{ borderRadius: 'var(--radius-lg)', padding: '8px 22px', fontSize: 13 }}
        >
          {loading ? 'Thinking…' : 'Ask'}
        </button>
      </div>
      {/* 🔥 QUICK ACCESS PANEL */}
<div className="quick-panel-container">
  <div className="quick-header">⚡ Quick Insights</div>

  

  <div className="quick-scroll">
    {[
      { label: "Show all relationships", key: "SHOW_ALL_RELATIONSHIPS" },
      { label: "List all voters", key: "LIST_ALL_VOTERS" },
      { label: "List all sections", key: "list_section" },
      { label: "Show all houses", key: "LIST_HOUSES" },
      { label: "Female Voters", key: "HOUSE_MEMBERS" },
      { label: "Senior citizens", key: "SENIOR_VOTERS" },
      { label: "Youth voters", key: "YOUTH_VOTERS" },
      { label: "Voters by issue", key: "VOTERS_BY_ISSUE" },
      { label: "Area relationships", key: "AREA_RELATIONS" },
      { label: "Full network graph", key: "FULL_GRAPH" },
    ].map((q, i) => (
      <button
        key={i}
        onClick={() => handleQuickQuery(q.key)}
        className="quick-chip"
      >
        {q.label}
      </button>
    ))}
  </div>
</div>

      {/* ── Loading ── */}
      {loading && (
        <div className="loading-state">
          <div className="spinner" />
          Querying the knowledge graph…
        </div>
      )}

      {/* ── Error ── */}
      {error && <div className="error-msg">{error}</div>}

      {/* ── Empty State ── */}
      {!loading && !result && !error && (
        <div className="card">
          <div className="empty-state" style={{ height: 260 }}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
            <p>Ask a question to query the knowledge graph</p>
          </div>
        </div>
      )}

      {/* ── Results ── */}
      {result && (
        <>
          {/* Answer */}
          <div className="answer-card">
            <h4>Answer</h4>
            <p>{result.answer}</p>
          </div>

          <div style={{ marginBottom: 24 }}>
            {/* Left: Cypher + Graph */}
            <div>
              <div className="cypher-block">
                <h4>Cypher Query</h4>
                <pre>{result.cypher}</pre>
              </div>
            {result.graph?.nodes?.length > 0 ? (
  <div>
    <div className={`graph-wrapper ${isFullScreen ? 'fullscreen' : ''}`}>
      <button 
        className="fullscreen-btn" 
        onClick={toggleFullScreen}
        title={isFullScreen ? "Minimize" : "Maximize"}
      >
        {isFullScreen ? (
          <>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ width: 14, height: 14 }}>
              <path d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3" />
            </svg>
            <span style={{ marginLeft: 6, fontWeight: 700, fontSize: 13 }}>
              Minimize View
            </span>
          </>
        ) : (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7" />
          </svg>
        )}
      </button>

      <div 
  className="graph-container" 
  ref={graphRef} 
    
/>
    </div>

    {/* 🔥 NODE DETAILS */}
    {selectedNode && (
      <div className="card" style={{ marginTop: 16 }}>
        <h2>Node Details</h2>
        <pre style={{ fontSize: 12 }}>
          {JSON.stringify(selectedNode.properties, null, 2)}
        </pre>
      </div>
    )}
  </div>
) : (
  <div className="card">
    <div className="empty-state" style={{ height: 180 }}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <circle cx="12" cy="12" r="10" />
        <line x1="8" y1="12" x2="16" y2="12" />
      </svg>
      <p>No graph data for this query</p>
    </div>
  </div>
)}

              

                


            </div>


          </div>
        </>
      )}
    </div>
  );
};


export default AskPanel;