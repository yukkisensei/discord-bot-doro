import 'dotenv/config';
import { Client, GatewayIntentBits, Partials } from 'discord.js';
import dmProtection from './src/dmProtection.js';
import { sanitizeForOutput } from './src/util/sanitizeMentions.js';
import { setClient, distube } from './music.js';
import fetch from 'node-fetch';

const WEBHOOK = process.env.DISCORD_WEBHOOK_URL || '';

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
  ]
});

setClient(client);

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

client.once('ready', async () => {
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

distube.on('error', async (channel, err) => {
  try {
    console.error('distube error', err);
    await sendWebhook('Distube error: ' + String(err));
  } catch {}
});

distube.on('playSong', async (queue, song) => {
  try {
    const text = `Now playing: ${song.name} (${song.formattedDuration})`;
    console.log(text);
    if (queue.textChannel) {
      queue.textChannel.send({ content: sanitizeForOutput(text), allowedMentions: { parse: [] } }).catch(()=>{});
    }
  } catch (e) {
    console.error(e);
  }
});

client.on('messageCreate', async (message) => {
  try {
    if (!message) return;
    if (message.author?.bot) return;

    if (message.channel?.type === 1 || message.channel?.type === 'DM') {
      const res = dmProtection.recordDm(message.author.id);
      if (res.blocked) return;
    }

    const clean = sanitizeForOutput(message.content || '');

    if (clean.startsWith('!play')) {
      const vc = message.member?.voice?.channel;
      if (!vc) {
        return message.channel.send({ content: 'Join a voice channel first.', allowedMentions: { parse: [] } }).catch(()=>{});
      }
      const q = clean.replace('!play', '').trim();
      await distube.play(vc, q, { member: message.member, textChannel: message.channel });
      return;
    }

    if (clean.startsWith('!stop')) {
      try {
        await distube.stop(message);
        return;
      } catch (e) {
        console.error(e);
        return;
      }
    }

    if (clean.startsWith('!skip')) {
      try {
        await distube.skip(message);
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
        await distube.play(vc, q, { member: interaction.member, textChannel: interaction.channel });
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
    await client.login(process.env.DISCORD_BOT_TOKEN);
  } catch (e) {
    console.error('login error', e);
    await sendWebhook('Login error: ' + String(e));
    process.exit(1);
  }
})();
