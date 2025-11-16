/**
 * AFK System - Manage user AFK status
 */
import { FileSystem } from '../util/fileSystem.js';

const AFK_FILE = 'afk_data.json';

export class AFKSystem {
    constructor() {
        this.data = {};
    }

    async init() {
        this.data = await FileSystem.loadJSON(AFK_FILE, {});
    }

    async save() {
        await FileSystem.saveJSON(AFK_FILE, this.data);
    }

    async setAFK(userId, reason = null) {
        this.data[userId] = {
            reason: reason || 'AFK',
            timestamp: new Date().toISOString()
        };
        await this.save();
    }

    async removeAFK(userId) {
        if (this.data[userId]) {
            const data = this.data[userId];
            delete this.data[userId];
            await this.save();
            return data;
        }
        return null;
    }

    isAFK(userId) {
        return !!this.data[userId];
    }

    getAFK(userId) {
        return this.data[userId] || null;
    }

    getAFKDuration(userId) {
        if (!this.data[userId]) return null;

        const afkTime = new Date(this.data[userId].timestamp);
        const duration = Date.now() - afkTime.getTime();

        const days = Math.floor(duration / (1000 * 60 * 60 * 24));
        const hours = Math.floor((duration % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60));

        const parts = [];
        if (days > 0) parts.push(`${days}d`);
        if (hours > 0) parts.push(`${hours}h`);
        if (minutes > 0 || parts.length === 0) parts.push(`${minutes}m`);

        return parts.join(' ');
    }
}

export const afkSystem = new AFKSystem();
