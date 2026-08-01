import os

os.makedirs("app/graph", exist_ok=True)

# 1. Builder
with open("app/graph/builder.py", "w") as f:
    f.write('''"""
app/graph/builder.py
Temporal Graph Builder bridging PostgreSQL to PyTorch Geometric.

Converts transactions and liquidity events into a continuous, ordered 
TemporalData object for the TGN module.
"""
from typing import Dict, Any, Tuple
import pandas as pd
import torch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# We conditionally import PyG components to allow the backend to run without ML dependencies if needed
try:
    from torch_geometric.data import TemporalData
    HAS_PYG = True
except ImportError:
    HAS_PYG = False

from app.models.transaction import Transaction
from app.models.liquidity_event import LiquidityEvent

class GraphBuilder:
    @staticmethod
    async def build_temporal_graph(db: AsyncSession, token_id: str) -> Any:
        """
        Builds a strictly temporally ordered event graph for TGN.
        Returns a torch_geometric.data.TemporalData object.
        """
        if not HAS_PYG:
            raise ImportError("PyTorch Geometric is not installed.")

        # 1. Fetch Transactions
        txs_result = await db.execute(
            select(Transaction)
            .filter(Transaction.token_id == token_id)
            .order_by(Transaction.block_timestamp.asc())
        )
        transactions = list(txs_result.scalars().all())

        # 2. Fetch Liquidity Events
        liq_result = await db.execute(
            select(LiquidityEvent)
            .filter(LiquidityEvent.token_id == token_id)
            .order_by(LiquidityEvent.block_timestamp.asc())
        )
        liquidity_events = list(liq_result.scalars().all())

        # 3. Merge and Sort chronologically
        events = []
        for tx in transactions:
            if tx.from_wallet_id and tx.to_wallet_id:
                events.append({
                    "timestamp": int(tx.block_timestamp.timestamp()),
                    "block_number": tx.block_number,
                    "tx_hash": tx.tx_hash,
                    "edge_type": tx.tx_type.value,
                    "value": float(tx.value_wei),
                    "gas": float(tx.gas_used or 0),
                    "token_address": str(tx.token_id), # Token identity
                    "src_wallet": str(tx.from_wallet_id),
                    "dst_wallet": str(tx.to_wallet_id)
                })

        for liq in liquidity_events:
            if liq.actor_wallet_id and liq.pool_wallet_id:
                # Map AMM events to directed edges
                if liq.event_type.value == 'mint':
                    src = str(liq.actor_wallet_id)
                    dst = str(liq.pool_wallet_id)
                else: # burn or swap
                    src = str(liq.pool_wallet_id)
                    dst = str(liq.actor_wallet_id)

                events.append({
                    "timestamp": int(liq.block_timestamp.timestamp()),
                    "block_number": liq.block_number,
                    "tx_hash": liq.tx_hash,
                    "edge_type": liq.event_type.value,
                    "value": float(liq.amount0 or 0) + float(liq.amount1 or 0), # Simplified
                    "gas": 0.0, # Not natively tracked on liq event table without join
                    "token_address": str(liq.token_id),
                    "src_wallet": src,
                    "dst_wallet": dst
                })

        # Sort strictly by timestamp
        df = pd.DataFrame(events)
        if df.empty:
            raise ValueError("No events found to build graph.")
            
        df = df.sort_values(by=["timestamp", "block_number"]).reset_index(drop=True)

        # 4. Map Wallet Addresses to Continuous Integers (Node IDs)
        unique_nodes = pd.concat([df['src_wallet'], df['dst_wallet']]).unique()
        node_mapping = {address: idx for idx, address in enumerate(unique_nodes)}
        
        df['src'] = df['src_wallet'].map(node_mapping)
        df['dst'] = df['dst_wallet'].map(node_mapping)

        # 5. Construct PyG Tensors
        src = torch.tensor(df['src'].values, dtype=torch.long)
        dst = torch.tensor(df['dst'].values, dtype=torch.long)
        t = torch.tensor(df['timestamp'].values, dtype=torch.long)
        
        # Edge features (msg): [value, gas, edge_type_encoded, block_number]
        # In practice, edge_type string would be one-hot encoded or embedded. 
        # Here we provide a simplified continuous matrix.
        df['edge_type_code'] = df['edge_type'].astype('category').cat.codes
        msg = torch.tensor(
            df[['value', 'gas', 'edge_type_code', 'block_number']].values, 
            dtype=torch.float
        )

        temporal_data = TemporalData(
            src=src,
            dst=dst,
            t=t,
            msg=msg
        )
        
        return temporal_data, node_mapping
''')

# 2. Fusion
with open("app/graph/fusion.py", "w") as f:
    f.write('''"""
app/graph/fusion.py
Multimodal Feature Fusion Preprocessor.

Extracts the 22 pre-computed features and pads missing values for the 
initial spatial representation matrix X.
"""
import torch
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.token_feature import TokenFeature

class FeatureFusionBuilder:
    @staticmethod
    async def build_initial_node_features(
        db: AsyncSession, 
        token_id: str, 
        node_mapping: Dict[str, int]
    ) -> torch.Tensor:
        """
        Builds the initial `x` node feature matrix required by GATv2.
        Assigns the token's fused feature profile to the relevant core nodes,
        and initializes empty/generic features for peripheral wallets.
        """
        # Fetch the latest pre-midpoint feature snapshot for this token
        result = await db.execute(
            select(TokenFeature)
            .filter(TokenFeature.token_id == token_id)
            .filter(TokenFeature.is_pre_midpoint == True)
            .order_by(TokenFeature.snapshot_at.desc())
            .limit(1)
        )
        feature_row = result.scalar_one_or_none()
        
        num_nodes = len(node_mapping)
        num_features = 22 # 22 explicitly defined features in Phase 4
        
        # Initialize the Node Matrix X
        x = torch.zeros((num_nodes, num_features), dtype=torch.float)
        
        if not feature_row:
            return x # Return zeros if no features calculated yet
            
        # Extract the 22 features into a dense vector
        token_vector = [
            # On-chain
            float(feature_row.total_transactions or 0),
            float(feature_row.unique_wallets or 0),
            float(feature_row.buy_to_sell_ratio or 0),
            float(feature_row.holder_gini or 0),
            float(feature_row.creator_supply_pct or 0),
            float(feature_row.days_since_deployment or 0),
            # Contract
            float(feature_row.has_mint_function or 0),
            float(feature_row.has_pause_function or 0),
            float(feature_row.has_blacklist_function or 0),
            float(feature_row.has_hidden_fee or 0),
            float(feature_row.is_proxy or 0),
            float(feature_row.is_source_verified or 0),
            float(feature_row.contract_risk_score or 0),
            # Graph
            float(feature_row.graph_node_count or 0),
            float(feature_row.graph_edge_count or 0),
            float(feature_row.deployer_betweenness or 0),
            float(feature_row.max_k_core or 0),
            float(feature_row.pool_connectivity or 0),
            # Temporal
            float(feature_row.tx_burstiness or 0),
            float(feature_row.avg_inter_tx_seconds or 0),
            float(feature_row.liquidity_add_velocity or 0),
            float(feature_row.supply_concentration_velocity or 0),
        ]
        
        token_tensor = torch.tensor(token_vector, dtype=torch.float)
        
        # In a full heterogeneous implementation, we would assign this vector
        # only to the specific Token/Contract/Deployer nodes, and use a separate
        # profile for standard wallets. For a homogenous PyG matrix, we broadcast
        # the token's global risk profile or handle it via GATv2 attention.
        
        # Assign the token profile to all nodes for now as an initial state.
        # The TGN Memory module will update individual node states dynamically.
        x = token_tensor.repeat(num_nodes, 1)
        
        return x
''')

# Inits
with open("app/graph/__init__.py", "w") as f: pass

print("Generated Graph Construction Layer.")
