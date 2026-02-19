import React, { useState } from 'react';
import axios from 'axios';
// FIX: Curly braces {} hata diye kyunki ye default export hai
import ForceGraph2D from 'react-force-graph-2d'; 

function App() {
  const [data, setData] = useState(null);
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      // Backend FastAPI port 8000 par hona chahiye
      const res = await axios.post("https://muling-detection-engine.onrender.com/analyze", formData);
      setData(res.data);
      
      const nodes = [];
      const links = [];
      const seenNodes = new Set();

      // Mandatary Requirement: Graph Visualization
      res.data.fraud_rings.forEach(ring => {
        ring.member_accounts.forEach(acc => {
          if (!seenNodes.has(acc)) {
            nodes.push({ 
              id: acc, 
              // Suspicious nodes clearly highlighted
              color: ring.pattern_type === 'cycle' ? '#ff4d4d' : '#ffcc00',
              size: ring.pattern_type === 'cycle' ? 10 : 6
            });
            seenNodes.add(acc);
          }
        });
        
        for (let i = 0; i < ring.member_accounts.length - 1; i++) {
          links.push({ source: ring.member_accounts[i], target: ring.member_accounts[i+1] });
        }
      });
      setGraphData({ nodes, links });
    } catch (err) {
      alert("Network Error: Check if Backend is running!");
    }
  };

  const downloadJSON = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = "fraud_analysis.json";
    link.click();
  };

  return (
    <div style={{ padding: '20px', backgroundColor: '#0f0f0f', color: '#fff', minHeight: '100vh' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <h1>RIFT 2026 ENGINE</h1>
        <div>
          <input type="file" onChange={handleFileUpload} />
          {data && <button onClick={downloadJSON} style={{ marginLeft: '10px' }}>Export JSON</button>}
        </div>
      </div>
      
      {/* 1. MANDATORY INTERACTIVE GRAPH */}
      <div style={{ border: '1px solid #333', backgroundColor: '#000', borderRadius: '10px', height: '400px' }}>
        <ForceGraph2D
          graphData={graphData}
          nodeLabel={node => `Account: ${node.id}`}
          nodeColor={node => node.color}
          nodeRelSize={6}
          linkDirectionalArrowLength={4}
          linkDirectionalArrowRelPos={1}
          linkColor={() => '#666'}
        />
      </div>

      {/* 2. FRAUD RING SUMMARY TABLE */}
      {data && (
        <div style={{ marginTop: '30px' }}>
          <h3>Fraud Ring Summary Table</h3>
          <table border="1" cellPadding="10" style={{ width: '100%', borderCollapse: 'collapse', color: '#fff', borderColor: '#444' }}>
            <thead style={{ backgroundColor: '#222' }}>
              <tr>
                <th>Ring ID</th>
                <th>Pattern Type</th>
                <th>Risk Score</th>
                <th>Member Count</th>
                <th>Accounts</th>
              </tr>
            </thead>
            <tbody>
              {data.fraud_rings.map((ring) => (
                <tr key={ring.ring_id}>
                  <td>{ring.ring_id}</td>
                  <td>{ring.pattern_type}</td>
                  <td>{ring.risk_score}%</td>
                  <td>{ring.member_accounts.length}</td>
                  <td style={{ fontSize: '11px', color: '#bbb' }}>{ring.member_accounts.join(", ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default App;