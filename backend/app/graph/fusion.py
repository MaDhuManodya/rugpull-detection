"""
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
