"""
Mute System - manage muted users with time tracking
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List

class MuteSystem:
    def __init__(self, data_file: str = "mute_data.json"):
        self.data_file = data_file
        self.data = self.load_data()
    
    def load_data(self) -> dict:
        """Load mute data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def save_data(self) -> None:
        """Save mute data to file"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def mute_user(self, guild_id: str, user_id: str, duration_minutes: int, reason: str = None) -> bool:
        """Mute a user for specified duration"""
        if guild_id not in self.data:
            self.data[guild_id] = {}
        
        mute_until = (datetime.now() + timedelta(minutes=duration_minutes)).isoformat()
        
        self.data[guild_id][user_id] = {
            "muted_at": datetime.now().isoformat(),
            "mute_until": mute_until,
            "duration_minutes": duration_minutes,
            "reason": reason or "no reason provided"
        }
        
        self.save_data()
        return True
    
    def unmute_user(self, guild_id: str, user_id: str) -> bool:
        """Unmute a user"""
        if guild_id in self.data and user_id in self.data[guild_id]:
            del self.data[guild_id][user_id]
            self.save_data()
            return True
        return False
    
    def is_muted(self, guild_id: str, user_id: str) -> bool:
        """Check if user is currently muted"""
        if guild_id not in self.data or user_id not in self.data[guild_id]:
            return False
        
        mute_data = self.data[guild_id][user_id]
        mute_until = datetime.fromisoformat(mute_data["mute_until"])
        
        # Auto-unmute if time expired
        if datetime.now() >= mute_until:
            self.unmute_user(guild_id, user_id)
            return False
        
        return True
    
    def get_mute_info(self, guild_id: str, user_id: str) -> Optional[Dict]:
        """Get mute info for a user"""
        if not self.is_muted(guild_id, user_id):
            return None
        
        mute_data = self.data[guild_id][user_id]
        mute_until = datetime.fromisoformat(mute_data["mute_until"])
        time_left = mute_until - datetime.now()
        
        # Format time left
        total_seconds = int(time_left.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            time_str = f"{hours}h {minutes}m"
        elif minutes > 0:
            time_str = f"{minutes}m {seconds}s"
        else:
            time_str = f"{seconds}s"
        
        return {
            "reason": mute_data["reason"],
            "duration_minutes": mute_data["duration_minutes"],
            "time_left": time_str,
            "mute_until": mute_until.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_all_muted(self, guild_id: str) -> List[Dict]:
        """Get all muted users in a guild"""
        if guild_id not in self.data:
            return []
        
        muted_users = []
        for user_id in list(self.data[guild_id].keys()):
            if self.is_muted(guild_id, user_id):
                info = self.get_mute_info(guild_id, user_id)
                if info:
                    muted_users.append({
                        "user_id": user_id,
                        **info
                    })
        
        return muted_users
    
    def cleanup_expired(self) -> int:
        """Remove all expired mutes, return count removed"""
        removed = 0
        for guild_id in list(self.data.keys()):
            for user_id in list(self.data[guild_id].keys()):
                if not self.is_muted(guild_id, user_id):
                    removed += 1
        return removed

# Global instance
mute_system = MuteSystem()
