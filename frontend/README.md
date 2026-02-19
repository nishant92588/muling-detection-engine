# 🛡️ RIFT 2026: Money Muling Detection Engine

**Project Overview:** An advanced financial crime detection engine that identifies sophisticated money muling patterns using **Graph Theory** and **Temporal Analysis**.

## 🧠 Core Detection Logic
The engine analyzes transaction flows to detect three primary illicit patterns:
1. **Circular Routing (Cycles):** Identifies closed-loop transfers (e.g., A -> B -> C -> A) using DFS.
2. **Smurfing / Fan-in:** Detects high-velocity transfers where 10+ accounts send funds to a single node within 72 hours.
3. **Layering:** Identifies complex multi-hop fund movements aimed at obscuring the source.

## 📊 Suspicion Scoring Methodology
Each detected fraud ring is assigned a **Risk Score**:
* **Cycle Patterns:** 85.0% - 87.5% (High Priority).
* **Smurfing Patterns:** 75.0% (Moderate-High Priority).

## ⚙️ Technical Complexity
- **Algorithm Complexity:** $O(V + E)$ using NetworkX, ensuring sub-second processing for large datasets.
- **Backend:** FastAPI (Python) for high-performance async processing.
- **Frontend:** React.js with `react-force-graph-2d` for interactive network visualization.

## 🚀 How to Run
1. **Backend:** `cd backend && pip install -r requirements.txt && uvicorn main:app --reload`
2. **Frontend:** `cd frontend && npm install && npm start`