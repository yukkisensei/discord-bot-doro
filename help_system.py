import discord
from discord.ext import commands

def build_help_embed(category: str = None, bot=None, prefix: str = "!", is_owner: bool = False) -> discord.Embed:
    """Build help embed with category support"""
    
    categories = {
        "music": {
            "title": "🎶 Music Commands",
            "description": "music player commands",
            "commands": [
                f"`{prefix}play [query]` – play music from SoundCloud",
                f"`{prefix}skip` – skip current track",
                f"`{prefix}queue` – view queue",
                f"`{prefix}pause` – pause music",
                f"`{prefix}resume` – resume music",
                f"`{prefix}stop` – stop and clear queue",
                f"`{prefix}np` – now playing",
                f"`{prefix}leave` – bot leave voice (owner only)"
            ]
        },
        "economy": {
            "title": "💰 Economy Commands", 
            "description": "money & currency commands",
            "commands": [
                f"`{prefix}balance [@user]` – check balance",
                f"`{prefix}daily` – daily reward (2000-3500 coins)",
                f"`{prefix}deposit [amount]` – deposit to bank",
                f"`{prefix}withdraw [amount]` – withdraw from bank",
                f"`{prefix}give @user <amount>` – give money (10% fee)"
            ]
        },
        "casino": {
            "title": "🎰 Casino Commands",
            "description": "gambling games",
            "commands": [
                f"`{prefix}cf [h/t] [bet]` – coinflip ",
                f"`{prefix}slots [bet]` – slot machine ",
                f"`{prefix}taixiu [tài/xỉu] [bet]` – dice game (tai xiu) ",
                f"`{prefix}bj [bet]` – blackjack "
            ]
        },
        "shop": {
            "title": "🏪 Shop Commands",
            "description": "shopping & items",
            "commands": [
                f"`{prefix}shop [page/category]` – view shop items",
                f"`{prefix}buy [ID/name]` – buy items",
                f"`{prefix}inventory [@user]` – view inventory",
                f"`{prefix}use [ID/name]` – use item",
                f"`{prefix}equip [ID/name]` – equip item",
                f"`{prefix}about [category]` – item details"
            ]
        },
        "marriage": {
            "title": "💍 Marriage Commands",
            "description": "marriage system",
            "commands": [
                f"`{prefix}marry @user` – propose (need ring) 💍",
                f"`{prefix}accept` – accept proposal ✅",
                f"`{prefix}reject` – reject proposal ❌",
                f"`{prefix}divorce` – divorce 💔",
                f"`{prefix}marriage [@user]` – marriage info 💑"
            ]
        },
        "ai": {
            "title": "🤖 AI Commands",
            "description": "AI chat",
            "commands": [
                "**@Doro** [message] – chat with Doro AI (cute & friendly)",
                f"`{prefix}reset` – clear AI chat history"
            ]
        },
        "fun": {
            "title": "🎮 Fun Commands",
            "description": "fun & games",
            "commands": [
                f"`{prefix}roll [dice]` – roll dice (e.g. 2d6)",
                f"`{prefix}cf` – flip a coin",
                f"`{prefix}rps [choice]` – rock paper scissors",
                f"`{prefix}8ball [question]` – magic 8ball"
            ]
        },
        "wordchain": {
            "title": "🔗 Word Chain Game",
            "description": "creative word connection game (any language!)",
            "commands": [
                f"`{prefix}wordchain` – view game info & status",
                f"`{prefix}wordchain enable` – enable in channel (admin)",
                f"`{prefix}wordchain disable` – disable in channel (admin)",
                f"`{prefix}wordchain restart` – restart chain",
                f"`{prefix}wordchain rules` – view game rules",
                f"`{prefix}wordchain stats` – your stats",
                f"`{prefix}wordchain leaderboard` – top players",
                "",
                "**How to play:**",
                "• Just type words in enabled channel!",
                "• Bot reacts ✅ (valid) or ❌ (invalid)",
                "• Connect via last letters OR meaning",
                "• English, Vietnamese, any language OK!",
                "",
                "**Examples:**",
                "• sky → heaven (meaning) ✅",
                "• thiên → thiên hà (Vietnamese) ✅",
                "• galaxy → universe (related) ✅"
            ]
        },
        "utility": {
            "title": "⚙️ Utility Commands",
            "description": "utility & info",
            "commands": [
                f"`{prefix}help [category]` – show help",
                f"`{prefix}prefix [new_prefix]` – view/set custom prefix (admin)",
                f"`{prefix}resetprefix` – reset prefix to ! (admin)",
                f"`{prefix}avatar [@user]` – show avatar",
                f"`{prefix}serverinfo` – server info",
                f"`{prefix}userinfo [@user]` – user info",
                f"`{prefix}card [@user]` – profile card (beautiful!)",
                f"`{prefix}afk [reason]` – set AFK status",
                f"`{prefix}stats [@user]` – user stats"
            ]
        },
        "moderation": {
            "title": "🛡️ Moderation Commands",
            "description": "moderation tools (mods only)",
            "commands": [
                f"`{prefix}mute @user <minutes> [reason]` – mute user",
                f"`{prefix}unmute @user` – unmute user",
                f"`{prefix}checkmute [@user]` – check mute status",
                f"`{prefix}mutelist` – list all muted users"
            ]
        },
        "owner": {
            "title": "👑 Owner Commands",
            "description": "owner-only commands",
            "commands": [
                f"`{prefix}say [text]` – send message as bot",
                f"`{prefix}say -r <msg_id> <emojis>` – react to message",
                f"`{prefix}say -re <msg_id> <text>` – reply with ping",
                f"`{prefix}say -rs <msg_id> <text>` – reply without ping",
                f"`{prefix}sync` – sync slash commands",
                f"`{prefix}model [name]` – view/change AI model",
                f"`{prefix}setlevel @user <level>` – set user level",
                f"`{prefix}setinfinity @user` – toggle infinity mode"
            ]
        }
    }
    
    if category and category.lower() in categories:
        # Prevent non-owners from viewing owner category
        if category.lower() == "owner" and not is_owner:
            embed = discord.Embed(
                title="❌ Access Denied",
                description="This category is only available to bot owners.",
                color=discord.Color.red()
            )
            return embed
        
        cat_data = categories[category.lower()]
        embed = discord.Embed(
            title=cat_data["title"],
            description=cat_data["description"],
            color=discord.Color.pink()
        )
        embed.set_thumbnail(url="https://i.imgur.com/UFyXMeo.png")
        embed.add_field(
            name="📋 command list",
            value="\n".join(cat_data["commands"]),
            inline=False
        )
        embed.set_footer(text=f"use {prefix}help to view all categories")
    else:
        # Main help menu
        embed = discord.Embed(
            title="🌸 Doro Bot - Help Menu",
            description="the cutest multi-function Discord bot!\n" +
                       f"use `{prefix}help [category]` to view detailed command groups",
            color=discord.Color.pink()
        )
        embed.set_author(name="Doro Bot", icon_url="https://i.imgur.com/UFyXMeo.png")
        
        categories_text = (
            f"`{prefix}help music` - 🎶 music commands\n"
            f"`{prefix}help economy` - 💰 economy commands\n"
            f"`{prefix}help casino` - 🎰 casino commands\n"
            f"`{prefix}help shop` - 🏪 shop commands\n"
            f"`{prefix}help marriage` - 💍 marriage commands\n"
            f"`{prefix}help wordchain` - 🔗 word chain game\n"
            f"`{prefix}help ai` - 🤖 AI commands\n"
            f"`{prefix}help fun` - 🎮 fun commands\n"
            f"`{prefix}help utility` - ⚙️ utility commands\n"
            f"`{prefix}help moderation` - 🛡️ moderation commands"
        )
        
        # Add owner category only for owners
        if is_owner:
            categories_text += f"\n`{prefix}help owner` - 👑 owner commands"
        
        embed.add_field(
            name="📚 Categories",
            value=categories_text,
            inline=False
        )
        
        embed.add_field(
            name="✨ features",
            value=(
                "• 🎵 SoundCloud music player\n"
                "• 💰 economy system with daily rewards\n"
                "• 🎰 full casino games\n"
                "• 💍 marriage system\n"
                "• 🔗 word chain game (multi-language!)\n"
                "• 🤖 smart AI chat\n"
                "• 🎨 beautiful profile cards"
            ),
            inline=False
        )
        
        embed.set_footer(text=f"prefix: {prefix} | made with 💖 by doro")
    
    return embed
