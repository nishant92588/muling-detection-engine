from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import networkx as nx
from datetime import timedelta
import time

app = FastAPI()

# Network Error fix karne ke liye CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_transactions(file: UploadFile = File(...)):
    start_time = time.time()
    df = pd.read_csv(file.file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Graph Construction
    G = nx.DiGraph()
    for _, row in df.iterrows():
        G.add_edge(row['sender_id'], row['receiver_id'], amount=row['amount'], ts=row['timestamp'])

    suspicious_accounts_dict = {}
    fraud_rings = []

    # --- 1. CIRCULAR FUND ROUTING (Cycles 3-5) ---
    cycles = list(nx.simple_cycles(G))
    for i, cycle in enumerate(cycles):
        if 3 <= len(cycle) <= 5:
            r_id = f"RING_C_{i+1:03d}"
            fraud_rings.append({
                "ring_id": r_id,
                "member_accounts": cycle,
                "pattern_type": "cycle",
                "risk_score": 85.0
            })
            for acc in cycle:
                suspicious_accounts_dict[acc] = {
                    "account_id": acc,
                    "suspicion_score": 87.5,
                    "detected_patterns": [f"cycle_length_{len(cycle)}"],
                    "ring_id": r_id
                }

    # --- 2. SMURFING (Fan-in 10+ Senders & 72h Window) ---
    for node in G.nodes():
        # False Positive Control: Ignore high-volume merchants
        if G.degree(node) > 100: continue 

        in_edges = list(G.in_edges(node, data=True))
        if len(in_edges) >= 10:
            timestamps = sorted([d['ts'] for _, _, d in in_edges])
            # Temporal analysis (72-hour window)
            if (timestamps[-1] - timestamps[0]) <= timedelta(hours=72):
                r_id = f"RING_S_{str(node)[:5]}"
                members = [u for u, v in G.in_edges(node)] + [node]
                fraud_rings.append({
                    "ring_id": r_id,
                    "member_accounts": list(set(members)),
                    "pattern_type": "smurfing_fan_in",
                    "risk_score": 75.0
                })
                if node not in suspicious_accounts_dict:
                    suspicious_accounts_dict[node] = {
                        "account_id": node,
                        "suspicion_score": 75.0,
                        "detected_patterns": ["smurfing_fan_in", "high_velocity"],
                        "ring_id": r_id
                    }

    # --- 3. LAYERED SHELL (3+ Hops & Shell TX Count 2-3) ---
    # Algorithm: Find paths and check intermediate node transaction counts
    for path in nx.all_simple_paths(G, source=df['sender_id'].iloc[0], target=df['receiver_id'].iloc[-1], cutoff=4):
        if len(path) >= 4:
            # Check intermediate accounts have only 2-3 transactions
            is_shell = all(2 <= G.degree(m) <= 3 for m in path[1:-1])
            if is_shell:
                r_id = f"RING_L_{str(path[1])[:5]}"
                fraud_rings.append({
                    "ring_id": r_id, 
                    "member_accounts": path, 
                    "pattern_type": "layered_shell", 
                    "risk_score": 60.0
                })
                for acc in path:
                    if acc not in suspicious_accounts_dict:
                        suspicious_accounts_dict[acc] = {
                            "account_id": acc, 
                            "suspicion_score": 60.0, 
                            "detected_patterns": ["layered_shell"], 
                            "ring_id": r_id
                        }

    # Formatting and Sorting (DESCENDING score is mandatory)
    sorted_accounts = sorted(suspicious_accounts_dict.values(), key=lambda x: x['suspicion_score'], reverse=True)

    return {
        "suspicious_accounts": sorted_accounts,
        "fraud_rings": fraud_rings,
        "summary": {
            "total_accounts_analyzed": len(G.nodes()),
            "suspicious_accounts_flagged": len(sorted_accounts),
            "fraud_rings_detected": len(fraud_rings),
            "processing_time_seconds": round(time.time() - start_time, 3)
        }
    }