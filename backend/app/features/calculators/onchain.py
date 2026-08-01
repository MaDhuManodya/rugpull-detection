"""
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
