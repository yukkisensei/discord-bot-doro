/**
 * Custom Prefix System - Allows each server to set their own prefix
 */
import { FileSystem } from '../utils/fileSystem.js';

const DATA_FILE = 'prefix_data.json';

export class PrefixSystem {
    constructor() {
        this.data = {};
        this.defaultPrefix = '!';
    }

    async init() {
        this.data = await FileSystem.loadJSON(DATA_FILE, {});
    }

    async save() {
        await FileSystem.saveJSON(DATA_FILE, this.data);
    }

    getPrefix(guildId) {
        return this.data[guildId] || this.defaultPrefix;
    }

    async setPrefix(guildId, prefix) {
        if (!prefix || prefix.length > 10) {
            return false;
        }
        this.data[guildId] = prefix;
        await this.save();
        return true;
    }

    async resetPrefix(guildId) {
        if (this.data[guildId]) {
            delete this.data[guildId];
            await this.save();
        }
    }
}

export const prefixSystem = new PrefixSystem();
