"""
Configuration file for Paimon Discord Bot
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Discord Bot Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID', '0'))

# Game API Configuration
GAME_API_BASE_URL = os.getenv('GAME_API_BASE_URL', 'http://localhost:5000/api')

# LLM Configuration for Agentic Workflow
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-sonnet-20240229')
CLAUDE_MAX_TOKENS = int(os.getenv('CLAUDE_MAX_TOKENS', '4000'))
CLAUDE_TEMPERATURE = float(os.getenv('CLAUDE_TEMPERATURE', '0.7'))

# Bot Behavior Configuration
MONITORING_INTERVAL = 600  # 10 minutes between periodic checks (changed from 30 seconds)
ANNOUNCEMENT_COOLDOWN = 300  # 5 minutes minimum between similar announcements
DAILY_SUMMARY_HOUR = 21  # 9 PM for daily summaries
QUIET_HOURS_START = 2  # 2 AM
QUIET_HOURS_END = 8  # 8 AM

# Rarity Configuration (matches characters.py)
RARITY_POINTS = {
    'FREE': 1,
    'R': 2,
    'SR': 3,
    'SSR': 4,
    'UR+': 6
}

RARITY_NAMES = {
    'FREE': 'Free',
    'R': 'Common',
    'SR': 'Super Rare',
    'SSR': 'Super Super Rare',
    'UR+': 'Ultra Rare Plus'
}

# Announcement Thresholds
RAPID_CLAIM_THRESHOLD = 3  # claims within time window
RAPID_CLAIM_WINDOW = 3600  # 1 hour in seconds
RARE_CLAIM_THRESHOLD = 'SSR'  # minimum rarity to announce individual claims
INACTIVE_PLAYER_THRESHOLD = 86400  # 24 hours in seconds

# Chat Response Configuration
GAME_KEYWORDS = [
    'bimbo', 'hunter', 'hunting', 'board', 'bingo', 'score', 'points', 
    'lead', 'leader', 'leaderboard', 'claim', 'square', 'character',
    'rarity', 'rare', 'progress', 'game'
]

# Paimon Personality Responses
PERSONALITY_RESPONSES = {
    'greeting': [
        "Hey there, fellow bimbo hunter! 🎯",
        "Ready to hunt some bimbos? Let's go! ✨",
        "Paimon's here to help with your hunting adventure! 🌟"
    ],
    'encouragement': [
        "Come on, {name}! Those bimbos won't hunt themselves! 💪",
        "Hey {name}, Paimon thinks you should get back out there! 🎯",
        "What's wrong {name}, there are bimbos that need hunting! Let's get to work! ⚡",
        "{name}, the hunt awaits! Don't let those rare finds slip away! 🔥"
    ],
    'celebration': [
        "Wow! Look at that amazing catch! 🎉",
        "That's what Paimon calls a successful hunt! ⭐",
        "Incredible work out there! 🌟",
        "Now that's some serious hunting skills! 💫"
    ],
    'off_topic': [
        "Sorry bro, the only thing Paimon knows is bimbo huntin'! 🎯",
        "Paimon only knows about the hunt! Got any bimbo hunting questions? 🤔",
        "That's not really Paimon's area... but how about those bingo boards? 📋",
        "Paimon's brain is full of hunting knowledge only! Ask me about the game! 🎮"
    ]
}
