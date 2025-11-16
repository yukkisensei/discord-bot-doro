/**
 * Marriage Commands - Marry, accept, divorce
 */
import { EmbedBuilder } from 'discord.js';
import { marriageSystem } from '../systems/marriageSystem.js';
import { shopSystem } from '../systems/shopSystem.js';

// Store pending proposals
const pendingProposals = new Map();

export const marriageCommands = {
    marry: {
        execute: async (message, args, context) => {
            const proposer = message.author;
            const target = message.mentions.users.first();
            
            if (!target) {
                await message.reply('usage: `marry @user`');
                return;
            }
            
            if (target.id === proposer.id) {
                await message.reply('❌ u cant marry urself!');
                return;
            }
            
            if (target.bot) {
                await message.reply('❌ u cant marry bots!');
                return;
            }
            
            // Check if user has a ring
            const rings = ['ring_love', 'ring_couple', 'ring_mandarin', 'ring_eternal', 'ring_destiny'];
            let hasRing = false;
            let ringUsed = null;
            
            for (const ring of rings) {
                if (shopSystem.hasItem(proposer.id, ring)) {
                    hasRing = true;
                    ringUsed = ring;
                    break;
                }
            }
            
            if (!hasRing && !context.isOwner) {
                await message.reply('❌ u need a ring to propose! buy one from the shop!');
                return;
            }
            
            // Check if can propose
            const proposeResult = marriageSystem.propose(proposer.id, target.id, context.isOwner);
            if (!proposeResult.success) {
                await message.reply(proposeResult.message);
                return;
            }
            
            // Create proposal
            pendingProposals.set(target.id, {
                proposerId: proposer.id,
                targetId: target.id,
                ringId: ringUsed,
                timestamp: Date.now(),
                isOwner: context.isOwner
            });
            
            // Auto-expire after 2 minutes
            setTimeout(() => {
                if (pendingProposals.has(target.id)) {
                    pendingProposals.delete(target.id);
                }
            }, 120000);
            
            const embed = new EmbedBuilder()
                .setColor('#FF69B4')
                .setTitle('💍 Marriage Proposal!')
                .setDescription(`${proposer} proposed to ${target}!`)
                .addFields(
                    { name: 'Ring', value: ringUsed ? shopSystem.getItemInfo(ringUsed).name : 'Owner bypass', inline: true },
                    { name: 'Status', value: 'Waiting for response...', inline: true }
                )
                .setFooter({ text: `${target.username}, use !accept or !reject` })
                .setTimestamp();
            
            await message.reply({ embeds: [embed] });
        }
    },

    accept: {
        execute: async (message) => {
            const userId = message.author.id;
            
            if (!pendingProposals.has(userId)) {
                await message.reply('❌ u dont have any pending proposals!');
                return;
            }
            
            const proposal = pendingProposals.get(userId);
            pendingProposals.delete(userId);
            
            // Remove ring if not owner
            if (proposal.ringId && !proposal.isOwner) {
                await shopSystem.removeItem(proposal.proposerId, proposal.ringId, 1);
            }
            
            // Create marriage
            const result = await marriageSystem.marry(
                proposal.proposerId,
                proposal.targetId,
                proposal.ringId,
                proposal.isOwner
            );
            
            const proposer = await message.client.users.fetch(proposal.proposerId);
            
            const embed = new EmbedBuilder()
                .setColor('#00FF00')
                .setTitle('💑 Married!')
                .setDescription(`${proposer} and ${message.author} are now married! 💍`)
                .setTimestamp();
            
            if (result.autoDivorced) {
                embed.setFooter({ text: 'Previous partner was auto-divorced' });
            }
            
            await message.reply({ embeds: [embed] });
        }
    },

    reject: {
        execute: async (message) => {
            const userId = message.author.id;
            
            if (!pendingProposals.has(userId)) {
                await message.reply('❌ u dont have any pending proposals!');
                return;
            }
            
            const proposal = pendingProposals.get(userId);
            pendingProposals.delete(userId);
            
            const proposer = await message.client.users.fetch(proposal.proposerId);
            
            await message.reply(`💔 ${message.author} rejected ${proposer}'s proposal!`);
        }
    },

    divorce: {
        execute: async (message) => {
            const userId = message.author.id;
            
            const result = await marriageSystem.divorce(userId);
            
            if (result.success) {
                await message.reply(result.message);
            } else {
                await message.reply(result.message);
            }
        }
    },

    marriage: {
        execute: async (message) => {
            const target = message.mentions.users.first() || message.author;
            const marriageInfo = marriageSystem.getMarriageInfo(target.id);
            
            if (!marriageInfo) {
                await message.reply(`${target.username} is not married!`);
                return;
            }
            
            const partner = await message.client.users.fetch(marriageInfo.partner);
            const marriedDate = new Date(marriageInfo.marriedAt);
            const duration = Date.now() - marriedDate.getTime();
            const days = Math.floor(duration / (1000 * 60 * 60 * 24));
            
            const ring = marriageInfo.ringUsed ? shopSystem.getItemInfo(marriageInfo.ringUsed) : null;
            
            const embed = new EmbedBuilder()
                .setColor('#FF69B4')
                .setTitle('💑 Marriage Info')
                .addFields(
                    { name: 'Partner', value: partner.username, inline: true },
                    { name: 'Married Since', value: `${days} days ago`, inline: true }
                )
                .setTimestamp(marriedDate);
            
            if (ring) {
                embed.addFields({ name: 'Ring', value: `${ring.emoji} ${ring.name}`, inline: true });
            }
            
            await message.reply({ embeds: [embed] });
        }
    }
};
