"""
Shop System - OWO-style shop with items
Includes rings, boxes, and special items
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class ShopSystem:
    """Manage shop items and user inventory"""
    
    def __init__(self):
        self.data_file = "shop_data.json"
        self.inventory_file = "user_inventory.json"
        
        # Shop items
        self.shop_items = {
            # ===== RINGS =====
            "ring_love": {
                "name": "💍 Love Ring",
                "description": "ring symbolizing true love",
                "price": 50000,
                "category": "ring",
                "emoji": "💍",
                "tradeable": True,
                "usable": True,
                "effect": "+5% coins when using +daily"
            },
            "ring_couple": {
                "name": "💕 Couple Ring",
                "description": "ring for loving couples",
                "price": 120000,
                "category": "ring",
                "emoji": "💕",
                "tradeable": True,
                "usable": True,
                "effect": "+10% coins when using +daily"
            },
            "ring_mandarin": {
                "name": "🦆 Mandarin Duck Ring",
                "description": "ring of inseparable mandarin ducks",
                "price": 250000,
                "category": "ring",
                "emoji": "🦆",
                "tradeable": True,
                "usable": True,
                "effect": "+15% coins when using +daily"
            },
            "ring_eternal": {
                "name": "💎 Eternal Ring",
                "description": "diamond ring symbolizing eternal love",
                "price": 500000,
                "category": "ring",
                "emoji": "💎",
                "tradeable": True,
                "usable": True,
                "effect": "+25% coins when using +daily"
            },
            "ring_destiny": {
                "name": "✨ Destiny Ring",
                "description": "ring of those bound by destiny",
                "price": 1000000,
                "category": "ring",
                "emoji": "✨",
                "tradeable": True,
                "usable": True,
                "effect": "+50% coins when using +daily"
            },
            
            # ===== LOOTBOXES =====
            "box_common": {
                "name": "📦 Common Box",
                "description": "basic lootbox containing random items",
                "price": 8000,
                "category": "lootbox",
                "emoji": "📦",
                "tradeable": True,
                "usable": True,
                "effect": "open to receive random items"
            },
            "box_rare": {
                "name": "🎁 Rare Box",
                "description": "rare lootbox containing valuable items",
                "price": 25000,
                "category": "lootbox",
                "emoji": "🎁",
                "tradeable": True,
                "usable": True,
                "effect": "open to receive rare items"
            },
            "box_epic": {
                "name": "🎀 Epic Box",
                "description": "epic lootbox with big rewards",
                "price": 60000,
                "category": "lootbox",
                "emoji": "🎀",
                "tradeable": True,
                "usable": True,
                "effect": "open to receive epic items"
            },
            "box_legendary": {
                "name": "🎊 Legendary Box",
                "description": "legendary lootbox with priceless treasures",
                "price": 100000,
                "category": "lootbox",
                "emoji": "🎊",
                "tradeable": True,
                "usable": True,
                "effect": "open to receive legendary items"
            },
            
            # ===== SPECIAL ITEMS =====
            "cookie": {
                "name": "🍪 Lucky Cookie",
                "description": "cookie bringing luck in casino",
                "price": 5000,
                "category": "consumable",
                "emoji": "🍪",
                "tradeable": True,
                "usable": True,
                "effect": "+10% casino win rate (1 time)"
            },
            "clover": {
                "name": "🍀 Four Leaf Clover",
                "description": "rare four leaf clover bringing fortune",
                "price": 12000,
                "category": "consumable",
                "emoji": "🍀",
                "tradeable": True,
                "usable": True,
                "effect": "+20% casino win rate (1 time)"
            },
            "horseshoe": {
                "name": "🧲 Lucky Horseshoe",
                "description": "ancient horseshoe bringing wealth",
                "price": 25000,
                "category": "consumable",
                "emoji": "🧲",
                "tradeable": True,
                "usable": True,
                "effect": "+30% casino win rate (1 time)"
            },
            "gem": {
                "name": "💠 Precious Gem",
                "description": "rare precious gem of high value",
                "price": 40000,
                "category": "collectible",
                "emoji": "💠",
                "tradeable": True,
                "usable": False,
                "effect": "collectible item"
            },
            "trophy": {
                "name": "🏆 Gold Trophy",
                "description": "gold trophy for champions",
                "price": 80000,
                "category": "collectible",
                "emoji": "🏆",
                "tradeable": True,
                "usable": False,
                "effect": "collectible item"
            },
            "crown": {
                "name": "👑 Royal Crown",
                "description": "crown of royalty",
                "price": 150000,
                "category": "collectible",
                "emoji": "👑",
                "tradeable": True,
                "usable": False,
                "effect": "collectible item"
            },
            
            # ===== PETS =====
            "pet_cat": {
                "name": "🐱 Pet Cat",
                "description": "cute and loyal cat",
                "price": 30000,
                "category": "pet",
                "emoji": "🐱",
                "tradeable": True,
                "usable": True,
                "effect": "+5% XP daily"
            },
            "pet_dog": {
                "name": "🐶 Pet Dog",
                "description": "smart and brave dog",
                "price": 30000,
                "category": "pet",
                "emoji": "🐶",
                "tradeable": True,
                "usable": True,
                "effect": "+5% XP daily"
            },
            "pet_dragon": {
                "name": "🐉 Divine Dragon",
                "description": "legendary divine dragon bringing power",
                "price": 120000,
                "category": "pet",
                "emoji": "🐉",
                "tradeable": True,
                "usable": True,
                "effect": "+15% XP daily"
            },
            "pet_phoenix": {
                "name": "🦅 Phoenix",
                "description": "immortal phoenix with rebirth power",
                "price": 250000,
                "category": "pet",
                "emoji": "🦅",
                "tradeable": True,
                "usable": True,
                "effect": "+25% XP daily"
            },
        }
        
        self.load_data()
    
    def load_data(self):
        """Load user inventory data"""
        if os.path.exists(self.inventory_file):
            try:
                with open(self.inventory_file, 'r', encoding='utf-8') as f:
                    self.inventory_data = json.load(f)
            except:
                self.inventory_data = {}
        else:
            self.inventory_data = {}
    
    def save_data(self):
        """Save user inventory data"""
        with open(self.inventory_file, 'w', encoding='utf-8') as f:
            json.dump(self.inventory_data, f, ensure_ascii=False, indent=2)
    
    def get_user_inventory(self, user_id: str) -> Dict:
        """Get user's inventory"""
        if user_id not in self.inventory_data:
            self.inventory_data[user_id] = {
                "items": {},
                "equipped": {},
                "active_effects": []
            }
            self.save_data()
        return self.inventory_data[user_id]
    
    def add_item(self, user_id: str, item_id: str, quantity: int = 1) -> bool:
        """Add item to user's inventory"""
        inventory = self.get_user_inventory(user_id)
        
        if item_id not in inventory["items"]:
            inventory["items"][item_id] = 0
        
        inventory["items"][item_id] += quantity
        self.save_data()
        return True
    
    def remove_item(self, user_id: str, item_id: str, quantity: int = 1) -> bool:
        """Remove item from user's inventory"""
        inventory = self.get_user_inventory(user_id)
        
        if item_id not in inventory["items"] or inventory["items"][item_id] < quantity:
            return False
        
        inventory["items"][item_id] -= quantity
        if inventory["items"][item_id] <= 0:
            del inventory["items"][item_id]
        
        self.save_data()
        return True
    
    def has_item(self, user_id: str, item_id: str, quantity: int = 1) -> bool:
        """Check if user has item"""
        inventory = self.get_user_inventory(user_id)
        return inventory["items"].get(item_id, 0) >= quantity
    
    def get_item_count(self, user_id: str, item_id: str) -> int:
        """Get item count"""
        inventory = self.get_user_inventory(user_id)
        return inventory["items"].get(item_id, 0)
    
    def get_shop_items(self, category: str = None) -> Dict:
        """Get shop items, optionally filtered by category"""
        if category:
            return {k: v for k, v in self.shop_items.items() if v["category"] == category}
        return self.shop_items
    
    def get_item_info(self, item_id: str) -> Optional[Dict]:
        """Get item information"""
        return self.shop_items.get(item_id)
    
    def equip_item(self, user_id: str, item_id: str) -> Tuple[bool, str]:
        """Equip an item (rings, pets)"""
        inventory = self.get_user_inventory(user_id)
        
        if not self.has_item(user_id, item_id):
            return False, "u dont have this item!"
        
        item = self.get_item_info(item_id)
        if not item:
            return False, "item doesnt exist!"
        
        category = item["category"]
        
        # Check if category can be equipped
        if category not in ["ring", "pet"]:
            return False, "this item cant be equipped!"
        
        # Unequip old item if exists
        if category in inventory["equipped"]:
            old_item = inventory["equipped"][category]
            if old_item != item_id:
                # Add old item back to inventory
                self.add_item(user_id, old_item, 1)
        
        # Equip new item
        inventory["equipped"][category] = item_id
        self.remove_item(user_id, item_id, 1)
        self.save_data()
        
        return True, f"equipped {item['emoji']} {item['name']}!"
    
    def unequip_item(self, user_id: str, category: str) -> Tuple[bool, str]:
        """Unequip an item"""
        inventory = self.get_user_inventory(user_id)
        
        if category not in inventory["equipped"]:
            return False, f"u dont have any {category} equipped!"
        
        item_id = inventory["equipped"][category]
        item = self.get_item_info(item_id)
        
        # Add item back to inventory
        self.add_item(user_id, item_id, 1)
        del inventory["equipped"][category]
        self.save_data()
        
        return True, f"unequipped {item['emoji']} {item['name']}!"
    
    def get_equipped_item(self, user_id: str, category: str) -> Optional[str]:
        """Get equipped item ID for category"""
        inventory = self.get_user_inventory(user_id)
        return inventory["equipped"].get(category)
    
    def use_item(self, user_id: str, item_id: str) -> Tuple[bool, str, Optional[Dict]]:
        """Use a consumable item"""
        if not self.has_item(user_id, item_id):
            return False, "u dont have this item!", None
        
        item = self.get_item_info(item_id)
        if not item or not item.get("usable"):
            return False, "this item cant be used!", None
        
        # Remove item
        self.remove_item(user_id, item_id, 1)
        
        # Return effect data
        effect_data = {
            "type": item["category"],
            "effect": item["effect"],
            "item_name": item["name"]
        }
        
        return True, f"used {item['emoji']} {item['name']}!", effect_data
    
    def open_lootbox(self, user_id: str, box_id: str) -> Tuple[bool, str, List[Dict]]:
        """Open a lootbox and get rewards"""
        if not self.has_item(user_id, box_id):
            return False, "u dont have this lootbox!", []
        
        item = self.get_item_info(box_id)
        if not item or item["category"] != "lootbox":
            return False, "this is not a lootbox!", []
        
        # Remove lootbox
        self.remove_item(user_id, box_id, 1)
        
        # Generate rewards based on box rarity
        import random
        rewards = []
        
        if box_id == "box_common":
            # Common box: 1-3 items, mostly common
            num_items = random.randint(1, 3)
            possible_items = ["cookie", "pet_cat", "pet_dog", "gem"]
            coins = random.randint(500, 2000)
        elif box_id == "box_rare":
            # Rare box: 2-4 items, mix of common and rare
            num_items = random.randint(2, 4)
            possible_items = ["cookie", "clover", "ring_love", "ring_couple", "gem", "trophy"]
            coins = random.randint(2000, 5000)
        elif box_id == "box_epic":
            # Epic box: 3-5 items, mostly rare and epic
            num_items = random.randint(3, 5)
            possible_items = ["clover", "horseshoe", "ring_couple", "ring_mandarin", "ring_eternal", "trophy", "pet_dragon"]
            coins = random.randint(5000, 15000)
        else:  # legendary
            # Legendary box: 4-6 items, epic and legendary
            num_items = random.randint(4, 6)
            possible_items = ["horseshoe", "ring_eternal", "ring_destiny", "trophy", "crown", "pet_dragon", "pet_phoenix"]
            coins = random.randint(15000, 50000)
        
        # Add coins reward
        rewards.append({
            "type": "coins",
            "amount": coins,
            "emoji": "💰",
            "name": f"{coins:,} coins"
        })
        
        # Add random items
        for _ in range(num_items):
            item_id = random.choice(possible_items)
            self.add_item(user_id, item_id, 1)
            item_info = self.get_item_info(item_id)
            rewards.append({
                "type": "item",
                "item_id": item_id,
                "emoji": item_info["emoji"],
                "name": item_info["name"]
            })
        
        return True, f"opened {item['emoji']} {item['name']}!", rewards
    
    def get_inventory_value(self, user_id: str) -> int:
        """Calculate total inventory value"""
        inventory = self.get_user_inventory(user_id)
        total = 0
        
        for item_id, quantity in inventory["items"].items():
            item = self.get_item_info(item_id)
            if item:
                total += item["price"] * quantity
        
        for item_id in inventory["equipped"].values():
            item = self.get_item_info(item_id)
            if item:
                total += item["price"]
        
        return total

# Global instance
shop_system = ShopSystem()
