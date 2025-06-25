"""
Paimon Discord Bot for Bingo Hunter Game
Main bot file that coordinates all functionality
"""

import discord
from discord.ext import tasks
from utils import setup_project_path, setup_paimon_logging

# Set up project path for imports
setup_project_path()

from config import DISCORD_TOKEN, DISCORD_CHANNEL_ID, MONITORING_INTERVAL
from game_context import GameContext
from notification_engine import NotificationEngine
from chat_handler import ChatHandler
from workflow_engine import get_workflow_engine
from context_manager import get_context_manager

# Configure logging
logger = setup_paimon_logging(__name__)

class PaimonBot(discord.Client):
    """Paimon Discord Bot for the Bimbo Hunter game"""

    def __init__(self):
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

        # Initialize components
        self.game_context = GameContext()
        self.notification_engine = NotificationEngine(self.game_context)
        self.chat_handler = ChatHandler(self.game_context)
        self.workflow_engine = get_workflow_engine()
        self.context_manager = get_context_manager()
        self.target_channel = None

    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'Paimon is ready! Logged in as {self.user}')

        # Get the target channel
        if DISCORD_CHANNEL_ID:
            self.target_channel = self.get_channel(DISCORD_CHANNEL_ID)
            if self.target_channel:
                logger.info(f'Connected to channel: {self.target_channel.name}')
                await self.target_channel.send("🌟 Paimon is now monitoring your bimbo hunting progress! 📊")
            else:
                logger.error(f'Could not find channel with ID: {DISCORD_CHANNEL_ID}')
        else:
            logger.warning('No Discord channel ID configured')

        # Start the monitoring loop
        if not self.monitor_game.is_running():
            self.monitor_game.start()

    async def on_message(self, message):
        """Handle incoming messages - DISABLED: Paimon only monitors and announces"""
        # Don't respond to our own messages
        if message.author == self.user:
            return

        # Only respond in the target channel (if configured)
        if self.target_channel and message.channel != self.target_channel:
            return

        # Chat responses are disabled - Paimon only monitors database and makes announcements
        # response = self.chat_handler.handle_message(message.content, message.author.display_name)
        # if response:
        #     await message.channel.send(response)

    @tasks.loop(seconds=MONITORING_INTERVAL)
    async def monitor_game(self):
        """Periodically monitor the game for changes and send announcements"""
        try:
            # Check if we should reset daily tracking
            if self.game_context.should_reset_daily_tracking():
                logger.info("Resetting daily tracking")

            # Process pending updates using the new workflow engine
            pending_updates = self.context_manager.get_pending_updates()
            if pending_updates:
                logger.info(f"Processing {len(pending_updates)} pending updates")
                workflow_messages = self.workflow_engine.process_updates(pending_updates)

                # Send workflow-generated messages
                for message in workflow_messages:
                    await self.send_workflow_message(message)

            # Run periodic check using workflow engine
            periodic_messages = self.workflow_engine.run_periodic_check()
            for message in periodic_messages:
                await self.send_workflow_message(message)

            # Keep the old system running in parallel for now (fallback)
            # Update game context
            changes = self.game_context.update_context()

            # Process changes and get announcements
            announcements = self.notification_engine.process_changes(changes)

            # Send announcements (only if no workflow messages were sent)
            if not pending_updates and not periodic_messages:
                for announcement in announcements:
                    await self.send_announcement(announcement)

        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")

    async def send_announcement(self, announcement: dict):
        """Send an announcement to the target channel"""
        if not self.target_channel:
            logger.warning("No target channel configured, cannot send announcement")
            return

        try:
            message = announcement['message']

            # Add some personality based on announcement type
            if announcement['type'] == 'rare_claim':
                message = f"🎉 {message}"
            elif announcement['type'] == 'rapid_claiming':
                message = f"🔥 {message}"
            elif announcement['type'] == 'encouragement':
                message = f"💪 {message}"
            elif announcement['type'] == 'daily_summary':
                message = f"📊 {message}"
            elif announcement['type'] == 'new_player':
                message = f"👋 {message}"

            await self.target_channel.send(message)
            logger.info(f"Sent {announcement['type']} announcement")

        except Exception as e:
            logger.error(f"Error sending announcement: {e}")

    async def send_workflow_message(self, message: str):
        """Send a message generated by the workflow engine to the target channel"""
        if not self.target_channel:
            logger.warning("No target channel configured, cannot send workflow message")
            return

        try:
            await self.target_channel.send(message)
            logger.info(f"Sent workflow message: {message[:100]}...")

        except Exception as e:
            logger.error(f"Error sending workflow message: {e}")

    async def close(self):
        """Clean shutdown"""
        logger.info("Paimon is shutting down...")
        if self.monitor_game.is_running():
            self.monitor_game.cancel()
        await super().close()


def main():
    """Main function to run the bot"""
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not found in environment variables")
        logger.error("Please create a .env file with your Discord bot token")
        return

    if not DISCORD_CHANNEL_ID:
        logger.error("DISCORD_CHANNEL_ID not found in environment variables")
        logger.error("Please add your Discord channel ID to the .env file")
        return

    # Create and run the bot
    bot = PaimonBot()

    try:
        bot.run(DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")


if __name__ == "__main__":
    main()