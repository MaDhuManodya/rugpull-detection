"""
app/collectors/parsers/contract.py
Smart Contract Collector.
Fetches bytecode, ABIs, metadata, and verification status via Explorer APIs.
"""
import httpx
from app.core.config import settings
from app.models.enums import ChainEnum

class ContractParser:
    @staticmethod
    async def fetch_contract_metadata(address: str, chain: ChainEnum) -> dict:
        """
        Fetches ABI and source code from Etherscan/BscScan if verified.
        """
        if chain == ChainEnum.ETHEREUM:
            api_url = settings.etherscan_api_url
            api_key = settings.etherscan_api_key
        else:
            api_url = settings.bscscan_api_url
            api_key = settings.bscscan_api_key
            
        if not api_url or not api_key:
            return {"is_verified": False, "abi": None}
            
        params = {
            "module": "contract",
            "action": "getsourcecode",
            "address": address,
            "apikey": api_key
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, params=params)
            data = response.json()
            
            if data.get("status") == "1" and data.get("result"):
                result = data["result"][0]
                return {
                    "is_verified": True,
                    "abi": result.get("ABI"),
                    "compiler_version": result.get("CompilerVersion"),
                    "source_code": result.get("SourceCode"),
                    "contract_name": result.get("ContractName")
                }
                
        return {"is_verified": False, "abi": None}
