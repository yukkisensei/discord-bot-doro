/**
 * Shop Commands - Shop, buy, inventory, use, equip
 */
import { EmbedBuilder } from 'discord.js';
import { shopSystem } from '../systems/shopSystem.js';
import { economy } from '../systems/economySystem.js';

export const shopCommands = {
    shop: {
        execute: async (message, args) => {
            const category = args[0]?.toLowerCase();
            const items = shopSystem.getShopItems(category);
            
            const embed = new EmbedBuilder()
                .setColor('#FFD700')
                .setTitle('🏪 Doro\'s Shop')
                .setDescription('Use `buy <item_id>` to purchase!')
                .setTimestamp();
            
            // Group by category
            const categories = {};
            for (const [id, item] of Object.entries(items)) {
                if (!categories[item.category]) {
                    categories[item.category] = [];
                }
                categories[item.category].push({ id, ...item });
            }
            
            // Display items by category
            for (const [cat, items] of Object.entries(categories)) {
                const itemList = items
                    .slice(0, 5) // Limit to 5 per category
                    .map(item => `\`${item.id}\` ${item.emoji} **${item.name}** - ${item.price.toLocaleString()} coins`)
                    .join('\n');
                
                embed.addFields({ name: `${cat.toUpperCase()}`, value: itemList || 'No items', inline: false });
            }
            
            embed.setFooter({ text: 'Categories: ring, lootbox, consumable, collectible, pet, upgrade' });
            
            await message.reply({ embeds: [embed] });
        }
    },

    buy: {
        execute: async (message, args) => {
            const userId = message.author.id;
            
            if (!args[0]) {
                await message.reply('usage: `buy <item_id>`');
                return;
            }
            
            const itemId = args[0].toLowerCase();
            const item = shopSystem.getItemInfo(itemId);
            
            if (!item) {
                await message.reply('❌ item not found!');
                return;
            }
            
            const balance = economy.getBalance(userId);
            
            if (!economy.isInfinity(userId) && balance < item.price) {
                await message.reply(`❌ u need ${item.price.toLocaleString()} coins! (u have ${balance.toLocaleString()})`);
                return;
            }
            
            if (!shopSystem.hasCapacity(userId, itemId, 1)) {
                const capacity = shopSystem.getCapacityStatus(userId);
                const isPet = item.category === 'pet';
                const status = isPet ? capacity.pet : capacity.item;
                await message.reply(`❌ your ${isPet ? 'pet' : 'bag'} slots are full (${status.used}/${status.capacity}). Buy slot upgrades first!`);
                return;
            }

            // Remove money
            await economy.removeMoney(userId, item.price);
            
            // Add item
            await shopSystem.addItem(userId, itemId, 1);
            
            await message.reply(`✅ purchased ${item.emoji} **${item.name}** for ${item.price.toLocaleString()} coins!`);
        }
    },

    inventory: {
        execute: async (message) => {
            const target = message.mentions.users.first() || message.author;
            const inventory = shopSystem.getUserInventory(target.id);
            const caps = shopSystem.getCapacityStatus(target.id);
            
            const embed = new EmbedBuilder()
                .setColor('#9B59B6')
                .setTitle(`🎒 ${target.username}'s Inventory`)
                .setTimestamp();
            
            // Show items
            const itemsList = [];
            for (const [itemId, quantity] of Object.entries(inventory.items)) {
                const item = shopSystem.getItemInfo(itemId);
                if (item) {
                    itemsList.push(`${item.emoji} **${item.name}** x${quantity}`);
                }
            }
            
            if (itemsList.length > 0) {
                embed.setDescription(itemsList.join('\n'));
            } else {
                embed.setDescription('*Empty inventory*');
            }
            
            // Show equipped items
            const equipped = [];
            for (const [category, itemId] of Object.entries(inventory.equipped)) {
                const item = shopSystem.getItemInfo(itemId);
                if (item) {
                    equipped.push(`${item.emoji} ${item.name}`);
                }
            }
            
            if (equipped.length > 0) {
                embed.addFields({ name: '✨ Equipped', value: equipped.join('\n'), inline: false });
            }
            
            const totalValue = shopSystem.getInventoryValue(target.id);
            embed.addFields(
                { name: '🎒 Bag Slots', value: `${caps.item.used}/${caps.item.capacity}`, inline: true },
                { name: '🐾 Pet Slots', value: `${caps.pet.used}/${caps.pet.capacity}`, inline: true }
            );
            embed.setFooter({ text: `Total Value: ${totalValue.toLocaleString()} coins` });
            
            await message.reply({ embeds: [embed] });
        }
    },

    inv: {
        execute: async (message, args, context) => {
            await shopCommands.inventory.execute(message, args, context);
        }
    },

    use: {
        execute: async (message, args) => {
            const userId = message.author.id;
            
            if (!args[0]) {
                await message.reply('usage: `use <item_id>`');
                return;
            }
            
            const itemId = args[0].toLowerCase();
            const result = await shopSystem.useItem(userId, itemId);
            
            if (result.success) {
                // Handle lootbox opening
                if (result.effect?.type === 'lootbox') {
                    const lootResult = await shopSystem.openLootbox(userId, itemId);
                    
                    if (lootResult.success) {
                        const rewardsList = lootResult.rewards
                            .map(r => `${r.emoji} ${r.name}`)
                            .join('\n');
                        
                        const embed = new EmbedBuilder()
                            .setColor('#FFD700')
                            .setTitle('🎁 Lootbox Opened!')
                            .setDescription(`**Rewards:**\n${rewardsList}`)
                            .setTimestamp();
                        
                        // Add coins from lootbox
                        const coinsReward = lootResult.rewards.find(r => r.type === 'coins');
                        if (coinsReward) {
                            await economy.addMoney(userId, coinsReward.amount);
                        }
                        
                        await message.reply({ embeds: [embed] });
                    } else {
                        await message.reply(lootResult.message);
                    }
                    return;
                }

                if (result.effect?.type === 'itemCapacity') {
                    const amount = typeof result.effect.effect === 'object' ? (result.effect.effect.amount || 0) : 0;
                    const status = await shopSystem.increaseCapacity(userId, 'itemCapacity', amount);
                    await message.reply(`🧳 Bag slots increased! (${status.item.used}/${status.item.capacity})`);
                    return;
                }

                if (result.effect?.type === 'petCapacity') {
                    const amount = typeof result.effect.effect === 'object' ? (result.effect.effect.amount || 0) : 0;
                    const status = await shopSystem.increaseCapacity(userId, 'petCapacity', amount);
                    await message.reply(`🐾 Pet slots increased! (${status.pet.used}/${status.pet.capacity})`);
                    return;
                }

                await message.reply(result.message);
            } else {
                await message.reply(result.message);
            }
        }
    },

    equip: {
        execute: async (message, args) => {
            const userId = message.author.id;
            
            if (!args[0]) {
                await message.reply('usage: `equip <item_id>`');
                return;
            }
            
            const itemId = args[0].toLowerCase();
            const result = await shopSystem.equipItem(userId, itemId);
            
            if (result.success) {
                await message.reply(result.message);
            } else {
                await message.reply(result.message);
            }
        }
    }
};
