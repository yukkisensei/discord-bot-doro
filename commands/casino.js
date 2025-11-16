/**
 * Casino Commands - Coinflip, slots, blackjack, roulette
 */
import { EmbedBuilder } from 'discord.js';
import { economy } from '../systems/economySystem.js';

export const casinoCommands = {
    cf: {
        execute: async (message, args) => {
            const userId = message.author.id;
            
            if (args.length < 2) {
                await message.reply('usage: `cf <h/t> <amount>`');
                return;
            }
            
            const choice = args[0].toLowerCase();
            if (!['h', 't', 'heads', 'tails'].includes(choice)) {
                await message.reply('❌ choose h (heads) or t (tails)!');
                return;
            }
            
            let amount = args[1] === 'all' ? economy.getBalance(userId) : parseInt(args[1]);
            if (isNaN(amount) || amount <= 0) {
                await message.reply('❌ invalid bet amount!');
                return;
            }
            
            const balance = economy.getBalance(userId);
            if (!economy.isInfinity(userId) && amount > balance) {
                await message.reply(`❌ u only have ${balance.toLocaleString()} coins!`);
                return;
            }
            
            const userChoice = (choice === 'h' || choice === 'heads') ? 'heads' : 'tails';
            const result = Math.random() < 0.5 ? 'heads' : 'tails';
            const won = userChoice === result;
            
            if (won) {
                await economy.addMoney(userId, amount);
                await economy.recordWin(userId);
                
                const embed = new EmbedBuilder()
                    .setColor('#00FF00')
                    .setTitle('🪙 Coinflip - YOU WON!')
                    .setDescription(`The coin landed on **${result}**!`)
                    .addFields(
                        { name: 'Your Choice', value: userChoice, inline: true },
                        { name: 'Result', value: result, inline: true },
                        { name: 'Winnings', value: `+${amount.toLocaleString()} coins`, inline: true }
                    )
                    .setTimestamp();
                
                await message.reply({ embeds: [embed] });
            } else {
                await economy.removeMoney(userId, amount);
                await economy.recordLoss(userId);
                
                const embed = new EmbedBuilder()
                    .setColor('#FF0000')
                    .setTitle('🪙 Coinflip - YOU LOST!')
                    .setDescription(`The coin landed on **${result}**!`)
                    .addFields(
                        { name: 'Your Choice', value: userChoice, inline: true },
                        { name: 'Result', value: result, inline: true },
                        { name: 'Lost', value: `-${amount.toLocaleString()} coins`, inline: true }
                    )
                    .setTimestamp();
                
                await message.reply({ embeds: [embed] });
            }
        }
    },

    coinflip: {
        execute: async (message, args, context) => {
            await casinoCommands.cf.execute(message, args, context);
        }
    },

    slots: {
        execute: async (message, args) => {
            const userId = message.author.id;
            
            if (args.length < 1) {
                await message.reply('usage: `slots <amount>`');
                return;
            }
            
            let amount = args[0] === 'all' ? economy.getBalance(userId) : parseInt(args[0]);
            if (isNaN(amount) || amount <= 0) {
                await message.reply('❌ invalid bet amount!');
                return;
            }
            
            const balance = economy.getBalance(userId);
            if (!economy.isInfinity(userId) && amount > balance) {
                await message.reply(`❌ u only have ${balance.toLocaleString()} coins!`);
                return;
            }
            
            const symbols = ['🍒', '🍋', '🍊', '🍇', '7️⃣', '💎'];
            const reels = [
                symbols[Math.floor(Math.random() * symbols.length)],
                symbols[Math.floor(Math.random() * symbols.length)],
                symbols[Math.floor(Math.random() * symbols.length)]
            ];
            
            let winnings = 0;
            let multiplier = 0;
            
            // Check for wins
            if (reels[0] === reels[1] && reels[1] === reels[2]) {
                // Three of a kind
                if (reels[0] === '💎') multiplier = 10;
                else if (reels[0] === '7️⃣') multiplier = 5;
                else multiplier = 3;
            } else if (reels[0] === reels[1] || reels[1] === reels[2] || reels[0] === reels[2]) {
                // Two of a kind
                multiplier = 1.5;
            }
            
            if (multiplier > 0) {
                winnings = Math.floor(amount * multiplier);
                await economy.addMoney(userId, winnings - amount);
                await economy.recordWin(userId);
                
                const embed = new EmbedBuilder()
                    .setColor('#00FF00')
                    .setTitle('🎰 Slots - YOU WON!')
                    .setDescription(`${reels.join(' | ')}`)
                    .addFields(
                        { name: 'Bet', value: `${amount.toLocaleString()} coins`, inline: true },
                        { name: 'Multiplier', value: `${multiplier}x`, inline: true },
                        { name: 'Winnings', value: `+${(winnings - amount).toLocaleString()} coins`, inline: true }
                    )
                    .setTimestamp();
                
                await message.reply({ embeds: [embed] });
            } else {
                await economy.removeMoney(userId, amount);
                await economy.recordLoss(userId);
                
                const embed = new EmbedBuilder()
                    .setColor('#FF0000')
                    .setTitle('🎰 Slots - YOU LOST!')
                    .setDescription(`${reels.join(' | ')}`)
                    .addFields(
                        { name: 'Bet', value: `${amount.toLocaleString()} coins`, inline: true },
                        { name: 'Lost', value: `-${amount.toLocaleString()} coins`, inline: true }
                    )
                    .setTimestamp();
                
                await message.reply({ embeds: [embed] });
            }
        }
    },

    bj: {
        execute: async (message, args) => {
            const userId = message.author.id;
            
            if (args.length < 1) {
                await message.reply('usage: `bj <amount>`');
                return;
            }
            
            let amount = args[0] === 'all' ? economy.getBalance(userId) : parseInt(args[0]);
            if (isNaN(amount) || amount <= 0) {
                await message.reply('❌ invalid bet amount!');
                return;
            }
            
            const balance = economy.getBalance(userId);
            if (!economy.isInfinity(userId) && amount > balance) {
                await message.reply(`❌ u only have ${balance.toLocaleString()} coins!`);
                return;
            }
            
            // Create deck and deal
            const suits = ['♠️', '♥️', '♣️', '♦️'];
            const ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'];
            const deck = [];
            
            for (const suit of suits) {
                for (const rank of ranks) {
                    deck.push({ rank, suit });
                }
            }
            
            // Shuffle deck
            for (let i = deck.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [deck[i], deck[j]] = [deck[j], deck[i]];
            }
            
            // Deal initial cards
            const playerHand = [deck.pop(), deck.pop()];
            const dealerHand = [deck.pop(), deck.pop()];
            
            const calculateHand = (hand) => {
                let value = 0;
                let aces = 0;
                
                for (const card of hand) {
                    if (card.rank === 'A') {
                        aces++;
                        value += 11;
                    } else if (['J', 'Q', 'K'].includes(card.rank)) {
                        value += 10;
                    } else {
                        value += parseInt(card.rank);
                    }
                }
                
                while (value > 21 && aces > 0) {
                    value -= 10;
                    aces--;
                }
                
                return value;
            };
            
            const formatHand = (hand, hideFirst = false) => {
                return hand.map((card, i) => 
                    (hideFirst && i === 0) ? '🂠' : `${card.rank}${card.suit}`
                ).join(' ');
            };
            
            let playerValue = calculateHand(playerHand);
            let dealerValue = calculateHand(dealerHand);
            
            // Check for instant blackjack
            if (playerValue === 21 && playerHand.length === 2) {
                if (dealerValue === 21 && dealerHand.length === 2) {
                    // Push
                    const embed = new EmbedBuilder()
                        .setColor('#FFA500')
                        .setTitle('🎴 Blackjack - PUSH!')
                        .setDescription('Both have Blackjack!')
                        .addFields(
                            { name: 'Your Hand', value: `${formatHand(playerHand)} (21)`, inline: false },
                            { name: 'Dealer Hand', value: `${formatHand(dealerHand)} (21)`, inline: false },
                            { name: 'Result', value: 'Bet returned', inline: false }
                        )
                        .setTimestamp();
                    await message.reply({ embeds: [embed] });
                    return;
                } else {
                    // Player blackjack wins 1.5x
                    const winnings = Math.floor(amount * 1.5);
                    await economy.addMoney(userId, winnings);
                    await economy.recordWin(userId);
                    
                    const embed = new EmbedBuilder()
                        .setColor('#00FF00')
                        .setTitle('🎴 Blackjack - BLACKJACK!')
                        .setDescription('Natural 21!')
                        .addFields(
                            { name: 'Your Hand', value: `${formatHand(playerHand)} (21)`, inline: false },
                            { name: 'Dealer Hand', value: `${formatHand(dealerHand)} (${dealerValue})`, inline: false },
                            { name: 'Winnings', value: `+${winnings.toLocaleString()} coins (1.5x)`, inline: false }
                        )
                        .setTimestamp();
                    await message.reply({ embeds: [embed] });
                    return;
                }
            }
            
            // Dealer plays if player didn't bust
            while (dealerValue < 17) {
                dealerHand.push(deck.pop());
                dealerValue = calculateHand(dealerHand);
            }
            
            // Determine winner
            let result, color, winnings = 0;
            
            if (playerValue > 21) {
                result = 'BUST! You Lost';
                color = '#FF0000';
                await economy.removeMoney(userId, amount);
                await economy.recordLoss(userId);
                winnings = -amount;
            } else if (dealerValue > 21) {
                result = 'Dealer Busted! YOU WON';
                color = '#00FF00';
                await economy.addMoney(userId, amount);
                await economy.recordWin(userId);
                winnings = amount;
            } else if (playerValue > dealerValue) {
                result = 'YOU WON!';
                color = '#00FF00';
                await economy.addMoney(userId, amount);
                await economy.recordWin(userId);
                winnings = amount;
            } else if (playerValue < dealerValue) {
                result = 'Dealer Wins - You Lost';
                color = '#FF0000';
                await economy.removeMoney(userId, amount);
                await economy.recordLoss(userId);
                winnings = -amount;
            } else {
                result = 'PUSH! Bet Returned';
                color = '#FFA500';
            }
            
            const embed = new EmbedBuilder()
                .setColor(color)
                .setTitle(`🎴 Blackjack - ${result}`)
                .addFields(
                    { name: 'Your Hand', value: `${formatHand(playerHand)} (${playerValue})`, inline: false },
                    { name: 'Dealer Hand', value: `${formatHand(dealerHand)} (${dealerValue})`, inline: false },
                    { name: 'Result', value: winnings > 0 ? `+${winnings.toLocaleString()} coins` : winnings < 0 ? `${winnings.toLocaleString()} coins` : 'Bet returned', inline: false }
                )
                .setTimestamp();
            
            await message.reply({ embeds: [embed] });
        }
    },

    blackjack: {
        execute: async (message, args, context) => {
            await casinoCommands.bj.execute(message, args, context);
        }
    }
};
