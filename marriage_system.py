"""
Marriage System for Discord bot
allows users to marry each other and receive benefits
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, List

class MarriageSystem:
    """Manage marriages between users"""
    
    def __init__(self):
        self.data_file = "marriage_data.json"
        self.owner_ids = []  # Will be set from lenh.py
        self.load_data()
    
    def load_data(self):
        """Load marriage data"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.marriages = json.load(f)
            except:
                self.marriages = {}
        else:
            self.marriages = {}
    
    def save_data(self):
        """Save marriage data"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.marriages, f, ensure_ascii=False, indent=2)
    
    def is_married(self, user_id: str) -> bool:
        """Check if user is married (owners can have multiple wives)"""
        return user_id in self.marriages
    
    def get_all_partners(self, user_id: str) -> List[str]:
        """Get all partners for a user (for owners with multiple wives)"""
        if user_id not in self.marriages:
            return []
        
        partner = self.marriages[user_id].get("partner")
        if isinstance(partner, list):
            return partner
        elif partner:
            return [partner]
        return []
    
    def get_partner(self, user_id: str) -> Optional[str]:
        """Get user's partner ID"""
        if user_id in self.marriages:
            return self.marriages[user_id]["partner"]
        return None
    
    def get_marriage_info(self, user_id: str) -> Optional[Dict]:
        """Get marriage information"""
        if user_id in self.marriages:
            return self.marriages[user_id]
        return None
    
    def propose(self, proposer_id: str, target_id: str, is_owner: bool = False) -> Tuple[bool, str]:
        """Propose marriage to someone"""
        # Check if proposing to self
        if proposer_id == target_id:
            return False, "u cant marry urself lol 😅"
        
        # Owners can have unlimited wives and can marry anyone
        if not is_owner:
            # Check if proposer is already married
            if self.is_married(proposer_id):
                return False, "ur already married! 💍"
            
            # Check if target is already married
            if self.is_married(target_id):
                return False, "they're already married! 💔"
        
        # Owner can propose to anyone, even if they're married
        return True, "proposal sent! ✨"
    
    def marry(self, user1_id: str, user2_id: str, ring_id: str = None, is_owner: bool = False) -> Tuple[bool, str]:
        """Marry two users (owners can have multiple wives)"""
        marriage_date = datetime.now().isoformat()
        
        # Track if we auto-divorced someone
        auto_divorced = False
        old_partner_id = None
        
        # If owner is marrying someone who's already married, divorce them first
        # Check is_owner flag directly (already validated in lenh.py)
        if is_owner:
            if self.is_married(user2_id):
                # Auto divorce target from their old partner
                old_partner_id = self.marriages[user2_id].get("partner")
                if old_partner_id:
                    auto_divorced = True
                    # Remove old partner's marriage
                    if old_partner_id in self.marriages:
                        del self.marriages[old_partner_id]
                    # Remove target's old marriage
                    del self.marriages[user2_id]
        else:
            # Normal users can't marry someone who's already married
            if self.is_married(user2_id):
                return False, f"they're already married! 💔"
        
        # Owner can have multiple wives
        if is_owner:
            # Check if owner already has marriages
            if user1_id in self.marriages:
                # Add to existing partners list
                if isinstance(self.marriages[user1_id]["partner"], list):
                    self.marriages[user1_id]["partner"].append(user2_id)
                else:
                    # Convert single partner to list
                    old_partner = self.marriages[user1_id]["partner"]
                    self.marriages[user1_id]["partner"] = [old_partner, user2_id]
                self.marriages[user1_id]["married_at"] = marriage_date
            else:
                # First marriage
                self.marriages[user1_id] = {
                    "partner": [user2_id],
                    "married_at": marriage_date,
                    "ring": ring_id,
                    "love_points": 0
                }
            
            # Target gets single partner
            self.marriages[user2_id] = {
                "partner": user1_id,
                "married_at": marriage_date,
                "ring": ring_id,
                "love_points": 0
            }
        else:
            # Normal marriage - validate both users are not married
            if self.is_married(user1_id):
                return False, "ur already married!"
            
            self.marriages[user1_id] = {
                "partner": user2_id,
                "married_at": marriage_date,
                "ring": ring_id,
                "love_points": 0
            }
            
            self.marriages[user2_id] = {
                "partner": user1_id,
                "married_at": marriage_date,
                "ring": ring_id,
                "love_points": 0
            }
        
        self.save_data()
        
        # Add note if auto-divorced
        success_msg = "🎉 congrats! u two r now married! 💍✨"
        if auto_divorced and old_partner_id:
            success_msg += f"\n\n⚠️ (auto-divorced previous partner: {old_partner_id})"
        
        return True, success_msg
    
    def can_divorce(self, user_id: str) -> Tuple[bool, str]:
        """Check if user can divorce (15 hour cooldown)"""
        if not self.is_married(user_id):
            return False, "ur not married!"
        
        married_at = datetime.fromisoformat(self.marriages[user_id]["married_at"])
        time_since_marriage = datetime.now() - married_at
        
        # 15 hour cooldown
        if time_since_marriage < timedelta(hours=15):
            hours_left = 15 - (time_since_marriage.total_seconds() / 3600)
            return False, f"⏰ wait **{hours_left:.1f} hours** before divorcing! (15hr cooldown)"
        
        return True, "OK"
    
    def divorce(self, user_id: str, target_partner: str = None) -> Tuple[bool, str]:
        """Divorce (break marriage) - with 15 hour cooldown"""
        if not self.is_married(user_id):
            return False, "ur not married!"
        
        # Check cooldown
        can_divorce, message = self.can_divorce(user_id)
        if not can_divorce:
            return False, message
        
        partner = self.marriages[user_id].get("partner")
        
        # Handle multiple partners (owner)
        if isinstance(partner, list):
            if target_partner and target_partner in partner:
                partner.remove(target_partner)
                if len(partner) == 1:
                    self.marriages[user_id]["partner"] = partner[0]
                elif len(partner) == 0:
                    del self.marriages[user_id]
                
                # Remove target's marriage
                if target_partner in self.marriages:
                    del self.marriages[target_partner]
            else:
                return False, "specify which partner to divorce!"
        else:
            # Single partner
            partner_id = partner
            del self.marriages[user_id]
            if partner_id and partner_id in self.marriages:
                del self.marriages[partner_id]
        
        self.save_data()
        return True, "💔 u two r now divorced..."
    
    def add_love_points(self, user_id: str, points: int) -> bool:
        """Add love points to marriage"""
        if not self.is_married(user_id):
            return False
        
        self.marriages[user_id]["love_points"] += points
        
        # Also update partner's points
        partner_id = self.get_partner(user_id)
        if partner_id and partner_id in self.marriages:
            self.marriages[partner_id]["love_points"] += points
        
        self.save_data()
        return True
    
    def get_marriage_duration(self, user_id: str) -> Optional[str]:
        """Get how long user has been married"""
        if not self.is_married(user_id):
            return None
        
        married_at = datetime.fromisoformat(self.marriages[user_id]["married_at"])
        duration = datetime.now() - married_at
        
        days = duration.days
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        
        if days == 0:
            if hours == 0:
                if minutes == 0:
                    return "few seconds"
                return f"{minutes} min"
            return f"{hours} hrs"
        elif days < 30:
            return f"{days} days"
        elif days < 365:
            months = days // 30
            return f"{months} months"
        else:
            years = days // 365
            return f"{years} years"
    
    def get_all_marriages(self) -> Dict:
        """Get all marriages"""
        return self.marriages

# Global instance
marriage_system = MarriageSystem()
