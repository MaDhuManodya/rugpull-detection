"""
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
