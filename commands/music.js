import DistubeModule from "distube";
import SoundcloudModule from "@distube/soundcloud";
import { sanitizeForOutput } from "../src/util/sanitizeMentions.js";

const DisTubeClass = DistubeModule?.default ?? DistubeModule?.DisTube ?? DistubeModule;
const SoundCloudPluginClass = SoundcloudModule?.default ?? SoundcloudModule?.SoundCloudPlugin ?? SoundcloudModule;

export let distube = null;

export function setClient(client) {
  if (distube) {
    return distube;
  }

  distube = new DisTubeClass(client, {
    leaveOnEmpty: true,
    leaveOnFinish: false,
    leaveOnStop: true,
    emitNewSongOnly: true,
    searchSongs: 1,
    nsfw: false,
    plugins: [new SoundCloudPluginClass()]
  });

  distube.on("playSong", (queue, song) => {
    console.log(`Now playing: ${song.name} (${song.formattedDuration})`);
    if (queue.textChannel) {
      queue.textChannel.send({
        content: sanitizeForOutput(`Now playing: ${song.name} (${song.formattedDuration})`),
        allowedMentions: { parse: [] }
      }).catch(() => {});
    }
  });

  return distube;
}

export async function playMusic(voiceChannel, queryOrUrl, textChannel, member) {
  if (!voiceChannel) throw new Error("no voiceChannel");
  if (!distube) throw new Error("music system not initialized");
  try {
    await distube.play(voiceChannel, queryOrUrl, { member, textChannel });
  } catch (error) {
    if (!/^https?:\/\//i.test(queryOrUrl)) {
      await distube.play(voiceChannel, `search:${queryOrUrl}`, { member, textChannel });
      return;
    }
    throw error;
  }
}
