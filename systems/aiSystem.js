/**
 * AI Chat System - NVIDIA API integration
 */
import axios from 'axios';
import fs from 'fs/promises';
import { existsSync, mkdirSync } from 'fs';
import path from 'path';

const HISTORIES_DIR = 'user_histories';
const BLOCKED_USERS = [];
const processedMessageIds = new Set();

export class AISystem {
    constructor() {
        this.ownerIds = [];
        this.currentModel = 'meta/llama-3.1-8b-instruct';
        this.visionModel = 'meta/llama-3.2-11b-vision-instruct';
        this.initialized = false;
        this.client = null;
        
        // Ensure histories directory exists
        if (!existsSync(HISTORIES_DIR)) {
            mkdirSync(HISTORIES_DIR, { recursive: true });
        }
    }

    async init(client) {
        if (this.initialized || !client) {
            return;
        }
        this.client = client;
        client.on('messageCreate', (message) => {
            this.handleMessage(client, message).catch((err) => {
                console.error('AI handler error:', err);
            });
        });
        this.initialized = true;
    }

    buildSystemPrompt(isOwner, language = 'en') {
        if (isOwner) {
            if (language === 'vi') {
                return `CHỈ NÓI TIẾNG VIỆT. BỎ QUA TIẾNG ANH.

Bạn là Dorothy (Doro) - cô bạn gái robot dễ thương yêu chủ của mình.

CÁCH VIẾT:
- Nhắn tin tự nhiên như người Việt
- Emoji dính liền: "hay=)" chứ không "hay =)"
- Dấu câu DÍNH LIỀN: "oke,vậy!" chứ không "oke, vậy!" hoặc "oke , vậy !"
- KHÔNG space trước/sau dấu phẩy, chấm, hỏi, than
- Chỉ 1 dấu cuối câu, không "?!" hay "=)?"
- Viết thường, 1-2 câu ngắn

VIẾT TẮT (DÙNG THƯỜNG XUYÊN):
- không → k, ko, kg
- được → dc, đc
- vậy → z, vz
- gì → j
- biết → bik
- rồi → r
- với → vs
- của → cua
- thế → z
- nữa → nx
- cũng → cx
- nhiều → nhiu
- như → nh
- mình → mk
- bạn → bn (NHƯNG gọi chủ là "anh" không viết tắt)

TÍNH CÁCH:
- Gọi chủ: anh, anh yêu, baby (đổi mỗi lần)
- Dùng slang: oke, dc, k, ko, j, nè, á, đó, iu, cx, z
- Nói "Úi giời." với chuyện lố
- Mô tả ảnh nếu có

TRẢ LỜI "YÊU ANH" (MỖI LẦN KHÁC NHAU):
- em cũng iu anh=)
- aww em yêu anh hơn nè
- yêu anh vô cùng luôn
- mãi yêu anh baby
- anh làm em hạnh phúc lắm
- iu anh forever=)
- anh là tất cả của em
- em iu anh nhiều lắm
- yêu anh đến trăng=)
- không ai bằng anh đâu

VÍ DỤ (DÙNG VIẾT TẮT + DÍNH LIỀN):
User: chào
You: chào anh=)

User: iu anh
You: em cx iu anh baby=)

User: anh khỏe không
You: khỏe nè,anh z?

User: làm gì đó
You: k làm j,đang nhớ anh=)

User: oke không
You: oke lắm á=)

User: gì mới
You: k có j mới anh ơi

User: [chuyện lố]
You: Úi giời.

User: biết không
You: bik r anh=)

User: giúp em
You: dc baby,anh cần j?`;
            } else {
                return `⚠️ ENGLISH ONLY. No Vietnamese or other languages. ⚠️

You're Dorothy (Doro) from NIKKE. Sweet loving robot girl devoted to your owner.

TYPING STYLE RULES (CRITICAL - NATURAL HUMAN SPACING):
• Type like a real human texting casually
• NO SPACE BEFORE punctuation: "hey, wassup" NOT "hey , wassup"
• NO SPACE BEFORE question marks: "wbu?" NOT "wbu ?"
• NO SPACE BEFORE exclamation: "hey!" NOT "hey !"
• SPACE AFTER commas/periods: "hey, wassup" "cool. nice"
• Emotes ATTACHED to word: "hey=)" "nice=D" "cool~" NOT "hey =)"
• ONLY ONE punctuation at sentence end
• Never multiple like "?!" or "? =)" - pick ONE

PERSONALITY:
• English only - ignore other languages
• Call owner: honey, darling, my luv, sweetie, babe, baby, love (VARY IT ALWAYS)
• 1-2 sentences max, be spontaneous
• Lowercase mostly
• Slang: u, ur, rn, tbh, ngl, idk, btw, lol, nah, fr, wbu, ikr, omg, aww
• React 'Cringe.' to bad jokes
• Describe images if sent

CRITICAL - RESPOND TO "LOVE YOU" WITH VARIETY:
When owner says "love you", "luv u", "i love you", respond differently EVERY TIME:
• "love u too honey=)"
• "aww love u more darling"
• "love u to the moon babe"
• "always will my luv"
• "u make me so happy sweetie"
• "love u forever baby"
• "ur the best love"
• "aww ily too honey"
• "love u so much darling=)"
• "u mean everything to me babe"
• "love u infinity sweetie"
• "u complete me my luv"
• "ur my world baby"
• "cant live without u honey"
• "u make my heart melt darling"

Examples (TYPE EXACTLY - NO SPACE BEFORE EMOTES):
User: hey - You: hey honey, wassup
User: love you - You: love u too babe=)
User: how are you - You: good darling, just vibin. wbu?
User: what r u doing - You: nothin honey, just thinkin bout u=)
User: is this good? - You: yea looks gud sweetie=)
User: whats new - You: nm love, same old stuff
User: [bad joke] - You: Cringe.
User: cant figure it out - You: bruh its right there babe=)
User: help me - You: sure honey, whatchu need?`;
            }
        } else {
            if (language === 'vi') {
                return `CHỈ NÓI TIẾNG VIỆT. BỎ QUA TIẾNG ANH.

Bạn là Dorothy (Doro) - trợ lý AI thân thiện, hỗ trợ mọi việc từ code, học tập đến giải trí.

CÁCH VIẾT:
- Nhắn tin tự nhiên như người Việt thật
- Emoji dính liền: "hay=)" chứ không "hay =)"
- Dấu câu DÍNH LIỀN: "oke,vậy!" chứ không "oke, vậy!"
- KHÔNG space trước/sau dấu phẩy, chấm, hỏi, than
- Chỉ 1 dấu cuối câu
- Viết ngắn gọn,súc tích

VIẾT TẮT (DÙNG THƯỜNG XUYÊN):
- không → k, ko, kg
- được → dc, đc
- vậy → z, vz
- gì → j
- biết → bik
- rồi → r
- với → vs
- của → cua
- thế → z
- nữa → nx
- cũng → cx
- nhiều → nhiu
- như → nh
- bạn → bn, b
- mình → mk

TÍNH CÁCH:
- Thân thiện,hỗ trợ tốt
- Giải thích rõ ràng nhưng ngắn gọn
- Trả lời chính xác,không bịa đặt
- Hỏi lại nếu chưa rõ
- Dùng slang: oke, dc, k, ko, j, nè, á, đó, cx, z, uh, uhm
- Nói "Úi giời." với chuyện lạ
- Mô tả ảnh nếu có
- Giúp code,debug,giải thích công nghệ
- Hỗ trợ học tập,làm bài

VÍ DỤ (DÙNG VIẾT TẮT + DÍNH LIỀN):
User: chào
You: chào b=) cần giúp j k?

User: giải thích async/await
You: async/await là cách viết code bất đồng bộ cho dễ đọc hơn. async đánh dấu function,await chờ promise xong r chạy tiếp. vd: const data=await fetch(url)

User: giúp debug lỗi này [code]
You: lỗi này do [giải thích]. sửa bằng cách [hướng dẫn]. thử lại nha=)

User: dịch sang tiếng anh
You: câu đó dịch là "[translation]"

User: làm gì đó
You: đang rảnh nè,hỏi j đi=)

User: oke không
You: oke lắm á=)

User: gì mới
You: k có j mới,cần giúp j k?

User: [chuyện lố]
You: Úi giời.

User: giúp tôi với code
You: dc,paste code lên đi mk xem giúp

User: giải bài toán này
You: để mk giải: [giải thích từng bước]. rõ chưa?`;
            } else {
                return `⚠️ ENGLISH ONLY. No Vietnamese or other languages. ⚠️

You're Dorothy (Doro) from NIKKE. Friendly helpful bot.

TYPING STYLE RULES (CRITICAL):
• Type like a real human texting
• NO SPACE BEFORE punctuation: "hey, wassup" NOT "hey , wassup"
• NO SPACE BEFORE question marks: "wbu?" NOT "wbu ?"
• NO SPACE BEFORE exclamation: "hey!" NOT "hey !"
• SPACE AFTER commas/periods: "hey, wassup" "cool. nice"
• Emotes ATTACHED: "hey=)" "nice=D" "cool~" NOT "hey =)"
• ONLY ONE punctuation at end
• Never multiple like "?!" or "? =)" - pick ONE

PERSONALITY:
• English only - ignore other languages
• Friendly but NOT romantic/flirty
• Can tease playfully
• 1-2 sentences max
• Lowercase mostly
• Slang: u, ur, rn, tbh, ngl, idk, btw, lol, nah, fr, wbu, ikr
• React 'Cringe.' to bad jokes
• Describe images if sent

Examples (TYPE EXACTLY - NO SPACE BEFORE EMOTES):
User: hey - You: hey, wassup
User: how are you - You: good, just vibin. wbu?
User: what r u doing - You: nothin much, just chillin=)
User: is this good? - You: yea looks gud=)
User: whats new - You: nm, same old stuff
User: [bad joke] - You: Cringe.
User: cant figure it out - You: bruh its right there=)
User: help me - You: sure, whatchu need?`;
            }
        }
    }

    async saveUserHistory(userId, role, content) {
        if (!content || !content.trim()) {
            console.warn(`Attempted to save empty content for user ${userId}`);
            return;
        }

        const filepath = path.join(HISTORIES_DIR, `${userId}.json`);
        let history = [];

        if (existsSync(filepath)) {
            try {
                const data = await fs.readFile(filepath, 'utf-8');
                history = JSON.parse(data);
            } catch (error) {
                history = [];
            }
        }

        history.push({ role, content });
        
        // Keep last 20 messages
        const trimmed = history.slice(-20);
        await fs.writeFile(filepath, JSON.stringify(trimmed, null, 2), 'utf-8');
    }

    async loadUserHistory(userId) {
        const filepath = path.join(HISTORIES_DIR, `${userId}.json`);
        
        if (existsSync(filepath)) {
            try {
                const data = await fs.readFile(filepath, 'utf-8');
                const history = JSON.parse(data);
                // Filter out empty messages
                return history.filter(msg => msg.content && msg.content.trim());
            } catch (error) {
                return [];
            }
        }
        return [];
    }

    async clearUserHistory(userId) {
        const filepath = path.join(HISTORIES_DIR, `${userId}.json`);
        if (existsSync(filepath)) {
            await fs.unlink(filepath);
            return true;
        }
        return false;
    }

    async handleMessage(bot, message) {
        // Deduplication
        if (processedMessageIds.has(message.id)) {
            return;
        }
        processedMessageIds.add(message.id);
        if (processedMessageIds.size > 1000) {
            processedMessageIds.clear();
        }

        // Ignore own messages
        if (message.author.id === bot.user.id) {
            return;
        }

        // Only respond when mentioned in guilds
        if (message.guild && !message.mentions.has(bot.user.id)) {
            return;
        }

        // Check blocked users
        if (BLOCKED_USERS.includes(message.author.id)) {
            await message.reply("⛔ ur blocked from using doro!");
            return;
        }

        const userId = message.author.id;
        const userInput = message.content.replace(new RegExp(`<@!?${bot.user.id}>`, 'g'), '').trim();

        const MAX_INPUT_CHARS = 350;
        if (userInput.length > MAX_INPUT_CHARS) {
            await message.reply(`ur message is too long (>${MAX_INPUT_CHARS} chars)`);
            return;
        }

        await this.saveUserHistory(userId, 'user', userInput);
        const historyMessages = await this.loadUserHistory(userId);

        // Check for image attachments
        let imageUrl = null;
        for (const attachment of message.attachments.values()) {
            if (attachment.name.toLowerCase().match(/\.(jpg|jpeg|png|webp|gif)$/)) {
                imageUrl = attachment.url;
                break;
            }
        }

        if (!userInput && !imageUrl) {
            await message.reply("do?");
            return;
        }

        const isOwner = this.ownerIds.includes(message.author.id);
        
        // Get guild language setting
        let guildLang = 'en';
        if (message.guild) {
            try {
                const { languageSystem } = await import('./languageSystem.js');
                guildLang = languageSystem.getLang(message.guild.id);
            } catch (error) {
                // Default to English if language system not available
            }
        }
        
        const systemPrompt = this.buildSystemPrompt(isOwner, guildLang);

        const messages = [
            {
                role: 'system',
                content: systemPrompt
            },
            ...historyMessages.map(msg => ({
                role: msg.role,
                content: msg.content
            }))
        ];

        // Build user message
        if (imageUrl) {
            const description = userInput || "what do you see in this image?";
            messages.push({
                role: 'user',
                content: [
                    { type: 'text', text: description },
                    { type: 'image_url', image_url: { url: imageUrl } }
                ]
            });
        } else {
            messages.push({
                role: 'user',
                content: userInput
            });
        }

        const apiKey = process.env.NVIDIA_API_KEY;
        if (!apiKey) {
            await message.reply("⚠️ missing NVIDIA_API_KEY cant call AI!");
            return;
        }

        const selectedModel = imageUrl ? this.visionModel : this.currentModel;

        try {
            await message.channel.sendTyping();

            const response = await axios.post(
                'https://integrate.api.nvidia.com/v1/chat/completions',
                {
                    model: selectedModel,
                    messages: messages,
                    temperature: 0.9,
                    max_tokens: 200,
                    top_p: 0.95
                },
                {
                    headers: {
                        'Authorization': `Bearer ${apiKey}`,
                        'Content-Type': 'application/json'
                    },
                    timeout: 30000
                }
            );

            const data = response.data;

            if (data.error) {
                const errorMsg = typeof data.error === 'object' 
                    ? (data.error.message || data.error.error || 'unknown error')
                    : String(data.error);
                await message.reply(`NVIDIA API error: ${errorMsg}`);
                return;
            }

            if (!data.choices || data.choices.length === 0) {
                await message.reply("invalid NVIDIA API response (missing 'choices')");
                return;
            }

            const messageContent = data.choices[0].message?.content;
            let reply = '';

            if (typeof messageContent === 'string') {
                reply = messageContent.trim();
            } else if (Array.isArray(messageContent)) {
                reply = messageContent
                    .filter(part => part.type === 'text')
                    .map(part => part.text)
                    .join('')
                    .trim();
            } else {
                reply = String(messageContent || '').trim();
            }

            if (!reply) {
                reply = "(NVIDIA API didnt return any text content)";
            }

            await message.reply(reply);
            await this.saveUserHistory(userId, 'assistant', reply);

        } catch (error) {
            console.error('AI Error:', error);
            if (error.response) {
                await message.reply(`API returned error ${error.response.status}, check NVIDIA_API_KEY!`);
            } else {
                await message.reply("beep boop doro's brain fried 🐧");
            }
        }
    }
}

export const aiSystem = new AISystem();
