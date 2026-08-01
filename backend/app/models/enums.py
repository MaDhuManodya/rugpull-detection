"""
app/models/enums.py
────────────────────
All Python Enum definitions that map to PostgreSQL ENUM types.
Every enum here corresponds exactly to a CREATE TYPE statement
in the Alembic initial migration.

Source: Chapter 4, Section 4.5 — Database Design
"""

from __future__ import annotations

import enum


class ChainEnum(str, enum.Enum):
    """Supported blockchain networks. Ch4 §4.5.1."""

    ETHEREUM = "ethereum"
    BSC = "bsc"


class LabelEnum(str, enum.Enum):
    """
    Ground-truth and predicted token label.
    Ch3 §3.11 — evaluation uses rug_pull as positive class.
    """

    RUG_PULL = "rug_pull"
    LEGITIMATE = "legitimate"
    UNKNOWN = "unknown"


class WalletTypeEnum(str, enum.Enum):
    """
    Coarse wallet classification.
    Ch4 §4.5.1 — 'a coarse wallet-type label'.
    """

    EOA = "eoa"                          # Externally-owned account
    CONTRACT = "contract"                # Generic contract
    DEPLOYER = "deployer"                # Token deployer wallet
    LIQUIDITY_POOL = "liquidity_pool"    # AMM liquidity pool
    EXCHANGE = "exchange"                # Centralised/decentralised exchange
    UNKNOWN = "unknown"


class TxTypeEnum(str, enum.Enum):
    """
    Transaction type decoded from calldata.
    Ch4 §4.4.2 — transfer, approval, swap, or liquidity operation.
    """

    TRANSFER = "transfer"
    APPROVAL = "approval"
    SWAP = "swap"
    MINT = "mint"
    BURN = "burn"
    LIQUIDITY_ADD = "liquidity_add"
    LIQUIDITY_REMOVE = "liquidity_remove"
    OTHER = "other"


class LiquidityEventTypeEnum(str, enum.Enum):
    """
    Liquidity pool event type.
    Ch4 §4.4.3 — 'Mint, Burn and Swap events emitted by AMM pools'.
    """

    MINT = "mint"
    BURN = "burn"
    SWAP = "swap"


class ModelTypeEnum(str, enum.Enum):
    """
    Model architectures for ablation study.
    Ch3 §3.11 — three baselines: feature-only, spatial-only, temporal-only.
    """

    GATV2_TGN = "gatv2_tgn"           # Full model (primary)
    GATV2_ONLY = "gatv2_only"          # Spatial-only ablation
    TGN_ONLY = "tgn_only"              # Temporal-only ablation
    XGBOOST = "xgboost"                # Tree-based baseline
    RANDOM_FOREST = "random_forest"    # Tree-based baseline


class TrainingStatusEnum(str, enum.Enum):
    """Training run lifecycle status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobStatusEnum(str, enum.Enum):
    """Data collection job lifecycle status. Ch4 §4.4.4."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
