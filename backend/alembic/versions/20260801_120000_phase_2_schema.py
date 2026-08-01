"""Phase 2 Schema

Revision ID: phase_2_schema
Revises: 
Create Date: 2026-08-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'phase_2_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ENUM TYPES
    sa.Enum('ethereum', 'bsc', name='chain_enum').create(op.get_bind())
    sa.Enum('rug_pull', 'legitimate', 'unknown', name='label_enum').create(op.get_bind())
    sa.Enum('eoa', 'contract', 'deployer', 'liquidity_pool', 'exchange', 'unknown', name='wallet_type_enum').create(op.get_bind())
    sa.Enum('transfer', 'approval', 'swap', 'mint', 'burn', 'liquidity_add', 'liquidity_remove', 'other', name='tx_type_enum').create(op.get_bind())
    sa.Enum('mint', 'burn', 'swap', name='liquidity_event_type_enum').create(op.get_bind())
    sa.Enum('gatv2_tgn', 'gatv2_only', 'tgn_only', 'xgboost', 'random_forest', name='model_type_enum').create(op.get_bind())
    sa.Enum('pending', 'running', 'completed', 'failed', name='training_status_enum').create(op.get_bind())
    sa.Enum('pending', 'running', 'completed', 'failed', 'retrying', name='job_status_enum').create(op.get_bind())

    # WALLETS
    op.create_table('wallets',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('address', sa.String(length=42), nullable=False),
        sa.Column('chain', postgresql.ENUM('ethereum', 'bsc', name='chain_enum', create_type=False), nullable=False),
        sa.Column('wallet_type', postgresql.ENUM('eoa', 'contract', 'deployer', 'liquidity_pool', 'exchange', 'unknown', name='wallet_type_enum', create_type=False), server_default='unknown', nullable=False),
        sa.Column('is_contract', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_exchange', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('first_seen_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('transaction_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('address', 'chain', name='uq_wallets_address_chain')
    )
    op.create_index('ix_wallets_address', 'wallets', ['address'], unique=False)
    op.create_index('ix_wallets_chain_type', 'wallets', ['chain', 'wallet_type'], unique=False)

    # TOKENS
    op.create_table('tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('address', sa.String(length=42), nullable=False),
        sa.Column('chain', postgresql.ENUM('ethereum', 'bsc', name='chain_enum', create_type=False), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=True),
        sa.Column('symbol', sa.String(length=32), nullable=True),
        sa.Column('decimals', sa.SmallInteger(), nullable=True),
        sa.Column('total_supply', sa.Numeric(precision=78, scale=0), nullable=True),
        sa.Column('token_standard', sa.String(length=16), server_default='ERC20', nullable=False),
        sa.Column('deployer_address', sa.String(length=42), nullable=True),
        sa.Column('deployed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('block_number_deployed', sa.BigInteger(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('label', postgresql.ENUM('rug_pull', 'legitimate', 'unknown', name='label_enum', create_type=False), nullable=True),
        sa.Column('label_source', sa.String(length=64), nullable=True),
        sa.Column('project_midpoint_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('liquidity_withdrawn_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('address', 'chain', name='uq_tokens_address_chain')
    )
    op.create_index('ix_tokens_address', 'tokens', ['address'], unique=False)
    op.create_index('ix_tokens_chain_label', 'tokens', ['chain', 'label'], unique=False)
    op.create_index('ix_tokens_deployer_address', 'tokens', ['deployer_address'], unique=False)

    # CONTRACTS
    op.create_table('contracts',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('token_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('address', sa.String(length=42), nullable=False),
        sa.Column('chain', postgresql.ENUM('ethereum', 'bsc', name='chain_enum', create_type=False), nullable=False),
        sa.Column('bytecode_hash', sa.String(length=66), nullable=True),
        sa.Column('compiler_version', sa.String(length=64), nullable=True),
        sa.Column('is_source_verified', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_proxy', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('owner_address', sa.String(length=42), nullable=True),
        sa.Column('has_mint_function', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('has_pause_function', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('has_blacklist_function', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('has_hidden_fee', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('has_owner_withdrawal', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('max_tx_limit_pct', sa.Float(), nullable=True),
        sa.Column('risk_flag_count', sa.SmallInteger(), server_default='0', nullable=False),
        sa.Column('raw_source_code', sa.Text(), nullable=True),
        sa.Column('abi_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['token_id'], ['tokens.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('address', 'chain', name='uq_contracts_address_chain')
    )
    op.create_index('ix_contracts_address', 'contracts', ['address'], unique=False)
    op.create_index('ix_contracts_risk_flags', 'contracts', ['risk_flag_count'], unique=False)
    op.create_index('ix_contracts_token_id', 'contracts', ['token_id'], unique=False)

    # TRANSACTIONS
    op.create_table('transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('token_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tx_hash', sa.String(length=66), nullable=False),
        sa.Column('log_index', sa.Integer(), nullable=True),
        sa.Column('chain', postgresql.ENUM('ethereum', 'bsc', name='chain_enum', create_type=False), nullable=False),
        sa.Column('block_number', sa.BigInteger(), nullable=False),
        sa.Column('block_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('transaction_index', sa.Integer(), nullable=True),
        sa.Column('from_wallet_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('to_wallet_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('value_wei', sa.Numeric(precision=78, scale=0), server_default='0', nullable=False),
        sa.Column('gas_used', sa.BigInteger(), nullable=True),
        sa.Column('gas_price_wei', sa.Numeric(precision=30, scale=0), nullable=True),
        sa.Column('tx_type', postgresql.ENUM('transfer', 'approval', 'swap', 'mint', 'burn', 'liquidity_add', 'liquidity_remove', 'other', name='tx_type_enum', create_type=False), server_default='other', nullable=False),
        sa.Column('is_reverted', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('decoded_calldata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['from_wallet_id'], ['wallets.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['to_wallet_id'], ['wallets.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['token_id'], ['tokens.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tx_hash', 'log_index', name='uq_transactions_tx_hash_log_index')
    )
    op.create_index('ix_transactions_block_number', 'transactions', ['block_number'], unique=False)
    op.create_index('ix_transactions_from_wallet', 'transactions', ['from_wallet_id'], unique=False)
    op.create_index('ix_transactions_to_wallet', 'transactions', ['to_wallet_id'], unique=False)
    op.create_index('ix_transactions_token_block', 'transactions', ['token_id', 'block_timestamp'], unique=False)
    op.create_index('ix_transactions_tx_hash', 'transactions', ['tx_hash'], unique=False)
    op.create_index('ix_transactions_tx_type', 'transactions', ['tx_type'], unique=False)

    # LIQUIDITY EVENTS
    op.create_table('liquidity_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('token_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tx_hash', sa.String(length=66), nullable=False),
        sa.Column('log_index', sa.Integer(), nullable=False),
        sa.Column('chain', postgresql.ENUM('ethereum', 'bsc', name='chain_enum', create_type=False), nullable=False),
        sa.Column('pool_address', sa.String(length=42), nullable=False),
        sa.Column('pool_wallet_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('block_number', sa.BigInteger(), nullable=False),
        sa.Column('block_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('event_type', postgresql.ENUM('mint', 'burn', 'swap', name='liquidity_event_type_enum', create_type=False), nullable=False),
        sa.Column('amount0', sa.Numeric(precision=78, scale=0), nullable=True),
        sa.Column('amount1', sa.Numeric(precision=78, scale=0), nullable=True),
        sa.Column('reserve0_after', sa.Numeric(precision=78, scale=0), nullable=True),
        sa.Column('reserve1_after', sa.Numeric(precision=78, scale=0), nullable=True),
        sa.Column('actor_wallet_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reserve_ratio_change', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['actor_wallet_id'], ['wallets.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['pool_wallet_id'], ['wallets.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['token_id'], ['tokens.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tx_hash', 'log_index', name='uq_liquidity_tx_hash_log_index')
    )
    op.create_index('ix_liquidity_actor_wallet', 'liquidity_events', ['actor_wallet_id'], unique=False)
    op.create_index('ix_liquidity_event_type', 'liquidity_events', ['event_type'], unique=False)
    op.create_index('ix_liquidity_pool_address', 'liquidity_events', ['pool_address'], unique=False)
    op.create_index('ix_liquidity_token_block', 'liquidity_events', ['token_id', 'block_timestamp'], unique=False)

    # TOKEN FEATURES
    op.create_table('token_features',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('token_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('snapshot_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_pre_midpoint', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('total_transactions', sa.Integer(), nullable=True),
        sa.Column('unique_wallets', sa.Integer(), nullable=True),
        sa.Column('buy_to_sell_ratio', sa.Float(), nullable=True),
        sa.Column('holder_gini', sa.Float(), nullable=True),
        sa.Column('creator_supply_pct', sa.Float(), nullable=True),
        sa.Column('days_since_deployment', sa.Float(), nullable=True),
        sa.Column('has_mint_function', sa.Boolean(), nullable=True),
        sa.Column('has_pause_function', sa.Boolean(), nullable=True),
        sa.Column('has_blacklist_function', sa.Boolean(), nullable=True),
        sa.Column('has_hidden_fee', sa.Boolean(), nullable=True),
        sa.Column('is_proxy', sa.Boolean(), nullable=True),
        sa.Column('is_source_verified', sa.Boolean(), nullable=True),
        sa.Column('contract_risk_score', sa.Float(), nullable=True),
        sa.Column('graph_node_count', sa.Integer(), nullable=True),
        sa.Column('graph_edge_count', sa.Integer(), nullable=True),
        sa.Column('deployer_betweenness', sa.Float(), nullable=True),
        sa.Column('max_k_core', sa.Float(), nullable=True),
        sa.Column('pool_connectivity', sa.Float(), nullable=True),
        sa.Column('tx_burstiness', sa.Float(), nullable=True),
        sa.Column('avg_inter_tx_seconds', sa.Float(), nullable=True),
        sa.Column('liquidity_add_velocity', sa.Float(), nullable=True),
        sa.Column('supply_concentration_velocity', sa.Float(), nullable=True),
        sa.Column('time_since_last_liquidity_add', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['token_id'], ['tokens.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_id', 'snapshot_at', name='uq_token_features_token_snapshot')
    )
    op.create_index('ix_token_features_token_snapshot', 'token_features', ['token_id', 'snapshot_at'], unique=False)

    # TRAINING RUNS
    op.create_table('training_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('experiment_name', sa.String(length=128), nullable=False),
        sa.Column('model_version', sa.String(length=64), nullable=False),
        sa.Column('model_type', postgresql.ENUM('gatv2_tgn', 'gatv2_only', 'tgn_only', 'xgboost', 'random_forest', name='model_type_enum', create_type=False), nullable=False),
        sa.Column('hyperparameters', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('val_f1', sa.Float(), nullable=True),
        sa.Column('val_roc_auc', sa.Float(), nullable=True),
        sa.Column('decision_threshold', sa.Float(), nullable=True),
        sa.Column('model_file_path', sa.String(length=512), nullable=True),
        sa.Column('status', postgresql.ENUM('pending', 'running', 'completed', 'failed', name='training_status_enum', create_type=False), server_default='pending', nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('model_version')
    )

    # PREDICTIONS
    op.create_table('predictions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('token_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('model_version', sa.String(length=64), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('predicted_label', postgresql.ENUM('rug_pull', 'legitimate', 'unknown', name='label_enum', create_type=False), nullable=False),
        sa.Column('decision_threshold', sa.Float(), nullable=False),
        sa.Column('is_above_threshold', sa.Boolean(), nullable=False),
        sa.Column('lead_time_hours', sa.Float(), nullable=True),
        sa.Column('evaluated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('evidence_window_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('evidence_window_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('explanation_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('training_run_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['token_id'], ['tokens.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['training_run_id'], ['training_runs.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_predictions_risk_score', 'predictions', [sa.text('risk_score DESC')], unique=False)
    op.create_index('ix_predictions_token_evaluated', 'predictions', ['token_id', sa.text('evaluated_at DESC')], unique=False)
    op.create_index('ix_predictions_token_id', 'predictions', ['token_id'], unique=False)

    # EXPLANATIONS
    op.create_table('explanations',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('prediction_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('token_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('shap_base_value', sa.Float(), nullable=True),
        sa.Column('shap_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('shap_top_features', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('important_node_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('important_edge_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('node_importance_scores', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('edge_importance_scores', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('risk_summary_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['prediction_id'], ['predictions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['token_id'], ['tokens.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('prediction_id', name='uq_explanations_prediction_id')
    )
    # Re-create FK from prediction to explanation that was deferred
    op.create_foreign_key('fk_predictions_explanation_id', 'predictions', 'explanations', ['explanation_id'], ['id'], ondelete='SET NULL')

    # COLLECTION JOBS
    op.create_table('collection_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('token_address', sa.String(length=42), nullable=False),
        sa.Column('chain', postgresql.ENUM('ethereum', 'bsc', name='chain_enum', create_type=False), nullable=False),
        sa.Column('job_type', sa.String(length=32), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'running', 'completed', 'failed', 'retrying', name='job_status_enum', create_type=False), server_default='pending', nullable=False),
        sa.Column('celery_task_id', sa.String(length=64), nullable=True),
        sa.Column('records_collected', sa.Integer(), server_default='0', nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_constraint('fk_predictions_explanation_id', 'predictions', type_='foreignkey')
    op.drop_table('collection_jobs')
    op.drop_table('explanations')
    op.drop_index('ix_predictions_token_id', table_name='predictions')
    op.drop_index('ix_predictions_token_evaluated', table_name='predictions')
    op.drop_index('ix_predictions_risk_score', table_name='predictions')
    op.drop_table('predictions')
    op.drop_table('training_runs')
    op.drop_index('ix_token_features_token_snapshot', table_name='token_features')
    op.drop_table('token_features')
    op.drop_index('ix_liquidity_token_block', table_name='liquidity_events')
    op.drop_index('ix_liquidity_pool_address', table_name='liquidity_events')
    op.drop_index('ix_liquidity_event_type', table_name='liquidity_events')
    op.drop_index('ix_liquidity_actor_wallet', table_name='liquidity_events')
    op.drop_table('liquidity_events')
    op.drop_index('ix_transactions_tx_type', table_name='transactions')
    op.drop_index('ix_transactions_tx_hash', table_name='transactions')
    op.drop_index('ix_transactions_token_block', table_name='transactions')
    op.drop_index('ix_transactions_to_wallet', table_name='transactions')
    op.drop_index('ix_transactions_from_wallet', table_name='transactions')
    op.drop_index('ix_transactions_block_number', table_name='transactions')
    op.drop_table('transactions')
    op.drop_index('ix_contracts_token_id', table_name='contracts')
    op.drop_index('ix_contracts_risk_flags', table_name='contracts')
    op.drop_index('ix_contracts_address', table_name='contracts')
    op.drop_table('contracts')
    op.drop_index('ix_tokens_deployer_address', table_name='tokens')
    op.drop_index('ix_tokens_chain_label', table_name='tokens')
    op.drop_index('ix_tokens_address', table_name='tokens')
    op.drop_table('tokens')
    op.drop_index('ix_wallets_chain_type', table_name='wallets')
    op.drop_index('ix_wallets_address', table_name='wallets')
    op.drop_table('wallets')

    sa.Enum(name='job_status_enum').drop(op.get_bind())
    sa.Enum(name='training_status_enum').drop(op.get_bind())
    sa.Enum(name='model_type_enum').drop(op.get_bind())
    sa.Enum(name='liquidity_event_type_enum').drop(op.get_bind())
    sa.Enum(name='tx_type_enum').drop(op.get_bind())
    sa.Enum(name='wallet_type_enum').drop(op.get_bind())
    sa.Enum(name='label_enum').drop(op.get_bind())
    sa.Enum(name='chain_enum').drop(op.get_bind())
