/**
 * Economy Commands - Balance, daily, deposit, withdraw, give
 */
import { EmbedBuilder } from 'discord.js';
import { economy } from '../systems/economySystem.js';
import { languageSystem } from '../systems/languageSystem.js';

export const economyCommands = {
    balance: {
        execute: async (message, args) => {
            const guildId = message.guild?.id;
            const target = message.mentions.users.first() || message.author;
            const userId = target.id;
            
            const balance = economy.getBalance(userId);
            const bank = economy.getBank(userId);
            const user = economy.getUser(userId);
            
            const balanceStr = balance === Infinity ? '∞' : balance.toLocaleString();
            const bankStr = bank === Infinity ? '∞' : bank.toLocaleString();
            const totalStr = balance === Infinity ? '∞' : (balance + bank).toLocaleString();
            
            const coinsText = languageSystem.t(guildId, 'coins');
            const daysText = languageSystem.t(guildId, 'days');
            
            const embed = new EmbedBuilder()
                .setColor('#FFD700')
                .setTitle(languageSystem.t(guildId, 'balance_title', { user: target.username }))
                .addFields(
                    { name: languageSystem.t(guildId, 'balance_wallet'), value: `${balanceStr} ${coinsText}`, inline: true },
                    { name: languageSystem.t(guildId, 'balance_bank'), value: `${bankStr} ${coinsText}`, inline: true },
                    { name: languageSystem.t(guildId, 'balance_total'), value: `${totalStr} ${coinsText}`, inline: true }
                )
                .addFields(
                    { name: languageSystem.t(guildId, 'balance_level'), value: `${user.level}`, inline: true },
                    { name: languageSystem.t(guildId, 'balance_xp'), value: `${user.xp}/${economy.getXPForLevel(user.level)}`, inline: true },
                    { name: languageSystem.t(guildId, 'balance_streak'), value: `${user.dailyStreak} ${daysText}`, inline: true }
                )
                .setTimestamp();
            
            if (economy.isInfinity(userId)) {
                embed.setFooter({ text: languageSystem.t(guildId, 'balance_infinity') });
            }
            
            await message.reply({ embeds: [embed] });
        }
    },

    bal: {
        execute: async (message, args, context) => {
            await economyCommands.balance.execute(message, args, context);
        }
    },

    daily: {
        execute: async (message) => {
            const guildId = message.guild?.id;
            const userId = message.author.id;
            
            if (!economy.canDaily(userId)) {
                const user = economy.getUser(userId);
                const lastDaily = new Date(user.lastDaily);
                const nextDaily = new Date(lastDaily.getTime() + 24 * 60 * 60 * 1000);
                const timeLeft = nextDaily - Date.now();
                
                const hours = Math.floor(timeLeft / (1000 * 60 * 60));
                const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
                
                const hoursText = languageSystem.t(guildId, 'hours');
                const minutesText = languageSystem.t(guildId, 'minutes');
                
                await message.reply(languageSystem.t(guildId, 'daily_cooldown', { 
                    time: `${hours}${hoursText} ${minutes}${minutesText}` 
                }));
                return;
            }
            
            const result = await economy.claimDaily(userId);
            const coinsText = languageSystem.t(guildId, 'coins');
            const daysText = languageSystem.t(guildId, 'days');
            
            const embed = new EmbedBuilder()
                .setColor('#00FF00')
                .setTitle(languageSystem.t(guildId, 'daily_claimed'))
                .setDescription(languageSystem.t(guildId, 'daily_received', { amount: result.amount.toLocaleString() }))
                .addFields(
                    { name: languageSystem.t(guildId, 'daily_streak'), value: `${result.streak} ${daysText}`, inline: true },
                    { name: languageSystem.t(guildId, 'balance_level'), value: `${result.level}`, inline: true },
                    { name: languageSystem.t(guildId, 'balance_xp'), value: `+${result.xpGained}`, inline: true }
                );
            
            // Add bonus fields
            const bonusFields = [
                { name: '📈 Streak Bonus', value: `+${result.streakBonus.toFixed(2)}%`, inline: true },
                { name: '💫 Level Bonus', value: `+${result.levelBonus.toFixed(2)}%`, inline: true }
            ];
            
            if (result.ringBonus > 0) {
                bonusFields.push({ name: '💍 Ring Bonus', value: `+${result.ringBonus.toFixed(2)}%`, inline: true });
            }
            
            embed.addFields(...bonusFields);
            embed.setTimestamp();
            
            if (result.newLevel) {
                embed.setFooter({ text: languageSystem.t(guildId, 'daily_levelup', { level: result.newLevel }) });
            }
            
            await message.reply({ embeds: [embed] });
        }
    },

    deposit: {
        execute: async (message, args) => {
            const userId = message.author.id;
            
            if (economy.isInfinity(userId)) {
                await message.reply('♾️ infinity users dont need to deposit!');
                return;
            }
            
            let amount = args[0];
            if (!amount) {
                await message.reply('usage: `deposit <amount|all>`');
                return;
            }
            
            const balance = economy.getBalance(userId);
            
            if (amount === 'all') {
                amount = balance;
            } else {
                amount = parseInt(amount);
                if (isNaN(amount) || amount <= 0) {
                    await message.reply('❌ invalid amount!');
                    return;
                }
            }
            
            if (amount > balance) {
                await message.reply(`❌ u only have ${balance.toLocaleString()} coins!`);
                return;
            }
            
            const success = await economy.deposit(userId, amount);
            if (success) {
                await message.reply(`✅ deposited **${amount.toLocaleString()}** coins to ur bank!`);
            } else {
                await message.reply('❌ failed to deposit!');
            }
        }
    },

    dep: {
        execute: async (message, args, context) => {
            await economyCommands.deposit.execute(message, args, context);
        }
    },

    withdraw: {
        execute: async (message, args) => {
            const userId = message.author.id;
            
            if (economy.isInfinity(userId)) {
                await message.reply('♾️ infinity users dont need to withdraw!');
                return;
            }
            
            let amount = args[0];
            if (!amount) {
                await message.reply('usage: `withdraw <amount|all>`');
                return;
            }
            
            const bank = economy.getBank(userId);
            
            if (amount === 'all') {
                amount = bank;
            } else {
                amount = parseInt(amount);
                if (isNaN(amount) || amount <= 0) {
                    await message.reply('❌ invalid amount!');
                    return;
                }
            }
            
            if (amount > bank) {
                await message.reply(`❌ u only have ${bank.toLocaleString()} coins in ur bank!`);
                return;
            }
            
            const success = await economy.withdraw(userId, amount);
            if (success) {
                await message.reply(`✅ withdrew **${amount.toLocaleString()}** coins from ur bank!`);
            } else {
                await message.reply('❌ failed to withdraw!');
            }
        }
    },

    with: {
        execute: async (message, args, context) => {
            await economyCommands.withdraw.execute(message, args, context);
        }
    },

    give: {
        execute: async (message, args) => {
            const userId = message.author.id;
            const target = message.mentions.users.first();
            
            if (!target) {
                await message.reply('usage: `give @user <amount>`');
                return;
            }
            
            if (target.id === userId) {
                await message.reply('❌ u cant give money to urself!');
                return;
            }
            
            if (target.bot) {
                await message.reply('❌ u cant give money to bots!');
                return;
            }
            
            let amount = parseInt(args[1]);
            if (isNaN(amount) || amount <= 0) {
                await message.reply('❌ invalid amount!');
                return;
            }
            
            const balance = economy.getBalance(userId);
            const isInfinity = economy.isInfinity(userId);
            
            if (!isInfinity && amount > balance) {
                await message.reply(`❌ u only have ${balance.toLocaleString()} coins!`);
                return;
            }
            
            // 10% fee for non-infinity users
            const fee = isInfinity ? 0 : Math.floor(amount * 0.1);
            const actualAmount = amount - fee;
            
            const success = await economy.transfer(userId, target.id, actualAmount);
            if (success) {
                const feeMsg = fee > 0 ? ` (${fee.toLocaleString()} fee)` : '';
                await message.reply(`✅ gave **${actualAmount.toLocaleString()}** coins to ${target}${feeMsg}`);
            } else {
                await message.reply('❌ failed to transfer!');
            }
        }
    },

    stats: {
        execute: async (message, args) => {
            const guildId = message.guild?.id;
            const target = message.mentions.users.first() || message.author;
            const stats = economy.getStats(target.id);
            
            const coinsText = languageSystem.t(guildId, 'coins');
            const daysText = languageSystem.t(guildId, 'days');
            
            const embed = new EmbedBuilder()
                .setColor('#9B59B6')
                .setTitle(`📊 ${target.username}'s Stats`)
                .addFields(
                    { name: '⭐ Level', value: `${stats.level}`, inline: true },
                    { name: '✨ XP', value: `${stats.xp}/${economy.getXPForLevel(stats.level)}`, inline: true },
                    { name: '🔥 Daily Streak', value: `${stats.dailyStreak} ${daysText}`, inline: true }
                )
                .addFields(
                    { name: '💰 Total Earned', value: `${stats.totalEarned.toLocaleString()} ${coinsText}`, inline: true },
                    { name: '💸 Total Spent', value: `${stats.totalSpent.toLocaleString()} ${coinsText}`, inline: true },
                    { name: '💵 Base Daily', value: `${stats.baseDaily.toLocaleString()} ${coinsText}`, inline: true }
                )
                .addFields(
                    { name: '🎰 Casino Wins', value: `${stats.wins || 0}`, inline: true },
                    { name: '💔 Casino Losses', value: `${stats.losses || 0}`, inline: true },
                    { name: '📈 Win Rate', value: `${((stats.wins || 0) / ((stats.wins || 0) + (stats.losses || 0) || 1) * 100).toFixed(1)}%`, inline: true }
                )
                .setTimestamp();
            
            if (economy.isInfinity(target.id)) {
                embed.setFooter({ text: '♾️ INFINITY MODE ACTIVE' });
            }
            
            await message.reply({ embeds: [embed] });
        }
    },

    leaderboard: {
        execute: async (message, args) => {
            const guildId = message.guild?.id;
            const type = args[0]?.toLowerCase() || 'balance';
            const validTypes = ['balance', 'level', 'streak', 'wins'];
            
            if (!validTypes.includes(type)) {
                await message.reply(`❌ Invalid type! Use: balance, level, streak, or wins`);
                return;
            }

            const leaderboard = economy.getLeaderboard(type, 10);
            
            if (leaderboard.length === 0) {
                await message.reply('No data available for leaderboard!');
                return;
            }

            const coinsText = languageSystem.t(guildId, 'coins');
            const daysText = languageSystem.t(guildId, 'days');

            const typeIcons = {
                balance: '💰',
                level: '⭐',
                streak: '🔥',
                wins: '🎰'
            };

            const typeNames = {
                balance: 'Total Balance',
                level: 'Level',
                streak: 'Daily Streak',
                wins: 'Casino Wins'
            };

            const embed = new EmbedBuilder()
                .setColor('#FFD700')
                .setTitle(`${typeIcons[type]} Leaderboard - ${typeNames[type]}`)
                .setTimestamp();

            let description = '';
            for (let i = 0; i < leaderboard.length; i++) {
                const entry = leaderboard[i];
                const medal = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `${i + 1}.`;
                
                try {
                    const user = await message.client.users.fetch(entry.userId);
                    let valueStr;
                    if (type === 'balance') {
                        valueStr = `${entry.value.toLocaleString()} ${coinsText}`;
                    } else if (type === 'streak') {
                        valueStr = `${entry.value} ${daysText}`;
                    } else {
                        valueStr = entry.value.toString();
                    }
                    description += `${medal} **${user.username}** - ${valueStr}\n`;
                } catch (error) {
                    description += `${medal} Unknown User - ${entry.value}\n`;
                }
            }

            embed.setDescription(description);
            await message.reply({ embeds: [embed] });
        }
    },

    lb: {
        execute: async (message, args, context) => {
            await economyCommands.leaderboard.execute(message, args, context);
        }
    }
};
