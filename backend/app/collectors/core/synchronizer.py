"""
app/collectors/core/synchronizer.py
───────────────────────────────────
Block Synchronizer.

Source: Chapter 4, Section 4.4.2
Tracks the latest processed block, resumes after restart, and
handles basic chain reorganizations.
"""

import asyncio
import logging
from typing import Callable, Coroutine, Any

from app.collectors.core.connector import blockchain_connector
from app.models.enums import ChainEnum

logger = logging.logger if hasattr(logging, "logger") else logging.getLogger(__name__)

class BlockSynchronizer:
    def __init__(self, chain: ChainEnum):
        self.chain = chain
        self.w3 = blockchain_connector.get_provider(chain)
        # In a full implementation, this state would be loaded from and saved to the database
        self.last_processed_block = 0
        self.current_block_hash = None

    async def initialize_state(self, start_block: int = None):
        """Loads the last processed block from DB or uses the provided start_block."""
        # TODO: Load from Database via Repository
        if start_block is not None:
            self.last_processed_block = start_block
        else:
            self.last_processed_block = await self.w3.eth.block_number

        block = await self.w3.eth.get_block(self.last_processed_block)
        self.current_block_hash = block['hash']
        logger.info(f"Initialized synchronizer for {self.chain} at block {self.last_processed_block}")

    async def sync_blocks(self, process_callback: Callable[[int], Coroutine[Any, Any, None]]):
        """
        Polls for new blocks continuously.
        Handles chain reorgs by verifying parent hashes.
        """
        while True:
            try:
                latest_block = await self.w3.eth.block_number
                
                if self.last_processed_block >= latest_block:
                    await asyncio.sleep(5)
                    continue
                    
                target_block = self.last_processed_block + 1
                block = await self.w3.eth.get_block(target_block)
                
                # Reorganization check (if we have a previous hash to compare)
                if self.current_block_hash and block['parentHash'] != self.current_block_hash:
                    logger.warning(f"Chain reorg detected at block {target_block} on {self.chain}")
                    # Revert one block and try again
                    self.last_processed_block -= 1
                    prev_block = await self.w3.eth.get_block(self.last_processed_block)
                    self.current_block_hash = prev_block['hash']
                    continue

                # Process block via callback
                await process_callback(target_block)

                # Update state
                self.last_processed_block = target_block
                self.current_block_hash = block['hash']
                # TODO: Save updated state to Database

            except Exception as e:
                logger.error(f"Error in sync loop for {self.chain}: {e}")
                await asyncio.sleep(5)

    async def backfill_historical(self, start_block: int, end_block: int, process_callback: Callable[[int], Coroutine[Any, Any, None]]):
        """Backfill a specific range of historical blocks."""
        logger.info(f"Starting backfill on {self.chain} from {start_block} to {end_block}")
        for block_num in range(start_block, end_block + 1):
            await process_callback(block_num)
        logger.info(f"Completed backfill on {self.chain} up to {end_block}")
