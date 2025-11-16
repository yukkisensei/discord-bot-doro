import 'dotenv/config';
import { Client, GatewayIntentBits, Partials } from 'discord.js';
import dmProtection from './src/dmProtection.js';
import { sanitizeForOutput } from './src/util/sanitizeMentions.js';
import { setClient, distube } from './music.js';

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.DirectMessages,
    GatewayIntentBits.GuildVoiceStates,
  ],
  partials: [Partials.Channel, Partials.Message, Partials.GuildMember, Partials.User]
});

setClient(client); // connect distube client reference

// Example command/event loader placeholder - keep your existing loader if present
// loadCommands();
// loadEvents();

client.on('messageCreate', async (message) => {
  try {
    if (!message) return;
    if (message.author?.bot) return; // ignore bot messages

    // DM handling
    if (message.channel?.type === 1 /* DM */ || message.channel?.type === 'DM') {
      const res = dmProtection.recordDm(message.author.id);
      if (res.blocked) {
        if (res.newlyBlocked) {
          const modChan = client.channels.cache.find(c => c.name === 'bot-logs' && c.isTextBased());
          if (modChan) {
            modChan.send({
              content: `User <@${message.author.id}> auto-blocked for DM spam.`,
              allowedMentions: { parse: [] }
            }).catch(() => {});
          }
        }
        return; // ignore blocked user
      }

      const reply = sanitizeForOutput('Cảm ơn đã nhắn. Hỗ trợ sẽ trả lời sớm.');
      return message.channel.send({ content: reply, allowedMentions: { parse: [] } });
    }

    // If user is blocked globally, ignore messages (applies to guild messages too)
    if (dmProtection.isBlocked(message.author.id)) return;

    // Continue existing command handling logic here (do not remove)
  } catch (err) {
    console.error('messageCreate error:', err);
  }
});

client.on('interactionCreate', async (interaction) => {
  try {
    if (!interaction) return;
    const userId = interaction.user?.id;
    if (dmProtection.isBlocked(userId)) return;

    // existing slash/button/select handling here
  } catch (err) {
    console.error('interactionCreate error:', err);
  }
});

client.once('ready', () => {
  console.log(`Logged in as ${client.user?.tag}`);
});

client.login(process.env.TOKEN);
