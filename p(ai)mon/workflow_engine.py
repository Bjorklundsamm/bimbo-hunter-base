"""
Workflow Engine for Paimon's agentic workflow
Uses LangGraph to orchestrate the step-by-step process
"""

from datetime import datetime
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from utils import setup_paimon_logging
from context_manager import get_context_manager
from llm_client import get_claude_client

# Configure logging
logger = setup_paimon_logging(__name__)

class WorkflowState:
    """State object for the workflow"""
    
    def __init__(self):
        self.context: str = ""
        self.latest_update: str = ""
        self.updated_context: str = ""
        self.message: str = ""
        self.should_publish: bool = False
        self.error: str = ""

class PaimonWorkflowEngine:
    """LangGraph-based workflow engine for Paimon"""
    
    def __init__(self):
        """Initialize the workflow engine"""
        self.context_manager = get_context_manager()
        self.claude_client = get_claude_client()
        self.workflow = self._build_workflow()
    
    def _build_workflow(self):
        """Build the LangGraph workflow"""
        
        # Create the state graph
        workflow = StateGraph(dict)
        
        # Add nodes
        workflow.add_node("preprocess_context", self._preprocess_context)
        workflow.add_node("evaluate_context", self._evaluate_context)
        workflow.add_node("publish_message", self._publish_message)
        
        # Add edges
        workflow.add_edge("preprocess_context", "evaluate_context")
        workflow.add_conditional_edges(
            "evaluate_context",
            self._should_publish_message,
            {
                True: "publish_message",
                False: END
            }
        )
        workflow.add_edge("publish_message", END)
        
        # Set entry point
        workflow.set_entry_point("preprocess_context")
        
        return workflow.compile()
    
    def _preprocess_context(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        First node: Update context with latest changes
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with new context
        """
        logger.info("Starting context preprocessing")
        
        try:
            current_context = state.get("context", "")
            latest_update = state.get("latest_update", "")
            
            if not current_context:
                logger.error("No current context provided")
                state["error"] = "No current context provided"
                return state
            
            if not latest_update:
                logger.info("No latest update provided, keeping context unchanged")
                state["updated_context"] = current_context
                return state
            
            # Use Claude to update the context
            updated_context = self.claude_client.update_context(current_context, latest_update)
            
            if updated_context:
                state["updated_context"] = updated_context
                
                # Save the updated context to database
                if self.context_manager.save_context(updated_context):
                    logger.info("Context updated and saved successfully")
                else:
                    logger.error("Failed to save updated context to database")
                    state["error"] = "Failed to save updated context"
            else:
                logger.error("Failed to update context using Claude")
                state["error"] = "Failed to update context using Claude"
                state["updated_context"] = current_context  # Fallback to original
            
        except Exception as e:
            logger.error(f"Error in preprocess_context: {e}")
            state["error"] = f"Error in preprocess_context: {e}"
            state["updated_context"] = state.get("context", "")
        
        return state
    
    def _evaluate_context(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Second node: Evaluate context to determine if message should be sent
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with message decision
        """
        logger.info("Starting context evaluation")
        
        try:
            updated_context = state.get("updated_context", "")
            
            if not updated_context:
                logger.error("No updated context available for evaluation")
                state["error"] = "No updated context available for evaluation"
                state["should_publish"] = False
                return state
            
            # Use Claude to evaluate if a message should be sent
            evaluation_result = self.claude_client.evaluate_for_message(updated_context)
            
            if evaluation_result:
                if evaluation_result.strip() == "NO MESSAGE REQUIRED":
                    logger.info("Claude determined no message is required")
                    state["should_publish"] = False
                    state["message"] = ""
                else:
                    logger.info("Claude determined a message should be sent")
                    state["should_publish"] = True
                    state["message"] = evaluation_result.strip()
            else:
                logger.error("Failed to evaluate context using Claude")
                state["error"] = "Failed to evaluate context using Claude"
                state["should_publish"] = False
                state["message"] = ""
            
        except Exception as e:
            logger.error(f"Error in evaluate_context: {e}")
            state["error"] = f"Error in evaluate_context: {e}"
            state["should_publish"] = False
            state["message"] = ""
        
        return state
    
    def _publish_message(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Third node: Publish message to Discord
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with publication result
        """
        logger.info("Starting message publication")
        
        try:
            message = state.get("message", "")
            
            if not message:
                logger.error("No message to publish")
                state["error"] = "No message to publish"
                return state
            
            # Store the message for the main bot to send
            # We'll use a simple approach - store in state for the bot to pick up
            state["published"] = True
            logger.info(f"Message ready for publication: {message[:100]}...")
            
        except Exception as e:
            logger.error(f"Error in publish_message: {e}")
            state["error"] = f"Error in publish_message: {e}"
            state["published"] = False
        
        return state
    
    def _should_publish_message(self, state: Dict[str, Any]) -> bool:
        """
        Conditional edge function to determine if message should be published
        
        Args:
            state: Current workflow state
            
        Returns:
            True if message should be published, False otherwise
        """
        return state.get("should_publish", False)
    
    def process_updates(self, updates: List[Dict]) -> List[str]:
        """
        Process a list of updates and return any messages to send
        
        Args:
            updates: List of update dictionaries
            
        Returns:
            List of messages to send to Discord
        """
        messages_to_send = []
        
        if not updates:
            logger.info("No updates to process")
            return messages_to_send
        
        # Get current context
        current_context = self.context_manager.get_current_context()
        if not current_context:
            logger.error("No current context available")
            return messages_to_send
        
        # Process each update
        for update in updates:
            try:
                # Format the update for context integration
                latest_update = self.context_manager.format_update_for_context(
                    update['update_type'], 
                    update['update_data']
                )
                
                # Prepare initial state
                initial_state = {
                    "context": current_context,
                    "latest_update": latest_update,
                    "updated_context": "",
                    "message": "",
                    "should_publish": False,
                    "error": "",
                    "published": False
                }
                
                # Run the workflow
                logger.info(f"Processing update: {update['update_type']}")
                final_state = self.workflow.invoke(initial_state)
                
                # Check for errors
                if final_state.get("error"):
                    logger.error(f"Workflow error: {final_state['error']}")
                    continue
                
                # Check if a message was generated
                if final_state.get("published") and final_state.get("message"):
                    messages_to_send.append(final_state["message"])
                    logger.info("Message added to send queue")
                
                # Mark update as processed
                self.context_manager.mark_update_processed(update['id'])
                
                # Update current context for next iteration
                current_context = final_state.get("updated_context", current_context)
                
            except Exception as e:
                logger.error(f"Error processing update {update.get('id', 'unknown')}: {e}")
                continue
        
        return messages_to_send
    
    def run_periodic_check(self) -> List[str]:
        """
        Run a periodic check and return any messages to send
        
        Returns:
            List of messages to send to Discord
        """
        logger.info("Running periodic check")
        
        # Get current game state and check for any notable changes
        game_state = self.context_manager.get_current_game_state()
        
        # Create a periodic update
        periodic_update = {
            'id': 0,  # Special ID for periodic checks
            'update_type': 'periodic_check',
            'update_data': {
                'total_players': game_state['total_players'],
                'active_players': game_state['active_players'],
                'timestamp': str(datetime.now())
            }
        }
        
        return self.process_updates([periodic_update])

# Global instance
_workflow_engine = None

def get_workflow_engine() -> PaimonWorkflowEngine:
    """Get the global workflow engine instance"""
    global _workflow_engine
    if _workflow_engine is None:
        _workflow_engine = PaimonWorkflowEngine()
    return _workflow_engine
