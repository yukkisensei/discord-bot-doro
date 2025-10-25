# Doro Discord Bot 🌸

An adorable multi-purpose Discord bot with music, economy, casino games, marriage system, and AI chat features!

## ✨ Key Features

### 🎵 Music System
- Stream music from SoundCloud
- Queue management with skip, pause, resume
- Auto-leave after inactivity
- Now playing display

### 💰 Economy System  
- Daily rewards (1200-1800 coins base)
- Streak bonus system (0.25% per day)
- Level progression with XP
- Bank deposit/withdraw
- Money transfer between users

### 🎰 Casino Games
- **Coinflip** - Classic heads or tails betting
- **Slots** - 3-reel slot machine with jackpots
- **Roulette** - Red/black/number betting
- **Blackjack** - Full blackjack experience with hit/stand

### 🏪 Shop System
- Various items to purchase:
  - 💍 Wedding rings (for marriage system)
  - 📦 Loot boxes with random rewards
  - 🍀 Lucky items for casino bonuses
  - 🎀 Cosmetic items and collectibles
- Inventory management
- Item equipping and usage

### 💍 Marriage System
- Propose to other users (requires ring)
- Accept/reject proposals
- Marriage status display
- Divorce option available

### 🤖 AI Chat
- Mention @Doro for cute AI conversations
- NVIDIA-powered responses
- Personality adapts based on user
- Remembers conversation context

### 🎮 Fun Commands
- Text transformations (OwO, UwU, mock text)
- Random dice rolls
- User profiles with beautiful cards
- AFK system with auto-reply

## 🚀 Quick Setup

### Prerequisites
- Python 3.12.10 (exact version recommended)
- Discord Bot Token
- API Keys (optional):
  - NVIDIA API key (for AI chat)
  - OpenRouter API key (for Takopi AI)

### Installation

1. Clone or download the bot files

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file with your tokens:
```env
DISCORD_BOT_TOKEN=your_bot_token_here
NVIDIA_API_KEY=your_nvidia_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
BOT_OWNER_IDS=your_discord_id_here
```

4. Run the bot:
```bash
python main.py
```

## 📝 Command List

### Music Commands
- `+play [song]` - Play or queue a song
- `+skip` - Skip current song
- `+queue` - View queue
- `+pause/resume` - Pause/resume playback
- `+stop` - Stop and clear queue
- `+np` - Now playing

### Economy Commands
- `+balance [@user]` - Check balance
- `+daily` - Claim daily reward
- `+deposit [amount]` - Deposit to bank
- `+withdraw [amount]` - Withdraw from bank
- `+give @user [amount]` - Transfer money (10% fee)

### Casino Commands
- `+coinflip [h/t] [bet]` - Flip a coin
- `+slots [bet]` - Play slots
- `+roulette [color/number] [bet]` - Play roulette
- `+blackjack [bet]` - Play blackjack

### Shop Commands
- `+shop [page/category]` - Browse shop
- `+buy [item]` - Purchase item
- `+inventory [@user]` - View inventory
- `+use [item]` - Use an item
- `+equip [item]` - Equip an item

### Marriage Commands
- `+marry @user` - Propose (needs ring)
- `+accept` - Accept proposal
- `+reject` - Reject proposal
- `+divorce` - End marriage
- `+marriage [@user]` - View marriage info

### Utility Commands
- `+help [category]` - View commands by category
- `+avatar [@user]` - Get user avatar
- `+serverinfo` - Server information
- `+userinfo [@user]` - User information
- `+card [@user]` - Generate profile card
- `+afk [reason]` - Set AFK status

### Fun Commands
- `+owo [text]` - OwOify text
- `+uwu [text]` - UwUify text
- `+mock [text]` - mOcK tExT
- `+roll [max]` - Roll dice

### AI Chat
- **@Doro [message]** - Chat with Doro AI
- `+takopi [message]` - Chat with Takopi AI

## ⚙️ Configuration

### Setting Bot Owners
Add Discord IDs in `.env`:
```env
BOT_OWNER_IDS=id1,id2,id3
```

### Customizing Economy
Edit values in `economy.py`:
- Starting balance
- Daily reward amounts  
- Level XP requirements
- Casino win rates

### Adjusting Shop Prices
Modify prices in `shop_system.py`:
- Ring prices
- Loot box costs
- Item effects

### AI Personality
Customize Doro's personality in `ai.py`:
- Response style
- Emoji usage
- Owner vs regular user behavior

## 🎨 Features Highlights

### Beautiful Profile Cards
- Custom designed cards with user stats
- Level and XP progress bars
- Marriage status display
- Economy statistics
- Badges and achievements

### Smart AI Responses  
- Context-aware conversations
- Personality that adapts to users
- Cute and playful responses
- Emoji reactions

### Streak System
- Daily login streaks
- Increasing rewards for consistency
- Bonus multipliers
- Level-based bonuses

## 🐛 Troubleshooting

### Bot not responding
- Check bot has required intents enabled
- Verify prefix is `+` 
- Ensure bot has permissions in channel

### Music not playing
- Verify ffmpeg is installed
- Check voice channel permissions
- Ensure SoundCloud links are valid

### AI not working
- Confirm API keys in `.env`
- Check API rate limits
- Verify internet connection

### Economy issues
- Data saves in JSON files
- Check file permissions
- Backup data regularly

## 📚 Data Storage

All data is stored locally in JSON files:
- `economy_data.json` - User balances and stats
- `shop_data.json` - Shop inventory
- `user_inventory.json` - User items
- `marriage_data.json` - Marriage records
- `afk_data.json` - AFK statuses
- `disabled_commands.json` - Disabled commands

## 🎯 Tips & Tricks

1. **Daily Streaks** - Don't break your streak for maximum rewards!
2. **Shop Strategy** - Buy rings before proposing
3. **Casino Tips** - Start with small bets
4. **Level Up** - Gain XP from daily claims and activities
5. **Profile Cards** - Customize your card with achievements

## 🌟 Special Features

- **Infinity Mode** - Owners get unlimited resources
- **Command Disabling** - Disable specific commands per server
- **Auto AFK** - Automatically set AFK when mentioned
- **Smart Help** - Category-based help system
- **Fast Response** - Optimized for quick reactions

---

> **Note:** I've already modified this bot so you can easily customize it into any bot you want. If you don't know how to do it, just give it to AI. If that fails... too bad! 😝

## 📄 License

Free to use, modify, and distribute. No attribution required.

## 🤝 Credits

- Powered by Discord.py
- AI by NVIDIA 
- Made with 💖 by Doro

---
*Doro Bot - Your Cute Discord Companion!*
