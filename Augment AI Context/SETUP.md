# Paimon Discord Bot Setup Guide

Paimon is an AI Discord bot that provides contextual announcements and chat interactions for the Bimbo Hunter game.

## 🎯 What Paimon Does

### Smart Announcements
- **Rare Claims**: "Incredible! Sarah just claimed Tsunade - a Super Super Rare! ⭐"
- **Rapid Claiming**: "🔥 Mike is on fire! That's 3 squares in the last hour!"
- **First Claims**: Special celebration for new players' first rare catches
- **Daily Summaries**: End-of-day leaderboard and highlights (9 PM)
- **Player Encouragement**: Gentle nudges for inactive players

### Chat Interactions
Players can ask questions like:
- "Who's in the lead?" → Current leaderboard
- "What's my score?" → Personal progress
- "How am I doing?" → Recent activity
- "Help" → Game rules and instructions

## 🚀 Quick Setup

### 1. Install Discord Bot Dependencies
```bash
pip install discord.py python-dotenv
```

### 2. Create Discord Bot
1. Go to https://discord.com/developers/applications
2. Create a new application and bot
3. Copy the bot token
4. Enable "Message Content Intent" in Bot settings
5. Invite bot to your server with "Send Messages" permission

### 3. Configure Paimon
```bash
cd p(ai)mon
cp .env.example .env
# Edit .env with your Discord bot token and channel ID
```

### 4. Test Components (Optional)
```bash
cd p(ai)mon
python test_components.py
```

### 5. Start Paimon
From the main project directory:
```bash
python start_paimon.py
```

Or from the paimon directory:
```bash
cd p(ai)mon
python start_paimon.py
```

## 📋 Detailed Setup

### Discord Bot Creation
1. **Create Application**: Go to https://discord.com/developers/applications
2. **Create Bot**: Navigate to "Bot" section and create a bot
3. **Get Token**: Copy the bot token (keep this secret!)
4. **Enable Intents**: Enable "Message Content Intent" in Bot settings
5. **Generate Invite URL**: 
   - Go to OAuth2 > URL Generator
   - Select "bot" scope
   - Select "Send Messages" and "Read Message History" permissions
   - Use the generated URL to invite the bot to your server

### Environment Configuration
Create `p(ai)mon/.env` with:
```env
DISCORD_TOKEN=your_bot_token_here
DISCORD_CHANNEL_ID=your_channel_id_here
GAME_API_BASE_URL=http://localhost:5000/api
```

To get your channel ID:
1. Enable Developer Mode in Discord (User Settings > Advanced)
2. Right-click on your channel
3. Select "Copy ID"

### Running Alongside the Game
Paimon works best when run alongside the main game:

**Terminal 1 - Game Server:**
```bash
./start-app.sh
# or
npm start
```

**Terminal 2 - Paimon Bot:**
```bash
python start_paimon.py
```

## ⚙️ Configuration

Edit `p(ai)mon/config.py` to customize:

### Timing Settings
- `MONITORING_INTERVAL`: How often to check for changes (default: 30 seconds)
- `ANNOUNCEMENT_COOLDOWN`: Minimum time between similar announcements (5 minutes)
- `DAILY_SUMMARY_HOUR`: When to send daily summaries (default: 9 PM)
- `QUIET_HOURS_START/END`: No announcements during these hours (2 AM - 8 AM)

### Announcement Thresholds
- `RAPID_CLAIM_THRESHOLD`: Claims needed for "on fire" announcement (default: 3)
- `RAPID_CLAIM_WINDOW`: Time window for rapid claiming (default: 1 hour)
- `RARE_CLAIM_THRESHOLD`: Minimum rarity to announce (default: SSR)

### Personality
- `PERSONALITY_RESPONSES`: Customize Paimon's chat responses
- Add new keywords to `GAME_KEYWORDS` for better chat recognition

## 🧪 Testing

### Component Testing
```bash
cd p(ai)mon
python test_components.py
```

This tests all bot components without requiring Discord connection.

### Manual Testing
1. Start the bot
2. Send messages in your Discord channel:
   - "Who's in the lead?"
   - "What's my score?"
   - "Help"
3. Make progress in the game to trigger announcements

## 🔧 Troubleshooting

### Bot Not Starting
- **Missing dependencies**: Run `pip install discord.py python-dotenv`
- **Invalid token**: Check your Discord bot token in `.env`
- **Wrong channel ID**: Verify the channel ID in `.env`

### No Announcements
- **Game not running**: Ensure the main game is running on localhost:5000
- **Quiet hours**: Check if it's between 2-8 AM (quiet hours)
- **No activity**: Announcements only trigger when players make progress

### Bot Not Responding to Chat
- **Wrong channel**: Bot only responds in the configured channel
- **Missing permissions**: Ensure bot can read and send messages
- **Message content intent**: Must be enabled in Discord Developer Portal

### Import Errors
- **Wrong directory**: Make sure you're running from the correct directory
- **Python path**: The bot automatically adjusts the Python path

## 📁 File Structure

```
p(ai)mon/
├── paimon.py              # Main bot file
├── config.py              # Configuration settings
├── game_context.py        # Game state tracking
├── notification_engine.py # Announcement logic
├── chat_handler.py        # Chat response logic
├── start_paimon.py        # Startup script
├── test_components.py     # Component tests
├── .env.example           # Environment template
├── .env                   # Your configuration (create this)
└── README.md              # Detailed documentation
```

## 🎮 Example Interactions

**Announcements:**
- "🎉 Incredible! Sarah just claimed Tsunade - a Super Super Rare! ⭐"
- "🔥 Mike is on fire! That's 3 squares in the last hour!"
- "💪 Come on, Alex! Those bimbos won't hunt themselves! 💪"

**Chat:**
- User: "Who's winning?"
- Paimon: "🏆 Sarah is in the lead with 24 points! But Mike is hot on their trail with 22 points! 🔥"

**Daily Summary:**
```
📊 🌟 Daily Hunt Summary! 🌟
🏆 Sarah leads with 24 points!
🥈 Mike is close behind with 22 points!
🎯 Rarest catch today: Illumi Zoldyck (Ultra Rare Plus) by Sarah!
```

## 🔄 Integration with Game

Paimon integrates with the existing game through:
- **API Endpoints**: Uses `/api/leaderboard`, `/api/admin/boards`, etc.
- **Database Monitoring**: Polls for changes in player progress
- **Character Data**: References the same rarity system from `characters.py`

No modifications to the main game code are required!
