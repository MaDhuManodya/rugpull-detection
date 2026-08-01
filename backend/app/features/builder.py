"""
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
