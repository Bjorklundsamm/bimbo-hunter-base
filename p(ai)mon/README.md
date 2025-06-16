# Paimon Discord Bot

Paimon is an AI Discord bot for the Bimbo Hunter game that provides contextual announcements and responds to player questions.

## Features

### 🎯 Smart Announcements
- **Rare Claims**: Announces when players claim SSR or UR+ characters
- **Rapid Claiming**: Celebrates players who claim multiple squares quickly
- **First Claims**: Special announcements for new players' first rare catches
- **Daily Summaries**: End-of-day leaderboard and highlights (9 PM)
- **Player Encouragement**: Gentle nudges for inactive players

### 💬 Chat Interactions
Players can ask Paimon questions like:
- "Who's in the lead?" - Current leaderboard
- "What's my score?" - Personal progress
- "How am I doing?" - Recent activity summary
- "What's the rarest catch today?" - Game status
- "Help" - Game rules and instructions

### 🧠 Context Awareness
- Tracks all player progress and board states
- Remembers previous announcements to avoid spam
- Respects quiet hours (2 AM - 8 AM)
- Maintains daily tracking that resets each day

## Setup

### 1. Install Dependencies
```bash
pip install discord.py python-dotenv requests
```

### 2. Create Discord Bot
1. Go to https://discord.com/developers/applications
2. Create a new application
3. Go to the "Bot" section
4. Create a bot and copy the token
5. Enable "Message Content Intent" in Bot settings

### 3. Configure Environment
1. Copy `.env.example` to `.env`
2. Add your Discord bot token
3. Add your Discord channel ID (enable Developer Mode in Discord, right-click channel, Copy ID)

### 4. Invite Bot to Server
1. Go to OAuth2 > URL Generator in Discord Developer Portal
2. Select "bot" scope
3. Select permissions: Send Messages, Read Message History
4. Use the generated URL to invite the bot

### 5. Run the Bot
```bash
cd p(ai)mon
python paimon.py
```

## Configuration

Edit `config.py` to customize:
- Monitoring intervals
- Announcement thresholds
- Quiet hours
- Personality responses
- Rarity settings

## Example Usage

**Upload Announcements:**
- "Incredible! Sarah just claimed Tsunade - a Super Super Rare! ⭐"
- "🔥 Mike is on fire! That's 3 squares in the last hour!"

**Chat Responses:**
- User: "Who's winning?"
- Paimon: "🏆 Sarah is in the lead with 24 points! But Mike is hot on their trail with 22 points! 🔥"

**Daily Summary:**
- "🌟 Daily Hunt Summary! 🌟
🏆 Sarah leads with 24 points!
🥈 Mike is close behind with 22 points!
🎯 Rarest catch today: Illumi Zoldyck (Ultra Rare Plus) by Sarah!"

## Architecture

- **`paimon.py`** - Main bot file and Discord integration
- **`game_context.py`** - Tracks player progress and game state
- **`notification_engine.py`** - Determines when to make announcements
- **`chat_handler.py`** - Handles player questions and chat
- **`config.py`** - Configuration and personality settings

## Troubleshooting

**Bot not responding:**
- Check Discord token and channel ID in .env
- Ensure bot has proper permissions
- Check console for error messages

**No announcements:**
- Verify game API is running on localhost:5000
- Check if it's during quiet hours (2-8 AM)
- Ensure players are actually making progress

**Import errors:**
- Make sure you're in the p(ai)mon directory when running
- Install all required dependencies
- Check Python path configuration
