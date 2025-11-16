/**
 * Marriage System - Allow users to marry each other
 */
import { FileSystem } from '../utils/fileSystem.js';

const MARRIAGE_FILE = 'marriage_data.json';

export class MarriageSystem {
    constructor() {
        this.marriages = {};
        this.ownerIds = [];
    }

    async init() {
        this.marriages = await FileSystem.loadJSON(MARRIAGE_FILE, {});
    }

    async save() {
        await FileSystem.saveJSON(MARRIAGE_FILE, this.marriages);
    }

    isMarried(userId) {
        return !!this.marriages[userId];
    }

    getAllPartners(userId) {
        if (!this.marriages[userId]) return [];

        const partner = this.marriages[userId].partner;
        if (Array.isArray(partner)) {
            return partner;
        } else if (partner) {
            return [partner];
        }
        return [];
    }

    getPartner(userId) {
        if (this.marriages[userId]) {
            return this.marriages[userId].partner;
        }
        return null;
    }

    getMarriageInfo(userId) {
        return this.marriages[userId] || null;
    }

    propose(proposerId, targetId, isOwner = false) {
        // Check if proposing to self
        if (proposerId === targetId) {
            return { success: false, message: "u cant marry urself lol 😅" };
        }

        // Owners can have unlimited wives
        if (!isOwner) {
            // Check if proposer is already married
            if (this.isMarried(proposerId)) {
                return { success: false, message: "ur already married! 💍" };
            }

            // Check if target is already married
            if (this.isMarried(targetId)) {
                return { success: false, message: "they're already married! 💔" };
            }
        }

        return { success: true, message: "proposal sent! ✨" };
    }

    async marry(user1Id, user2Id, ringId = null, isOwner = false) {
        const marriageDate = new Date().toISOString();

        let autoDivorced = false;
        let oldPartnerId = null;

        // If owner is marrying someone who's already married, divorce them first
        if (isOwner) {
            if (this.isMarried(user2Id)) {
                oldPartnerId = this.marriages[user2Id]?.partner;
                if (oldPartnerId) {
                    autoDivorced = true;
                    // Remove old partner's marriage
                    if (this.marriages[oldPartnerId]) {
                        delete this.marriages[oldPartnerId];
                    }
                }
            }
        }

        // Create marriage for both users
        this.marriages[user1Id] = {
            partner: user2Id,
            marriedAt: marriageDate,
            ringUsed: ringId
        };

        this.marriages[user2Id] = {
            partner: user1Id,
            marriedAt: marriageDate,
            ringUsed: ringId
        };

        await this.save();

        return {
            success: true,
            message: autoDivorced ? 
                `💍 married successfully! (auto-divorced previous partner)` : 
                `💍 married successfully!`,
            autoDivorced,
            oldPartnerId
        };
    }

    async divorce(userId) {
        if (!this.isMarried(userId)) {
            return { success: false, message: "ur not married! 💔" };
        }

        const partner = this.marriages[userId].partner;

        // Remove both marriages
        delete this.marriages[userId];
        if (partner && this.marriages[partner]) {
            delete this.marriages[partner];
        }

        await this.save();

        return {
            success: true,
            message: "💔 divorced successfully",
            exPartner: partner
        };
    }
}

export const marriageSystem = new MarriageSystem();
