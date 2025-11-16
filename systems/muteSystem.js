/**
 * Mute System - Manage muted users with time tracking
 */
import { FileSystem } from '../utils/fileSystem.js';

const MUTE_FILE = 'mute_data.json';

export class MuteSystem {
    constructor() {
        this.data = {};
    }

    async init() {
        this.data = await FileSystem.loadJSON(MUTE_FILE, {});
    }

    async save() {
        await FileSystem.saveJSON(MUTE_FILE, this.data);
    }

    async muteUser(guildId, userId, durationMinutes, reason = null) {
        if (!this.data[guildId]) {
            this.data[guildId] = {};
        }

        const muteUntil = new Date(Date.now() + durationMinutes * 60 * 1000);

        this.data[guildId][userId] = {
            mutedAt: new Date().toISOString(),
            muteUntil: muteUntil.toISOString(),
            durationMinutes: durationMinutes,
            reason: reason || 'no reason provided'
        };

        await this.save();
        return true;
    }

    async unmuteUser(guildId, userId) {
        if (this.data[guildId]?.[userId]) {
            delete this.data[guildId][userId];
            await this.save();
            return true;
        }
        return false;
    }

    isMuted(guildId, userId) {
        if (!this.data[guildId]?.[userId]) return false;

        const muteData = this.data[guildId][userId];
        const muteUntil = new Date(muteData.muteUntil);

        // Auto-unmute if time expired
        if (Date.now() >= muteUntil.getTime()) {
            this.unmuteUser(guildId, userId);
            return false;
        }

        return true;
    }

    getMuteInfo(guildId, userId) {
        if (!this.isMuted(guildId, userId)) return null;

        const muteData = this.data[guildId][userId];
        const muteUntil = new Date(muteData.muteUntil);
        const timeLeft = muteUntil.getTime() - Date.now();

        const totalSeconds = Math.floor(timeLeft / 1000);
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;

        let timeStr;
        if (hours > 0) {
            timeStr = `${hours}h ${minutes}m`;
        } else if (minutes > 0) {
            timeStr = `${minutes}m ${seconds}s`;
        } else {
            timeStr = `${seconds}s`;
        }

        return {
            reason: muteData.reason,
            durationMinutes: muteData.durationMinutes,
            timeLeft: timeStr,
            muteUntil: muteUntil.toLocaleString()
        };
    }

    getAllMuted(guildId) {
        if (!this.data[guildId]) return [];

        const mutedUsers = [];
        for (const userId of Object.keys(this.data[guildId])) {
            if (this.isMuted(guildId, userId)) {
                const info = this.getMuteInfo(guildId, userId);
                if (info) {
                    mutedUsers.push({
                        userId,
                        ...info
                    });
                }
            }
        }
        return mutedUsers;
    }

    cleanupExpired() {
        let removed = 0;
        for (const guildId of Object.keys(this.data)) {
            for (const userId of Object.keys(this.data[guildId])) {
                if (!this.isMuted(guildId, userId)) {
                    removed++;
                }
            }
        }
        return removed;
    }
}

export const muteSystem = new MuteSystem();
