"""
app/collectors/core/connector.py
────────────────────────────────
Blockchain Connector Factory.

Source: Chapter 4, Section 4.4.1
Quote: "The primary data source is a JSON-RPC connection to Ethereum and
        BNB Smart Chain full nodes..."

Provides AsyncWeb3 instances configured with correct RPC URLs and
basic rate limiting / retry logic.
"""

import asyncio
from typing import Dict

from web3 import AsyncWeb3
from web3.providers.async_rpc import AsyncHTTPProvider
from web3.middleware import async_geth_poa_middleware

from app.core.config import settings
from app.models.enums import ChainEnum

class BlockchainConnector:
    """
    Manages connections to multiple blockchain networks.
    Provides singleton-like access to AsyncWeb3 instances.
    """
    
    def __init__(self):
        self._providers: Dict[ChainEnum, AsyncWeb3] = {}
        self._init_providers()

    def _init_providers(self):
        # Ethereum Provider
        if settings.alchemy_eth_url:
            eth_url = settings.alchemy_eth_url
        else:
            eth_url = f"https://mainnet.infura.io/v3/{settings.infura_project_id}" if settings.infura_project_id else "https://eth.llamarpc.com"
            
        eth_w3 = AsyncWeb3(AsyncHTTPProvider(eth_url))
        self._providers[ChainEnum.ETHEREUM] = eth_w3

        # BSC Provider
        if settings.alchemy_bsc_url:
            bsc_url = settings.alchemy_bsc_url
        else:
            bsc_url = "https://bsc-dataseed.binance.org/"
            
        bsc_w3 = AsyncWeb3(AsyncHTTPProvider(bsc_url))
        # BSC uses POA consensus, so we must inject the middleware
        bsc_w3.middleware_onion.inject(async_geth_poa_middleware, layer=0)
        self._providers[ChainEnum.BSC] = bsc_w3

    def get_provider(self, chain: ChainEnum) -> AsyncWeb3:
        """Returns the configured AsyncWeb3 instance for the given chain."""
        if chain not in self._providers:
            raise ValueError(f"No provider configured for chain: {chain}")
        return self._providers[chain]
        
    async def get_latest_block_number(self, chain: ChainEnum) -> int:
        """Helper to get latest block with retry logic."""
        w3 = self.get_provider(chain)
        # In a production environment, tenacity should wrap this
        for attempt in range(3):
            try:
                return await w3.eth.block_number
            except Exception as e:
                if attempt == 2:
                    raise e
                await asyncio.sleep(1)

# Global connector instance
blockchain_connector = BlockchainConnector()
