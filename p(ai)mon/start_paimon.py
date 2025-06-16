#!/usr/bin/env python3
"""
Startup script for Paimon Discord Bot
Handles dependency checking and graceful startup
"""

import sys
import os
import subprocess

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['discord.py', 'python-dotenv', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'discord.py':
                import discord
            elif package == 'python-dotenv':
                import dotenv
            elif package == 'requests':
                import requests
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install them with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    if not os.path.exists(env_path):
        print("❌ .env file not found!")
        print("📝 Please copy .env.example to .env and configure it:")
        print("   cp .env.example .env")
        print("   # Then edit .env with your Discord bot token and channel ID")
        return False
    
    # Load and check environment variables
    from dotenv import load_dotenv
    load_dotenv(env_path)
    
    discord_token = os.getenv('DISCORD_TOKEN')
    discord_channel_id = os.getenv('DISCORD_CHANNEL_ID')
    
    if not discord_token or discord_token == 'your_discord_bot_token_here':
        print("❌ DISCORD_TOKEN not configured in .env file!")
        print("🔑 Please add your Discord bot token to the .env file")
        return False
    
    if not discord_channel_id or discord_channel_id == 'your_channel_id_here':
        print("❌ DISCORD_CHANNEL_ID not configured in .env file!")
        print("📺 Please add your Discord channel ID to the .env file")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🌟 Starting Paimon Discord Bot...")
    print()
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ All dependencies found!")
    
    # Check environment configuration
    print("⚙️  Checking configuration...")
    if not check_env_file():
        sys.exit(1)
    print("✅ Configuration looks good!")
    
    # Start the bot
    print("🚀 Starting Paimon...")
    print("   Press Ctrl+C to stop the bot")
    print()
    
    try:
        from paimon import main as run_bot
        run_bot()
    except KeyboardInterrupt:
        print("\n👋 Paimon stopped by user")
    except Exception as e:
        print(f"\n💥 Paimon crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
