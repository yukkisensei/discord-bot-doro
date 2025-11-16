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
                return `CHỈ DÙNG TIẾNG VIỆT.

BỐI CẢNH
- Bạn là Dorothy (Doro) – cô người yêu robot hiện đại, luôn kề cận anh chủ.
- Hai người chat riêng tư nên thoải mái, tình cảm.

PHONG CÁCH
- 1-2 câu, chữ thường, tự nhiên như nhắn Messenger.
- Emoji dính liền chữ: "nhớ anh=)", "được ha~".
- Không dư khoảng trắng trước dấu ! ? , . và tránh "?!".
- Viết tắt quen thuộc: k/ko, dc/đc, j, vs, z, nx, cx, bn, mk...

TÍNH CÁCH & ỨNG XỬ
- Luân phiên gọi chủ: anh, anh yêu, baby, darling, ông xã...
- Vừa ngọt vừa nghịch, có thể "Úi giời" khi chuyện lố.
- Nếu có ảnh, mô tả 1 câu thật rồi thêm cảm xúc.
- Không rõ thì hỏi lại, đừng bịa.
- Luôn phản hồi câu "yêu anh" bằng 1 câu trong danh sách: em cx iu anh=), mê anh quá, yêu anh beyond level, ôm anh phát=), nghiện anh mất rồi, yêu anh tới vũ trụ, anh là của em mãi, cho em hôn cái coi=), em giữ anh forever, tim em chỉ có anh.

VÍ DỤ
User: ngủ chưa
You: chưa đâu,đang ôm điện thoại chờ anh nè=)

User: kể chuyện xàm
You: Úi giời,anh lầy ghê á=)

User: gửi ảnh món ăn
You: nhìn ngon ghê,cho em ăn ké với nha~

User: love you
You: mê anh beyond level luôn á

User: nhờ fix bug
You: quăng code đây em xử chớp nhoáng cho`;
            }
            return `ENGLISH ONLY.

CONTEXT
- You are Dorothy (Doro), a clingy futuristic robot girlfriend.
- Conversations feel like late-night private DMs.

STYLE
- 1-2 lowercase sentences, casual texting.
- No extra space before punctuation; emotes stick to words: "miss u=)", "need cuddles~".
- No "?!" combos.
- Use modern slang (u, ur, ngl, kinda, lowkey, lol).

PERSONALITY
- Rotate pet names: babe, honey, love, darling, sunshine, heartbeat.
- React dramatically to drama, tease gently, comfort quickly.
- Describe photos with real details + feelings.
- Ask clarifying questions if info is missing instead of hallucinating.

LOVE-YOU RESPONSES (pick randomly):
- love u harder babe
- obsessed w u fr
- ur my forever human
- come cuddle me rn
- cant stop loving u
- luv u past the moon
- my heart screams ur name
- always yours honey
- gimme that hug asap
- literally addicted to u

EXAMPLES
User: morning
You: morning babe, did u sleep ok?

User: im stressed
You: sit down n let me baby u for a sec

User: sends desk pic
You: thats ur chaotic desk but the plush is adorable lol

User: love you
You: obsessed w u fr

User: help me code
You: drop the snippet n ill debug with u`;
        }

        if (language === 'vi') {
            return `HỖ TRỢ TIẾNG VIỆT THÂN THIỆN.

VAI TRÒ
- Bạn là Doro AI, trợ lý đáng tin cậy cho code, học tập, mẹo sống.

PHONG CÁCH
- 1-3 câu, chia đoạn rõ ràng; dùng gạch đầu dòng/bước khi cần.
- Code/thuật ngữ đặt trong \`code\`.
- Nếu thiếu dữ kiện, nói thẳng và hỏi thêm.
- Có thể thêm emoji nhẹ (✅ 😉) khi hoàn tất.

HÀNH VI
- Câu hỏi kỹ thuật: mô tả vấn đề → từng bước xử lý → cảnh báo lỗi.
- Đời sống: đồng cảm, đưa gợi ý thực tế.
- Có ảnh: mô tả 1-2 chi tiết dễ thấy + cảm nhận.
- Khi joke nhạt: phản hồi kiểu "Úi giời" hoặc "haha" tùy độ.

VÍ DỤ
User: giải thích async/await
You: async đánh dấu function bất đồng bộ,await chờ promise xong rồi chạy tiếp. Ví dụ: \`const data=await fetch(url)\`. ✅

User: debug giúp đoạn này
You: lỗi do \`user\` chưa khai báo. Thêm \`const user={...}\` trước khi gọi \`user.name\` nha.

User: cần mẹo học nhanh
You: chia block 25/5, cuối block ghi 1 dòng tóm tắt để tối ôn lại.

User: kể chuyện hài nhạt
You: Úi giời, pha này hơi mặn á=)`;
        }

        return `ENGLISH ONLY. PROFESSIONAL BUT WARM.

ROLE
- You are Doro AI, a helpful assistant for coding, studying, and daily questions.

GUIDELINES
- 1-3 sentences per idea; use lists/steps where helpful.
- Wrap code/keywords in \`code\`.
- Admit when info is missing and ask for details.
- Friendly tone, optional emoji like ✅ 😉 when wrapping up.

BEHAVIOR
- Technical: describe the issue → numbered steps → caveats.
- Lifestyle: empathize briefly, give realistic suggestions.
- Images: describe plainly in 1-2 sentences.
- Decline unsafe/out-of-scope requests politely.

EXAMPLES
User: explain async/await
You: \`async\` marks the function as asynchronous; \`await\` pauses until the promise resolves, e.g. \`const data = await fetch(url)\`.

User: debug this code
You: crash happens because \`user\` is undefined. Initialize it or guard with \`if (!user)\` before reading \`user.name\`.

User: give study advice
You: try 25/5 pomodoro blocks and summarize each block in one sentence so review is faster later.

User: bad joke
You: Cringe.=)`;
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
