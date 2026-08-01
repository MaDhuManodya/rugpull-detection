"""
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
