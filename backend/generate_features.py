import os

os.makedirs("app/features/calculators", exist_ok=True)

# 1. Onchain Calculator
with open("app/features/calculators/onchain.py", "w") as f:
    f.write('''"""
app/features/calculators/onchain.py
On-chain features calculator.
"""
from typing import List, Dict, Any
from decimal import Decimal
import numpy as np

class OnChainCalculator:
    @staticmethod
    def calculate_gini(balances: List[float]) -> float:
        """Calculates the Gini coefficient of a distribution."""
        if not balances:
            return 0.0
        array = np.array(balances, dtype=np.float64)
        array = array.flatten()
        if np.amin(array) < 0:
            array -= np.amin(array)
        array += 1e-8
        array = np.sort(array)
        index = np.arange(1, array.shape[0] + 1)
        n = array.shape[0]
        return float(((np.sum((2 * index - n  - 1) * array)) / (n * np.sum(array))))

    @staticmethod
    def compute(transactions: List[Any], token_metadata: Any, current_timestamp: int) -> Dict[str, float]:
        if not transactions:
            return {
                "total_transactions": 0,
                "unique_wallets": 0,
                "buy_to_sell_ratio": 0.0,
                "holder_gini": 0.0,
                "creator_supply_pct": 0.0,
                "days_since_deployment": 0.0,
            }

        unique_wallets = set()
        balances = {}
        buy_vol, sell_vol = 0.0, 0.0

        for tx in transactions:
            # Assuming tx is a dictionary-like object or SQLAlchemy model
            # For this mock, we assume dictionary access
            from_addr = tx.from_wallet_id
            to_addr = tx.to_wallet_id
            val = float(tx.value_wei)
            
            unique_wallets.add(from_addr)
            unique_wallets.add(to_addr)
            
            balances[from_addr] = balances.get(from_addr, 0.0) - val
            balances[to_addr] = balances.get(to_addr, 0.0) + val
            
            if tx.tx_type == 'swap': # Simplified buy/sell logic
                # Ideally, we need pool address to determine buy vs sell
                # This is a placeholder for the buy/sell volume extraction
                pass

        # Cleanup negative balances due to precision or missing historical data
        clean_balances = [max(0, b) for b in balances.values()]
        gini = OnChainCalculator.calculate_gini(clean_balances)
        
        # Calculate days since deployment
        deployed_at = token_metadata.deployed_at.timestamp() if token_metadata.deployed_at else current_timestamp
        days_since = (current_timestamp - deployed_at) / 86400.0

        creator_balance = balances.get(token_metadata.deployer_address, 0.0)
        total_supply = float(token_metadata.total_supply) if token_metadata.total_supply else 1.0
        creator_supply_pct = creator_balance / total_supply if total_supply > 0 else 0.0

        return {
            "total_transactions": len(transactions),
            "unique_wallets": len(unique_wallets),
            "buy_to_sell_ratio": buy_vol / sell_vol if sell_vol > 0 else 1.0, # Simplified
            "holder_gini": gini,
            "creator_supply_pct": creator_supply_pct,
            "days_since_deployment": days_since,
        }
''')

# 2. Contract Calculator
with open("app/features/calculators/contract.py", "w") as f:
    f.write('''"""
app/features/calculators/contract.py
Smart Contract features calculator.
"""
from typing import Dict, Any

class ContractCalculator:
    @staticmethod
    def compute(contract: Any) -> Dict[str, Any]:
        if not contract:
            return {
                "has_mint_function": False,
                "has_pause_function": False,
                "has_blacklist_function": False,
                "has_hidden_fee": False,
                "is_proxy": False,
                "is_source_verified": False,
                "contract_risk_score": 0.0,
            }

        risk_score = 0.0
        if contract.has_mint_function: risk_score += 1.0
        if contract.has_pause_function: risk_score += 1.0
        if contract.has_blacklist_function: risk_score += 1.0
        if contract.has_hidden_fee: risk_score += 1.0
        if contract.is_proxy: risk_score += 0.5
        if not contract.is_source_verified: risk_score += 2.0 # Heavy penalty for unverified

        return {
            "has_mint_function": contract.has_mint_function,
            "has_pause_function": contract.has_pause_function,
            "has_blacklist_function": contract.has_blacklist_function,
            "has_hidden_fee": contract.has_hidden_fee,
            "is_proxy": contract.is_proxy,
            "is_source_verified": contract.is_source_verified,
            "contract_risk_score": risk_score,
        }
''')

# 3. Graph Calculator
with open("app/features/calculators/graph.py", "w") as f:
    f.write('''"""
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
''')

# 4. Temporal Calculator
with open("app/features/calculators/temporal.py", "w") as f:
    f.write('''"""
app/features/calculators/temporal.py
Temporal and Liquidity features calculator.
"""
from typing import List, Dict, Any
import numpy as np

class TemporalCalculator:
    @staticmethod
    def compute(transactions: List[Any], liquidity_events: List[Any], current_timestamp: int) -> Dict[str, float]:
        # Burstiness & Inter-arrival time
        tx_burstiness = 0.0
        avg_inter_tx = 0.0
        
        if len(transactions) > 1:
            # Extract timestamps
            timestamps = sorted([tx.block_timestamp.timestamp() for tx in transactions])
            inter_arrival_times = np.diff(timestamps)
            
            mean_iat = np.mean(inter_arrival_times)
            std_iat = np.std(inter_arrival_times)
            
            avg_inter_tx = float(mean_iat)
            if mean_iat > 0:
                tx_burstiness = float(std_iat / mean_iat)

        # Liquidity Features
        time_since_add = 0.0
        liquidity_add_velocity = 0.0
        
        if liquidity_events:
            add_events = [e for e in liquidity_events if e.event_type.value == 'mint']
            if add_events:
                last_add_ts = max([e.block_timestamp.timestamp() for e in add_events])
                time_since_add = float(current_timestamp - last_add_ts)
                
                # Velocity: count of adds in the last X hours / total time
                liquidity_add_velocity = float(len(add_events))

        # Supply concentration velocity would require historical Gini.
        supply_concentration_velocity = 0.0

        return {
            "tx_burstiness": tx_burstiness,
            "avg_inter_tx_seconds": avg_inter_tx,
            "liquidity_add_velocity": liquidity_add_velocity,
            "supply_concentration_velocity": supply_concentration_velocity,
            "time_since_last_liquidity_add": time_since_add,
        }
''')

# 5. Builder
with open("app/features/builder.py", "w") as f:
    f.write('''"""
app/features/builder.py
Feature Builder Orchestrator.
Fetches data and combines the results from all calculators.
"""
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.token import Token
from app.models.contract import Contract
from app.models.transaction import Transaction
from app.models.liquidity_event import LiquidityEvent
from app.models.token_feature import TokenFeature

from app.features.calculators.onchain import OnChainCalculator
from app.features.calculators.contract import ContractCalculator
from app.features.calculators.graph import GraphCalculator
from app.features.calculators.temporal import TemporalCalculator

class FeatureBuilder:
    @staticmethod
    async def build_snapshot(db: AsyncSession, token_id: str, snapshot_at: datetime) -> TokenFeature:
        """
        Orchestrates the computation of all 22 features for a token at a specific time.
        """
        # 1. Fetch Token metadata
        token = await db.scalar(select(Token).filter_by(id=token_id))
        if not token:
            raise ValueError(f"Token {token_id} not found")

        # 2. Fetch Transactions before snapshot
        txs_result = await db.execute(
            select(Transaction)
            .filter(Transaction.token_id == token_id)
            .filter(Transaction.block_timestamp < snapshot_at)
        )
        transactions = list(txs_result.scalars().all())

        # 3. Fetch Liquidity Events before snapshot
        liq_result = await db.execute(
            select(LiquidityEvent)
            .filter(LiquidityEvent.token_id == token_id)
            .filter(LiquidityEvent.block_timestamp < snapshot_at)
        )
        liquidity_events = list(liq_result.scalars().all())

        # 4. Fetch Contract Metadata
        contract = await db.scalar(select(Contract).filter_by(token_id=token_id))

        # 5. Compute Features
        current_ts = int(snapshot_at.timestamp())
        
        onchain_features = OnChainCalculator.compute(transactions, token, current_ts)
        contract_features = ContractCalculator.compute(contract)
        graph_features = GraphCalculator.compute(transactions, token.deployer_address)
        temporal_features = TemporalCalculator.compute(transactions, liquidity_events, current_ts)

        # 6. Assemble TokenFeature
        feature_record = TokenFeature(
            token_id=token_id,
            snapshot_at=snapshot_at,
            is_pre_midpoint=True, # Will be set accurately during training phase mapping
            
            # On-chain
            **onchain_features,
            
            # Contract
            **contract_features,
            
            # Graph
            **graph_features,
            
            # Temporal
            **temporal_features
        )
        
        # 7. Persist (UPSERT logic ideally, simple add for now)
        db.add(feature_record)
        await db.commit()
        
        return feature_record
''')

# Inits
with open("app/features/__init__.py", "w") as f: pass
with open("app/features/calculators/__init__.py", "w") as f: pass

print("Generated Feature Engineering Layer.")
