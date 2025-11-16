import DisTube from 'distube';
import { SoundCloudPlugin } from '@distube/soundcloud';

// This module expects the main file to call setClient(client) after client creation
let clientInstance = null;
export function setClient(client) {
  clientInstance = client;
}

export const distube = new DisTube.default(clientInstance, {
  leaveOnEmpty: true,
  leaveOnFinish: false,
  leaveOnStop: true,
  emitNewSongOnly: true,
  plugins: [new SoundCloudPlugin()],
  youtubeDL: false,
});

export async function playMusic(voiceChannel, queryOrUrl, textChannel, member) {
  if (!voiceChannel) throw new Error('No voice channel provided');
  try {
    await distube.play(voiceChannel, queryOrUrl, { member, textChannel });
  } catch (err) {
    if (!/^https?:\/\//i.test(queryOrUrl)) {
      try {
        await distube.play(voiceChannel, `search:${queryOrUrl}`, { member, textChannel });
        return;
      } catch (err2) {
        throw err;
      }
    } else {
      throw err;
    }
  }
}
