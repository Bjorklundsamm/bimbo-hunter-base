"""
LLM Client for Paimon's agentic workflow
Handles communication with Claude via Anthropic API
"""

from typing import Optional
from anthropic import Anthropic
from utils import setup_paimon_logging
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, CLAUDE_MAX_TOKENS, CLAUDE_TEMPERATURE

# Configure logging
logger = setup_paimon_logging(__name__)

class ClaudeClient:
    """Client for interacting with Claude via Anthropic API"""
    
    def __init__(self):
        """Initialize the Claude client"""
        if not ANTHROPIC_API_KEY:
            logger.warning("ANTHROPIC_API_KEY not found - running in mock mode")
            self.client = None
            self.mock_mode = True
        else:
            self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
            self.mock_mode = False

        self.model = CLAUDE_MODEL
        self.max_tokens = CLAUDE_MAX_TOKENS
        self.temperature = CLAUDE_TEMPERATURE
        
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """
        Generate a response from Claude

        Args:
            prompt (str): The user prompt to send to Claude
            system_prompt (str, optional): System prompt to set context

        Returns:
            str: Claude's response, or None if there was an error
        """
        if self.mock_mode:
            logger.info("Running in mock mode - returning mock response")
            return self._generate_mock_response(prompt)

        try:
            messages = [{"role": "user", "content": prompt}]

            kwargs = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "messages": messages
            }

            if system_prompt:
                kwargs["system"] = system_prompt

            response = self.client.messages.create(**kwargs)

            if response.content and len(response.content) > 0:
                return response.content[0].text
            else:
                logger.error("Empty response from Claude")
                return None

        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            return None

    def _generate_mock_response(self, prompt: str) -> str:
        """Generate a mock response when API key is not available"""
        if "latest update" in prompt.lower() and "context" in prompt.lower():
            # Mock context update - return a simple updated context
            return "** DO NOT EDIT THIS SECTION **\n[Base context preserved]\n\n** EDIT THIS SECTION **\nMock mode active - context updated.\n\nLatest update:\nMock update processed."
        elif "should a message be sent" in prompt.lower() or "notification" in prompt.lower():
            # Mock message evaluation - usually return no message for testing
            return "NO MESSAGE REQUIRED"
        else:
            return "NO MESSAGE REQUIRED"
    
    def update_context(self, current_context: str, latest_update: str) -> Optional[str]:
        """
        Update the context using Claude
        
        Args:
            current_context (str): The current context string
            latest_update (str): The latest update to integrate
            
        Returns:
            str: Updated context, or None if there was an error
        """
        from prompts import CONTEXT_UPDATE_PROMPT
        
        prompt = CONTEXT_UPDATE_PROMPT.format(
            context=current_context,
            latest_update=latest_update
        )
        
        system_prompt = "You are Paimon, a Discord bot for the Bimbo Hunter game. You maintain context about the game state and integrate new updates while preserving the required structure."
        
        response = self.generate_response(prompt, system_prompt)
        
        if response:
            logger.info("Successfully updated context using Claude")
            return response
        else:
            logger.error("Failed to update context using Claude")
            return None
    
    def evaluate_for_message(self, context: str) -> Optional[str]:
        """
        Evaluate context to determine if a message should be sent
        
        Args:
            context (str): The current context to evaluate
            
        Returns:
            str: Message to send, "NO MESSAGE REQUIRED", or None if error
        """
        from prompts import MESSAGE_EVALUATION_PROMPT
        
        prompt = MESSAGE_EVALUATION_PROMPT.format(context=context)
        
        system_prompt = "You are Paimon, a Discord bot for the Bimbo Hunter game. Evaluate the context and determine if a notification should be sent to Discord. Follow the notification standards strictly."
        
        response = self.generate_response(prompt, system_prompt)
        
        if response:
            logger.info(f"Claude evaluation result: {response[:100]}...")
            return response.strip()
        else:
            logger.error("Failed to evaluate context using Claude")
            return None

# Global instance
_claude_client = None

def get_claude_client() -> ClaudeClient:
    """Get the global Claude client instance"""
    global _claude_client
    if _claude_client is None:
        _claude_client = ClaudeClient()
    return _claude_client
