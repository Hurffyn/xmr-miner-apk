"""
Balance tracking by parsing XMRig API output and pool data.
"""
import re
import subprocess
import requests
from typing import Optional


class BalanceTracker:
    def __init__(self, pool_host: str, wallet: str):
        self.pool_host = pool_host
        self.wallet = wallet
        self.local_hashrate = 0.0
        self.shares_accepted = 0
        self.shares_rejected = 0
        
    def parse_xmrig_output(self, line: str):
        """Parse XMRig console output for hashrate and shares."""
        # Multiple patterns for hashrate
        # Pattern 1: "speed 10s/60s/15m 1234.5 1230.0 1225.5 H/s"
        # Pattern 2: "miner speed 10s/60s/15m 1234.5 1230.0 1225.5 H/s max 1500.0 H/s"
        # Pattern 3: "speed 2.5s/60s/15m 123.4 H/s 120.0 H/s 118.5 H/s"
        
        line_lower = line.lower()
        
        if 'speed' in line_lower and 'h/s' in line_lower:
            # Find all numbers followed by H/s or h/s
            matches = re.findall(r'(\d+\.?\d*)\s*[hH]/s', line)
            if matches:
                # Take the first hashrate value (usually 10s average)
                try:
                    self.local_hashrate = float(matches[0])
                except (ValueError, IndexError):
                    pass
        
        # Alternative pattern: look for hashrate in format "1234.5 H/s"
        elif 'h/s' in line_lower:
            matches = re.findall(r'(\d+\.?\d*)\s*[hH]/s', line)
            if matches:
                try:
                    self.local_hashrate = float(matches[0])
                except (ValueError, IndexError):
                    pass
        
        # Count accepted/rejected shares
        if 'accepted' in line_lower and 'share' in line_lower:
            self.shares_accepted += 1
        elif 'rejected' in line_lower and 'share' in line_lower:
            self.shares_rejected += 1
    
    def get_pool_balance(self) -> Optional[float]:
        """
        Query pool API for mined balance.
        Different pools have different APIs - this is a generic stub.
        """
        try:
            # Example for MoneroOcean
            if 'moneroocean' in self.pool_host:
                url = f"https://api.moneroocean.stream/miner/{self.wallet}/stats"
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    # Balance is usually in atomic units (piconero), divide by 1e12 for XMR
                    return data.get('amtDue', 0) / 1e12
            
            # Example for SupportXMR
            elif 'supportxmr' in self.pool_host:
                url = f"https://supportxmr.com/api/miner/{self.wallet}/stats"
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    return data.get('amtDue', 0) / 1e12
            
            # Add more pool APIs as needed
            
        except Exception as e:
            print(f"Pool API error: {e}")
        
        return None
    
    def get_estimated_balance(self) -> float:
        """
        Estimate balance based on hashrate and time.
        This is approximate; real balance comes from pool API.
        """
        # Rough estimate: current network difficulty ~300 GH/s for 2 XMR/min
        # User hashrate ratio * block reward
        # This is very simplified; use pool API for accuracy
        return 0.0
    
    def get_hashrate(self) -> float:
        """Get current hashrate."""
        return self.local_hashrate
