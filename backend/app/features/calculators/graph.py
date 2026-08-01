"""
app/features/calculators/graph.py
Graph features calculator using NetworkX.
"""
import networkx as nx
from typing import List, Dict, Any

class GraphCalculator:
    @staticmethod
    def compute(transactions: List[Any], deployer_id: Any) -> Dict[str, float]:
        if not transactions:
            return {
                "graph_node_count": 0,
                "graph_edge_count": 0,
                "deployer_betweenness": 0.0,
                "max_k_core": 0.0,
                "pool_connectivity": 0.0,
            }

        G = nx.DiGraph()
        
        for tx in transactions:
            u = tx.from_wallet_id
            v = tx.to_wallet_id
            if u and v:
                G.add_edge(u, v)

        node_count = G.number_of_nodes()
        edge_count = G.number_of_edges()

        deployer_betweenness = 0.0
        if node_count > 0:
            # Betweenness centrality can be expensive, so we might want to approximate for very large graphs
            # We'll use the exact for now as token subgraphs are relatively small initially
            if node_count < 1000:
                betweenness = nx.betweenness_centrality(G)
                deployer_betweenness = betweenness.get(deployer_id, 0.0)

        max_k_core = 0.0
        if node_count > 0:
            # Convert to undirected for k-core
            G_undirected = G.to_undirected()
            G_undirected.remove_edges_from(nx.selfloop_edges(G_undirected))
            try:
                core_numbers = nx.core_number(G_undirected)
                if core_numbers:
                    max_k_core = float(max(core_numbers.values()))
            except Exception:
                pass

        # Pool connectivity is the ratio of edges connected to known pool nodes.
        # This requires pool addresses, which we would get from LiquidityEvents.
        # We simplify here for the prototype.
        pool_connectivity = 0.5 

        return {
            "graph_node_count": node_count,
            "graph_edge_count": edge_count,
            "deployer_betweenness": deployer_betweenness,
            "max_k_core": max_k_core,
            "pool_connectivity": pool_connectivity,
        }
