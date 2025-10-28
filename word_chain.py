"""
Word Chain Game System for Doro Bot
Like Glitch Bucket bot but with unlimited valid connections
"""

import json
import os
from typing import Dict, Optional, Set
from datetime import datetime

WORD_CHAIN_FILE = "word_chain_data.json"

class WordChainSystem:
    def __init__(self):
        self.data = self.load_data()
        # Cache enabled channels for fast lookup
        self._enabled_channels = set(self.data.get("auto_channels", {}).keys())
        # Structure: {
        #   "auto_channels": {"channel_id": {"enabled": True, "last_word": "word", "players": {...}}},
        #   "game_stats": {"user_id": {"wins": 0, "total_words": 0}}
        # }
    
    def load_data(self) -> Dict:
        """Load word chain data from file"""
        if os.path.exists(WORD_CHAIN_FILE):
            try:
                with open(WORD_CHAIN_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {"auto_channels": {}, "game_stats": {}}
        return {"auto_channels": {}, "game_stats": {}}
    
    def save_data(self):
        """Save word chain data to file"""
        with open(WORD_CHAIN_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def is_auto_channel(self, channel_id: str) -> bool:
        """Check if channel has word chain enabled - uses cache for speed"""
        return channel_id in self._enabled_channels
    
    def enable_auto_channel(self, channel_id: str) -> bool:
        """Enable word chain for channel"""
        if "auto_channels" not in self.data:
            self.data["auto_channels"] = {}
        
        self.data["auto_channels"][channel_id] = {
            "enabled": True,
            "last_word": None,
            "last_user_id": None,
            "chain_count": 0,
            "used_words": [],
            "created_at": datetime.now().isoformat()
        }
        self._enabled_channels.add(channel_id)  # Update cache
        self.save_data()
        return True
    
    def disable_auto_channel(self, channel_id: str) -> bool:
        """Disable word chain for channel"""
        if channel_id in self.data.get("auto_channels", {}):
            del self.data["auto_channels"][channel_id]
            self._enabled_channels.discard(channel_id)  # Update cache
            self.save_data()
            return True
        return False
    
    def get_channel_data(self, channel_id: str) -> Optional[Dict]:
        """Get channel word chain data"""
        return self.data.get("auto_channels", {}).get(channel_id)
    
    def restart_chain(self, channel_id: str) -> bool:
        """Restart word chain in channel"""
        if channel_id in self.data.get("auto_channels", {}):
            self.data["auto_channels"][channel_id].update({
                "last_word": None,
                "last_user_id": None,
                "chain_count": 0,
                "used_words": []
            })
            self.save_data()  # Always save on restart
            return True
        return False
    
    def force_save(self):
        """Force save data (call on bot shutdown)"""
        self.save_data()
    
    def is_valid_connection(self, word1: Optional[str], word2: str) -> tuple[bool, str]:
        """
        Check if word2 is a valid continuation from word1
        Rules:
        - If no previous word, any word is valid
        - Word2 must start with last 1-2 letters of word1
        - OR word2 can be semantically related (very flexible)
        - Must be actual word (2+ letters)
        - Can be any language
        """
        if not word2 or len(word2) < 2:
            return False, "word must be at least 2 letters"
        
        # First word in chain
        if not word1:
            return True, "first word"
        
        word1_lower = word1.lower().strip()
        word2_lower = word2.lower().strip()
        
        # Rule 1: Starts with last 1-2 letters
        if word2_lower.startswith(word1_lower[-1:]):
            return True, "starts with last letter"
        if len(word1_lower) >= 2 and word2_lower.startswith(word1_lower[-2:]):
            return True, "starts with last 2 letters"
        
        # Rule 2: Very flexible semantic connections
        # For now, we'll allow ANY word and let players decide via reactions
        # This makes it like human-judged connections
        return True, "valid connection (pending verification)"
    
    def add_word(self, channel_id: str, user_id: str, word: str) -> tuple[bool, str]:
        """Add word to chain - optimized for speed"""
        channel_data = self.get_channel_data(channel_id)
        if not channel_data:
            return False, "channel not set up"
        
        # FAST check: same user
        if channel_data.get("last_user_id") == user_id:
            return False, "cannot post twice"
        
        # FAST check: word already used (use set for O(1) lookup)
        word_lower = word.lower()
        used_words = channel_data.get("used_words", [])
        if word_lower in [w.lower() for w in used_words[-50:]]:  # Only check last 50 words
            return False, "word already used"
        
        # Validate connection
        last_word = channel_data.get("last_word")
        is_valid, reason = self.is_valid_connection(last_word, word)
        
        if not is_valid:
            return False, reason
        
        # Update chain (in memory)
        channel_data["last_word"] = word
        channel_data["last_user_id"] = user_id
        channel_data["chain_count"] += 1
        channel_data["used_words"].append(word)
        
        # Keep only last 100 words to avoid memory issues
        if len(channel_data["used_words"]) > 100:
            channel_data["used_words"] = channel_data["used_words"][-100:]
        
        # Update player stats
        self.update_player_stats(user_id, 1)
        
        # BATCH SAVE: Only save every 5 words or on disable
        if channel_data["chain_count"] % 5 == 0:
            self.save_data()
        
        return True, reason
    
    def update_player_stats(self, user_id: str, words_added: int):
        """Update player statistics - NO auto-save for performance"""
        if "game_stats" not in self.data:
            self.data["game_stats"] = {}
        
        if user_id not in self.data["game_stats"]:
            self.data["game_stats"][user_id] = {
                "total_words": 0,
                "total_chains": 0
            }
        
        self.data["game_stats"][user_id]["total_words"] += words_added
        # Don't save here - save happens in add_word every 5 words
    
    def get_player_stats(self, user_id: str) -> Dict:
        """Get player statistics"""
        return self.data.get("game_stats", {}).get(user_id, {
            "total_words": 0,
            "total_chains": 0
        })
    
    def get_leaderboard(self, limit: int = 10) -> list:
        """Get top players by words contributed"""
        stats = self.data.get("game_stats", {})
        sorted_players = sorted(
            stats.items(),
            key=lambda x: x[1].get("total_words", 0),
            reverse=True
        )
        return sorted_players[:limit]

# Global instance
word_chain_system = WordChainSystem()
