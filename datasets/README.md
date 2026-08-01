# Datasets

This directory stores raw and processed data for training and evaluation.

## Expected Files (not tracked in git)

```
datasets/
├── raw/
│   ├── ethereum_tokens.csv        # Raw collected token data
│   ├── bsc_tokens.csv
│   └── labels.csv                 # Rug pull / legitimate labels
├── processed/
│   ├── features_ethereum.parquet  # Engineered features
│   ├── features_bsc.parquet
│   └── graph_data/                # PyG graph objects
└── splits/
    ├── train.parquet
    ├── val.parquet
    └── test.parquet
```

## Labelling Protocol (per TM-RugPull methodology)
- A token is labelled **rug pull** if it shows a 72-hour absence of liquidity, on-chain activity, and trading volume.
- All features are extracted BEFORE the **Project Midpoint** (first half of token lifespan).
- Labels cross-referenced with CertiK, De.Fi, and Rekt.news.

## Data Sources
- Etherscan API (Ethereum)
- BscScan API (BSC)
- DeFiLlama (TVL data)
- Web3 RPC via Alchemy
