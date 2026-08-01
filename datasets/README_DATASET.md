# Integrated Rug Pull Dataset

## Data Sources
1. TM-RugPull (Primary Label Truth)
2. CRPWarner (Secondary Verification)
3. Dianxiang Sun (Secondary Verification)

## Download Date
August 2026

## Merge Strategy
Data from all three sources was loaded and unified into an internal 9-column schema. Token addresses were used as the primary conflict resolution key. TM-RugPull labels take absolute priority. Conflicting labels across secondary datasets without TM-RugPull consensus were excluded and logged in `reports/conflict_report.csv`.

## Preprocessing & Cleaning
- Standardized chain strings (e.g. 'ETH' to 'Ethereum').
- Enforced chronological sorting to eliminate lookahead bias (Project Midpoint approach).

## On-Chain Collection Fallback
As API keys for Etherscan/BscScan were not supplied during execution, the deep blockchain RPC crawling for transactions and liquidity events (via Phase 3 Connector) was bypassed to prevent immediate rate-limit pipeline failures. The integrated schema uses the properties provided strictly within the parsed dataset files.
