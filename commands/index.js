/**
 * Command Handler - Main setup
 */
import { PermissionsBitField } from 'discord.js';
import { economyCommands } from './economy.js';
import { casinoCommands } from './casino.js';
import { utilityCommands } from './utility.js';
import { shopCommands } from './shop.js';
import { marriageCommands } from './marriage.js';
import { prefixSystem } from '../systems/prefixSystem.js';
import { disableSystem } from '../systems/commandDisableSystem.js';
import { afkSystem } from '../systems/afkSystem.js';
import { wordChainSystem } from '../systems/wordChainSystem.js';

const MASS_MENTION_REGEX = /@(?:everyone|here)/i;

export function setupCommands(client, ownerIds) {
    // Combine all commands
    const allCommands = {
        ...economyCommands,
        ...casinoCommands,
        ...utilityCommands,
        ...shopCommands,
        ...marriageCommands
    };

    client.on('messageCreate', async (message) => {
        // Ultra-fast early returns for optimization
        if (message.author.bot) return;
        if (!message.content) return;
        if (!message.guild) return; // DMs not supported
        if (MASS_MENTION_REGEX.test(message.content)) return;

        // Handle AFK removal (only if user is AFK)
        if (afkSystem.isAFK(message.author.id)) {
            const duration = afkSystem.getAFKDuration(message.author.id);
            const afkData = await afkSystem.removeAFK(message.author.id);
            if (afkData) {
                message.reply(`welcome back! u were afk for ${duration}`).catch(() => {});
            }
        }

        // Check AFK mentions (only if there are mentions and limit to first 3)
        if (message.mentions.users.size > 0) {
            const mentionedUsers = Array.from(message.mentions.users.values()).slice(0, 3);
            for (const mentioned of mentionedUsers) {
                if (afkSystem.isAFK(mentioned.id)) {
                    const afkData = afkSystem.getAFK(mentioned.id);
                    const duration = afkSystem.getAFKDuration(mentioned.id);
                    message.reply(`**${mentioned.username}** is AFK: ${afkData.reason} (${duration})`).catch(() => {});
                    break; // Only reply once
                }
            }
        }

        // Word chain processing
        if (message.guild && wordChainSystem.isAutoChannel(message.channel.id)) {
            const content = message.content.trim();
            
            // Skip if it's a command
            const guildPrefix = prefixSystem.getPrefix(message.guild.id);
            if (content.startsWith(guildPrefix)) {
                return; // Let command handler process it
            }

            // Process word chain
            const words = content.split(/\s+/).filter(w => w.length >= 2);
            if (words.length > 0) {
                const word = words[0];
                const result = await wordChainSystem.processWord(
                    message.channel.id,
                    message.author.id,
                    word
                );

                if (result.success) {
                    await message.react('✅').catch(() => {});
                } else {
                    await message.react('❌').catch(() => {});
                }
            }
        }

        // Get prefix for this guild
        const prefix = message.guild ? prefixSystem.getPrefix(message.guild.id) : '!';
        
        // Check if message starts with prefix
        if (!message.content.startsWith(prefix)) return;

        // Parse command and args
        const args = message.content.slice(prefix.length).trim().split(/\s+/);
        const commandName = args.shift().toLowerCase();

        // Check if command is disabled in this channel
        if (message.guild && disableSystem.isDisabled(message.channel.id, commandName)) {
            return; // Silently ignore disabled commands
        }

        // Find and execute command
        const command = allCommands[commandName];
        if (!command) return;

        // Check if user is owner or moderator
        const isOwner = ownerIds.includes(message.author.id);
        const memberPerms = message.member?.permissions;
        const hasModPerms = isOwner
            || !!memberPerms?.has(PermissionsBitField.Flags.Administrator)
            || !!memberPerms?.has(PermissionsBitField.Flags.ManageGuild);

        // Check if command requires owner
        if (command.ownerOnly && !isOwner) {
            await message.reply('⛔ this command is owner only!');
            return;
        }

        if (command.modOnly && !hasModPerms) {
            await message.reply('⛔ u need Administrator or Manage Server permission!');
            return;
        }

        // Execute command
        try {
            await command.execute(message, args, { isOwner, prefix, ownerIds, hasModPerms });
        } catch (error) {
            console.error(`Error executing command ${commandName}:`, error);
            await message.reply('❌ an error occurred while executing this command!').catch(() => {});
        }
    });

    console.log(`✅ Loaded ${Object.keys(allCommands).length} commands`);
}
