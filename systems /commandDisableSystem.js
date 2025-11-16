/**
 * Command Disable System - Disable commands per channel
 */
import { FileSystem } from '../utils/fileSystem.js';

const DISABLE_FILE = 'disabled_commands.json';

export class CommandDisableSystem {
    constructor() {
        this.data = {};
    }

    async init() {
        this.data = await FileSystem.loadJSON(DISABLE_FILE, {});
    }

    async save() {
        await FileSystem.saveJSON(DISABLE_FILE, this.data);
    }

    async disableCommand(channelId, command) {
        if (!this.data[channelId]) {
            this.data[channelId] = [];
        }
        
        if (!this.data[channelId].includes(command)) {
            this.data[channelId].push(command);
            await this.save();
            return true;
        }
        return false;
    }

    async enableCommand(channelId, command) {
        if (this.data[channelId]?.includes(command)) {
            this.data[channelId] = this.data[channelId].filter(c => c !== command);
            if (this.data[channelId].length === 0) {
                delete this.data[channelId];
            }
            await this.save();
            return true;
        }
        return false;
    }

    isDisabled(channelId, command) {
        return this.data[channelId]?.includes(command) || false;
    }

    getDisabledCommands(channelId) {
        return this.data[channelId] || [];
    }

    async clearChannel(channelId) {
        if (this.data[channelId]) {
            delete this.data[channelId];
            await this.save();
            return true;
        }
        return false;
    }

    getAllCommands() {
        return new Set([
            // Music commands
            'play', 'skip', 'pause', 'resume', 'stop', 'queue', 'np',
            'loop', 'shuffle', 'volume', 'history', 'move', 'remove', 'stay', 'leave',
            
            // Economy commands
            'balance', 'daily', 'deposit', 'withdraw', 'give', 'stats', 'leaderboard',
            
            // Casino commands
            'cf', 'slots', 'bj', 'gamble',
            
            // AI commands
            'reset', 'remember', 'recall', 'forget',
            
            // Fun commands
            '8ball', 'roll', 'coinflip', 'rps',
            
            // Utility commands
            'help', 'ping', 'avatar', 'serverinfo', 'userinfo', 'say',
            
            // AFK
            'afk'
        ]);
    }
}

export const disableSystem = new CommandDisableSystem();
