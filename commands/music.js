import DisTube from "distube";
import { SoundCloudPlugin } from "@distube/soundcloud";

let clientRef = null;

export function setClient(c) {
  clientRef = c;
}

export const distube = new DisTube(clientRef, {
  leaveOnEmpty: true,
  leaveOnFinish: false,
  leaveOnStop: true,
  emitNewSongOnly: true,
  searchSongs: 1,
  nsfw: false,
  youtubeDL: false,
  plugins: [new SoundCloudPlugin()]
});

distube.on("playSong", (queue, song) => {
  if (queue.textChannel) {
    queue.textChannel.send({
      content: `Now playing: ${song.name} (${song.formattedDuration})`,
      allowedMentions: { parse: [] }
    }).catch(() => {});
  }
});

export async function playMusic(voiceChannel, queryOrUrl, textChannel, member) {
  if (!voiceChannel) throw new Error("no voiceChannel");
  try {
    await distube.play(voiceChannel, queryOrUrl, { member, textChannel });
  } catch {
    if (!/^https?:\/\//i.test(queryOrUrl)) {
      await distube.play(voiceChannel, `search:${queryOrUrl}`, { member, textChannel });
      return;
    }
    throw err;
  }
}
