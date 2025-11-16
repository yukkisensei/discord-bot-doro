/**
 * Word Chain Game System
 */
import { FileSystem } from '../util/fileSystem.js';

const WORD_CHAIN_FILE = 'word_chain_data.json';

export class WordChainSystem {
    constructor() {
        this.data = {
            autoChannels: {},
            gameStats: {}
        };
        this._enabledChannels = new Set();
    }

    async init() {
        this.data = await FileSystem.loadJSON(WORD_CHAIN_FILE, {
            autoChannels: {},
            gameStats: {}
        });
        // Rebuild cache
        this._enabledChannels = new Set(Object.keys(this.data.autoChannels || {}));
    }

    async save() {
        await FileSystem.saveJSON(WORD_CHAIN_FILE, this.data);
    }

    isAutoChannel(channelId) {
        return this._enabledChannels.has(channelId);
    }

    async enableAutoChannel(channelId, language = 'en') {
        if (!this.data.autoChannels) {
            this.data.autoChannels = {};
        }

        this.data.autoChannels[channelId] = {
            enabled: true,
            language: language,
            lastWord: null,
            lastUserId: null,
            chainCount: 0,
            usedWords: [],
            createdAt: new Date().toISOString()
        };
        this._enabledChannels.add(channelId);
        await this.save();
        return true;
    }

    async disableAutoChannel(channelId) {
        if (this.data.autoChannels?.[channelId]) {
            delete this.data.autoChannels[channelId];
            this._enabledChannels.delete(channelId);
            await this.save();
            return true;
        }
        return false;
    }

    getChannelData(channelId) {
        return this.data.autoChannels?.[channelId] || null;
    }

    async restartChain(channelId) {
        if (this.data.autoChannels?.[channelId]) {
            this.data.autoChannels[channelId].lastWord = null;
            this.data.autoChannels[channelId].lastUserId = null;
            this.data.autoChannels[channelId].chainCount = 0;
            this.data.autoChannels[channelId].usedWords = [];
            await this.save();
            return true;
        }
        return false;
    }

    async forceSave() {
        await this.save();
    }

    isValidConnection(word1, word2, language = 'en') {
        if (!word2 || word2.length < 2) {
            return { 
                valid: false, 
                reason: language === 'vi' ? 'từ phải ít nhất 2 chữ cái' : 'word must be at least 2 letters' 
            };
        }

        if (!word1) {
            return { 
                valid: true, 
                reason: language === 'vi' ? 'từ đầu tiên' : 'first word' 
            };
        }

        const w1 = word1.toLowerCase().trim();
        const w2 = word2.toLowerCase().trim();
        
        if (language === 'vi') {
            const lastChar = w1[w1.length - 1];
            const last2Chars = w1.length >= 2 ? w1.slice(-2) : lastChar;
            
            if (w2.startsWith(lastChar) || w2.startsWith(last2Chars)) {
                return { valid: true, reason: 'nối chữ đúng' };
            }
            
            return { 
                valid: false, 
                reason: `từ phải bắt đầu bằng "${lastChar}" hoặc "${last2Chars}"` 
            };
        } else {
            const lastChar = w1[w1.length - 1];
            const last2Chars = w1.length >= 2 ? w1.slice(-2) : lastChar;
            
            if (w2.startsWith(lastChar) || w2.startsWith(last2Chars)) {
                return { valid: true, reason: 'letter connection' };
            }
            
            return { 
                valid: false, 
                reason: `word must start with "${lastChar}" or "${last2Chars}"` 
            };
        }
    }

    async processWord(channelId, userId, word) {
        const channelData = this.getChannelData(channelId);
        if (!channelData) {
            return { success: false, reason: 'channel not enabled' };
        }

        const lang = channelData.language || 'en';

        if (channelData.lastUserId === userId) {
            return { 
                success: false, 
                reason: lang === 'vi' ? 'không thể nối từ của chính mình' : 'cant chain your own word' 
            };
        }

        if (channelData.usedWords.includes(word.toLowerCase())) {
            return { 
                success: false, 
                reason: lang === 'vi' ? 'từ đã được dùng rồi' : 'word already used' 
            };
        }

        const validation = this.isValidConnection(channelData.lastWord, word, lang);
        if (!validation.valid) {
            return { success: false, reason: validation.reason };
        }

        channelData.lastWord = word;
        channelData.lastUserId = userId;
        channelData.chainCount += 1;
        channelData.usedWords.push(word.toLowerCase());

        if (!this.data.gameStats) {
            this.data.gameStats = {};
        }
        if (!this.data.gameStats[userId]) {
            this.data.gameStats[userId] = {
                totalWords: 0,
                wins: 0
            };
        }
        this.data.gameStats[userId].totalWords += 1;

        await this.save();
        return { success: true, chainCount: channelData.chainCount };
    }

    getUserStats(userId) {
        return this.data.gameStats?.[userId] || { totalWords: 0, wins: 0 };
    }

    getLeaderboard(limit = 10) {
        const stats = Object.entries(this.data.gameStats || {})
            .map(([userId, data]) => ({ userId, ...data }))
            .sort((a, b) => b.totalWords - a.totalWords)
            .slice(0, limit);
        return stats;
    }
}

export const wordChainSystem = new WordChainSystem();
