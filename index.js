import 'dotenv/config';
import { Client, GatewayIntentBits, Partials } from 'discord.js';
import dmProtection from './src/dmProtection.js';
import { sanitizeForOutput } from './src/util/sanitizeMentions.js';
import { setClient } from './commands/music.js';
import { setupCommands } from './commands/index.js';
import { prefixSystem } from './systems/prefixSystem.js';
import { economy } from './systems/economySystem.js';
import { shopSystem } from './systems/shopSystem.js';
import { marriageSystem } from './systems/marriageSystem.js';
import { afkSystem } from './systems/afkSystem.js';
import { languageSystem } from './systems/languageSystem.js';
import { disableSystem } from './systems/commandDisableSystem.js';
import { muteSystem } from './systems/muteSystem.js';
import { wordChainSystem } from './systems/wordChainSystem.js';
import { aiSystem } from './systems/aiSystem.js';
import fetch from 'node-fetch';

const WEBHOOK = process.env.DISCORD_WEBHOOK_URL || '';
const MASS_MENTION_REGEX = /@(?:everyone|here)/i;
const OWNER_IDS = (process.env.BOT_OWNER_IDS || '')
  .split(',')
  .map((id) => id.trim())
  .filter(Boolean);

economy.ownerIds = OWNER_IDS;
aiSystem.ownerIds = OWNER_IDS;
marriageSystem.ownerIds = OWNER_IDS;

async function initSystems() {
  await Promise.all([
    prefixSystem.init(),
    economy.init(),
    shopSystem.init(),
    marriageSystem.init(),
    afkSystem.init(),
    languageSystem.init(),
    disableSystem.init(),
    muteSystem.init(),
    wordChainSystem.init(),
    aiSystem.init()
  ]);
}

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.DirectMessages,
    GatewayIntentBits.GuildVoiceStates
  ],
  partials: [
    Partials.Channel,
    Partials.Message,
    Partials.GuildMember,
    Partials.User
  ],
  allowedMentions: {
    parse: [],
    repliedUser: false
  }
});

const music = setClient(client);

async function sendWebhook(content) {
  try {
    if (!WEBHOOK) return;
    await fetch(WEBHOOK, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content })
    });
  } catch (e) {
    console.error('webhook error', e);
  }
}

client.once('clientReady', async () => {
  try {
    const msg = `Bot ready: ${client.user?.tag || 'unknown'}`;
    console.log(msg);
    await sendWebhook(msg);
  } catch (e) {
    console.error(e);
  }
});

client.on('error', (err) => {
  console.error('client error', err);
});

process.on('unhandledRejection', async (reason) => {
  try {
    console.error('unhandledRejection', reason);
    await sendWebhook('UnhandledRejection: ' + String(reason));
    process.exit(1);
  } catch {
    process.exit(1);
  }
});

process.on('uncaughtException', async (err) => {
  try {
    console.error('uncaughtException', err);
    await sendWebhook('UncaughtException: ' + String(err));
    process.exit(1);
  } catch {
    process.exit(1);
  }
});

music.on('error', async (channel, err) => {
  try {
    console.error('distube error', err);
    await sendWebhook('Distube error: ' + String(err));
  } catch {}
});

client.on('messageCreate', async (message) => {
  try {
    if (!message) return;
    if (message.author?.bot) return;

    if (message.channel?.type === 1 || message.channel?.type === 'DM') {
      const res = dmProtection.recordDm(message.author.id);
      if (res.blocked) return;
    }

    const rawContent = message.content ?? '';
    const content = rawContent.trim();
    if (!content) return;
    if (MASS_MENTION_REGEX.test(content)) {
      return;
    }
    if (!content.startsWith('!')) return;

    const normalized = content.toLowerCase();
    const clean = sanitizeForOutput(content);

    if (normalized.startsWith('!play')) {
      const vc = message.member?.voice?.channel;
      if (!vc) {
        return message.channel.send({ content: 'Join a voice channel first.', allowedMentions: { parse: [] } }).catch(()=>{});
      }
      const q = clean.slice('!play'.length).trim();
      if (!q) {
        return message.channel.send({ content: 'Please provide a song name or link.', allowedMentions: { parse: [] } }).catch(()=>{});
      }
      await music.play(vc, q, { member: message.member, textChannel: message.channel });
      return;
    }

    if (normalized.startsWith('!stop')) {
      try {
        await music.stop(message);
        return;
      } catch (e) {
        console.error(e);
        return;
      }
    }

    if (normalized.startsWith('!skip')) {
      try {
        await music.skip(message);
        return;
      } catch (e) {
        console.error(e);
        return;
      }
    }

  } catch (err) {
    console.error('messageCreate handler error', err);
  }
});

client.on('interactionCreate', async (interaction) => {
  try {
    if (!interaction) return;
    const userId = interaction.user?.id;
    if (dmProtection.isBlocked(userId)) return;
    if (interaction.isChatInputCommand()) {
      if (interaction.commandName === 'play') {
        const vc = interaction.member?.voice?.channel;
        if (!vc) {
          return interaction.reply({ content: 'Join a voice channel first.', ephemeral: true, allowedMentions: { parse: [] } });
        }
        const q = interaction.options.getString('query');
        await music.play(vc, q, { member: interaction.member, textChannel: interaction.channel });
        await interaction.reply({ content: 'Playing.', ephemeral: true, allowedMentions: { parse: [] } });
      }
    }
  } catch (e) {
    console.error('interaction handler error', e);
  }
});

(async () => {
  try {
    if (!process.env.DISCORD_BOT_TOKEN) {
      console.error('DISCORD_BOT_TOKEN not set');
      await sendWebhook('DISCORD_BOT_TOKEN not set');
      process.exit(1);
    }

    await initSystems();
    setupCommands(client, OWNER_IDS);

    await client.login(process.env.DISCORD_BOT_TOKEN);
  } catch (e) {
    console.error('login error', e);
    await sendWebhook('Login error: ' + String(e));
    process.exit(1);
  }
})();
