/**
 * Utility Commands - Help, ping, avatar, etc.
 */
import { EmbedBuilder } from 'discord.js';
import { afkSystem } from '../systems/afkSystem.js';
import { prefixSystem } from '../systems/prefixSystem.js';
import { aiSystem } from '../systems/aiSystem.js';
import { languageSystem } from '../systems/languageSystem.js';
import { wordChainSystem } from '../systems/wordChainSystem.js';
import { sanitizeForOutput } from '../src/util/sanitizeMentions.js';

const helpCategories = {
    en: {
        main: {
            title: '🌸 Doro Bot V4.1 - Help',
            description: 'Choose a category to view commands:',
            categories: {
                economy: '💰 Economy - Balance, daily rewards, banking',
                casino: '🎰 Casino - Games and gambling',
                shop: '🏪 Shop - Buy items and inventory',
                marriage: '💍 Marriage - Relationships system',
                music: '🎵 Music - Play songs and manage queue',
                ai: '🤖 AI - Chat with Doro',
                utility: '⚙️ Utility - Bot tools and settings'
            },
            footer: 'Use {prefix}help <category> for details | V4.1'
        },
        economy: {
            title: '💰 Economy Commands',
            commands: [
                ['balance [@user]', 'Check your or someone\'s balance'],
                ['daily', 'Claim daily reward (increases with streak)'],
                ['deposit <amount>', 'Deposit money to bank'],
                ['withdraw <amount>', 'Withdraw money from bank'],
                ['give @user <amount>', 'Transfer money (10% fee)'],
                ['stats [@user]', 'View economy statistics']
            ]
        },
        casino: {
            title: '🎰 Casino Commands',
            commands: [
                ['cf <h/t> <bet>', 'Coinflip - Heads or tails'],
                ['slots <bet>', 'Slot machine with jackpots'],
                ['bj <bet>', 'Blackjack game']
            ]
        },
        shop: {
            title: '🏪 Shop Commands',
            commands: [
                ['shop [page]', 'Browse shop items'],
                ['buy <item>', 'Purchase an item'],
                ['inventory [@user]', 'View inventory'],
                ['use <item>', 'Use an item from inventory']
            ]
        },
        marriage: {
            title: '💍 Marriage Commands',
            commands: [
                ['marry @user', 'Propose marriage (needs ring)'],
                ['accept', 'Accept marriage proposal'],
                ['reject', 'Reject marriage proposal'],
                ['divorce', 'End your marriage'],
                ['marriage [@user]', 'View marriage info']
            ]
        },
        music: {
            title: '🎵 Music Commands',
            commands: [
                ['play <song>', 'Play or queue a song'],
                ['skip', 'Skip current song'],
                ['queue', 'View music queue'],
                ['pause', 'Pause playback'],
                ['resume', 'Resume playback'],
                ['stop', 'Stop and clear queue'],
                ['np', 'Now playing info']
            ]
        },
        ai: {
            title: '🤖 AI Commands',
            commands: [
                ['@Doro <message>', 'Chat with Doro AI'],
                ['reset', 'Clear your AI chat history']
            ]
        },
        utility: {
            title: '⚙️ Utility Commands',
            commands: [
                ['help [category]', 'Show this help menu'],
                ['ping', 'Check bot latency'],
                ['avatar [@user]', 'Get user avatar'],
                ['afk [reason]', 'Set AFK status'],
                ['say <message>', 'Make bot say something'],
                ['setprefix <prefix>', 'Change server prefix (Admin)'],
                ['/language', 'Change bot language (Admin)'],
                ['wordchain', 'Word chain game (see !wordchain for help)']
            ]
        }
    },
    vi: {
        main: {
            title: '🌸 Doro Bot V4.1 - Trợ Giúp',
            description: 'Chọn danh mục để xem lệnh:',
            categories: {
                economy: '💰 Kinh Tế - Số dư, thưởng hàng ngày, ngân hàng',
                casino: '🎰 Casino - Trò chơi và cá cược',
                shop: '🏪 Cửa Hàng - Mua vật phẩm và túi đồ',
                marriage: '💍 Kết Hôn - Hệ thống quan hệ',
                music: '🎵 Nhạc - Phát nhạc và quản lý',
                ai: '🤖 AI - Trò chuyện với Doro',
                utility: '⚙️ Tiện Ích - Công cụ và cài đặt'
            },
            footer: 'Dùng {prefix}help <danh mục> để xem chi tiết | V4.1'
        },
        economy: {
            title: '💰 Lệnh Kinh Tế',
            commands: [
                ['balance [@user]', 'Kiểm tra số dư của bạn hoặc ai đó'],
                ['daily', 'Nhận thưởng hàng ngày (tăng theo chuỗi)'],
                ['deposit <số tiền>', 'Gửi tiền vào ngân hàng'],
                ['withdraw <số tiền>', 'Rút tiền từ ngân hàng'],
                ['give @user <số tiền>', 'Chuyển tiền (phí 10%)'],
                ['stats [@user]', 'Xem thống kê kinh tế']
            ]
        },
        casino: {
            title: '🎰 Lệnh Casino',
            commands: [
                ['cf <h/t> <cược>', 'Tung xu - Ngửa hay sấp'],
                ['slots <cược>', 'Máy quay số với jackpot'],
                ['bj <cược>', 'Trò chơi Blackjack']
            ]
        },
        shop: {
            title: '🏪 Lệnh Cửa Hàng',
            commands: [
                ['shop [trang]', 'Duyệt cửa hàng'],
                ['buy <vật phẩm>', 'Mua vật phẩm'],
                ['inventory [@user]', 'Xem túi đồ'],
                ['use <vật phẩm>', 'Sử dụng vật phẩm']
            ]
        },
        marriage: {
            title: '💍 Lệnh Kết Hôn',
            commands: [
                ['marry @user', 'Cầu hôn (cần nhẫn)'],
                ['accept', 'Chấp nhận lời cầu hôn'],
                ['reject', 'Từ chối lời cầu hôn'],
                ['divorce', 'Ly hôn'],
                ['marriage [@user]', 'Xem thông tin kết hôn']
            ]
        },
        music: {
            title: '🎵 Lệnh Nhạc',
            commands: [
                ['play <bài hát>', 'Phát hoặc xếp hàng bài hát'],
                ['skip', 'Bỏ qua bài hiện tại'],
                ['queue', 'Xem hàng đợi nhạc'],
                ['pause', 'Tạm dừng'],
                ['resume', 'Tiếp tục'],
                ['stop', 'Dừng và xóa hàng đợi'],
                ['np', 'Thông tin bài đang phát']
            ]
        },
        ai: {
            title: '🤖 Lệnh AI',
            commands: [
                ['@Doro <tin nhắn>', 'Trò chuyện với Doro AI'],
                ['reset', 'Xóa lịch sử trò chuyện AI']
            ]
        },
        utility: {
            title: '⚙️ Lệnh Tiện Ích',
            commands: [
                ['help [danh mục]', 'Hiển thị menu trợ giúp'],
                ['ping', 'Kiểm tra độ trễ bot'],
                ['avatar [@user]', 'Lấy avatar người dùng'],
                ['afk [lý do]', 'Đặt trạng thái AFK'],
                ['say <tin nhắn>', 'Bắt bot nói gì đó'],
                ['setprefix <prefix>', 'Thay đổi prefix server (Admin)'],
                ['/language', 'Thay đổi ngôn ngữ bot (Admin)'],
                ['wordchain', 'Trò chơi nối từ (xem !wordchain để biết thêm)']
            ]
        }
    }
};

export const utilityCommands = {
    help: {
        execute: async (message, args, context) => {
            const { prefix } = context;
            const guildId = message.guild?.id;
            const lang = languageSystem.getLang(guildId);
            const helpData = helpCategories[lang];
            
            const category = args[0]?.toLowerCase();
            
            if (!category) {
                const embed = new EmbedBuilder()
                    .setColor('#FF69B4')
                    .setTitle(helpData.main.title)
                    .setDescription(helpData.main.description);
                
                for (const [key, value] of Object.entries(helpData.main.categories)) {
                    embed.addFields({ name: value, value: `\`${prefix}help ${key}\``, inline: false });
                }
                
                embed.setFooter({ text: helpData.main.footer.replace('{prefix}', prefix) })
                    .setTimestamp();
                
                await message.reply({ embeds: [embed] });
                return;
            }
            
            const categoryData = helpData[category];
            if (!categoryData) {
                await message.reply(`❌ Unknown category. Use \`${prefix}help\` to see all categories.`);
                return;
            }
            
            const embed = new EmbedBuilder()
                .setColor('#FF69B4')
                .setTitle(categoryData.title);
            
            for (const [cmd, desc] of categoryData.commands) {
                embed.addFields({ 
                    name: `${prefix}${cmd}`, 
                    value: desc, 
                    inline: false 
                });
            }
            
            embed.setFooter({ text: `Use ${prefix}help to see all categories | V4.1` })
                .setTimestamp();
            
            await message.reply({ embeds: [embed] });
        }
    },

    ping: {
        execute: async (message) => {
            const sent = await message.reply('🏓 Pinging...');
            const latency = sent.createdTimestamp - message.createdTimestamp;
            
            await sent.edit(`🏓 Pong! Latency: ${latency}ms | API: ${message.client.ws.ping}ms`);
        }
    },

    avatar: {
        execute: async (message) => {
            const target = message.mentions.users.first() || message.author;
            const avatarURL = target.displayAvatarURL({ size: 4096, dynamic: true });
            
            const embed = new EmbedBuilder()
                .setColor('#00FFFF')
                .setTitle(`${target.username}'s Avatar`)
                .setImage(avatarURL)
                .setTimestamp();
            
            await message.reply({ embeds: [embed] });
        }
    },

    afk: {
        execute: async (message, args) => {
            const userId = message.author.id;
            const reason = sanitizeForOutput(args.join(' ') || 'AFK');
            
            await afkSystem.setAFK(userId, reason);
            await message.reply(`✅ ur now AFK: ${reason}`);
        }
    },

    reset: {
        execute: async (message) => {
            const userId = message.author.id;
            const cleared = await aiSystem.clearUserHistory(userId);
            
            if (cleared) {
                await message.reply('✅ AI chat history cleared!');
            } else {
                await message.reply('❌ no chat history to clear!');
            }
        }
    },

    setprefix: {
        execute: async (message, args) => {
            if (!message.member.permissions.has('Administrator')) {
                await message.reply('⛔ u need Administrator permission!');
                return;
            }
            
            if (!args[0]) {
                await message.reply('usage: `setprefix <prefix>`');
                return;
            }
            
            const newPrefix = args[0];
            const success = await prefixSystem.setPrefix(message.guild.id, newPrefix);
            
            if (success) {
                await message.reply(`✅ prefix changed to \`${sanitizeForOutput(newPrefix)}\``);
            } else {
                await message.reply('❌ invalid prefix (max 10 characters)!');
            }
        }
    },

    say: {
        execute: async (message, args) => {
            if (!args[0]) {
                await message.reply('usage: `say <message>`');
                return;
            }
            
            const text = sanitizeForOutput(args.join(' '));
            if (!text.trim()) {
                await message.reply('❌ nothing to send!');
                return;
            }
            
            try {
                await message.delete();
            } catch (error) {
            }
            
            await message.channel.send({ content: text, allowedMentions: { parse: [] } });
        }
    },

    wordchain: {
        execute: async (message, args, context) => {
            const { prefix } = context;
            const subcommand = args[0]?.toLowerCase();
            const guildLang = languageSystem.getLang(message.guild.id);
            
            if (!subcommand) {
                const channelData = wordChainSystem.getChannelData(message.channel.id);
                const isEnabled = wordChainSystem.isAutoChannel(message.channel.id);
                
                const embed = new EmbedBuilder()
                    .setColor('#9B59B6')
                    .setTitle(guildLang === 'vi' ? '🔗 Nối Từ - Trợ Giúp' : '🔗 Word Chain - Help')
                    .addFields(
                        { 
                            name: guildLang === 'vi' ? '📊 Trạng Thái' : '📊 Status', 
                            value: isEnabled 
                                ? (guildLang === 'vi' ? `✅ Đang bật (${channelData.language === 'vi' ? 'Tiếng Việt' : 'English'})` : `✅ Enabled (${channelData.language})`) 
                                : (guildLang === 'vi' ? '❌ Đang tắt' : '❌ Disabled'),
                            inline: false 
                        }
                    );
                
                if (isEnabled && channelData) {
                    embed.addFields(
                        { 
                            name: guildLang === 'vi' ? '🔤 Từ Hiện Tại' : '🔤 Current Word', 
                            value: channelData.lastWord || (guildLang === 'vi' ? 'Chưa có' : 'None'), 
                            inline: true 
                        },
                        { 
                            name: guildLang === 'vi' ? '📊 Chuỗi' : '📊 Chain', 
                            value: `${channelData.chainCount}`, 
                            inline: true 
                        }
                    );
                }
                
                embed.addFields(
                    { 
                        name: guildLang === 'vi' ? '📖 Lệnh' : '📖 Commands', 
                        value: guildLang === 'vi' 
                            ? `\`${prefix}wordchain enable <en/vi>\` - Bật nối từ\n\`${prefix}wordchain disable\` - Tắt nối từ\n\`${prefix}wordchain restart\` - Khởi động lại chuỗi\n\`${prefix}wordchain stats [@user]\` - Xem thống kê`
                            : `\`${prefix}wordchain enable <en/vi>\` - Enable word chain\n\`${prefix}wordchain disable\` - Disable word chain\n\`${prefix}wordchain restart\` - Restart chain\n\`${prefix}wordchain stats [@user]\` - View stats`,
                        inline: false 
                    }
                );
                
                await message.reply({ embeds: [embed] });
                return;
            }
            
            if (subcommand === 'enable') {
                if (!message.member.permissions.has('Administrator')) {
                    await message.reply(guildLang === 'vi' ? '⛔ Bạn cần quyền Administrator!' : '⛔ u need Administrator permission!');
                    return;
                }
                
                const lang = args[1]?.toLowerCase();
                if (!lang || !['en', 'vi'].includes(lang)) {
                    await message.reply(guildLang === 'vi' ? 'usage: `wordchain enable <en/vi>`' : 'usage: `wordchain enable <en/vi>`');
                    return;
                }
                
                await wordChainSystem.enableAutoChannel(message.channel.id, lang);
                await message.reply(
                    guildLang === 'vi' 
                        ? `✅ Nối từ đã bật cho kênh này (${lang === 'vi' ? 'Tiếng Việt' : 'English'})!`
                        : `✅ Word chain enabled for this channel (${lang})!`
                );
            } else if (subcommand === 'disable') {
                if (!message.member.permissions.has('Administrator')) {
                    await message.reply(guildLang === 'vi' ? '⛔ Bạn cần quyền Administrator!' : '⛔ u need Administrator permission!');
                    return;
                }
                
                const success = await wordChainSystem.disableAutoChannel(message.channel.id);
                if (success) {
                    await message.reply(guildLang === 'vi' ? '✅ Nối từ đã tắt!' : '✅ Word chain disabled!');
                } else {
                    await message.reply(guildLang === 'vi' ? '❌ Nối từ chưa được bật ở kênh này!' : '❌ Word chain not enabled in this channel!');
                }
            } else if (subcommand === 'restart') {
                if (!message.member.permissions.has('Administrator')) {
                    await message.reply(guildLang === 'vi' ? '⛔ Bạn cần quyền Administrator!' : '⛔ u need Administrator permission!');
                    return;
                }
                
                const success = await wordChainSystem.restartChain(message.channel.id);
                if (success) {
                    await message.reply(guildLang === 'vi' ? '🔄 Chuỗi nối từ đã được khởi động lại!' : '🔄 Word chain restarted!');
                } else {
                    await message.reply(guildLang === 'vi' ? '❌ Nối từ chưa được bật ở kênh này!' : '❌ Word chain not enabled in this channel!');
                }
            } else if (subcommand === 'stats') {
                const target = message.mentions.users.first() || message.author;
                const stats = wordChainSystem.getUserStats(target.id);
                
                const embed = new EmbedBuilder()
                    .setColor('#9B59B6')
                    .setTitle(guildLang === 'vi' ? `🔗 Thống Kê Nối Từ - ${target.username}` : `🔗 Word Chain Stats - ${target.username}`)
                    .addFields(
                        { 
                            name: guildLang === 'vi' ? '📝 Tổng Số Từ' : '📝 Total Words', 
                            value: `${stats.totalWords}`, 
                            inline: true 
                        },
                        { 
                            name: guildLang === 'vi' ? '🏆 Thắng' : '🏆 Wins', 
                            value: `${stats.wins}`, 
                            inline: true 
                        }
                    )
                    .setTimestamp();
                
                await message.reply({ embeds: [embed] });
            } else {
                await message.reply(
                    guildLang === 'vi' 
                        ? `❌ Lệnh không hợp lệ! Dùng \`${prefix}wordchain\` để xem trợ giúp.`
                        : `❌ Invalid subcommand! Use \`${prefix}wordchain\` for help.`
                );
            }
        }
    }
};
