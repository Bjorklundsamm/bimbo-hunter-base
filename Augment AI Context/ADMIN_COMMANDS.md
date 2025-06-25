# Admin Commands for Bingo Hunter

This document describes the administrative commands available for managing the Bingo Hunter application.

## Overview

The `admin_commands.py` script provides five essential admin commands for managing boards and users in your Bingo Hunter application:

1. **Delete all boards** - Removes all boards and progress data from the database
2. **Delete a specific board** - Removes a specific user's board by display name
3. **Delete all players** - Removes all players and their associated data from the database
4. **Delete a specific player** - Removes a specific player and all their data by display name
5. **Generate test user** - Creates a test user with random or specified name and optional claimed squares

## Prerequisites

- Python 3.6+
- All project dependencies installed
- Database initialized (the script will handle this automatically)

## Usage

### Basic Command Structure

```bash
python admin_commands.py <command> [arguments]
```

### Available Commands

#### 1. Delete All Boards

Removes all boards and progress data from the database. **Use with caution!**

```bash
python admin_commands.py delete-all-boards
```

**Example output:**
```
🔧 Initializing database...
🗑️  Deleting all boards and progress data...
✅ Successfully deleted 5 boards and 5 progress records

🎉 Command completed successfully!
```

#### 2. Delete Specific Board

Removes a specific user's board and progress by their display name.

```bash
python admin_commands.py delete-board "<display_name>"
```

**Examples:**
```bash
python admin_commands.py delete-board "Mayjay"
python admin_commands.py delete-board "TestUser123"
```

**Example output:**
```
🔧 Initializing database...
🗑️  Deleting board for user 'Mayjay'...
✅ Successfully deleted 1 boards and 1 progress records for 'Mayjay'

🎉 Command completed successfully!
```

**Error handling:**
```
🗑️  Deleting board for user 'NonExistentUser'...
❌ User 'NonExistentUser' not found

💥 Command failed!
```

#### 3. Delete All Players

Removes all players (users) and their associated data from the database. **Use with extreme caution!**

```bash
python admin_commands.py delete-all-players
```

**Example output:**
```
🔧 Initializing database...
🗑️  Deleting all players and associated data...
✅ Successfully deleted 15 players, 4 boards, and 4 progress records

🎉 Command completed successfully!
```

#### 4. Delete Specific Player

Removes a specific player and all their associated data (boards, progress) by their display name.

```bash
python admin_commands.py delete-player "<display_name>"
```

**Examples:**
```bash
python admin_commands.py delete-player "Mayjay"
python admin_commands.py delete-player "TestUser123"
```

**Example output:**
```
🔧 Initializing database...
🗑️  Deleting player 'Silent429' and all associated data...
✅ Successfully deleted player 'Silent429' with 1 boards and 1 progress records

🎉 Command completed successfully!
```

**Error handling:**
```
🗑️  Deleting player 'NonExistentUser' and all associated data...
❌ Player 'NonExistentUser' not found

💥 Command failed!
```

#### 5. Generate Test User

Creates a test user with a random or specified name and board. Optionally specify the number of squares to claim.

```bash
# Generate user with random name and random number of claimed squares (1-15)
python admin_commands.py generate-test-user

# Generate user with random name and specific number of claimed squares
python admin_commands.py generate-test-user <number_of_squares>

# Generate user with specific name and random number of claimed squares
python admin_commands.py generate-test-user --name "<display_name>"

# Generate user with specific name and specific number of claimed squares
python admin_commands.py generate-test-user <number_of_squares> --name "<display_name>"
```

**Examples:**
```bash
python admin_commands.py generate-test-user
python admin_commands.py generate-test-user 5
python admin_commands.py generate-test-user 12
python admin_commands.py generate-test-user --name "Spoon"
python admin_commands.py generate-test-user 8 --name "TestPlayer"
```

**Example output:**
```
🔧 Initializing database...
👤 Generating test user...
✅ Created user: 'ShadowTeal' (PIN: 3359, ID: 11)
✅ Created board for user 'ShadowTeal' (Board ID: 12)
✅ Created progress: 8 squares claimed, 22 points
🎯 Test user ready! Access at: /boards/ShadowTeal

🎉 Command completed successfully!
```

## Test User Details

When generating test users:

- **Random Names**: Generated from combinations of adjectives and names (e.g., "ShadowTeal", "GoldenIndigo", "Swift787")
- **Random PINs**: 4-digit PINs between 1000-9999
- **Automatic Board Generation**: Each user gets a balanced bingo board
- **Smart Progress**: Always includes the FREE space, plus random additional squares
- **Score Calculation**: Automatically calculates score based on rarity points

## Safety Features

- **Unique Name Generation**: Attempts up to 50 times to generate a unique display name
- **Database Validation**: Checks for existing users before creating duplicates
- **Error Handling**: Comprehensive error messages and proper exit codes
- **Transaction Safety**: Uses database transactions to ensure data consistency

## Help

Get help for any command:

```bash
python admin_commands.py --help
python admin_commands.py delete-board --help
python admin_commands.py generate-test-user --help
```

## Examples for Testing

Here's a typical workflow for testing:

```bash
# Generate some test users
python admin_commands.py generate-test-user 3
python admin_commands.py generate-test-user 7 --name "TestPlayer"
python admin_commands.py generate-test-user --name "Spoon"

# Delete a specific user's board (keeps the player)
python admin_commands.py delete-board "ShadowTeal"

# Delete a specific player and all their data
python admin_commands.py delete-player "TestPlayer"

# Clean up everything - boards only
python admin_commands.py delete-all-boards

# Clean up everything - players and all data
python admin_commands.py delete-all-players
```

## Notes

- The script automatically initializes the database if needed
- All operations provide clear feedback with emojis for easy reading
- Failed operations return non-zero exit codes for scripting
- The FREE space is always included in claimed squares for test users
- Maximum 25 squares can be claimed (the entire board)
