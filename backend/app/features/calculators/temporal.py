"""
app/features/calculators/temporal.py
Temporal and Liquidity features calculator.
"""
from typing import List, Dict, Any
import numpy as np

class TemporalCalculator:
    @staticmethod
    def compute(transactions: List[Any], liquidity_events: List[Any], current_timestamp: int) -> Dict[str, float]:
        # Burstiness & Inter-arrival time
        tx_burstiness = 0.0
        avg_inter_tx = 0.0
        
        if len(transactions) > 1:
            # Extract timestamps
            timestamps = sorted([tx.block_timestamp.timestamp() for tx in transactions])
            inter_arrival_times = np.diff(timestamps)
            
            mean_iat = np.mean(inter_arrival_times)
            std_iat = np.std(inter_arrival_times)
            
            avg_inter_tx = float(mean_iat)
            if mean_iat > 0:
                tx_burstiness = float(std_iat / mean_iat)

        # Liquidity Features
        time_since_add = 0.0
        liquidity_add_velocity = 0.0
        
        if liquidity_events:
            add_events = [e for e in liquidity_events if e.event_type.value == 'mint']
            if add_events:
                last_add_ts = max([e.block_timestamp.timestamp() for e in add_events])
                time_since_add = float(current_timestamp - last_add_ts)
                
                # Velocity: count of adds in the last X hours / total time
                liquidity_add_velocity = float(len(add_events))

        # Supply concentration velocity would require historical Gini.
        supply_concentration_velocity = 0.0

        return {
            "tx_burstiness": tx_burstiness,
            "avg_inter_tx_seconds": avg_inter_tx,
            "liquidity_add_velocity": liquidity_add_velocity,
            "supply_concentration_velocity": supply_concentration_velocity,
            "time_since_last_liquidity_add": time_since_add,
        }
