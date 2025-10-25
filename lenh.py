import asyncio
import logging
import os
import re
import shutil
import urllib.parse
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Deque, Dict, Optional

import discord
from discord.ext import commands
import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError

import ai
from economy import economy
from afk_system import afk_system
from command_disable import disable_system
from profile_card import profile_card_generator
from shop_system import shop_system
from marriage_system import marriage_system
from help_system import build_help_embed
from prefix_system import prefix_system
from mute_system import mute_system


# Load owner IDs from env - defaults to your ID if not set
default_owner = "1344312732278591500"  # your discord ID
BOT_OWNER_IDS = os.getenv("BOT_OWNER_IDS", default_owner)
OWNER_IDS = [int(x) for x in BOT_OWNER_IDS.split(",") if x.strip().isdigit()]

# debug print to check
if not OWNER_IDS:
    print("⚠️ WARNING: No owner IDs loaded! Using default.")
    OWNER_IDS = [int(default_owner)]

YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
    "default_search": "scsearch1",
    "source_address": "0.0.0.0",
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

_FFMPEG_EXEC: Optional[str] = None
_FFMPEG_HINTS = [
    r"C:\\ffmpeg\\bin\\ffmpeg.exe",
    r"C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
    r"C:\\Program Files (x86)\\ffmpeg\\bin\\ffmpeg.exe",
]


def resolve_ffmpeg_path() -> Optional[str]:
    global _FFMPEG_EXEC

    if _FFMPEG_EXEC and os.path.exists(_FFMPEG_EXEC):
        return _FFMPEG_EXEC

    candidates = []
    env_path = os.getenv("FFMPEG_PATH")
    if env_path:
        cleaned = env_path.strip().strip('"')
        if cleaned:
            candidates.append(cleaned)

    for name in ("ffmpeg", "ffmpeg.exe"):
        found = shutil.which(name)
        if found:
            candidates.append(found)

    candidates.extend(hint for hint in _FFMPEG_HINTS if os.path.exists(hint))

    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            _FFMPEG_EXEC = candidate
            return _FFMPEG_EXEC

    _FFMPEG_EXEC = None
    return None


@dataclass
class MusicTrack:
    title: str
    stream_url: str
    webpage_url: str


@dataclass
class MusicState:
    queue: Deque[MusicTrack] = field(default_factory=deque)
    voice_client: Optional[discord.VoiceClient] = None
    now_playing: Optional[MusicTrack] = None
    stay_mode: bool = False
    text_channel: Optional[discord.abc.Messageable] = None
    auto_leave_task: Optional[asyncio.Task] = None
    loop_mode: str = "off"  # "off", "one", "all"
    volume: float = 1.0
    play_history: Deque[MusicTrack] = field(default_factory=lambda: deque(maxlen=50))


def setup(bot_instance: commands.Bot) -> None:
    global bot
    bot = bot_instance
    
    # Set owner IDs for marriage system
    marriage_system.owner_ids = OWNER_IDS
    
    # Set owner IDs for economy system - CRITICAL for auto-infinity
    economy.owner_ids = OWNER_IDS
    
    # Add check for disabled commands
    @bot.check
    async def check_command_disabled(ctx: commands.Context):
        # Skip check for DMs
        if not ctx.guild:
            return True
        
        # Skip check for owners
        if ctx.author.id in OWNER_IDS:
            return True
        
        # Check if command is disabled in this channel
        channel_id = str(ctx.channel.id)
        command_name = ctx.command.name if ctx.command else None
        
        if command_name and disable_system.is_disabled(channel_id, command_name):
            # Silently ignore - don't respond
            return False
        
        return True

    music_states: Dict[int, MusicState] = {}

    def get_state(guild_id: int) -> MusicState:
        state = music_states.get(guild_id)
        if state is None:
            state = MusicState()
            music_states[guild_id] = state
        return state

    def cancel_auto_leave(state: MusicState) -> None:
        if state.auto_leave_task and not state.auto_leave_task.done():
            state.auto_leave_task.cancel()
        state.auto_leave_task = None

    def schedule_auto_leave(guild_id: int) -> None:
        state = music_states.get(guild_id)
        if not state:
            return
        cancel_auto_leave(state)

        async def _delayed_leave() -> None:
            try:
                await asyncio.sleep(120)
            except asyncio.CancelledError:
                return

            state_after = music_states.get(guild_id)
            if not state_after:
                return
            if state_after.stay_mode:
                state_after.auto_leave_task = None
                return

            voice_client_after = state_after.voice_client
            if not voice_client_after or state_after.queue or state_after.now_playing:
                state_after.auto_leave_task = None
                return

            if not voice_client_after.is_connected():
                state_after.auto_leave_task = None
                return

            try:
                await voice_client_after.disconnect()
            except discord.HTTPException:
                logging.warning("couldnt disconnect voice client at guild %s", guild_id)
            else:
                state_after.voice_client = None
                state_after.now_playing = None
                if state_after.text_channel:
                    await state_after.text_channel.send("no ones here so im leaving!")
            state_after.auto_leave_task = None

        state.auto_leave_task = bot.loop.create_task(_delayed_leave())

    async def ensure_voice(ctx: commands.Context) -> Optional[discord.VoiceClient]:
        if ctx.guild is None:
            await ctx.reply("this command only works in servers!", mention_author=False)
            return None
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.reply("join a voice channel first!", mention_author=False)
            return None

        channel = ctx.author.voice.channel
        voice_client = ctx.voice_client

        try:
            if voice_client:
                if voice_client.channel != channel:
                    await voice_client.move_to(channel)
            else:
                voice_client = await channel.connect()
        except discord.Forbidden:
            await ctx.reply("dont have permission to join that voice channel!", mention_author=False)
            return None
        except discord.HTTPException:
            await ctx.reply("discord is laggy, try again!", mention_author=False)
            return None

        state = get_state(ctx.guild.id)
        state.voice_client = voice_client
        state.text_channel = ctx.channel
        cancel_auto_leave(state)
        return voice_client

    async def extract_track(query: str) -> MusicTrack:
        raw_query = query.strip()
        if not raw_query:
            raise ValueError("missing search query")

        search = raw_query
        # Decode repeatedly to eliminate nested percent-encoding from embeds/API urls
        while True:
            decoded = urllib.parse.unquote(search)
            if decoded == search:
                break
            search = decoded

        track_id: Optional[str] = None

        match = re.search(r"(?:soundcloud:)?tracks?:(\d+)", search)
        if match:
            track_id = match.group(1)
        elif search.startswith("https://api.soundcloud.com/tracks/"):
            tail = search.rsplit("/", 1)[-1]
            if tail.isdigit():
                track_id = tail

        candidates: list[str] = []

        def add_candidate(value: Optional[str]) -> None:
            if value and value not in candidates:
                candidates.append(value)

        if track_id:
            add_candidate(f"https://api.soundcloud.com/tracks/{track_id}")
            add_candidate(f"scsearch1:{track_id}")
            add_candidate(f"scsearch1:soundcloud track {track_id}")
        else:
            if search.startswith(("http://", "https://")):
                add_candidate(search)
            else:
                add_candidate(f"scsearch1:{search}")

        logging.debug("SoundCloud candidates for '%s': %s", raw_query, candidates)

        loop = asyncio.get_event_loop()

        def _parse_id_from_error(error: Exception) -> Optional[str]:
            message = str(getattr(error, "msg", None) or error)
            match = re.search(r"soundcloud%3Atracks%3A(\d+)", message)
            if match:
                return match.group(1)
            return None

        def _add_retry_candidates(track_num: str) -> None:
            add_candidate(f"https://api.soundcloud.com/tracks/{track_num}")
            add_candidate(f"scsearch1:{track_num}")
            add_candidate(f"scsearch1:soundcloud track {track_num}")

        def _resolve_entry(entry: Dict) -> Optional[Dict]:
            if not entry:
                return None

            entry_url = entry.get("url")
            entry_id = entry.get("id")

            candidates_to_try: list[str] = []

            if entry_id and str(entry_id).isdigit():
                candidates_to_try.append(f"https://api.soundcloud.com/tracks/{entry_id}")

            if entry_url:
                decoded_entry_url = urllib.parse.unquote(entry_url)
                match = re.search(r"(?:soundcloud:)?tracks?:(\d+)", decoded_entry_url)
                if match:
                    candidates_to_try.append(f"https://api.soundcloud.com/tracks/{match.group(1)}")
                if entry_url.startswith(("http://", "https://")):
                    candidates_to_try.append(entry_url)

            for candidate_url in candidates_to_try:
                try:
                    return ytdl.extract_info(candidate_url, download=False)
                except (DownloadError, ExtractorError):
                    continue

            # if entry already has formats, return it for further processing
            if entry.get("formats"):
                return entry

            return None

        def _extract():
            attempted: set[str] = set()
            queue: Deque[str] = deque(candidates)
            last_error: Optional[Exception] = None

            while queue:
                candidate = queue.popleft()
                if candidate in attempted:
                    continue
                attempted.add(candidate)

                logging.debug("Trying SoundCloud candidate: %s", candidate)
                try:
                    info = ytdl.extract_info(candidate, download=False)
                except (DownloadError, ExtractorError) as exc:
                    last_error = exc
                    new_id = _parse_id_from_error(exc)
                    if new_id:
                        _add_retry_candidates(new_id)
                        for extra_candidate in list(candidates):
                            if extra_candidate not in attempted:
                                queue.append(extra_candidate)
                    continue

                if "entries" in info:
                    for entry in info["entries"]:
                        resolved = _resolve_entry(entry)
                        if resolved:
                            return resolved
                    continue

                return info

            if last_error is not None:
                raise last_error

            raise ValueError("no valid SoundCloud results found")

        try:
            info = await loop.run_in_executor(None, _extract)
        except (DownloadError, ExtractorError) as exc:
            raise ValueError(str(exc)) from exc

        stream_url: Optional[str] = info.get("url")

        if not stream_url or stream_url.startswith("soundcloud:"):
            formats = info.get("formats") or []
            # prioritize progressive audio for easier FFMPEG playback
            def sort_key(fmt: Dict) -> int:
                proto = fmt.get("protocol") or ""
                preference = fmt.get("preference", 0)
                # prioritize http > hls > others
                proto_score = {
                    "http": 3,
                    "https": 3,
                    "progressive": 3,
                    "hls": 2,
                    "m3u8": 2,
                    "m3u8_native": 2,
                }.get(proto, 1)
                return (preference, proto_score, fmt.get("abr") or 0)

            if not formats:
                raise ValueError("no valid SoundCloud stream found for this track")

            best = max(formats, key=sort_key)
            stream_url = best.get("url")

        if not stream_url or stream_url.startswith("soundcloud:"):
            raise ValueError("couldnt get valid SoundCloud stream after trying multiple formats")

        title = info.get("title", "SoundCloud track")
        webpage_url = info.get("webpage_url") or info.get("original_url") or search
        return MusicTrack(title=title, stream_url=stream_url, webpage_url=webpage_url)

    async def play_next(guild_id: int) -> None:
        state = music_states.get(guild_id)
        voice_client = state.voice_client if state else None
        if not state or not voice_client:
            return

        cancel_auto_leave(state)

        # Handle loop mode
        if state.loop_mode == "one" and state.now_playing:
            track = state.now_playing
        elif not state.queue:
            if state.loop_mode == "all" and state.play_history:
                # Reload queue from history
                state.queue = deque(state.play_history)
                track = state.queue.popleft()
            else:
                state.now_playing = None
                if not state.stay_mode and voice_client.is_connected():
                    schedule_auto_leave(guild_id)
                return
        else:
            track = state.queue.popleft()

        # Add to history if not looping one song
        if state.loop_mode != "one":
            state.play_history.append(track)
        
        state.now_playing = track

        ffmpeg_exec = resolve_ffmpeg_path()
        if not ffmpeg_exec:
            logging.error("FFmpeg not found when playing at guild %s", guild_id)
            state.queue.appendleft(track)
            if state.text_channel:
                await state.text_channel.send(
                    "FFmpeg not found. install it or set `FFMPEG_PATH` environment variable!"
                )
            return

        def after_play(error: Optional[Exception]) -> None:
            asyncio.run_coroutine_threadsafe(handle_after(guild_id, error), bot.loop)

        source = discord.FFmpegPCMAudio(track.stream_url, executable=ffmpeg_exec, **FFMPEG_OPTIONS)
        # Apply volume
        source = discord.PCMVolumeTransformer(source, volume=state.volume)
        
        try:
            voice_client.play(source, after=after_play)
        except discord.ClientException as exc:
            logging.error("cant play at guild %s: %s", guild_id, exc)
            state.queue.appendleft(track)
            return

        if state.text_channel:
            loop_emoji = ""
            if state.loop_mode == "one":
                loop_emoji = " 🔂"
            elif state.loop_mode == "all":
                loop_emoji = " 🔁"
            await state.text_channel.send(f"now playing **{track.title}** 🎶{loop_emoji} ({track.webpage_url})")

    async def handle_after(guild_id: int, error: Optional[Exception]) -> None:
        state = music_states.get(guild_id)
        if state:
            state.now_playing = None
        if error:
            logging.error("Playback error at guild %s: %s", guild_id, error)
        await play_next(guild_id)

    @bot.command(name="say", aliases=["speak"], help="doro says something for u | add -r <msg_id> to react to a message")
    async def say(ctx: commands.Context, *, message: str) -> None:
        if ctx.author.id not in OWNER_IDS:
            await ctx.reply("owner only!", mention_author=False)
            return
        
        # Check for reaction mode (-r <message_id> <reactions>)
        import re
        reaction_match = re.match(r'^-r\s+(\d+)\s+(.+)$', message)
        
        if reaction_match:
            # Reaction mode
            msg_id = int(reaction_match.group(1))
            reactions_text = reaction_match.group(2)
            
            try:
                # Find message in current channel
                target_msg = await ctx.channel.fetch_message(msg_id)
                
                # Parse reactions (split by space, handle both emoji and :emoji_name:)
                reactions = reactions_text.split()
                
                for reaction in reactions:
                    try:
                        # Add each reaction
                        await target_msg.add_reaction(reaction)
                    except discord.HTTPException:
                        # Try to find custom emoji if standard fails
                        if reaction.startswith(':') and reaction.endswith(':'):
                            emoji_name = reaction[1:-1]
                            # Search in guild emojis
                            for emoji in ctx.guild.emojis:
                                if emoji.name.lower() == emoji_name.lower():
                                    await target_msg.add_reaction(emoji)
                                    break
                
                # Delete command message
                try:
                    await ctx.message.delete()
                except discord.Forbidden:
                    pass
                    
            except discord.NotFound:
                await ctx.reply(f"message {msg_id} not found in this channel!", mention_author=False)
            except Exception as e:
                await ctx.reply(f"error: {e}", mention_author=False)
        else:
            # Normal say mode
            try:
                await ctx.message.delete()
            except discord.Forbidden:
                pass
            
            await ctx.send(message)

    @bot.command(name="sync", help="sync slash commands (owner)")
    async def sync_commands(ctx: commands.Context) -> None:
        if ctx.author.id not in OWNER_IDS:
            await ctx.reply("owner only!", mention_author=False)
        
        try:
            synced = await bot.tree.sync()
            await ctx.reply(f"✅ synced {len(synced)} slash commands!", mention_author=False)
        except Exception as e:
            await ctx.reply(f"❌ sync error: {e}", mention_author=False)
    
    @bot.command(name="model", help="view/change AI model (owner)")
    async def model_cmd(ctx: commands.Context, *, model_name: str = None) -> None:
        if ctx.author.id not in OWNER_IDS:
            await ctx.reply("owner only!", mention_author=False)
        
        if model_name is None:
            # Show current model
            await ctx.reply(f"🤖 current model: `{ai.current_model}`", mention_author=False)
        else:
            # Change model
            ai.current_model = model_name
            await ctx.reply(f"✅ changed model to: `{model_name}`", mention_author=False)
    
    @bot.command(name="testpersonality", help="test personality consistency (owner)")
    async def testpersonality_cmd(ctx: commands.Context) -> None:
        if ctx.author.id not in OWNER_IDS:
            await ctx.reply("owner only!", mention_author=False)
        
        is_owner = ctx.author.id in OWNER_IDS
        prompt = ai.build_system_prompt(is_owner)
        
        embed = discord.Embed(
            title="🎭 personality test",
            description=f"**is owner:** {is_owner}",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="system prompt",
            value=f"```\n{prompt[:1000]}...\n```" if len(prompt) > 1000 else f"```\n{prompt}\n```",
            inline=False
        )
        
        if is_owner:
            embed.add_field(
                name="✅ expected",
                value="casual english, sweet & loving",
                inline=False
            )
        else:
            embed.add_field(
                name="✅ expected",
                value="casual english, friendly (not romantic)",
                inline=False
            )
        
        await ctx.reply(embed=embed, mention_author=False)

    @bot.command(name="ping", help="check bot latency (prefix)")
    async def ping_prefix(ctx: commands.Context) -> None:
        if ctx.author.id not in OWNER_IDS:
            await ctx.reply("owner only!", mention_author=False)
        latency_ms = ctx.bot.latency * 1000
        await ctx.reply(f"pong~ `{latency_ms:.0f}ms`", mention_author=False)

    @bot.command(name="help", help="view command list")
    async def help_prefix(ctx: commands.Context, category: str = None) -> None:
        guild_id = str(ctx.guild.id) if ctx.guild else None
        current_prefix = prefix_system.get_prefix(guild_id) if guild_id else "!"
        await ctx.reply(embed=build_help_embed(category, bot, current_prefix), mention_author=False)

    @bot.tree.command(name="help", description="view doro's command list")
    async def help_slash(interaction: discord.Interaction) -> None:
        guild_id = str(interaction.guild_id) if interaction.guild_id else None
        current_prefix = prefix_system.get_prefix(guild_id) if guild_id else "!"
        await interaction.response.send_message(embed=build_help_embed(None, bot, current_prefix), ephemeral=True)

    @bot.command(name="play", aliases=["p"], help="play music or add to queue")
    async def play(ctx: commands.Context, *, query: str) -> None:
        voice_client = await ensure_voice(ctx)
        if voice_client is None:
            return

        try:
            track = await extract_track(query)
        except ValueError as exc:
            logging.exception("failed to get track info: %s", exc)
            return await ctx.reply("couldnt find that track, try different keywords!", mention_author=False)

        state = get_state(ctx.guild.id)
        state.queue.append(track)
        state.text_channel = ctx.channel
        cancel_auto_leave(state)

        if voice_client.is_playing() or voice_client.is_paused():
            await ctx.reply(f"added **{track.title}** to queue ❤️", mention_author=False)
        else:
            await play_next(ctx.guild.id)

    @bot.command(name="skip", aliases=["s"], help="skip current track")
    async def skip(ctx: commands.Context) -> None:
        state = music_states.get(ctx.guild.id)
        voice_client = ctx.voice_client
        if not state or not voice_client or not voice_client.is_connected():
            return await ctx.reply("nothing is playing rn!", mention_author=False)

        if not voice_client.is_playing():
            return await ctx.reply("nothing is playing to skip!", mention_author=False)

        voice_client.stop()
        await ctx.reply("skipped!", mention_author=False)

    @bot.command(name="queue", aliases=["q"], help="view queue")
    async def queue_cmd(ctx: commands.Context) -> None:
        state = music_states.get(ctx.guild.id)
        if not state or (not state.queue and not state.now_playing):
            return await ctx.reply("queue is empty!", mention_author=False)
        
        entries = []
        if state.now_playing:
            entries.append(f"**now playing:** {state.now_playing.title}")
        
        for idx, track in enumerate(state.queue, start=1):
            entries.append(f"{idx}. {track.title}")
        
        text = "\n".join(entries[:15])
        if len(entries) > 15:
            text += f"\n... and {len(entries) - 15} more tracks"

        await ctx.reply(text, mention_author=False)

    @bot.command(name="pause", help="pause music")
    async def pause(ctx: commands.Context) -> None:
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_playing():
            return await ctx.reply("nothing is playing to pause!", mention_author=False)

        voice_client.pause()
        await ctx.reply("paused!", mention_author=False)

    @bot.command(name="resume", help="resume music")
    async def resume(ctx: commands.Context) -> None:
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_paused():
            return await ctx.reply("nothing is paused to resume!", mention_author=False)

        voice_client.resume()
        await ctx.reply("resumed!", mention_author=False)

    @bot.command(name="stop", help="stop music and clear queue")
    async def stop(ctx: commands.Context) -> None:
        state = music_states.get(ctx.guild.id)
        voice_client = ctx.voice_client
        if state:
            state.queue.clear()
            state.now_playing = None

        if voice_client and voice_client.is_playing():
            voice_client.stop()

        await ctx.reply("stopped and cleared queue!", mention_author=False)

    @bot.command(name="leave", aliases=["disconnect"], help="make doro leave voice")
    async def leave(ctx: commands.Context) -> None:
        if ctx.author.id not in OWNER_IDS:
            await ctx.reply("owner only!", mention_author=False)
            return
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await ctx.reply("not in a voice channel!", mention_author=False)

        await voice_client.disconnect()
        state = music_states.get(ctx.guild.id)
        if state:
            state.voice_client = None
            state.now_playing = None
            cancel_auto_leave(state)
        await ctx.reply("left voice channel!", mention_author=False)

    @bot.command(name="stay", help="toggle stay mode - bot stays in voice after queue ends")
    async def stay(ctx: commands.Context) -> None:
        state = get_state(ctx.guild.id)
        state.stay_mode = not state.stay_mode
        status = "enabled" if state.stay_mode else "disabled"
        if state.stay_mode:
            cancel_auto_leave(state)
        await ctx.reply(f"stay mode {status}!", mention_author=False)

    @bot.command(name="np", aliases=["nowplaying"], help="view now playing track")
    async def now_playing(ctx: commands.Context) -> None:
        state = music_states.get(ctx.guild.id)
        if not state or not state.now_playing:
            return await ctx.reply("nothing is playing!", mention_author=False)

        track = state.now_playing
        await ctx.reply(f"now playing: **{track.title}**\n{track.webpage_url}", mention_author=False)

    @bot.command(name="move", help="move a track to a new position in queue")
    async def move_track(ctx: commands.Context, current_index: int, new_index: int) -> None:
        state = music_states.get(ctx.guild.id)
        if not state or not state.queue:
            return await ctx.reply("queue is empty!", mention_author=False)

        queue_list = list(state.queue)
        if current_index < 1 or current_index > len(queue_list):
            return await ctx.reply("invalid position!", mention_author=False)

        new_index_clamped = max(1, min(new_index, len(queue_list)))
        track = queue_list.pop(current_index - 1)
        queue_list.insert(new_index_clamped - 1, track)
        state.queue = deque(queue_list)

        await ctx.reply(f"moved **{track.title}** to position {new_index_clamped}!", mention_author=False)

    @bot.command(name="remove", aliases=["rm"], help="remove a track from queue")
    async def remove_track(ctx: commands.Context, index: int) -> None:
        state = music_states.get(ctx.guild.id)
        if not state or not state.queue:
            return await ctx.reply("queue is empty!", mention_author=False)

        queue_list = list(state.queue)
        if index < 1 or index > len(queue_list):
            return await ctx.reply("invalid position!", mention_author=False)

        removed_track = queue_list.pop(index - 1)
        state.queue = deque(queue_list)
        await ctx.reply(f"removed **{removed_track.title}** from queue!", mention_author=False)

    @bot.command(name="loop", aliases=["repeat"], help="toggle loop mode (off/one/all)")
    async def loop_cmd(ctx: commands.Context, mode: str = None) -> None:
        state = get_state(ctx.guild.id)
        
        if mode is None:
            # Cycle through modes
            if state.loop_mode == "off":
                state.loop_mode = "one"
                await ctx.reply("enabled loop for current song 🔂", mention_author=False)
            elif state.loop_mode == "one":
                state.loop_mode = "all"
                await ctx.reply("enabled loop for entire queue 🔁", mention_author=False)
            else:
                state.loop_mode = "off"
                await ctx.reply("disabled loop mode ❌", mention_author=False)
        else:
            mode = mode.lower()
            if mode in ["off", "0", "none"]:
                state.loop_mode = "off"
                await ctx.reply("disabled loop mode ❌", mention_author=False)
            elif mode in ["one", "1", "single"]:
                state.loop_mode = "one"
                await ctx.reply("enabled loop for current song 🔂", mention_author=False)
            elif mode in ["all", "queue", "2"]:
                state.loop_mode = "all"
                await ctx.reply("enabled loop for entire queue 🔁", mention_author=False)
            else:
                await ctx.reply("invalid mode! use: off/one/all", mention_author=False)

    @bot.command(name="shuffle", help="shuffle the queue")
    async def shuffle_cmd(ctx: commands.Context) -> None:
        state = music_states.get(ctx.guild.id)
        if not state or not state.queue:
            return await ctx.reply("queue is empty, cant shuffle!", mention_author=False)

        import random
        queue_list = list(state.queue)
        random.shuffle(queue_list)
        state.queue = deque(queue_list)
        await ctx.reply(f"shuffled {len(queue_list)} tracks in queue 🔀", mention_author=False)

    @bot.command(name="volume", aliases=["vol"], help="adjust volume (0-100)")
    async def volume_cmd(ctx: commands.Context, volume: int = None) -> None:
        state = get_state(ctx.guild.id)
        voice_client = ctx.voice_client
        
        if volume is None:
            current_vol = int(state.volume * 100)
            return await ctx.reply(f"current volume: **{current_vol}%** 🔊", mention_author=False)
        
        if volume < 0 or volume > 100:
            return await ctx.reply("volume must be between 0-100!", mention_author=False)
        
        state.volume = volume / 100.0
        
        # Update current playing track volume
        if voice_client and voice_client.source:
            if isinstance(voice_client.source, discord.PCMVolumeTransformer):
                voice_client.source.volume = state.volume
        
        await ctx.reply(f"set volume to **{volume}%** 🔊", mention_author=False)

    @bot.command(name="history", aliases=["hist"], help="view music play history")
    async def history_cmd(ctx: commands.Context) -> None:
        state = music_states.get(ctx.guild.id)
        if not state or not state.play_history:
            return await ctx.reply("no music history yet!", mention_author=False)

        entries = []
        for idx, track in enumerate(reversed(list(state.play_history)), start=1):
            entries.append(f"{idx}. {track.title}")
            if idx >= 10:
                break

        text = "**music history (last 10 tracks):**\n" + "\n".join(entries)
        await ctx.reply(text, mention_author=False)

    @bot.command(name="reset", aliases=["clear"], help="clear AI chat history")
    async def reset_ai(ctx: commands.Context) -> None:
        user_id = str(ctx.author.id)
        if ai.clear_user_history(user_id):
            await ctx.reply("cleared ur chat history! 🗑️", mention_author=False)
        else:
            await ctx.reply("u dont have any chat history yet!", mention_author=False)

    @bot.command(name="cleanhistory", help="clean empty messages in history (owner)")
    async def cleanhistory_cmd(ctx: commands.Context) -> None:
        if ctx.author.id not in OWNER_IDS:
            await ctx.reply("owner only!", mention_author=False)
            return
        
        import os
        import json
        
        cleaned = 0
        history_dir = "user_histories"
        
        if not os.path.exists(history_dir):
            await ctx.reply("no history folder!", mention_author=False)
            return
        
        for filename in os.listdir(history_dir):
            if filename.endswith(".json") and not filename.endswith("_memory.json"):
                filepath = os.path.join(history_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        history = json.load(f)
                    
                    # Filter out empty messages
                    original_len = len(history)
                    cleaned_history = [
                        msg for msg in history
                        if msg.get("content") and msg.get("content").strip()
                    ]
                    
                    if len(cleaned_history) < original_len:
                        with open(filepath, "w", encoding="utf-8") as f:
                            json.dump(cleaned_history, f, ensure_ascii=False, indent=2)
                        cleaned += 1
                except Exception as e:
                    continue
        
        await ctx.reply(f"✅ cleaned {cleaned} history files!", mention_author=False)

    @bot.command(name="remember", help="save important info")
    async def remember_cmd(ctx: commands.Context, key: str, *, value: str) -> None:
        user_id = str(ctx.author.id)
        ai.save_user_memory(user_id, key, value)
        await ctx.reply(f"saved **{key}**: {value} to memory! 💾", mention_author=False)

    @bot.command(name="recall", aliases=["memories"], help="view saved info")
    async def recall_cmd(ctx: commands.Context, key: str = None) -> None:
        user_id = str(ctx.author.id)
        memories = ai.load_user_memories(user_id)
        
        if not memories:
            return await ctx.reply("no saved info about u yet!", mention_author=False)
        
        if key:
            if key in memories:
                mem = memories[key]
                await ctx.reply(f"**{key}**: {mem['value']}", mention_author=False)
            else:
                await ctx.reply(f"couldnt find info about **{key}**!", mention_author=False)
        else:
            entries = [f"**{k}**: {v['value']}" for k, v in memories.items()]
            text = "**saved info about u:**\n" + "\n".join(entries[:10])
            if len(entries) > 10:
                text += f"\n... and {len(entries) - 10} more"
            await ctx.reply(text, mention_author=False)

    @bot.command(name="forget", help="delete saved info")
    async def forget_cmd(ctx: commands.Context, key: str) -> None:
        user_id = str(ctx.author.id)
        if ai.delete_user_memory(user_id, key):
            await ctx.reply(f"deleted **{key}** from memory! 🗑️", mention_author=False)
        else:
            await ctx.reply(f"couldnt find **{key}** to delete!", mention_author=False)

    @bot.command(name="8ball", help="ask the magic 8ball")
    async def eight_ball(ctx: commands.Context, *, question: str = None) -> None:
        if not question:
            return await ctx.reply("what do u wanna ask? 🔮", mention_author=False)
        
        import random
        responses = [
            "definitely yes! ✨",
            "no doubt about it~ 💯",
            "absolutely! 😊",
            "looks promising~ ✨",
            "signs point to yes~ 🌟",
            "ask again later~ 🤔",
            "im not sure... 😅",
            "dont count on it~ ❌",
            "my answer is no 🙅‍♀️",
            "very doubtful~ 😔",
            "hmm... maybe~ 🤷‍♀️",
            "i think so! 💖",
            "dont get ur hopes up~ 😬",
            "future is unclear... 🌫️"
        ]
        answer = random.choice(responses)
        await ctx.reply(f"🔮 **{question}**\n{answer}", mention_author=False)

    @bot.command(name="roll", help="roll dice (e.g. 2d6, 1d20)")
    async def roll_dice(ctx: commands.Context, dice: str = "1d6") -> None:
        import random
        try:
            # Parse dice notation (e.g., 2d6 = 2 dice with 6 sides)
            match = re.match(r"(\d+)d(\d+)", dice.lower())
            if not match:
                return await ctx.reply("wrong format! use: 1d6, 2d20, 3d12", mention_author=False)
            
            num_dice = int(match.group(1))
            num_sides = int(match.group(2))
            
            if num_dice < 1 or num_dice > 100:
                return await ctx.reply("dice count must be 1-100!", mention_author=False)
            if num_sides < 2 or num_sides > 1000:
                return await ctx.reply("sides must be 2-1000!", mention_author=False)
            
            rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
            total = sum(rolls)
            
            if num_dice == 1:
                await ctx.reply(f"🎲 rolled {dice}: **{total}**", mention_author=False)
            else:
                rolls_str = ", ".join(str(r) for r in rolls)
                await ctx.reply(f"🎲 rolled {dice}: [{rolls_str}] = **{total}**", mention_author=False)
        except Exception as e:
            await ctx.reply(f"error: {e}", mention_author=False)

    @bot.command(name="coinflip", aliases=["flip", "coin"], help="flip a coin")
    async def coinflip(ctx: commands.Context) -> None:
        import random
        result = random.choice(["heads 🪙", "tails 🪙"])
        await ctx.reply(f"result: **{result}**", mention_author=False)

    @bot.command(name="rps", help="rock paper scissors with doro")
    async def rock_paper_scissors(ctx: commands.Context, choice: str = None) -> None:
        if not choice:
            return await ctx.reply("choose rock, paper, or scissors!", mention_author=False)
        
        import random
        choices = {
            "rock": "🪨 rock",
            "paper": "📄 paper",
            "scissors": "✂️ scissors",
            "r": "🪨 rock",
            "p": "📄 paper",
            "s": "✂️ scissors"
        }
        
        user_choice = choice.lower()
        if user_choice not in choices:
            return await ctx.reply("invalid choice! choose rock/paper/scissors", mention_author=False)
        
        user_pick = choices[user_choice]
        bot_pick = random.choice(list(set(choices.values())))
        
        # Determine winner
        wins = {
            "🪨 rock": "✂️ scissors",
            "📄 paper": "🪨 rock",
            "✂️ scissors": "📄 paper"
        }
        
        if user_pick == bot_pick:
            result = "its a tie! 🤝"
        elif wins[user_pick] == bot_pick:
            result = "u win! 🎉"
        else:
            result = "i win~ 😊"
        
        await ctx.reply(f"u chose: {user_pick}\ni chose: {bot_pick}\n**{result}**", mention_author=False)
    
    # ==================== SHOP COMMANDS ====================
    
    @bot.command(name="shop", help="view shop 🏪")
    async def shop_cmd(ctx: commands.Context, category: str = None) -> None:
        if not category:
            # Show all categories
            embed = discord.Embed(
                title="🏪 SHOP",
                description="welcome to doro's shop!\n\n**usage:** `+shop <category>`",
                color=discord.Color.gold()
            )
            embed.add_field(
                name="📂 categories",
                value="• `ring` - rings 💍 (1M-10M coins)\n• `pet` - pets 🐾\n• `lootbox` - lootboxes 🎁\n• `consumable` - consumables 🍪\n• `collectible` - collectibles 💎",
                inline=False
            )
            embed.set_footer(text="example: +shop ring • use +about <category> for details")
            return await ctx.reply(embed=embed, mention_author=False)
        
        category = category.lower()
        items = shop_system.get_shop_items(category)
        
        if not items:
            return await ctx.reply(f"❌ category `{category}` not found!", mention_author=False)
        
        # Create shop embed
        category_names = {
            "ring": "💍 RINGS",
            "pet": "🐾 PETS",
            "lootbox": "🎁 LOOTBOXES",
            "consumable": "🍪 CONSUMABLES",
            "collectible": "💎 COLLECTIBLES"
        }
        
        embed = discord.Embed(
            title=f"🏪 {category_names.get(category, category.upper())}",
            description=f"use `+buy <item_id>` to buy\nuse `+about {category}` for details",
            color=discord.Color.gold()
        )
        
        for item_id, item in sorted(items.items(), key=lambda x: x[1]["price"]):
            embed.add_field(
                name=f"{item['emoji']} {item['name']}",
                value=f"**ID:** `{item_id}`\n💰 **{item['price']:,}** coins",
                inline=True
            )
        
        embed.set_footer(text="buy: +buy <item_id> • view inventory: +inventory")
        await ctx.reply(embed=embed, mention_author=False)
    
    @bot.command(name="buy", help="buy items 🛍️")
    async def buy_cmd(ctx: commands.Context, item_id: str = None, quantity: int = 1) -> None:
        if not item_id:
            return await ctx.reply("what do u wanna buy? use `+shop` to view items", mention_author=False)
        
        if quantity < 1:
            return await ctx.reply("quantity must be > 0!", mention_author=False)
        
        item = shop_system.get_item_info(item_id)
        if not item:
            return await ctx.reply(f"❌ item `{item_id}` not found!", mention_author=False)
        
        total_cost = item["price"] * quantity
        
        # Check balance (skip for infinity users)
        user_id = str(ctx.author.id)
        stats = economy.get_user(user_id)
        is_infinity = economy.is_infinity(user_id)
        
        if not is_infinity and stats["balance"] < total_cost:
            return await ctx.reply(f"❌ not enough money! need **{total_cost:,}** coins but u only have **{stats['balance']:,}** coins", mention_author=False)
        
        # Deduct money (infinity users don't lose money)
        if not is_infinity:
            economy.remove_money(user_id, total_cost)
        
        # Add item
        shop_system.add_item(str(ctx.author.id), item_id, quantity)
        
        embed = discord.Embed(
            title="✅ PURCHASE SUCCESS!",
            description=f"bought **{quantity}x** {item['emoji']} **{item['name']}**!",
            color=discord.Color.green()
        )
        embed.add_field(name="total cost", value=f"💰 **{total_cost:,}** coins", inline=True)
        if is_infinity:
            embed.add_field(name="balance remaining", value=f"💵 **∞** coins", inline=True)
        else:
            new_balance = economy.get_balance(user_id)
            embed.add_field(name="balance remaining", value=f"💵 **{new_balance:,}** coins", inline=True)
        embed.set_footer(text="use +inventory to view items")
        
        await ctx.reply(embed=embed, mention_author=False)
    
    @bot.command(name="inventory", aliases=["inv", "bag"], help="view inventory 🎒")
    async def inventory_cmd(ctx: commands.Context, member: discord.Member = None) -> None:
        target = member or ctx.author
        inventory = shop_system.get_user_inventory(str(target.id))
        
        items = inventory.get("items", {})
        equipped = inventory.get("equipped", {})
        
        if not items and not equipped:
            if target.id == ctx.author.id:
                return await ctx.reply("ur inventory is empty! use `+shop` to buy items", mention_author=False)
            else:
                return await ctx.reply(f"{target.mention}'s inventory is empty!", mention_author=False)
        
        embed = discord.Embed(
            title=f"🎒 INVENTORY - {target.display_name}",
            color=discord.Color.blue()
        )
        
        # Show equipped items
        if equipped:
            equipped_text = []
            for category, item_id in equipped.items():
                item_info = shop_system.get_item_info(item_id)
                if item_info:
                    equipped_text.append(f"{item_info['emoji']} **{item_info['name']}** ({category})")
            
            if equipped_text:
                embed.add_field(
                    name="✨ EQUIPPED",
                    value="\n".join(equipped_text),
                    inline=False
                )
        
        # Show items by category
        categories = {}
        for item_id, quantity in items.items():
            item_info = shop_system.get_item_info(item_id)
            if item_info:
                cat = item_info["category"]
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(f"{item_info['emoji']} **{item_info['name']}** x{quantity}")
        
        for category, item_list in categories.items():
            cat_names = {
                "ring": "💍 rings",
                "pet": "🐾 pets",
                "lootbox": "🎁 lootboxes",
                "consumable": "🍪 consumables",
                "collectible": "💎 collectibles"
            }
            embed.add_field(
                name=cat_names.get(category, category.upper()),
                value="\n".join(item_list),
                inline=True
            )
        
        # Show total value
        total_value = shop_system.get_inventory_value(str(target.id))
        # Get current prefix
        prefix = prefix_system.get_prefix(str(ctx.guild.id)) if ctx.guild else "!"
        embed.set_footer(text=f"total value: {total_value:,} coins • use {prefix}equip <item_id> to equip")
        
        await ctx.reply(embed=embed, mention_author=False)
    
    @bot.command(name="equip", help="equip item ⚔️")
    async def equip_cmd(ctx: commands.Context, item_id: str = None) -> None:
        if not item_id:
            prefix = prefix_system.get_prefix(str(ctx.guild.id)) if ctx.guild else "!"
            return await ctx.reply(f"what do u wanna equip? use `{prefix}inventory` to view items", mention_author=False)
        
        success, message = shop_system.equip_item(str(ctx.author.id), item_id)
        await ctx.reply(message, mention_author=False)
    
    @bot.command(name="unequip", help="unequip item 🔓")
    async def unequip_cmd(ctx: commands.Context, category: str = None) -> None:
        if not category:
            prefix = prefix_system.get_prefix(str(ctx.guild.id)) if ctx.guild else "!"
            return await ctx.reply(f"what do u wanna unequip? use `{prefix}unequip ring` or `{prefix}unequip pet`", mention_author=False)
        
        category = category.lower()
        if category not in ["ring", "pet"]:
            return await ctx.reply("❌ invalid category! only `ring` or `pet`", mention_author=False)
        
        success, message = shop_system.unequip_item(str(ctx.author.id), category)
        await ctx.reply(message, mention_author=False)
    
    @bot.command(name="use", help="use item 🎯")
    async def use_cmd(ctx: commands.Context, item_id: str = None) -> None:
        if not item_id:
            prefix = prefix_system.get_prefix(str(ctx.guild.id)) if ctx.guild else "!"
            return await ctx.reply(f"what do u wanna use? use `{prefix}inventory` to view items", mention_author=False)
        
        item = shop_system.get_item_info(item_id)
        if not item:
            return await ctx.reply(f"❌ item `{item_id}` not found!", mention_author=False)
        
        # Check if it's a lootbox
        if item["category"] == "lootbox":
            success, message, rewards = shop_system.open_lootbox(str(ctx.author.id), item_id)
            if not success:
                return await ctx.reply(message, mention_author=False)
            
            # Add coins to user
            coins_reward = next((r["amount"] for r in rewards if r["type"] == "coins"), 0)
            if coins_reward > 0:
                economy.add_money(str(ctx.author.id), coins_reward)
            
            # Create rewards embed
            embed = discord.Embed(
                title="🎁 LOOTBOX OPENED!",
                description=f"opened {item['emoji']} **{item['name']}**!",
                color=discord.Color.gold()
            )
            
            rewards_text = []
            for reward in rewards:
                if reward["type"] == "coins":
                    rewards_text.append(f"💰 **{reward['amount']:,}** coins")
                else:
                    rewards_text.append(f"{reward['emoji']} **{reward['name']}**")
            
            embed.add_field(name="🎉 rewards", value="\n".join(rewards_text), inline=False)
            prefix = prefix_system.get_prefix(str(ctx.guild.id)) if ctx.guild else "!"
            embed.set_footer(text=f"congrats! use {prefix}inventory to view items")
            
            await ctx.reply(embed=embed, mention_author=False)
        else:
            # Use consumable or other items
            success, message, effect_data = shop_system.use_item(str(ctx.author.id), item_id)
            await ctx.reply(message, mention_author=False)
    
    @bot.command(name="sell", help="sell item 💵")
    async def sell_cmd(ctx: commands.Context, item_id: str = None, quantity: int = 1) -> None:
        if not item_id:
            prefix = prefix_system.get_prefix(str(ctx.guild.id)) if ctx.guild else "!"
            return await ctx.reply(f"what do u wanna sell? use `{prefix}inventory` to view items", mention_author=False)
        
        if quantity < 1:
            return await ctx.reply("quantity must be > 0!", mention_author=False)
        
        item = shop_system.get_item_info(item_id)
        if not item:
            return await ctx.reply(f"❌ item `{item_id}` not found!", mention_author=False)
        
        # Check if user has item
        if not shop_system.has_item(str(ctx.author.id), item_id, quantity):
            return await ctx.reply(f"❌ u dont have **{quantity}x** {item['emoji']} **{item['name']}**!", mention_author=False)
        
        # Sell for 50% of original price
        sell_price = int(item["price"] * 0.5 * quantity)
        
        # Remove item and add money
        shop_system.remove_item(str(ctx.author.id), item_id, quantity)
        economy.add_money(str(ctx.author.id), sell_price)
        
        embed = discord.Embed(
            title="✅ SOLD!",
            description=f"sold **{quantity}x** {item['emoji']} **{item['name']}**!",
            color=discord.Color.green()
        )
        embed.add_field(name="received", value=f"💰 **{sell_price:,}** coins", inline=True)
        embed.set_footer(text="sell price = 50% of buy price")
        
        await ctx.reply(embed=embed, mention_author=False)
    
    @bot.command(name="gift", help="gift item to someone 🎁 (10% fee)")
    async def gift_cmd(ctx: commands.Context, member: discord.Member = None, item_id: str = None) -> None:
        if not member or not item_id:
            prefix = prefix_system.get_prefix(str(ctx.guild.id)) if ctx.guild else "!"
            return await ctx.reply(f"usage: `{prefix}gift @user <item_id>`\n\n⚠️ **transaction fee:** 10% of item value", mention_author=False)
        
        if member.bot:
            return await ctx.reply("cant gift items to bots!", mention_author=False)
        
        if member.id == ctx.author.id:
            return await ctx.reply("cant gift to urself!", mention_author=False)
        
        item = shop_system.get_item_info(item_id)
        if not item:
            return await ctx.reply(f"❌ item `{item_id}` not found!", mention_author=False)
        
        if not item.get("tradeable", False):
            return await ctx.reply(f"❌ {item['emoji']} **{item['name']}** is not tradeable!", mention_author=False)
        
        # Check if user has item
        if not shop_system.has_item(str(ctx.author.id), item_id):
            return await ctx.reply(f"❌ u dont have {item['emoji']} **{item['name']}**!", mention_author=False)
        
        # Calculate 10% fee
        fee = int(item["price"] * 0.1)
        user_id = str(ctx.author.id)
        
        # Check if user has enough money for fee
        is_infinity = economy.is_infinity(user_id)
        if not is_infinity and economy.get_balance(user_id) < fee:
            return await ctx.reply(f"❌ u need **{fee:,}** coins for transaction fee (10% of item value)!", mention_author=False)
        
        # Deduct fee
        if not is_infinity:
            economy.remove_money(user_id, fee)
        
        # Transfer item
        shop_system.remove_item(user_id, item_id)
        shop_system.add_item(str(member.id), item_id)
        
        embed = discord.Embed(
            title="🎁 GIFT SENT!",
            description=f"{ctx.author.mention} gifted {member.mention}\n{item['emoji']} **{item['name']}**!",
            color=discord.Color.from_rgb(255, 182, 193)
        )
        embed.add_field(name="💸 transaction fee", value=f"**{fee:,}** coins (10%)", inline=True)
        if is_infinity:
            embed.add_field(name="balance remaining", value="**∞** coins", inline=True)
        else:
            new_balance = economy.get_balance(user_id)
            embed.add_field(name="balance remaining", value=f"**{new_balance:,}** coins", inline=True)
        embed.set_footer(text="how kind! 💕")
        
        await ctx.reply(embed=embed, mention_author=False)
    
    # ==================== MARRIAGE COMMANDS ====================
    
    # Temporary storage for marriage proposals
    marriage_proposals = {}
    
    @bot.command(name="marry", help="propose to someone 💍")
    async def marry_cmd(ctx: commands.Context, member: discord.Member = None) -> None:
        if not member:
            return await ctx.reply("who do u wanna propose to? tag them~ 💕", mention_author=False)
        
        if member.bot:
            return await ctx.reply("cant propose to bots~ 😅", mention_author=False)
        
        if member.id == ctx.author.id:
            return await ctx.reply("cant propose to urself! 😂", mention_author=False)
        
        # Check if proposer has a ring equipped
        equipped_ring = shop_system.get_equipped_item(str(ctx.author.id), "ring")
        if not equipped_ring:
            prefix = prefix_system.get_prefix(str(ctx.guild.id)) if ctx.guild else "!"
            return await ctx.reply(f"u need to equip a ring before proposing! use `{prefix}shop ring` to buy a ring~ 💍", mention_author=False)
        
        # Check if can propose (owner can have unlimited wives)
        is_owner = ctx.author.id in OWNER_IDS
        can_propose, message = marriage_system.propose(str(ctx.author.id), str(member.id), is_owner=is_owner)
        if not can_propose:
            return await ctx.reply(message, mention_author=False)
        
        # Clear any existing proposal for this target (prevent stuck proposals)
        target_id_str = str(member.id)
        if target_id_str in marriage_proposals:
            del marriage_proposals[target_id_str]
        
        # Store proposal with STRING ID
        marriage_proposals[target_id_str] = {
            "proposer_id": str(ctx.author.id),
            "ring_id": equipped_ring,
            "timestamp": datetime.now()
        }
        
        # Create proposal embed
        ring_info = shop_system.get_item_info(equipped_ring)
        embed = discord.Embed(
            title="💍 MARRIAGE PROPOSAL 💍",
            description=f"{ctx.author.mention} is proposing to {member.mention}!\n\n{ring_info['emoji']} **{ring_info['name']}**\n\n{member.mention}, do u accept?",
            color=discord.Color.from_rgb(255, 182, 193)
        )
        prefix = prefix_system.get_prefix(str(ctx.guild.id)) if ctx.guild else "!"
        embed.set_footer(text=f"use {prefix}accept to accept or {prefix}reject to decline • u have 5 mins to decide")
        
        await ctx.reply(embed=embed, mention_author=False)
    
    @bot.command(name="accept", help="accept marriage proposal ✅")
    async def accept_proposal_cmd(ctx: commands.Context) -> None:
        user_id_str = str(ctx.author.id)
        
        if user_id_str not in marriage_proposals:
            return await ctx.reply("no one proposed to u! 💔", mention_author=False)
        
        proposal = marriage_proposals[user_id_str]
        
        # Check if proposal expired (5 minutes)
        if (datetime.now() - proposal["timestamp"]).total_seconds() > 300:
            del marriage_proposals[user_id_str]
            return await ctx.reply("⏰ proposal expired!", mention_author=False)
        
        proposer_id_str = proposal["proposer_id"]
        ring_id = proposal["ring_id"]
        
        # Accept proposal (check if proposer is owner)
        is_owner = int(proposer_id_str) in OWNER_IDS
        success, result = marriage_system.marry(proposer_id_str, user_id_str, ring_id, is_owner=is_owner)
        
        # Always remove proposal after attempt
        del marriage_proposals[user_id_str]
        
        if success:
            # Remove ring from proposer's equipped
            shop_system.unequip_item(proposer_id_str, "ring")
            
            proposer = await bot.fetch_user(int(proposer_id_str))
            
            embed = discord.Embed(
                title="🎉 CONGRATULATIONS! 🎉",
                description=f"{proposer.mention} ❤️ {ctx.author.mention}\n\n{result}\n\nu are now married! 💑",
                color=discord.Color.from_rgb(255, 105, 180)
            )
            prefix = prefix_system.get_prefix(str(ctx.guild.id)) if ctx.guild else "!"
            embed.set_footer(text=f"use {prefix}marriage to view marriage info")
            await ctx.send(embed=embed)
        else:
            await ctx.reply(result, mention_author=False)
    
    @bot.command(name="reject", help="reject marriage proposal ❌")
    async def reject_proposal_cmd(ctx: commands.Context) -> None:
        user_id_str = str(ctx.author.id)
        
        if user_id_str not in marriage_proposals:
            return await ctx.reply("no one proposed to u! 💔", mention_author=False)
        
        proposal = marriage_proposals[user_id_str]
        proposer_id_str = proposal["proposer_id"]
        
        proposer = await bot.fetch_user(int(proposer_id_str))
        
        await ctx.reply(f"💔 {ctx.author.mention} rejected {proposer.mention}'s proposal...", mention_author=False)
        
        # Remove proposal
        del marriage_proposals[user_id_str]
    
    @bot.command(name="divorce", help="divorce 💔")
    async def divorce_cmd(ctx: commands.Context, member: discord.Member = None) -> None:
        if not marriage_system.is_married(str(ctx.author.id)):
            return await ctx.reply("ur not married!", mention_author=False)
        
        # Check cooldown (15 hours)
        can_divorce, cooldown_msg = marriage_system.can_divorce(str(ctx.author.id))
        if not can_divorce:
            return await ctx.reply(cooldown_msg, mention_author=False)
        
        partner_data = marriage_system.get_partner(str(ctx.author.id))
        
        # Handle multiple partners (owner)
        if isinstance(partner_data, list):
            if not member:
                partners_list = []
                for pid in partner_data:
                    p = await bot.fetch_user(int(pid))
                    partners_list.append(p.mention)
                prefix = prefix_system.get_prefix(str(ctx.guild.id)) if ctx.guild else "!"
                return await ctx.reply(f"u have multiple spouses! specify who: `{prefix}divorce @user`\n\nmarried to: {', '.join(partners_list)}", mention_author=False)
            partner_id = str(member.id)
            if partner_id not in partner_data:
                return await ctx.reply("ur not married to this person!", mention_author=False)
        else:
            partner_id = partner_data
        
        partner = await bot.fetch_user(int(partner_id))
        
        embed = discord.Embed(
            title="💔 DIVORCE",
            description=f"are u sure u wanna divorce {partner.mention}?\n\nthis is a serious decision!",
            color=discord.Color.red()
        )
        embed.set_footer(text="react ✅ to confirm, ❌ to cancel • u have 30 seconds")
        
        msg = await ctx.reply(embed=embed, mention_author=False)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        
        def check(reaction, user):
            return user.id == ctx.author.id and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == msg.id
        
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
            
            if str(reaction.emoji) == "✅":
                # Pass target partner for owners with multiple wives
                target_partner = str(member.id) if member else None
                success, result = marriage_system.divorce(str(ctx.author.id), target_partner)
                await ctx.reply(result, mention_author=False)
            else:
                await ctx.reply("divorce cancelled", mention_author=False)
        
        except asyncio.TimeoutError:
            await ctx.reply("⏰ time's up! divorce cancelled", mention_author=False)
    
    @bot.command(name="checkmarriage", help="[DEBUG] Check marriage status")
    async def check_marriage_cmd(ctx: commands.Context, member: discord.Member = None) -> None:
        """Debug command to check marriage status"""
        if ctx.author.id not in OWNER_IDS:
            return
        
        target = member or ctx.author
        user_id = str(target.id)
        
        is_married = marriage_system.is_married(user_id)
        marriage_info = marriage_system.get_marriage_info(user_id)
        
        embed = discord.Embed(title="🔍 Marriage Debug Info", color=discord.Color.blue())
        embed.add_field(name="User", value=target.mention, inline=False)
        embed.add_field(name="User ID", value=user_id, inline=True)
        embed.add_field(name="Is Married", value=str(is_married), inline=True)
        embed.add_field(name="Marriage Data", value=f"```json\n{json.dumps(marriage_info, indent=2, ensure_ascii=False) if marriage_info else 'None'}```", inline=False)
        
        await ctx.reply(embed=embed, mention_author=False)
    
    @bot.command(name="forcedivorce", help="[DEBUG] Force clear marriage")
    async def force_divorce_cmd(ctx: commands.Context, member: discord.Member = None) -> None:
        """Debug command to force clear marriage"""
        if ctx.author.id not in OWNER_IDS:
            return
        
        target = member or ctx.author
        user_id = str(target.id)
        
        if user_id in marriage_system.marriages:
            partner_data = marriage_system.marriages[user_id].get("partner")
            
            # Remove user's marriage
            del marriage_system.marriages[user_id]
            
            # Remove partner's marriage
            if isinstance(partner_data, list):
                for pid in partner_data:
                    if pid in marriage_system.marriages:
                        del marriage_system.marriages[pid]
            elif partner_data and partner_data in marriage_system.marriages:
                del marriage_system.marriages[partner_data]
            
            marriage_system.save_data()
            await ctx.reply(f"✅ deleted marriage data for {target.mention}!", mention_author=False)
        else:
            await ctx.reply(f"❌ {target.mention} has no marriage data!", mention_author=False)
    
    @bot.command(name="marriage", aliases=["married", "spouse"], help="view marriage info 💑")
    async def marriage_info_cmd(ctx: commands.Context, member: discord.Member = None) -> None:
        target = member or ctx.author
        
        if not marriage_system.is_married(str(target.id)):
            if target.id == ctx.author.id:
                prefix = prefix_system.get_prefix(str(ctx.guild.id)) if ctx.guild else "!"
                return await ctx.reply(f"ur not married! use `{prefix}marry @user` to propose~ 💍", mention_author=False)
            else:
                return await ctx.reply(f"{target.mention} is not married!", mention_author=False)
        
        marriage_info = marriage_system.get_marriage_info(str(target.id))
        partner_data = marriage_info["partner"]
        
        # Handle multiple partners (owner)
        if isinstance(partner_data, list):
            partners = []
            for pid in partner_data:
                p = await bot.fetch_user(int(pid))
                partners.append(p.mention)
            partner_text = " + ".join(partners)
        else:
            partner = await bot.fetch_user(int(partner_data))
            partner_text = partner.mention
        
        duration = marriage_system.get_marriage_duration(str(target.id))
        love_points = marriage_info.get("love_points", 0)
        ring_id = marriage_info.get("ring")
        
        ring_info = shop_system.get_item_info(ring_id) if ring_id else None
        ring_text = f"{ring_info['emoji']} {ring_info['name']}" if ring_info else "no ring"
        
        embed = discord.Embed(
            title="💑 MARRIAGE INFO",
            color=discord.Color.from_rgb(255, 182, 193)
        )
        embed.add_field(name="spouse", value=f"{target.mention} ❤️ {partner_text}", inline=False)
        embed.add_field(name="wedding ring", value=ring_text, inline=True)
        embed.add_field(name="duration", value=duration, inline=True)
        embed.add_field(name="love points", value=f"💕 {love_points:,}", inline=True)
        prefix = prefix_system.get_prefix(str(ctx.guild.id)) if ctx.guild else "!"
        embed.set_footer(text=f"use {prefix}divorce to divorce")
        
        await ctx.reply(embed=embed, mention_author=False)
    
    @bot.command(name="about", help="view detailed item info 📖")
    async def about_cmd(ctx: commands.Context, category: str = None) -> None:
        if not category:
            # Show available categories
            embed = discord.Embed(
                title="📖 ABOUT - ITEM INFO",
                description=f"view detailed info about shop items!\n\n**usage:** `{prefix_system.get_prefix(str(ctx.guild.id)) if ctx.guild else '!'}about <category>`",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="📂 categories",
                value="• `ring` - rings 💍\n• `pet` - pets 🐾\n• `lootbox` - lootboxes 🎁\n• `consumable` - consumables 🍪\n• `collectible` - collectibles 💎",
                inline=False
            )
            prefix = prefix_system.get_prefix(str(ctx.guild.id)) if ctx.guild else "!"
            embed.set_footer(text=f"example: {prefix}about ring")
            return await ctx.reply(embed=embed, mention_author=False)
        
        category = category.lower()
        
        # Get items by category
        items = shop_system.get_shop_items(category)
        
        if not items:
            prefix = prefix_system.get_prefix(str(ctx.guild.id)) if ctx.guild else "!"
            return await ctx.reply(f"❌ category `{category}` not found!\nuse `{prefix}about` to view category list", mention_author=False)
        
        # Create detailed embed based on category
        if category == "ring":
            embed = discord.Embed(
                title="💍 RINGS - WEDDING RINGS",
                description=f"**⚠️ IMPORTANT NOTE:**\nrings only work when **MARRIED** (use `{prefix_system.get_prefix(str(ctx.guild.id)) if ctx.guild else '!'}marry`)!\nwhen not married, rings are just decorations\n\n**buffs when married:**",
                color=discord.Color.from_rgb(255, 182, 193)
            )
            
            for item_id, item in sorted(items.items(), key=lambda x: x[1]["price"]):
                embed.add_field(
                    name=f"{item['emoji']} {item['name']}",
                    value=f"💰 **price:** {item['price']:,} coins\n📋 {item['description']}\n✨ **buff:** {item['effect']}\n──────────────",
                    inline=False
                )
            
            prefix = prefix_system.get_prefix(str(ctx.guild.id)) if ctx.guild else "!"
            embed.set_footer(text=f"buy ring: {prefix}buy <item_id> • equip: {prefix}equip <item_id> • propose: {prefix}marry @user")
        
        elif category == "pet":
            embed = discord.Embed(
                title="🐾 PETS",
                description="pets help u gain XP daily!\n**buffs activate when equipped**",
                color=discord.Color.from_rgb(100, 200, 255)
            )
            
            for item_id, item in sorted(items.items(), key=lambda x: x[1]["price"]):
                embed.add_field(
                    name=f"{item['emoji']} {item['name']}",
                    value=f"💰 **price:** {item['price']:,} coins\n📋 {item['description']}\n✨ **effect:** {item['effect']}\n──────────────",
                    inline=False
                )
            
            prefix = prefix_system.get_prefix(str(ctx.guild.id)) if ctx.guild else "!"
            embed.set_footer(text=f"buy pet: {prefix}buy <item_id> • equip: {prefix}equip <item_id>")
        
        elif category == "lootbox":
            embed = discord.Embed(
                title="🎁 LOOTBOXES",
                description="open lootboxes to get random items and coins!",
                color=discord.Color.from_rgb(255, 215, 0)
            )
            
            for item_id, item in sorted(items.items(), key=lambda x: x[1]["price"]):
                embed.add_field(
                    name=f"{item['emoji']} {item['name']}",
                    value=f"💰 **price:** {item['price']:,} coins\n📋 {item['description']}\n✨ {item['effect']}\n──────────────",
                    inline=False
                )
            
            embed.set_footer(text="buy: +buy <item_id> • open: +use <item_id>")
        
        elif category == "consumable":
            embed = discord.Embed(
                title="🍪 CONSUMABLES",
                description="single-use items to boost casino win rates!",
                color=discord.Color.from_rgb(255, 140, 0)
            )
            
            for item_id, item in sorted(items.items(), key=lambda x: x[1]["price"]):
                embed.add_field(
                    name=f"{item['emoji']} {item['name']}",
                    value=f"💰 **price:** {item['price']:,} coins\n📋 {item['description']}\n✨ **effect:** {item['effect']}\n──────────────",
                    inline=False
                )
            
            embed.set_footer(text="buy: +buy <item_id> • use: +use <item_id>")
        
        elif category == "collectible":
            embed = discord.Embed(
                title="💎 COLLECTIBLES",
                description="rare items to flex on ur friends!",
                color=discord.Color.from_rgb(138, 43, 226)
            )
            
            for item_id, item in sorted(items.items(), key=lambda x: x[1]["price"]):
                embed.add_field(
                    name=f"{item['emoji']} {item['name']}",
                    value=f"💰 **price:** {item['price']:,} coins\n📝 {item['description']}\n✨ {item['effect']}\n━━━━━━━━━━━━━━",
                    inline=False
                )
            
            embed.set_footer(text="buy: +buy <item_id> • view: +inventory")
        
        else:
            return await ctx.reply(f"❌ category `{category}` has no detailed info!", mention_author=False)
        
        await ctx.reply(embed=embed, mention_author=False)

    @bot.command(name="avatar", aliases=["av", "pfp"], help="view user avatar")
    async def avatar_cmd(ctx: commands.Context, member: discord.Member = None) -> None:
        member = member or ctx.author
        embed = discord.Embed(
            title=f"{member.display_name}'s avatar",
            color=member.color
        )
        embed.set_image(url=member.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        await ctx.reply(embed=embed, mention_author=False)

    @bot.command(name="serverinfo", aliases=["si", "server"], help="view server info")
    async def serverinfo_cmd(ctx: commands.Context) -> None:
        if not ctx.guild:
            return await ctx.reply("this command only works in servers!", mention_author=False)
        
        guild = ctx.guild
        embed = discord.Embed(
            title=f"📊 {guild.name}",
            color=discord.Color.blue()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="👑 Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="🆔 Server ID", value=guild.id, inline=True)
        embed.add_field(name="📅 Created", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="👥 Members", value=guild.member_count, inline=True)
        embed.add_field(name="💬 Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="😀 Emojis", value=len(guild.emojis), inline=True)
        embed.add_field(name="🎭 Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="🚀 Boost Level", value=guild.premium_tier, inline=True)
        embed.add_field(name="💎 Boosts", value=guild.premium_subscription_count or 0, inline=True)
        
        await ctx.reply(embed=embed, mention_author=False)

    @bot.command(name="userinfo", aliases=["ui", "whois"], help="view user info")
    async def userinfo_cmd(ctx: commands.Context, member: discord.Member = None) -> None:
        member = member or ctx.author
        
        embed = discord.Embed(
            title=f"👤 {member.display_name}",
            color=member.color
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        
        embed.add_field(name="🏷️ Username", value=f"{member.name}", inline=True)
        embed.add_field(name="🆔 User ID", value=member.id, inline=True)
        embed.add_field(name="🤖 Bot", value="Yes" if member.bot else "No", inline=True)
        embed.add_field(name="📅 Account Created", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
        
        if ctx.guild and member in ctx.guild.members:
            embed.add_field(name="📥 Joined Server", value=member.joined_at.strftime("%d/%m/%Y") if member.joined_at else "Unknown", inline=True)
            roles = [role.mention for role in member.roles if role.name != "@everyone"]
            if roles:
                embed.add_field(
                    name=f"🎭 Roles [{len(roles)}]",
                    value=" ".join(roles[:10]),
                    inline=False
                )
        
        await ctx.reply(embed=embed, mention_author=False)

    # ==================== ECONOMY COMMANDS ====================
    
    @bot.command(name="balance", aliases=["bal", "money"], help="view balance")
    async def balance_cmd(ctx: commands.Context, member: discord.Member = None) -> None:
        member = member or ctx.author
        user_id = str(member.id)
        
        is_infinity = economy.is_infinity(user_id)
        
        if is_infinity:
            balance_str = "**∞**"
            bank_str = "**∞**"
            total_str = "**∞**"
        else:
            balance = economy.get_balance(user_id)
            bank = economy.get_bank(user_id)
            total = balance + bank
            balance_str = f"**{balance:,}** coins"
            bank_str = f"**{bank:,}** coins"
            total_str = f"**{total:,}** coins"
        
        embed = discord.Embed(
            title=f"💰 {member.display_name}'s Balance",
            color=discord.Color.gold()
        )
        embed.add_field(name="💵 Wallet", value=balance_str, inline=True)
        embed.add_field(name="🏦 Bank", value=bank_str, inline=True)
        embed.add_field(name="💎 Total", value=total_str, inline=True)
        
        if is_infinity:
            embed.set_footer(text="♾️ Infinity Mode Active")
        
        await ctx.reply(embed=embed, mention_author=False)
    
    @bot.command(name="daily", help="claim daily reward")
    async def daily_cmd(ctx: commands.Context) -> None:
        user_id = str(ctx.author.id)
        
        if not economy.can_daily(user_id):
            user = economy.get_user(user_id)
            last_daily = datetime.fromisoformat(user["last_daily"])
            next_daily = last_daily + timedelta(hours=24)
            time_left = next_daily - datetime.now()
            hours = int(time_left.total_seconds() // 3600)
            minutes = int((time_left.total_seconds() % 3600) // 60)
            
            await ctx.reply(f"⏰ u already claimed daily! come back in **{hours}h {minutes}m**", mention_author=False)
            return
        
        result = economy.claim_daily(user_id)
        
        embed = discord.Embed(
            title="🎁 Daily Reward",
            color=discord.Color.gold()
        )
        embed.add_field(name="💰 Coins", value=f"+{result['amount']:,}", inline=True)
        embed.add_field(name="⭐ XP", value=f"+{result['xp_gained']}", inline=True)
        embed.add_field(name="📊 Level", value=f"{result['level']}", inline=True)
        embed.add_field(name="🔥 Streak", value=f"{result['streak']} days", inline=True)
        embed.add_field(name="📈 Streak Bonus", value=f"+{result['streak_bonus']:.1f}%", inline=True)
        embed.add_field(name="🎯 Level Bonus", value=f"+{result['level_bonus']:.1f}%", inline=True)
        
        if result['new_level']:
            embed.add_field(
                name="🎉 Level Up!",
                value=f"congrats! u reached **Level {result['new_level']}**!",
                inline=False
            )
        
        await ctx.reply(embed=embed, mention_author=False)
    
    @bot.command(name="deposit", aliases=["dep"], help="deposit money to bank")
    async def deposit_cmd(ctx: commands.Context, amount: str) -> None:
        user_id = str(ctx.author.id)
        
        if amount.lower() == "all":
            amount = economy.get_balance(user_id)
        else:
            try:
                amount = int(amount)
            except ValueError:
                return await ctx.reply("invalid amount! use a number or 'all'", mention_author=False)
        
        if amount <= 0:
            return await ctx.reply("amount must be > 0!", mention_author=False)
        
        if economy.deposit(user_id, amount):
            await ctx.reply(f"🏦 deposited **{amount:,}** coins to bank!", mention_author=False)
        else:
            await ctx.reply("not enough money in wallet!", mention_author=False)
    
    @bot.command(name="withdraw", aliases=["with"], help="withdraw money from bank")
    async def withdraw_cmd(ctx: commands.Context, amount: str) -> None:
        user_id = str(ctx.author.id)
        
        if amount.lower() == "all":
            amount = economy.get_bank(user_id)
        else:
            try:
                amount = int(amount)
            except ValueError:
                return await ctx.reply("invalid amount! use a number or 'all'", mention_author=False)
        
        if amount <= 0:
            return await ctx.reply("amount must be > 0!", mention_author=False)
        
        if economy.withdraw(user_id, amount):
            await ctx.reply(f"💵 withdrew **{amount:,}** coins from bank!", mention_author=False)
        else:
            await ctx.reply("not enough money in bank!", mention_author=False)
    
    @bot.command(name="setbalance", aliases=["setbal", "setmoney"], help="[OWNER] set user balance")
    async def setbalance_cmd(ctx: commands.Context, member: discord.Member, amount: int) -> None:
        """Owner-only command to set user balance"""
        if ctx.author.id not in OWNER_IDS:
            return await ctx.reply("❌ owner only!", mention_author=False)
        
        if member.bot:
            return await ctx.reply("cant set balance for bots!", mention_author=False)
        
        user_id = str(member.id)
        
        # Check if user has infinity mode
        is_infinity = economy.is_infinity(user_id)
        
        # Get current balance (raw data, not from get_balance which returns inf)
        user_data = economy.get_user(user_id)
        old_balance = user_data.get("balance", 0)
        
        # Set new balance
        if amount < 0:
            return await ctx.reply("❌ amount cant be negative!", mention_author=False)
        
        # Calculate difference
        diff = amount - old_balance
        
        # Update balance directly
        user_data["balance"] = amount
        economy.save_data()
        
        embed = discord.Embed(
            title="💰 SET BALANCE",
            description=f"set balance for {member.mention}!",
            color=discord.Color.gold()
        )
        
        # Display old balance
        if is_infinity and old_balance == 0:
            old_display = "∞ (Infinity Mode)"
        else:
            old_display = f"**{old_balance:,}** coins"
        
        embed.add_field(name="old balance", value=old_display, inline=True)
        embed.add_field(name="new balance", value=f"**{amount:,}** coins", inline=True)
        if not (is_infinity and old_balance == 0):
            embed.add_field(name="change", value=f"**{diff:+,}** coins", inline=True)
        embed.set_footer(text=f"By {ctx.author.display_name}")
        
        await ctx.reply(embed=embed, mention_author=False)
    
    @bot.command(name="give", aliases=["pay"], help="give money to someone (owner: unlimited)")
    async def give_cmd(ctx: commands.Context, member: discord.Member, amount: int) -> None:
        if member.bot:
            return await ctx.reply("cant give money to bots!", mention_author=False)
        
        if member.id == ctx.author.id:
            return await ctx.reply("cant give money to urself!", mention_author=False)
        
        if amount <= 0:
            return await ctx.reply("amount must be > 0!", mention_author=False)
        
        from_user = str(ctx.author.id)
        to_user = str(member.id)
        
        # Owner can give unlimited money
        is_owner = ctx.author.id in OWNER_IDS
        if is_owner:
            economy.add_money(to_user, amount)
            await ctx.reply(f"💸 [Owner] gave **{amount:,}** coins to {member.mention}!", mention_author=False)
        elif economy.transfer(from_user, to_user, amount):
            await ctx.reply(f"💸 transferred **{amount:,}** coins to {member.mention}!", mention_author=False)
        else:
            await ctx.reply("not enough money!", mention_author=False)
    
    # ==================== CASINO GAMES ====================
    
    @bot.command(name="cf", aliases=["coinflip_bet"], help="bet on coinflip (cf <heads/tails> <amount>)")
    async def coinflip_bet(ctx: commands.Context, choice: str, amount: int) -> None:
        user_id = str(ctx.author.id)
        
        if amount <= 0:
            return await ctx.reply("amount must be > 0!", mention_author=False)
        
        is_infinity = economy.is_infinity(user_id)
        if not is_infinity and amount > economy.get_balance(user_id):
            return await ctx.reply("not enough money!", mention_author=False)
        
        choice = choice.lower()
        if choice not in ["heads", "tails", "h", "t"]:
            return await ctx.reply("choose heads or tails!", mention_author=False)
        
        # Normalize choice
        if choice in ["heads", "h"]:
            user_choice = "heads"
        else:
            user_choice = "tails"
        
        import random
        result = random.choice(["heads", "tails"])
        
        if result == user_choice:
            economy.add_money(user_id, amount)
            economy.record_win(user_id)
            await ctx.reply(f"🪙 result: **{result}**\n🎉 u won **{amount:,}** coins!", mention_author=False)
        else:
            economy.remove_money(user_id, amount)
            economy.record_loss(user_id)
            await ctx.reply(f"🪙 result: **{result}**\n😔 u lost **{amount:,}** coins!", mention_author=False)
    
    @bot.command(name="slots", aliases=["slot"], help="play slot machine (slots <amount>)")
    async def slots_cmd(ctx: commands.Context, amount: int) -> None:
        user_id = str(ctx.author.id)
        
        if amount <= 0:
            return await ctx.reply("amount must be > 0!", mention_author=False)
        
        is_infinity = economy.is_infinity(user_id)
        if not is_infinity and amount > economy.get_balance(user_id):
            return await ctx.reply("not enough money!", mention_author=False)
        
        import random
        
        # SUPER RARE JACKPOTS (check first)
        roll = random.random() * 100  # 0-100
        
        if roll < 0.25:  # 0.25% chance - MEGA JACKPOT
            multiplier = 100000
            winnings = amount * multiplier
            economy.add_money(user_id, winnings)
            economy.record_win(user_id)
            await ctx.reply(f"🎰 | 💎 💎 💎 |\n🌟🌟🌟 MEGA JACKPOT!!! 🌟🌟🌟\nu won **{winnings:,}** coins! (x{multiplier:,})", mention_author=False)
            return
        elif roll < 2.25:  # 2% chance (0.25% + 2%)
            multiplier = 100
            winnings = amount * multiplier
            economy.add_money(user_id, winnings)
            economy.record_win(user_id)
            await ctx.reply(f"🎰 | 7️⃣ 7️⃣ 7️⃣ |\n💰💰 SUPER JACKPOT! 💰💰\nu won **{winnings:,}** coins! (x{multiplier})", mention_author=False)
            return
        elif roll < 7.25:  # 5% chance (2.25% + 5%)
            multiplier = 50
            winnings = amount * multiplier
            economy.add_money(user_id, winnings)
            economy.record_win(user_id)
            await ctx.reply(f"🎰 | ⭐ ⭐ ⭐ |\n🎉 ULTRA JACKPOT! 🎉\nu won **{winnings:,}** coins! (x{multiplier})", mention_author=False)
            return
        
        # Normal slot machine
        emojis = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣"]
        
        slot1 = random.choice(emojis)
        slot2 = random.choice(emojis)
        slot3 = random.choice(emojis)
        
        # Calculate winnings
        if slot1 == slot2 == slot3:
            if slot1 == "💎":
                multiplier = 10
            elif slot1 == "7️⃣":
                multiplier = 7
            else:
                multiplier = 5
            winnings = amount * multiplier
            economy.add_money(user_id, winnings)
            economy.record_win(user_id)
            await ctx.reply(f"🎰 | {slot1} {slot2} {slot3} |\n🎉 JACKPOT! u won **{winnings:,}** coins! (x{multiplier})", mention_author=False)
        elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
            winnings = amount * 2
            economy.add_money(user_id, winnings - amount)
            economy.record_win(user_id)
            await ctx.reply(f"🎰 | {slot1} {slot2} {slot3} |\n✨ u won **{winnings:,}** coins! (x2)", mention_author=False)
        else:
            economy.remove_money(user_id, amount)
            economy.record_loss(user_id)
            await ctx.reply(f"🎰 | {slot1} {slot2} {slot3} |\n😔 u lost **{amount:,}** coins!", mention_author=False)
    
    @bot.command(name="taixiu", aliases=["tx", "dice"], help="play tai xiu (taixiu <tai/xiu> <amount>)")
    async def taixiu_cmd(ctx: commands.Context, bet_choice: str, amount: int) -> None:
        """Tài xỉu - Bet on dice roll total being Tài (11-18) or Xỉu (3-10)"""
        user_id = str(ctx.author.id)
        
        # Validate bet choice
        bet_choice = bet_choice.lower()
        if bet_choice not in ['tai', 'xiu', 'high', 'low', 'h', 'l']:
            return await ctx.reply("❌ choose **tai** (high) or **xiu** (low)!\nexample: `+taixiu tai 1000`", mention_author=False)
        
        # Normalize choice
        if bet_choice in ['tai', 'high', 'h']:
            bet_choice = 'tai'
        else:
            bet_choice = 'xiu'
        
        if amount <= 0:
            return await ctx.reply("amount must be > 0!", mention_author=False)
        
        is_infinity = economy.is_infinity(user_id)
        if not is_infinity and amount > economy.get_balance(user_id):
            return await ctx.reply("not enough money!", mention_author=False)
        
        import random
        
        # Roll 3 dice
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        dice3 = random.randint(1, 6)
        total = dice1 + dice2 + dice3
        
        # Determine result
        if total >= 11:
            result = 'tai'
            result_emoji = "🔴"
        else:
            result = 'xiu'
            result_emoji = "⚪"
        
        # Dice emojis
        dice_emoji_map = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
        dice_str = f"{dice_emoji_map[dice1]} {dice_emoji_map[dice2]} {dice_emoji_map[dice3]}"
        
        # Check win/loss
        if bet_choice == result:
            winnings = amount * 2
            economy.add_money(user_id, winnings - amount)
            economy.record_win(user_id)
            await ctx.reply(
                f"🎲 **TAI XIU** 🎲\n"
                f"{dice_str}\n"
                f"total: **{total}** {result_emoji} **{result.upper()}**\n"
                f"✅ u won **{winnings:,}** coins! (x2)",
                mention_author=False
            )
        else:
            economy.remove_money(user_id, amount)
            economy.record_loss(user_id)
            await ctx.reply(
                f"🎲 **TAI XIU** 🎲\n"
                f"{dice_str}\n"
                f"total: **{total}** {result_emoji} **{result.upper()}**\n"
                f"❌ u lost **{amount:,}** coins!",
                mention_author=False
            )
    
    @bot.command(name="bj", aliases=["blackjack"], help="play blackjack (bj <amount>)")
    async def blackjack_cmd(ctx: commands.Context, amount: int) -> None:
        user_id = str(ctx.author.id)
        
        if amount <= 0:
            return await ctx.reply("amount must be > 0!", mention_author=False)
        
        is_infinity = economy.is_infinity(user_id)
        if not is_infinity and amount > economy.get_balance(user_id):
            return await ctx.reply("not enough money!", mention_author=False)
        
        import random
        
        def card_value(card):
            if card in ['J', 'Q', 'K']:
                return 10
            elif card == 'A':
                return 11
            else:
                return int(card)
        
        def hand_value(hand):
            value = sum(card_value(card) for card in hand)
            aces = hand.count('A')
            while value > 21 and aces:
                value -= 10
                aces -= 1
            return value
        
        deck = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4
        random.shuffle(deck)
        
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]
        
        player_value = hand_value(player_hand)
        dealer_value = hand_value(dealer_hand)
        
        embed = discord.Embed(title="🃏 Blackjack", color=discord.Color.green())
        embed.add_field(name="Your Hand", value=f"{' '.join(player_hand)} = **{player_value}**", inline=False)
        embed.add_field(name="Dealer's Hand", value=f"{dealer_hand[0]} ❓", inline=False)
        
        if player_value == 21:
            winnings = int(amount * 2.5)
            economy.add_money(user_id, winnings)
            economy.record_win(user_id)
            embed.add_field(name="result", value=f"🎉 BLACKJACK! u won **{winnings:,}** coins!", inline=False)
            return await ctx.reply(embed=embed, mention_author=False)
        
        msg = await ctx.reply(embed=embed, mention_author=False)
        
        # Simple AI dealer logic
        while dealer_value < 17:
            dealer_hand.append(deck.pop())
            dealer_value = hand_value(dealer_hand)
        
        # Reveal dealer's hand
        embed.set_field_at(1, name="Dealer's Hand", value=f"{' '.join(dealer_hand)} = **{dealer_value}**", inline=False)
        
        if dealer_value > 21:
            winnings = amount * 2
            economy.add_money(user_id, winnings)
            economy.record_win(user_id)
            embed.add_field(name="result", value=f"🎉 dealer busts! u won **{winnings:,}** coins!", inline=False)
        elif player_value > dealer_value:
            winnings = amount * 2
            economy.add_money(user_id, winnings)
            economy.record_win(user_id)
            embed.add_field(name="result", value=f"🎉 u won **{winnings:,}** coins!", inline=False)
        elif player_value == dealer_value:
            embed.add_field(name="result", value=f"🤝 push! ur **{amount:,}** coins returned", inline=False)
        else:
            economy.remove_money(user_id, amount)
            economy.record_loss(user_id)
            embed.add_field(name="result", value=f"😔 dealer wins! u lost **{amount:,}** coins!", inline=False)
        
        await msg.edit(embed=embed)
    
    @bot.command(name="stats", aliases=["profile"], help="view ur stats")
    async def stats_cmd(ctx: commands.Context, member: discord.Member = None) -> None:
        member = member or ctx.author
        user_id = str(member.id)
        stats = economy.get_stats(user_id)
        
        is_infinity = economy.is_infinity(user_id)
        
        # For infinity users, show 100% winrate
        if is_infinity:
            total_games = 1000  # Show a reasonable number
            win_rate = 100.0
            stats["wins"] = 1000
            stats["losses"] = 0
        else:
            total_games = stats["wins"] + stats["losses"]
            win_rate = (stats["wins"] / total_games * 100) if total_games > 0 else 0
        
        level = stats.get("level", 1)
        xp = stats.get("xp", 0)
        xp_needed = economy.get_xp_for_level(level)
        streak = stats.get("daily_streak", 0)
        
        embed = discord.Embed(
            title=f"📊 {member.display_name}'s Profile",
            color=discord.Color.gold() if is_infinity else discord.Color.blue()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        
        # Level & XP
        if is_infinity:
            embed.add_field(name="📊 Level", value="**∞**", inline=True)
            embed.add_field(name="⭐ XP", value="**∞**", inline=True)
        else:
            embed.add_field(name="📊 Level", value=f"**{level}**", inline=True)
            embed.add_field(name="⭐ XP", value=f"**{xp}/{xp_needed}**", inline=True)
        embed.add_field(name="🔥 Daily Streak", value=f"**{streak}** days", inline=True)
        
        # Economy
        if is_infinity:
            embed.add_field(name="💰 Total Wealth", value="**∞** coins", inline=True)
        else:
            embed.add_field(name="💰 Total Wealth", value=f"**{stats['balance'] + stats['bank']:,}** coins", inline=True)
        embed.add_field(name="📈 Total Earned", value=f"**{stats['total_earned']:,}** coins", inline=True)
        embed.add_field(name="📉 Total Spent", value=f"**{stats['total_spent']:,}** coins", inline=True)
        
        # Casino Stats - show 100% winrate for infinity users
        if is_infinity:
            embed.add_field(name="🎮 Games Played", value=f"**{total_games}**", inline=True)
            embed.add_field(name="✅ Wins", value=f"**{stats['wins']}**", inline=True)
            embed.add_field(name="❌ Losses", value=f"**{stats['losses']}**", inline=True)
            embed.add_field(name="📊 Win Rate", value=f"**100.0%** 🏆", inline=True)
        else:
            embed.add_field(name="🎮 Games Played", value=f"**{total_games}**", inline=True)
            embed.add_field(name="✅ Wins", value=f"**{stats['wins']}**", inline=True)
            embed.add_field(name="❌ Losses", value=f"**{stats['losses']}**", inline=True)
            embed.add_field(name="📊 Win Rate", value=f"**{win_rate:.1f}%**", inline=True)
        
        if is_infinity:
            embed.set_footer(text="♾️ Infinity Mode Active - Unlimited Power!")
        
        await ctx.reply(embed=embed, mention_author=False)
    
    @bot.command(name="card", aliases=["profile-card", "pc"], help="Generate profile card image")
    async def card_cmd(ctx: commands.Context, member: discord.Member = None) -> None:
        member = member or ctx.author
        user_id = str(member.id)
        stats = economy.get_stats(user_id)
        
        # Get data
        is_infinity = economy.is_infinity(user_id)
        level = stats.get("level", 1)
        xp = stats.get("xp", 0)
        xp_needed = economy.get_xp_for_level(level)
        balance = stats.get("balance", 0)
        bank = stats.get("bank", 0)
        streak = stats.get("daily_streak", 0)
        wins = stats.get("wins", 0)
        losses = stats.get("losses", 0)
        
        # Get avatar URL
        avatar_url = member.display_avatar.url
        
        # Get equipped items
        equipped_ring_id = shop_system.get_equipped_item(str(member.id), "ring")
        equipped_pet_id = shop_system.get_equipped_item(str(member.id), "pet")
        
        equipped_ring_name = None
        equipped_pet_name = None
        
        if equipped_ring_id:
            ring_info = shop_system.get_item_info(equipped_ring_id)
            equipped_ring_name = ring_info["name"] if ring_info else None
        
        if equipped_pet_id:
            pet_info = shop_system.get_item_info(equipped_pet_id)
            equipped_pet_name = pet_info["name"] if pet_info else None
        
        # Get marriage partner
        partner_name = None
        if marriage_system.is_married(str(member.id)):
            partner_id = marriage_system.get_partner(str(member.id))
            try:
                partner = await bot.fetch_user(int(partner_id))
                partner_name = partner.display_name
            except:
                pass
        
        # Show typing indicator
        async with ctx.typing():
            try:
                # Generate card
                card_image = await profile_card_generator.generate_profile_card(
                    username=member.display_name,
                    avatar_url=avatar_url,
                    level=level,
                    xp=xp,
                    xp_needed=xp_needed,
                    balance=balance,
                    bank=bank,
                    streak=streak,
                    wins=wins,
                    losses=losses,
                    is_infinity=is_infinity,
                    equipped_ring=equipped_ring_name,
                    equipped_pet=equipped_pet_name,
                    partner_name=partner_name
                )
                
                # Send as file
                file = discord.File(card_image, filename=f"{member.name}_profile.png")
                await ctx.reply(file=file, mention_author=False)
                
            except Exception as e:
                await ctx.reply(f"❌ error creating profile card: {e}", mention_author=False)
                logging.exception("Error generating profile card")
    
    @bot.command(name="setlevel", help="set user level (owner only)")
    async def setlevel_cmd(ctx: commands.Context, member: discord.Member = None, level: int = None) -> None:
        if ctx.author.id not in OWNER_IDS:
            await ctx.reply("owner only!", mention_author=False)
            return
        
        if not member:
            prefix = prefix_system.get_prefix(str(ctx.guild.id)) if ctx.guild else "!"
            await ctx.reply(f"❌ please tag user! example: `{prefix}setlevel @user 5`", mention_author=False)
            return
        
        if member.bot:
            await ctx.reply("❌ cant set level for bots!", mention_author=False)
            return
        
        if level is None:
            prefix = prefix_system.get_prefix(str(ctx.guild.id)) if ctx.guild else "!"
            await ctx.reply(f"❌ please enter level! example: `{prefix}setlevel @user 5`", mention_author=False)
            return
        
        if level < 1:
            await ctx.reply("❌ level must be > 0!", mention_author=False)
            return
        
        user_id = str(member.id)
        economy.set_level(user_id, level)
        if level > 1:
            economy.set_infinity(user_id, False)  # Remove infinity if setting specific level
            await ctx.reply(f"✅ set **Level {level}** for {member.mention}!", mention_author=False)
    
    @bot.command(name="setinfinity", aliases=["setinf"], help="set infinity mode (owner only)")
    async def setinfinity_cmd(ctx: commands.Context, member: discord.Member = None) -> None:
        if ctx.author.id not in OWNER_IDS:
            await ctx.reply("owner only!", mention_author=False)
            return
        
        if not member:
            prefix = prefix_system.get_prefix(str(ctx.guild.id)) if ctx.guild else "!"
            await ctx.reply(f"❌ please tag user! example: `{prefix}setinfinity @user`", mention_author=False)
            return
        
        if member.bot:
            await ctx.reply("❌ cant set infinity for bots!", mention_author=False)
            return
        
        user_id = str(member.id)
        is_infinity = economy.is_infinity(user_id)
        
        if not is_infinity:
            economy.set_infinity(user_id, True)
            await ctx.reply(f"✅ enabled **∞ mode** for {member.mention}!", mention_author=False)
        else:
            await ctx.reply(f"✅ disabled **∞ mode** for {member.mention}!", mention_author=False)
    
    @bot.command(name="listinfinity", aliases=["infinitylist", "inflist"], help="view infinity users (owner only)")
    async def list_infinity_cmd(ctx: commands.Context) -> None:
        if ctx.author.id not in OWNER_IDS:
            await ctx.reply("owner only!", mention_author=False)
            return
        
        infinity_users = []
        for user_id, user_data in economy.data.items():
            if user_data.get("infinity", False):
                try:
                    user = await bot.fetch_user(int(user_id))
                    infinity_users.append(user)
                except:
                    pass
        
        if not infinity_users:
            await ctx.reply("🚫 no **infinity mode** users yet!", mention_author=False)
            return
        
        embed = discord.Embed(
            title="🔥 INFINITY USERS",
            description="users with **infinity mode**:",
            color=discord.Color.gold()
        )
        
        user_list = []
        for idx, user in enumerate(infinity_users[:20], 1):  # Limit to 20
            user_list.append(f"{idx}. {user.name} (`{user.id}`)")
        
        if user_list:
            embed.add_field(name="Users", value="\n".join(user_list), inline=False)
        
        if len(infinity_users) > 20:
            embed.set_footer(text=f"and {len(infinity_users) - 20} more...")
        
        await ctx.reply(embed=embed, mention_author=False)
    
    @bot.command(name="leaderboard", aliases=["lb", "top"], help="richest leaderboard")
    async def leaderboard_cmd(ctx: commands.Context) -> None:
        # Sort users by total wealth
        sorted_users = sorted(
            economy.data.items(),
            key=lambda x: x[1]['balance'] + x[1]['bank'],
            reverse=True
        )[:10]
        
        if not sorted_users:
            await ctx.reply("no data yet!", mention_author=False)
            return
        
        embed = discord.Embed(
            title="💰 RICHEST LEADERBOARD",
            color=discord.Color.gold()
        )
        
        description = []
        for idx, (user_id, data) in enumerate(sorted_users, 1):
            try:
                user = await bot.fetch_user(int(user_id))
                total = data["balance"] + data["bank"]
                medal = ["🥇", "🥈", "🥉"][idx-1] if idx <= 3 else f"**{idx}.**"
                description.append(f"{medal} {user.name} - **{total:,}** coins")
            except:
                continue
        
        embed.description = "\n".join(description) if description else "No data yet!"
        await ctx.reply(embed=embed, mention_author=False)
    
    # ==================== AFK SYSTEM ====================
    
    @bot.command(name="afk", help="set AFK status")
    async def afk_cmd(ctx: commands.Context, *, reason: str = None) -> None:
        user_id = str(ctx.author.id)
        afk_system.set_afk(user_id, reason)
        
        if reason:
            await ctx.reply(f"💤 set AFK: **{reason}**", mention_author=False)
        else:
            await ctx.reply("💤 set AFK!", mention_author=False)

    # ==================== PREFIX SYSTEM ====================
    
    @bot.command(name="prefix", help="view or set custom prefix")
    async def prefix_cmd(ctx: commands.Context, new_prefix: str = None) -> None:
        if not ctx.guild:
            await ctx.reply("this command only works in servers!", mention_author=False)
            return
        
        guild_id = str(ctx.guild.id)
        current_prefix = prefix_system.get_prefix(guild_id)
        
        # Just view current prefix
        if new_prefix is None:
            await ctx.reply(f"current prefix: `{current_prefix}`", mention_author=False)
            return
        
        # Set new prefix (admin only)
        if not ctx.author.guild_permissions.administrator:
            await ctx.reply("only admins can change the prefix!", mention_author=False)
            return
        
        if len(new_prefix) > 10:
            await ctx.reply("prefix too long! max 10 characters", mention_author=False)
            return
        
        prefix_system.set_prefix(guild_id, new_prefix)
        await ctx.reply(f"✅ prefix changed to `{new_prefix}`", mention_author=False)
    
    @bot.command(name="resetprefix", help="reset prefix to default (!)")
    async def reset_prefix_cmd(ctx: commands.Context) -> None:
        if not ctx.guild:
            await ctx.reply("this command only works in servers!", mention_author=False)
            return
        
        if not ctx.author.guild_permissions.administrator:
            await ctx.reply("only admins can reset the prefix!", mention_author=False)
            return
        
        guild_id = str(ctx.guild.id)
        prefix_system.reset_prefix(guild_id)
        await ctx.reply("✅ prefix reset to default: `!`", mention_author=False)

    # ==================== MUTE SYSTEM ====================
    
    @bot.command(name="mute", help="mute user for specified time (mod only)")
    async def mute_cmd(ctx: commands.Context, member: discord.Member, duration: int, *, reason: str = None) -> None:
        if not ctx.guild:
            await ctx.reply("this command only works in servers!", mention_author=False)
            return
        
        # Check permissions
        if not ctx.author.guild_permissions.moderate_members:
            await ctx.reply("u need moderate members permission!", mention_author=False)
            return
        
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)
        
        # Mute user
        mute_system.mute_user(guild_id, user_id, duration, reason)
        
        reason_text = f" reason: **{reason}**" if reason else ""
        await ctx.reply(f"🔇 muted {member.mention} for **{duration} minutes**{reason_text}", mention_author=False)
    
    @bot.command(name="unmute", help="unmute user (mod only)")
    async def unmute_cmd(ctx: commands.Context, member: discord.Member) -> None:
        if not ctx.guild:
            await ctx.reply("this command only works in servers!", mention_author=False)
            return
        
        # Check permissions
        if not ctx.author.guild_permissions.moderate_members:
            await ctx.reply("u need moderate members permission!", mention_author=False)
            return
        
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)
        
        if mute_system.unmute_user(guild_id, user_id):
            await ctx.reply(f"🔊 unmuted {member.mention}", mention_author=False)
        else:
            await ctx.reply(f"{member.mention} is not muted!", mention_author=False)
    
    @bot.command(name="checkmute", help="check if user is muted")
    async def checkmute_cmd(ctx: commands.Context, member: discord.Member = None) -> None:
        if not ctx.guild:
            await ctx.reply("this command only works in servers!", mention_author=False)
            return
        
        member = member or ctx.author
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)
        
        mute_info = mute_system.get_mute_info(guild_id, user_id)
        
        if mute_info:
            embed = discord.Embed(
                title=f"🔇 {member.name} is muted",
                color=discord.Color.red()
            )
            embed.add_field(name="time left", value=mute_info["time_left"], inline=True)
            embed.add_field(name="duration", value=f"{mute_info['duration_minutes']} min", inline=True)
            embed.add_field(name="reason", value=mute_info["reason"], inline=False)
            embed.add_field(name="unmute at", value=mute_info["mute_until"], inline=False)
            await ctx.reply(embed=embed, mention_author=False)
        else:
            await ctx.reply(f"{member.mention} is not muted!", mention_author=False)
    
    @bot.command(name="mutelist", help="list all muted users")
    async def mutelist_cmd(ctx: commands.Context) -> None:
        if not ctx.guild:
            await ctx.reply("this command only works in servers!", mention_author=False)
            return
        
        guild_id = str(ctx.guild.id)
        muted_users = mute_system.get_all_muted(guild_id)
        
        if not muted_users:
            await ctx.reply("no users are muted rn!", mention_author=False)
            return
        
        embed = discord.Embed(
            title=f"🔇 muted users in {ctx.guild.name}",
            color=discord.Color.red()
        )
        
        for muted in muted_users[:10]:  # Limit to 10
            user = ctx.guild.get_member(int(muted["user_id"]))
            username = user.name if user else f"user {muted['user_id']}"
            embed.add_field(
                name=username,
                value=f"⏰ {muted['time_left']} left\n📝 {muted['reason']}",
                inline=False
            )
        
        if len(muted_users) > 10:
            embed.set_footer(text=f"showing 10/{len(muted_users)} muted users")
        
        await ctx.reply(embed=embed, mention_author=False)

    # ==================== COMMAND DISABLE SYSTEM (SLASH COMMANDS) ====================
    
    class DisableCommandSelect(discord.ui.Select):
        def __init__(self, channel_id: str):
            self.channel_id = channel_id
            
            # Get all commands grouped by category
            all_commands = disable_system.get_all_commands()
            currently_disabled = set(disable_system.get_disabled_commands(channel_id))
            
            options = []
            for cmd in sorted(all_commands)[:25]:  # Discord limit 25 options
                is_disabled = cmd in currently_disabled
                options.append(discord.SelectOption(
                    label=f"+{cmd}",
                    value=cmd,
                    description="✅ Enabled" if not is_disabled else "❌ Disabled",
                    emoji="✅" if not is_disabled else "❌"
                ))
            
            super().__init__(
                placeholder="select command to disable/enable...",
                min_values=1,
                max_values=len(options),
                options=options
            )
        
        async def callback(self, interaction: discord.Interaction):
            disabled_count = 0
            enabled_count = 0
            
            for command in self.values:
                if disable_system.is_disabled(self.channel_id, command):
                    # Already disabled, enable it
                    disable_system.enable_command(self.channel_id, command)
                    enabled_count += 1
                else:
                    # Not disabled, disable it
                    disable_system.disable_command(self.channel_id, command)
                    disabled_count += 1
            
            msg = []
            if disabled_count > 0:
                msg.append(f"✅ disabled **{disabled_count}** commands")
            if enabled_count > 0:
                msg.append(f"✅ enabled **{enabled_count}** commands")
            
            await interaction.response.send_message("\n".join(msg), ephemeral=True)
    
    class DisableCommandView(discord.ui.View):
        def __init__(self, channel_id: str):
            super().__init__(timeout=60)
            self.add_item(DisableCommandSelect(channel_id))
    
    @bot.tree.command(name="disable", description="disable/enable command in channel (owner only)")
    async def disable_command_slash(interaction: discord.Interaction):
        # Check if user is owner
        if interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("❌ owner only!", ephemeral=True)
            return
        
        channel_id = str(interaction.channel_id)
        view = DisableCommandView(channel_id)
        
        await interaction.response.send_message(
            "🔧 select command to toggle disable/enable:",
            view=view,
            ephemeral=True
        )
    
    @bot.tree.command(name="disabled", description="view disabled commands in this channel")
    async def list_disabled_slash(interaction: discord.Interaction):
        channel_id = str(interaction.channel_id)
        disabled = disable_system.get_disabled_commands(channel_id)
        
        if not disabled:
            await interaction.response.send_message("✅ no commands are disabled in this channel!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"🚫 disabled commands in #{interaction.channel.name}",
            description="\n".join([f"• `+{cmd}`" for cmd in disabled]),
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @bot.tree.command(name="clearall", description="clear all disabled commands in this channel (owner only)")
    async def clear_disabled_slash(interaction: discord.Interaction):
        # Check if user is owner
        if interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("❌ owner only!", ephemeral=True)
            return
        
        channel_id = str(interaction.channel_id)
        
        if disable_system.clear_channel(channel_id):
            await interaction.response.send_message("✅ cleared all disabled commands in this channel!", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ no commands are disabled in this channel!", ephemeral=True)

    # XP cooldown tracker (prevent spam)
    xp_cooldowns = {}
    
    @bot.event
    async def on_message(message: discord.Message) -> None:
        if message.author.bot:
            return

        user_id = str(message.author.id)
        
        # XP system - gain XP from chatting (with cooldown)
        import time
        current_time = time.time()
        if user_id not in xp_cooldowns or current_time - xp_cooldowns[user_id] >= 60:  # 1 minute cooldown
            # Give random XP (5-15 per message)
            import random
            xp_gain = random.randint(5, 15)
            
            # Get current level
            user_data = economy.get_user(user_id)
            old_level = user_data.get("level", 1)
            
            # Add XP
            new_level = economy.add_xp(user_id, xp_gain)
            if new_level is None:
                new_level = old_level
            
            # Level up notification
            if new_level > old_level:
                # Calculate level up rewards
                levels_gained = new_level - old_level
                
                # Money reward: level * 2000 coins per level
                money_reward = 0
                for lv in range(old_level + 1, new_level + 1):
                    money_reward += lv * 2000
                
                # Add 3% permanent daily bonus per level
                user_data = economy.get_user(user_id)
                if "level_daily_bonus" not in user_data:
                    user_data["level_daily_bonus"] = 0.0
                user_data["level_daily_bonus"] += levels_gained * 3.0  # 3% per level
                economy.save_data()
                
                # Give money reward
                economy.add_money(user_id, money_reward)
                
                embed = discord.Embed(
                    title="🎉 LEVEL UP!",
                    description=f"{message.author.mention} leveled up to **{new_level}**!",
                    color=discord.Color.gold()
                )
                embed.add_field(name="💰 money reward", value=f"**{money_reward:,}** coins", inline=True)
                embed.add_field(name="📈 daily bonus", value=f"+**{levels_gained * 3}%** (permanent)", inline=True)
                embed.add_field(name="💎 total daily bonus", value=f"**{user_data['level_daily_bonus']:.1f}%**", inline=True)
                await message.channel.send(embed=embed, delete_after=15)
            
            xp_cooldowns[user_id] = current_time
        
        # Check if user is returning from AFK
        if afk_system.is_afk(user_id):
            duration = afk_system.get_afk_duration(user_id) or "a few seconds"
            afk_data = afk_system.remove_afk(user_id)
            await message.channel.send(
                f"👋 welcome back {message.author.mention}! u were AFK for **{duration}**",
                delete_after=5
            )
        
        # Check if message mentions someone who is AFK
        for mentioned in message.mentions:
            mentioned_id = str(mentioned.id)
            if afk_system.is_afk(mentioned_id):
                afk_data = afk_system.get_afk(mentioned_id)
                reason = afk_data.get("reason", "AFK")
                
                # Just show the reason text
                await message.channel.send(reason, delete_after=10)

        try:
            await ai.ai_handle_message(bot, message)
        except Exception:
            logging.exception("error processing message with AI")

        await bot.process_commands(message)
    
    @bot.event
    async def on_command_error(ctx: commands.Context, error: commands.CommandError) -> None:
        """Handle command errors"""
        # Ignore commands from DMs that don't exist
        if isinstance(error, commands.CommandNotFound):
            # Check if message starts with a common prefix pattern
            if ctx.message.content and len(ctx.message.content) > 1:
                first_char = ctx.message.content[0]
                if first_char in ['!', '+', '>', '.', '/', '-', '=']:
                    await ctx.send("bro wdym =)", delete_after=5)
            return
        
        # Let other errors pass through for logging
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("u dont have permission for that!", mention_author=False, delete_after=5)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(f"missing argument: `{error.param.name}`", mention_author=False, delete_after=5)
        else:
            # Log unexpected errors
            logging.error(f"Command error: {error}", exc_info=error)
