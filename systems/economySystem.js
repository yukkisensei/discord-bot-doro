/**
 * Economy System - Money, levels, XP, daily rewards
 */
import { FileSystem } from '../utils/fileSystem.js';

const ECONOMY_FILE = 'economy_data.json';

export class EconomySystem {
    constructor() {
        this.data = {};
        this.ownerIds = [];
        this.infinityUsers = new Set();
    }

    async init() {
        this.data = await FileSystem.loadJSON(ECONOMY_FILE, {});
        // Rebuild infinity users cache
        for (const [userId, userData] of Object.entries(this.data)) {
            if (userData.infinity) {
                this.infinityUsers.add(userId);
            }
        }
    }

    async save() {
        await FileSystem.saveJSON(ECONOMY_FILE, this.data);
    }

    getUser(userId) {
        const isOwner = this.ownerIds.includes(userId);

        if (!this.data[userId]) {
            this.data[userId] = {
                balance: 1000,
                bank: 0,
                lastDaily: null,
                dailyStreak: 0,
                baseDaily: Math.floor(Math.random() * 601) + 1200, // 1200-1800
                xp: 0,
                level: 1,
                infinity: isOwner,
                totalEarned: 1000,
                totalSpent: 0,
                wins: 0,
                losses: 0,
                createdAt: new Date().toISOString()
            };
            this.save();
        }

        const user = this.data[userId];

        // Migrate old data
        let updated = false;
        if (!user.level) { user.level = 1; updated = true; }
        if (!user.xp) { user.xp = 0; updated = true; }
        if (!user.dailyStreak) { user.dailyStreak = 0; updated = true; }
        if (!user.baseDaily) { user.baseDaily = Math.floor(Math.random() * 601) + 1200; updated = true; }
        if (user.infinity === undefined) { user.infinity = isOwner; updated = true; }

        // Always ensure owners have infinity
        if (isOwner && !user.infinity) {
            user.infinity = true;
            updated = true;
        }

        // Track infinity users
        if (user.infinity) {
            this.infinityUsers.add(userId);
        }

        if (updated) this.save();

        return user;
    }

    isInfinity(userId) {
        const user = this.getUser(userId);
        return user.infinity || false;
    }

    async setInfinity(userId, enabled = true) {
        const user = this.getUser(userId);
        user.infinity = enabled;

        if (enabled) {
            this.infinityUsers.add(userId);
        } else {
            this.infinityUsers.delete(userId);
        }

        await this.save();
    }

    getAllInfinityUsers() {
        const infinityList = [];
        for (const [userId, data] of Object.entries(this.data)) {
            if (data.infinity) {
                infinityList.push(userId);
            }
        }
        return infinityList;
    }

    getBalance(userId) {
        if (this.isInfinity(userId)) {
            return Infinity;
        }
        return this.getUser(userId).balance;
    }

    getBank(userId) {
        if (this.isInfinity(userId)) {
            return Infinity;
        }
        return this.getUser(userId).bank;
    }

    async addMoney(userId, amount, toBank = false) {
        const user = this.getUser(userId);
        if (toBank) {
            user.bank += amount;
        } else {
            user.balance += amount;
        }
        user.totalEarned += amount;
        await this.save();
    }

    async removeMoney(userId, amount, fromBank = false) {
        // Infinity users never lose money
        if (this.isInfinity(userId)) {
            return true;
        }

        const user = this.getUser(userId);
        if (fromBank) {
            if (user.bank >= amount) {
                user.bank -= amount;
                user.totalSpent += amount;
                await this.save();
                return true;
            }
        } else {
            if (user.balance >= amount) {
                user.balance -= amount;
                user.totalSpent += amount;
                await this.save();
                return true;
            }
        }
        return false;
    }

    async transfer(fromUser, toUser, amount) {
        // Infinity users can give unlimited money
        if (this.isInfinity(fromUser)) {
            await this.addMoney(toUser, amount);
            return true;
        }

        if (await this.removeMoney(fromUser, amount)) {
            await this.addMoney(toUser, amount);
            return true;
        }
        return false;
    }

    canDaily(userId) {
        const user = this.getUser(userId);
        if (!user.lastDaily) return true;
        
        const lastDaily = new Date(user.lastDaily);
        const now = new Date();
        const hoursSince = (now - lastDaily) / (1000 * 60 * 60);
        
        return hoursSince >= 24;
    }

    async setLevel(userId, level) {
        const user = this.getUser(userId);
        user.level = level;
        user.xp = 0;
        await this.save();
    }

    getXPForLevel(level) {
        return Math.floor(100 * Math.pow(level, 1.5));
    }

    async addXP(userId, amount) {
        const user = this.getUser(userId);
        user.xp = (user.xp || 0) + amount;

        const currentLevel = user.level || 1;
        const xpNeeded = this.getXPForLevel(currentLevel);

        if (user.xp >= xpNeeded) {
            user.xp -= xpNeeded;
            user.level = currentLevel + 1;
            await this.save();
            return user.level;
        }

        await this.save();
        return null;
    }

    async claimDaily(userId) {
        const user = this.getUser(userId);

        // Check streak
        if (user.lastDaily) {
            const lastDaily = new Date(user.lastDaily);
            const hoursSince = (Date.now() - lastDaily.getTime()) / (1000 * 60 * 60);

            if (hoursSince < 48) {
                user.dailyStreak = (user.dailyStreak || 0) + 1;
            } else {
                user.dailyStreak = 1;
            }
        } else {
            user.dailyStreak = 1;
        }

        // Get base daily
        if (!user.baseDaily) {
            user.baseDaily = Math.floor(Math.random() * 601) + 1200; // 1200-1800 as per README
        }

        const baseAmount = user.baseDaily;
        const streak = user.dailyStreak;
        const level = user.level || 1;

        // Initialize level daily bonus
        if (!user.levelDailyBonus) {
            user.levelDailyBonus = 0.0;
        }

        // Calculate bonus
        const streakBonusPct = streak * 0.25; // 0.25% per day
        const levelBonusPct = user.levelDailyBonus; // 3% per level (permanent)
        
        // Check for equipped ring bonus
        let ringBonusPct = 0;
        try {
            const { shopSystem } = await import('./shopSystem.js');
            const equippedRing = shopSystem.getEquippedItem(userId, 'ring');
            if (equippedRing) {
                const ringBonuses = {
                    'ring_love': 5,
                    'ring_couple': 10,
                    'ring_mandarin': 15,
                    'ring_eternal': 25,
                    'ring_destiny': 50
                };
                ringBonusPct = ringBonuses[equippedRing] || 0;
            }
        } catch (error) {
            // ShopSystem might not be loaded yet
        }

        const totalBonusPct = streakBonusPct + levelBonusPct + ringBonusPct;
        const totalMultiplier = 1 + (totalBonusPct / 100);
        const amount = Math.floor(baseAmount * totalMultiplier);

        // Add money and XP
        user.balance += amount;
        user.totalEarned += amount;
        user.lastDaily = new Date().toISOString();

        const xpGained = 10;
        user.xp = (user.xp || 0) + xpGained;

        // Check level up
        let newLevel = null;
        const currentLevel = user.level || 1;
        const xpNeeded = this.getXPForLevel(currentLevel);

        if (user.xp >= xpNeeded) {
            user.xp -= xpNeeded;
            user.level = currentLevel + 1;
            newLevel = user.level;
        }

        await this.save();

        return {
            amount,
            streak,
            level: user.level,
            xpGained,
            newLevel,
            streakBonus: streakBonusPct,
            levelBonus: levelBonusPct,
            ringBonus: ringBonusPct
        };
    }

    async recordWin(userId) {
        const user = this.getUser(userId);
        user.wins = (user.wins || 0) + 1;
        await this.save();
    }

    async recordLoss(userId) {
        const user = this.getUser(userId);
        user.losses = (user.losses || 0) + 1;
        await this.save();
    }

    getStats(userId) {
        return this.getUser(userId);
    }

    async deposit(userId, amount) {
        if (this.isInfinity(userId)) return true;

        const user = this.getUser(userId);
        if (user.balance >= amount) {
            user.balance -= amount;
            user.bank += amount;
            await this.save();
            return true;
        }
        return false;
    }

    async withdraw(userId, amount) {
        if (this.isInfinity(userId)) return true;

        const user = this.getUser(userId);
        if (user.bank >= amount) {
            user.bank -= amount;
            user.balance += amount;
            await this.save();
            return true;
        }
        return false;
    }

    getLeaderboard(type = 'balance', limit = 10) {
        const users = Object.entries(this.data).map(([userId, userData]) => {
            let value;
            switch (type) {
                case 'balance':
                    value = (userData.balance || 0) + (userData.bank || 0);
                    break;
                case 'level':
                    value = userData.level || 1;
                    break;
                case 'streak':
                    value = userData.dailyStreak || 0;
                    break;
                case 'wins':
                    value = userData.wins || 0;
                    break;
                default:
                    value = (userData.balance || 0) + (userData.bank || 0);
            }
            return { userId, value, userData };
        });

        // Filter out infinity users from leaderboard for fairness
        const filtered = users.filter(u => !u.userData.infinity || type !== 'balance');

        return filtered
            .sort((a, b) => b.value - a.value)
            .slice(0, limit);
    }
}

export const economy = new EconomySystem();
