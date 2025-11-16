import { Client, GatewayIntentBits, Partials } from "discord.js";
import dmProtection from "./src/dmProtection.js";
import { sanitizeForOutput } from "./src/util/sanitizeMentions.js";
import { setClient, distube } from "./music.js";
import dotenv from "dotenv";
dotenv.config();

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

client.on("messageCreate", async (message) => {
  try {
    if (!message) return;
    if (message.author?.bot) return;

    if (message.channel?.type === 1 || message.channel?.type === "DM") {
      const res = dmProtection.recordDm(message.author.id);
      if (res.blocked) return;
    }

    const clean = sanitizeForOutput(message.content);

    if (clean.startsWith("!play")) {
      const vc = message.member?.voice?.channel;
      if (!vc) return;
      const q = clean.replace("!play", "").trim();
      await distube.play(vc, q, { member: message.member, textChannel: message.channel });
      return;
    }

    if (clean.startsWith("!stop")) {
      await distube.stop(message);
      return;
    }

    if (clean.startsWith("!skip")) {
      await distube.skip(message);
      return;
    }

  } catch {}
});

client.on("interactionCreate", async (i) => {
  try {
    if (!i) return;

    if (i.isChatInputCommand()) {
      if (i.commandName === "play") {
        const vc = i.member?.voice?.channel;
        if (!vc) return;
        const q = i.options.getString("query");
        await distube.play(vc, q, { member: i.member, textChannel: i.channel });
        await i.reply("Playing.");
      }
    }
  } catch {}
});

client.login(process.env.DISCORD_BOT_TOKEN);
