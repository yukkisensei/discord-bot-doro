/**
 * Shop System - OWO-style shop with items
 */
import { FileSystem } from '../util/fileSystem.js';
import { economy } from './economySystem.js';

const INVENTORY_FILE = 'user_inventory.json';

export class ShopSystem {
    constructor() {
        this.inventoryData = {};
        
        // Shop items catalog
        this.shopItems = {
            // ===== RINGS =====
            ring_love: {
                name: "💍 Love Ring",
                description: "ring symbolizing true love",
                price: 50000,
                category: "ring",
                emoji: "💍",
                tradeable: true,
                usable: true,
                effect: "+5% coins when using daily"
            },
            ring_couple: {
                name: "💕 Couple Ring",
                description: "ring for loving couples",
                price: 120000,
                category: "ring",
                emoji: "💕",
                tradeable: true,
                usable: true,
                effect: "+10% coins when using daily"
            },
            ring_mandarin: {
                name: "🦆 Mandarin Duck Ring",
                description: "ring of inseparable mandarin ducks",
                price: 250000,
                category: "ring",
                emoji: "🦆",
                tradeable: true,
                usable: true,
                effect: "+15% coins when using daily"
            },
            ring_eternal: {
                name: "💎 Eternal Ring",
                description: "diamond ring symbolizing eternal love",
                price: 500000,
                category: "ring",
                emoji: "💎",
                tradeable: true,
                usable: true,
                effect: "+25% coins when using daily"
            },
            ring_destiny: {
                name: "✨ Destiny Ring",
                description: "ring of those bound by destiny",
                price: 1000000,
                category: "ring",
                emoji: "✨",
                tradeable: true,
                usable: true,
                effect: "+50% coins when using daily"
            },
            
            // ===== LOOTBOXES =====
            box_common: {
                name: "📦 Common Box",
                description: "basic lootbox containing random items",
                price: 8000,
                category: "lootbox",
                emoji: "📦",
                tradeable: true,
                usable: true,
                effect: "open to receive random items"
            },
            box_rare: {
                name: "🎁 Rare Box",
                description: "rare lootbox containing valuable items",
                price: 25000,
                category: "lootbox",
                emoji: "🎁",
                tradeable: true,
                usable: true,
                effect: "open to receive rare items"
            },
            box_epic: {
                name: "🎀 Epic Box",
                description: "epic lootbox with big rewards",
                price: 60000,
                category: "lootbox",
                emoji: "🎀",
                tradeable: true,
                usable: true,
                effect: "open to receive epic items"
            },
            box_legendary: {
                name: "🎊 Legendary Box",
                description: "legendary lootbox with priceless treasures",
                price: 100000,
                category: "lootbox",
                emoji: "🎊",
                tradeable: true,
                usable: true,
                effect: "open to receive legendary items"
            },
            
            // ===== SPECIAL ITEMS =====
            cookie: {
                name: "🍪 Lucky Cookie",
                description: "cookie bringing luck in casino",
                price: 5000,
                category: "consumable",
                emoji: "🍪",
                tradeable: true,
                usable: true,
                effect: "+10% casino win rate (1 time)"
            },
            clover: {
                name: "🍀 Four Leaf Clover",
                description: "rare four leaf clover bringing fortune",
                price: 12000,
                category: "consumable",
                emoji: "🍀",
                tradeable: true,
                usable: true,
                effect: "+20% casino win rate (1 time)"
            },
            horseshoe: {
                name: "🧲 Lucky Horseshoe",
                description: "ancient horseshoe bringing wealth",
                price: 25000,
                category: "consumable",
                emoji: "🧲",
                tradeable: true,
                usable: true,
                effect: "+30% casino win rate (1 time)"
            },
            gem: {
                name: "💠 Precious Gem",
                description: "rare precious gem of high value",
                price: 40000,
                category: "collectible",
                emoji: "💠",
                tradeable: true,
                usable: false,
                effect: "collectible item"
            },
            trophy: {
                name: "🏆 Gold Trophy",
                description: "gold trophy for champions",
                price: 80000,
                category: "collectible",
                emoji: "🏆",
                tradeable: true,
                usable: false,
                effect: "collectible item"
            },
            crown: {
                name: "👑 Royal Crown",
                description: "crown of royalty",
                price: 150000,
                category: "collectible",
                emoji: "👑",
                tradeable: true,
                usable: false,
                effect: "collectible item"
            },
            
            // ===== PETS =====
            pet_cat: {
                name: "🐱 Pet Cat",
                description: "cute and loyal cat",
                price: 30000,
                category: "pet",
                emoji: "🐱",
                tradeable: true,
                usable: true,
                effect: "+5% XP daily"
            },
            pet_dog: {
                name: "🐶 Pet Dog",
                description: "smart and brave dog",
                price: 30000,
                category: "pet",
                emoji: "🐶",
                tradeable: true,
                usable: true,
                effect: "+5% XP daily"
            },
            pet_dragon: {
                name: "🐉 Divine Dragon",
                description: "legendary divine dragon bringing power",
                price: 120000,
                category: "pet",
                emoji: "🐉",
                tradeable: true,
                usable: true,
                effect: "+15% XP daily"
            },
            pet_phoenix: {
                name: "🦅 Phoenix",
                description: "immortal phoenix with rebirth power",
                price: 250000,
                category: "pet",
                emoji: "🦅",
                tradeable: true,
                usable: true,
                effect: "+25% XP daily"
            },

            // ===== UPGRADES =====
            bag_slot_20: {
                name: "🧳 Bag Slot +20",
                description: "permanent +20 inventory slots",
                price: 45000,
                category: "upgrade",
                emoji: "🧳",
                tradeable: false,
                usable: true,
                effect: { type: 'itemCapacity', amount: 20 }
            },
            pet_slot_1: {
                name: "🐾 Pet Slot +1",
                description: "permanent +1 pet slot",
                price: 60000,
                category: "upgrade",
                emoji: "🐾",
                tradeable: false,
                usable: true,
                effect: { type: 'petCapacity', amount: 1 }
            }
        };
    }

    async init() {
        this.inventoryData = await FileSystem.loadJSON(INVENTORY_FILE, {});
    }

    async save() {
        await FileSystem.saveJSON(INVENTORY_FILE, this.inventoryData);
    }

    getUserInventory(userId) {
        if (!this.inventoryData[userId]) {
            this.inventoryData[userId] = {
                items: {},
                equipped: {},
                activeEffects: [],
                itemCapacity: 100,
                petCapacity: 3,
                unlimitedSlots: false
            };
            this.save();
        }
        const inventory = this.inventoryData[userId];
        if (typeof inventory.itemCapacity !== 'number' || Number.isNaN(inventory.itemCapacity)) {
            inventory.itemCapacity = 100;
        }
        if (typeof inventory.petCapacity !== 'number' || Number.isNaN(inventory.petCapacity)) {
            inventory.petCapacity = 3;
        }
        if (typeof inventory.unlimitedSlots !== 'boolean') {
            inventory.unlimitedSlots = false;
        }
        if (economy.isInfinity(userId) && !inventory.unlimitedSlots) {
            inventory.unlimitedSlots = true;
        }
        return inventory;
    }

    getUsedSlots(userId, type = 'item') {
        const inventory = this.getUserInventory(userId);
        let total = 0;
        for (const [itemId, quantity] of Object.entries(inventory.items)) {
            const info = this.getItemInfo(itemId);
            const category = info?.category || 'misc';
            const isPetItem = category === 'pet';
            if (type === 'pet') {
                if (isPetItem) total += quantity;
            } else {
                if (!isPetItem) total += quantity;
            }
        }
        return total;
    }

    hasCapacity(userId, itemId, quantity = 1) {
        const inventory = this.getUserInventory(userId);
        if (inventory.unlimitedSlots || economy.isInfinity(userId)) {
            return true;
        }
        const item = this.getItemInfo(itemId);
        if (!item) return true;
        if (item.category === 'upgrade') return true;
        const isPet = item.category === 'pet';
        const capacity = isPet ? inventory.petCapacity : inventory.itemCapacity;
        const used = this.getUsedSlots(userId, isPet ? 'pet' : 'item');
        return used + quantity <= capacity;
    }

    async addItem(userId, itemId, quantity = 1) {
        const inventory = this.getUserInventory(userId);
        if (!this.hasCapacity(userId, itemId, quantity)) {
            return false;
        }
        
        if (!inventory.items[itemId]) {
            inventory.items[itemId] = 0;
        }
        
        inventory.items[itemId] += quantity;
        await this.save();
        return true;
    }

    async removeItem(userId, itemId, quantity = 1) {
        const inventory = this.getUserInventory(userId);
        
        if (!inventory.items[itemId] || inventory.items[itemId] < quantity) {
            return false;
        }
        
        inventory.items[itemId] -= quantity;
        if (inventory.items[itemId] <= 0) {
            delete inventory.items[itemId];
        }
        
        await this.save();
        return true;
    }

    hasItem(userId, itemId, quantity = 1) {
        const inventory = this.getUserInventory(userId);
        return (inventory.items[itemId] || 0) >= quantity;
    }

    getItemCount(userId, itemId) {
        const inventory = this.getUserInventory(userId);
        return inventory.items[itemId] || 0;
    }

    getShopItems(category = null) {
        if (category) {
            return Object.fromEntries(
                Object.entries(this.shopItems).filter(([k, v]) => v.category === category)
            );
        }
        return this.shopItems;
    }

    getItemInfo(itemId) {
        return this.shopItems[itemId] || null;
    }

    async equipItem(userId, itemId) {
        const inventory = this.getUserInventory(userId);
        
        if (!this.hasItem(userId, itemId)) {
            return { success: false, message: "u dont have this item!" };
        }
        
        const item = this.getItemInfo(itemId);
        if (!item) {
            return { success: false, message: "item doesnt exist!" };
        }
        
        const category = item.category;
        
        if (!['ring', 'pet'].includes(category)) {
            return { success: false, message: "this item cant be equipped!" };
        }
        
        // Unequip old item
        if (inventory.equipped[category]) {
            const oldItem = inventory.equipped[category];
            if (oldItem !== itemId) {
                if (!this.hasCapacity(userId, oldItem, 1)) {
                    return { success: false, message: "no free slots to unequip current item!" };
                }
                await this.addItem(userId, oldItem, 1);
            }
        }
        
        // Equip new item
        inventory.equipped[category] = itemId;
        await this.removeItem(userId, itemId, 1);
        await this.save();
        
        return { success: true, message: `equipped ${item.emoji} ${item.name}!` };
    }

    async unequipItem(userId, category) {
        const inventory = this.getUserInventory(userId);
        
        if (!inventory.equipped[category]) {
            return { success: false, message: `u dont have any ${category} equipped!` };
        }
        
        const itemId = inventory.equipped[category];
        const item = this.getItemInfo(itemId);

        if (!this.hasCapacity(userId, itemId, 1)) {
            return { success: false, message: "ur bag is full!" };
        }
        
        await this.addItem(userId, itemId, 1);
        delete inventory.equipped[category];
        await this.save();
        
        return { success: true, message: `unequipped ${item.emoji} ${item.name}!` };
    }

    getEquippedItem(userId, category) {
        const inventory = this.getUserInventory(userId);
        return inventory.equipped[category] || null;
    }

    async useItem(userId, itemId) {
        if (!this.hasItem(userId, itemId)) {
            return { success: false, message: "u dont have this item!", effect: null };
        }
        
        const item = this.getItemInfo(itemId);
        if (!item || !item.usable) {
            return { success: false, message: "this item cant be used!", effect: null };
        }
        
        await this.removeItem(userId, itemId, 1);
        
        const rawEffect = item.effect;
        const effectType = typeof rawEffect === 'object' && rawEffect?.type ? rawEffect.type : item.category;
        const effectData = {
            type: effectType,
            effect: rawEffect,
            itemName: item.name
        };
        
        return { success: true, message: `used ${item.emoji} ${item.name}!`, effect: effectData };
    }

    async openLootbox(userId, boxId) {
        if (!this.hasItem(userId, boxId)) {
            return { success: false, message: "u dont have this lootbox!", rewards: [] };
        }
        
        const item = this.getItemInfo(boxId);
        if (!item || item.category !== 'lootbox') {
            return { success: false, message: "this is not a lootbox!", rewards: [] };
        }
        
        await this.removeItem(userId, boxId, 1);
        
        // Generate rewards
        const rewards = [];
        let numItems, possibleItems, coins;
        
        switch (boxId) {
            case 'box_common':
                numItems = Math.floor(Math.random() * 3) + 1;
                possibleItems = ['cookie', 'pet_cat', 'pet_dog', 'gem'];
                coins = Math.floor(Math.random() * 1501) + 500;
                break;
            case 'box_rare':
                numItems = Math.floor(Math.random() * 3) + 2;
                possibleItems = ['cookie', 'clover', 'ring_love', 'ring_couple', 'gem', 'trophy'];
                coins = Math.floor(Math.random() * 3001) + 2000;
                break;
            case 'box_epic':
                numItems = Math.floor(Math.random() * 3) + 3;
                possibleItems = ['clover', 'horseshoe', 'ring_couple', 'ring_mandarin', 'ring_eternal', 'trophy', 'pet_dragon'];
                coins = Math.floor(Math.random() * 10001) + 5000;
                break;
            default: // legendary
                numItems = Math.floor(Math.random() * 3) + 4;
                possibleItems = ['horseshoe', 'ring_eternal', 'ring_destiny', 'trophy', 'crown', 'pet_dragon', 'pet_phoenix'];
                coins = Math.floor(Math.random() * 35001) + 15000;
                break;
        }
        
        // Add coins
        rewards.push({
            type: 'coins',
            amount: coins,
            emoji: '💰',
            name: `${coins.toLocaleString()} coins`
        });
        
        // Add items
        for (let i = 0; i < numItems; i++) {
            const itemId = possibleItems[Math.floor(Math.random() * possibleItems.length)];
            const itemInfo = this.getItemInfo(itemId);
            if (!itemInfo) continue;
            const added = await this.addItem(userId, itemId, 1);
            if (!added) {
                rewards.push({
                    type: 'item',
                    itemId,
                    emoji: '⚠️',
                    name: `${itemInfo.name} (inventory full)`
                });
            } else {
                rewards.push({
                    type: 'item',
                    itemId,
                    emoji: itemInfo.emoji,
                    name: itemInfo.name
                });
            }
        }
        
        return { success: true, message: `opened ${item.emoji} ${item.name}!`, rewards };
    }

    getInventoryValue(userId) {
        const inventory = this.getUserInventory(userId);
        let total = 0;
        
        for (const [itemId, quantity] of Object.entries(inventory.items)) {
            const item = this.getItemInfo(itemId);
            if (item) {
                total += item.price * quantity;
            }
        }
        
        for (const itemId of Object.values(inventory.equipped)) {
            const item = this.getItemInfo(itemId);
            if (item) {
                total += item.price;
            }
        }
        
        return total;
    }

    async increaseCapacity(userId, type, amount) {
        if (!amount) return this.getCapacityStatus(userId);
        const inventory = this.getUserInventory(userId);
        if (inventory.unlimitedSlots || economy.isInfinity(userId)) {
            return this.getCapacityStatus(userId);
        }
        if (type === 'itemCapacity') {
            inventory.itemCapacity += amount;
        } else if (type === 'petCapacity') {
            inventory.petCapacity += amount;
        }
        await this.save();
        return this.getCapacityStatus(userId);
    }

    async setUnlimitedSlots(userId, enabled) {
        const inventory = this.getUserInventory(userId);
        inventory.unlimitedSlots = enabled;
        await this.save();
    }

    getCapacityStatus(userId) {
        const inventory = this.getUserInventory(userId);
        const itemCap = (inventory.unlimitedSlots || economy.isInfinity(userId)) ? '∞' : inventory.itemCapacity;
        const petCap = (inventory.unlimitedSlots || economy.isInfinity(userId)) ? '∞' : inventory.petCapacity;
        return {
            item: {
                used: this.getUsedSlots(userId, 'item'),
                capacity: itemCap
            },
            pet: {
                used: this.getUsedSlots(userId, 'pet'),
                capacity: petCap
            }
        };
    }
}

export const shopSystem = new ShopSystem();
