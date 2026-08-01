"""
app/collectors/parsers/wallet.py
Wallet Collector.
Extracts wallet metadata and handles classification (EOA vs Contract).
"""
from web3 import AsyncWeb3
from app.models.enums import WalletTypeEnum

class WalletParser:
    @staticmethod
    async def classify_wallet(w3: AsyncWeb3, address: str) -> dict:
        """Determines if an address is an EOA or a smart contract."""
        code = await w3.eth.get_code(address)
        is_contract = len(code) > 2  # '0x' means empty
        
        wallet_type = WalletTypeEnum.CONTRACT if is_contract else WalletTypeEnum.EOA
        
        return {
            "address": address,
            "is_contract": is_contract,
            "wallet_type": wallet_type.value
        }
