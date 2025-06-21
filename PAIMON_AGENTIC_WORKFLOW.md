# Paimon Agentic Workflow Implementation

## Overview

Paimon has been overhauled to work as a step-by-step agentic workflow using LangChain and LangGraph. This new architecture makes her more intelligent, context-aware, and capable of making nuanced decisions about when and what to post to Discord.

## Architecture

### Core Components

1. **Context Manager** (`p(ai)mon/context_manager.py`)
   - Stores and manages the evolving context string
   - Handles the update queue for database changes
   - Formats updates for LLM consumption

2. **LLM Client** (`p(ai)mon/llm_client.py`)
   - Integrates with Anthropic's Claude API
   - Handles context updates and message evaluation
   - Provides error handling and logging

3. **Workflow Engine** (`p(ai)mon/workflow_engine.py`)
   - Implements the LangGraph-based workflow
   - Orchestrates the three-node process
   - Manages state between workflow steps

4. **Prompt Templates** (`p(ai)mon/prompts.py`)
   - Contains the base context and instructions
   - Defines prompt templates for LLM interactions
   - Includes helper functions for formatting

### Database Schema

Two new tables have been added:

```sql
-- Stores the evolving context string
CREATE TABLE paimon_context (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    context_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Queues updates for processing
CREATE TABLE paimon_updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    update_type TEXT NOT NULL,
    update_data TEXT NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP NULL
);
```

## Workflow Process

### Three-Node Workflow

1. **Preprocess Context Node**
   - Takes current context and latest update
   - Uses Claude to integrate the update into context
   - Saves updated context to database

2. **Evaluate Context Node**
   - Uses Claude to evaluate if a message should be sent
   - Returns either a message or "NO MESSAGE REQUIRED"
   - Follows strict notification standards

3. **Publish Message Node**
   - Prepares message for Discord publication
   - Only executes if evaluation determines message is needed

### Trigger Points

Paimon is now triggered in two scenarios:

1. **Database Changes** (Real-time)
   - User registration
   - Board creation
   - Progress updates (claiming squares)

2. **Periodic Checks** (Every 10 minutes)
   - Reviews overall game state
   - Checks for patterns or milestones
   - Provides encouragement or summaries

## Configuration

### Environment Variables

Add these to `p(ai)mon/.env`:

```bash
# Existing Discord configuration
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_CHANNEL_ID=your_discord_channel_id_here
GAME_API_BASE_URL=http://localhost:5000/api

# New Anthropic Claude configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here
CLAUDE_MODEL=claude-3-sonnet-20240229
CLAUDE_MAX_TOKENS=4000
CLAUDE_TEMPERATURE=0.7
```

### Dependencies

Install the new dependencies:

```bash
pip install -r p(ai)mon/requirements.txt
```

New packages include:
- `langchain==0.1.0`
- `langchain-anthropic==0.1.0`
- `langgraph==0.0.20`
- `anthropic==0.8.0`

## Context Structure

The context follows a specific structure:

```
** DO NOT EDIT THIS SECTION **
[Base context with game rules, notification standards, and examples]

** EDIT THIS SECTION **
[Current game state, player information, and recent activities]

Latest update:
[Most recent change to process]
```

### Example Context Evolution

**Initial State:**
```
** EDIT THIS SECTION **
The database is currently empty and there are no players yet.

Latest update:
None
```

**After User Registration:**
```
** EDIT THIS SECTION **
User1 has signed up and generated their board, but has no claimed squares.
User1's cards:
Frieren(Free)

Latest update:
User1 signed up.
```

**After Progress Update:**
```
** EDIT THIS SECTION **
User1 has claimed 3 cards in total (Score: 8 points).
User1's cards:
Frieren(Free), Brazil Miku(SR), Agnes Tachyon(R)

User2 has signed up and generated their board but has claimed no squares yet.
User2's cards:
Momo Ayase(Free)

Latest update:
User1 claimed new characters: Brazil Miku(SR), Agnes Tachyon(R). Score increased from 1 to 8 points.
```

## Integration Points

### Main Application Hooks

The main Flask app (`app.py`) now includes trigger calls:

```python
# User registration
trigger_paimon_update('user_registered', {
    'user_id': user['id'],
    'display_name': user['display_name'],
    'pin': user['pin']
})

# Board creation
trigger_paimon_update('board_created', {
    'user_id': user_id,
    'display_name': user['display_name'],
    'board_id': new_board['id']
})

# Progress updates
trigger_paimon_update('progress_updated', {
    'user_id': user_id,
    'display_name': user['display_name'],
    'board_id': board_id,
    'old_score': old_score,
    'new_score': score,
    'new_claims': new_claims,
    'total_marked': len(marked_cells)
})
```

### Backward Compatibility

The old notification system remains active as a fallback, ensuring continuity during the transition period.

## Testing

Run the test suite to verify the implementation:

```bash
python p(ai)mon/test_agentic_workflow.py
```

This tests:
- Database schema creation
- Context manager functionality
- Workflow engine (mock mode)
- Update processing

## Deployment

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp p(ai)mon/.env.example p(ai)mon/.env
   # Edit .env with your API keys
   ```

3. **Initialize Database**
   ```bash
   python -c "from database import init_db; init_db()"
   ```

4. **Start Paimon**
   ```bash
   python start_paimon.py
   ```

## Benefits

### Improved Intelligence
- Context-aware decision making
- Nuanced understanding of game state
- Better timing for notifications

### Scalability
- Handles complex game scenarios
- Adapts to changing player behavior
- Maintains conversation continuity

### Maintainability
- Clear separation of concerns
- Modular architecture
- Comprehensive logging

### Flexibility
- Easy to modify notification rules
- Adjustable personality and tone
- Extensible for new game features

## Monitoring

Check the logs for workflow execution:

```bash
tail -f p(ai)mon/logs/paimon.log
```

Key log messages:
- Context updates
- LLM API calls
- Workflow state transitions
- Message generation decisions

## Troubleshooting

### Common Issues

1. **Missing API Key**
   - Ensure `ANTHROPIC_API_KEY` is set in `.env`
   - Verify API key is valid

2. **Database Errors**
   - Run database initialization
   - Check file permissions

3. **Import Errors**
   - Install all dependencies
   - Verify Python path configuration

4. **LLM Timeouts**
   - Check network connectivity
   - Verify API rate limits

### Debug Mode

Enable debug logging in `config.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```
