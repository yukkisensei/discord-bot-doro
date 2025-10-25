"""
Custom prefix system - allows each server to set their own prefix
"""

import json
import os
from typing import Optional

class PrefixSystem:
    def __init__(self, data_file: str = "prefix_data.json"):
        self.data_file = data_file
        self.data = self.load_data()
    
    def load_data(self) -> dict:
        """Load prefix data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def save_data(self) -> None:
        """Save prefix data to file"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def get_prefix(self, guild_id: str) -> str:
        """Get prefix for a guild, return default if not set"""
        return self.data.get(guild_id, "!")
    
    def set_prefix(self, guild_id: str, prefix: str) -> bool:
        """Set custom prefix for a guild"""
        if not prefix or len(prefix) > 10:  # Limit prefix length
            return False
        
        self.data[guild_id] = prefix
        self.save_data()
        return True
    
    def reset_prefix(self, guild_id: str) -> None:
        """Reset guild prefix to default"""
        if guild_id in self.data:
            del self.data[guild_id]
            self.save_data()

# Global instance
prefix_system = PrefixSystem()
