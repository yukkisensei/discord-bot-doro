/**
 * Multi-language System - English & Vietnamese
 */
import { FileSystem } from '../utils/fileSystem.js';

const LANG_FILE = 'language_data.json';

// Language cache for instant access (< 1ms)
const langCache = new Map();

export const translations = {
    en: {
        // Economy
        balance_title: "💰 {user}'s Balance",
        balance_wallet: "💵 Wallet",
        balance_bank: "🏦 Bank",
        balance_total: "💎 Total",
        balance_level: "⭐ Level",
        balance_xp: "✨ XP",
        balance_streak: "🔥 Daily Streak",
        balance_infinity: "♾️ INFINITY MODE ACTIVE",
        
        daily_claimed: "🎁 Daily Reward Claimed!",
        daily_received: "u received **{amount}** coins!",
        daily_cooldown: "⏰ u already claimed ur daily! come back in {time}",
        daily_streak: "🔥 Streak",
        daily_levelup: "🎉 LEVEL UP! You're now level {level}!",
        
        deposit_success: "✅ deposited **{amount}** coins to ur bank!",
        withdraw_success: "✅ withdrew **{amount}** coins from ur bank!",
        give_success: "✅ gave **{amount}** coins to {user}",
        
        // Casino
        cf_win: "🪙 Coinflip - YOU WON!",
        cf_loss: "🪙 Coinflip - YOU LOST!",
        slots_win: "🎰 Slots - YOU WON!",
        slots_loss: "🎰 Slots - YOU LOST!",
        
        // Shop
        shop_title: "🏪 Doro's Shop",
        shop_buy: "Use `buy <item_id>` to purchase!",
        buy_success: "✅ purchased {item} for {price} coins!",
        inventory_title: "🎒 {user}'s Inventory",
        inventory_empty: "*Empty inventory*",
        
        // Marriage
        marry_proposal: "💍 Marriage Proposal!",
        marry_success: "💑 Married!",
        marry_rejected: "💔 {user} rejected {proposer}'s proposal!",
        divorce_success: "💔 divorced successfully",
        
        // Utility
        help_title: "🌸 Doro Bot - Commands",
        ping_pong: "🏓 Pong! Latency: {latency}ms | API: {api}ms",
        afk_set: "✅ ur now AFK: {reason}",
        
        // Errors
        error_amount: "❌ invalid amount!",
        error_balance: "❌ u only have {balance} coins!",
        error_permission: "⛔ u need {permission} permission!",
        error_generic: "❌ an error occurred!",
        
        // Word units
        days: "days",
        hours: "h",
        minutes: "m",
        seconds: "s",
        coins: "coins"
    },
    
    vi: {
        // Economy
        balance_title: "💰 Số Dư Của {user}",
        balance_wallet: "💵 Ví",
        balance_bank: "🏦 Ngân Hàng",
        balance_total: "💎 Tổng",
        balance_level: "⭐ Cấp Độ",
        balance_xp: "✨ Kinh Nghiệm",
        balance_streak: "🔥 Chuỗi Ngày",
        balance_infinity: "♾️ CHẾ ĐỘ VÔ HẠN",
        
        daily_claimed: "🎁 Đã Nhận Phần Thưởng Hàng Ngày!",
        daily_received: "bạn nhận được **{amount}** xu!",
        daily_cooldown: "⏰ bạn đã nhận rồi! quay lại sau {time}",
        daily_streak: "🔥 Chuỗi",
        daily_levelup: "🎉 THĂNG CẤP! Bạn đã lên cấp {level}!",
        
        deposit_success: "✅ đã gửi **{amount}** xu vào ngân hàng!",
        withdraw_success: "✅ đã rút **{amount}** xu từ ngân hàng!",
        give_success: "✅ đã tặng **{amount}** xu cho {user}",
        
        // Casino
        cf_win: "🪙 Tung Xu - THẮNG!",
        cf_loss: "🪙 Tung Xu - THUA!",
        slots_win: "🎰 Quay Số - THẮNG!",
        slots_loss: "🎰 Quay Số - THUA!",
        
        // Shop
        shop_title: "🏪 Cửa Hàng Doro",
        shop_buy: "Dùng `buy <item_id>` để mua!",
        buy_success: "✅ đã mua {item} với giá {price} xu!",
        inventory_title: "🎒 Túi Đồ Của {user}",
        inventory_empty: "*Túi đồ trống*",
        
        // Marriage
        marry_proposal: "💍 Lời Cầu Hôn!",
        marry_success: "💑 Đã Kết Hôn!",
        marry_rejected: "💔 {user} đã từ chối lời cầu hôn của {proposer}!",
        divorce_success: "💔 đã ly hôn thành công",
        
        // Utility
        help_title: "🌸 Doro Bot - Lệnh",
        ping_pong: "🏓 Pong! Độ trễ: {latency}ms | API: {api}ms",
        afk_set: "✅ bạn đã AFK: {reason}",
        
        // Errors
        error_amount: "❌ số tiền không hợp lệ!",
        error_balance: "❌ bạn chỉ có {balance} xu!",
        error_permission: "⛔ bạn cần quyền {permission}!",
        error_generic: "❌ đã có lỗi xảy ra!",
        
        // Word units
        days: "ngày",
        hours: "giờ",
        minutes: "phút",
        seconds: "giây",
        coins: "xu"
    }
};

export class LanguageSystem {
    constructor() {
        this.data = {};
        this.defaultLang = 'en';
    }

    async init() {
        this.data = await FileSystem.loadJSON(LANG_FILE, {});
        // Rebuild cache for O(1) lookups
        for (const [guildId, lang] of Object.entries(this.data)) {
            langCache.set(guildId, lang);
        }
    }

    async save() {
        await FileSystem.saveJSON(LANG_FILE, this.data);
    }

    /**
     * Get language for guild (cached for < 1ms access)
     */
    getLang(guildId) {
        if (!guildId) return this.defaultLang;
        
        // Check cache first (O(1))
        if (langCache.has(guildId)) {
            return langCache.get(guildId);
        }
        
        return this.defaultLang;
    }

    /**
     * Set language for guild
     */
    async setLang(guildId, lang) {
        if (!['en', 'vi'].includes(lang)) {
            return false;
        }
        
        this.data[guildId] = lang;
        langCache.set(guildId, lang); // Update cache immediately
        await this.save();
        return true;
    }

    /**
     * Get translated text with variable replacement
     * @param {string} guildId - Guild ID
     * @param {string} key - Translation key
     * @param {object} vars - Variables to replace {var}
     */
    t(guildId, key, vars = {}) {
        const lang = this.getLang(guildId);
        let text = translations[lang]?.[key] || translations.en[key] || key;
        
        // Replace variables {var} with values
        for (const [k, v] of Object.entries(vars)) {
            text = text.replace(`{${k}}`, v);
        }
        
        return text;
    }

    /**
     * Get all translations for a language
     */
    getTranslations(lang) {
        return translations[lang] || translations.en;
    }
}

export const languageSystem = new LanguageSystem();
