"""
Tools module for the bingo game.

This module contains utility functions for generating and managing bingo boards.
"""

import random
import math
import json
from typing import List, Dict, Tuple, Any, Optional

# Point values for each rarity
RARITY_POINTS = {
    "FREE": 1,
    "R": 2,
    "SR": 3,
    "SSR": 4,
    "UR+": 6
}

def generate_balanced_bingo_board(characters: List[Dict[str, Any]], seed: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Generate a balanced 5x5 bingo board from the characters list.

    Rules:
    - The center (slot 13) must be one of the FREE characters
    - Exactly 2 UR+ cards must be placed on the board, and they cannot share a row or column
    - Every row and column must have at least 1 SSR or UR+ card in it
    - Rarity quantity priority: R > SR > SSR > UR+
    - Characters can't appear more than once
    - R, SR, and SSR cards should be well-shuffled for good dispersion
    - Rows and columns should be balanced in terms of total rarity points

    Args:
        characters: List of character dictionaries
        seed: Optional random seed for reproducibility

    Returns:
        A list of 25 character dictionaries representing the bingo board
    """
    if seed is not None:
        random.seed(seed)

    # Group characters by rarity
    free_chars = [c for c in characters if c["rarity"] == "FREE"]
    r_chars = [c for c in characters if c["rarity"] == "R"]
    sr_chars = [c for c in characters if c["rarity"] == "SR"]
    ssr_chars = [c for c in characters if c["rarity"] == "SSR"]
    urplus_chars = [c for c in characters if c["rarity"] == "UR+"]

    # Shuffle each rarity group for randomness
    random.shuffle(free_chars)
    random.shuffle(r_chars)
    random.shuffle(sr_chars)
    random.shuffle(ssr_chars)
    random.shuffle(urplus_chars)

    # Create an empty 5x5 board
    board = [None] * 25

    # Place a FREE character in the center (index 12)
    center_free = random.choice(free_chars)
    board[12] = center_free

    # Calculate how many of each rarity we need
    # We need 24 characters (excluding center)
    # NEW RULE: Exactly 2 UR+ cards
    num_urplus = 2

    # Determine the distribution of the remaining 22 slots
    # Priority: R > SR > SSR
    # We'll allocate a percentage of the remaining slots to each rarity
    # based on their availability and priority

    # Calculate the proportion of each rarity in the remaining character pool
    # but with priority R > SR > SSR
    r_weight = 0.5  # 50% of slots for R
    sr_weight = 0.3  # 30% of slots for SR
    ssr_weight = 0.2  # 20% of slots for SSR

    # Calculate the expected number of each rarity
    num_r = min(round(22 * r_weight), len(r_chars))
    num_sr = min(round(22 * sr_weight), len(sr_chars))
    num_ssr = min(round(22 * ssr_weight), len(ssr_chars))

    # Adjust to ensure we have exactly 22 characters (excluding center and UR+)
    total_expected = num_r + num_sr + num_ssr

    # If we don't have exactly 22, adjust the counts based on priority R > SR > SSR
    while total_expected < 22:
        if num_r < len(r_chars):
            num_r += 1
        elif num_sr < len(sr_chars):
            num_sr += 1
        elif num_ssr < len(ssr_chars):
            num_ssr += 1
        else:
            # If we can't add any more, break out
            break
        total_expected = num_r + num_sr + num_ssr

    while total_expected > 22:
        if num_ssr > 0:
            num_ssr -= 1
        elif num_sr > 0:
            num_sr -= 1
        elif num_r > 0:
            num_r -= 1
        else:
            # If we can't remove any more, break out
            break
        total_expected = num_r + num_sr + num_ssr

    # Select the required number of each rarity
    selected_r = r_chars[:num_r]
    selected_sr = sr_chars[:num_sr]
    selected_ssr = ssr_chars[:num_ssr]
    selected_urplus = urplus_chars[:num_urplus]

    # Make sure we have enough SSR cards to satisfy the new rule
    # We need at least 3 SSR cards (to cover rows/columns not covered by UR+ cards)
    min_ssr_needed = 3
    if num_ssr < min_ssr_needed and len(ssr_chars) >= min_ssr_needed:
        # Adjust the counts to ensure we have enough SSR cards
        num_ssr = min_ssr_needed
        selected_ssr = ssr_chars[:num_ssr]

        # Reduce R or SR cards to maintain the total
        if num_r > min_ssr_needed:
            num_r -= (min_ssr_needed - len(selected_ssr))
            selected_r = r_chars[:num_r]
        elif num_sr > min_ssr_needed:
            num_sr -= (min_ssr_needed - len(selected_ssr))
            selected_sr = sr_chars[:num_sr]

    # Place the 2 UR+ cards in positions that don't share a row or column
    # First, define all possible positions (excluding center)
    all_positions = [i for i in range(25) if i != 12]

    # Choose positions for UR+ cards that don't share a row or column
    valid_urplus_positions = False
    urplus_positions = []

    while not valid_urplus_positions:
        # Try a random position for the first UR+ card
        pos1 = random.choice(all_positions)
        row1, col1 = pos1 // 5, pos1 % 5

        # Find all positions that don't share a row or column with pos1
        valid_pos2 = [
            pos for pos in all_positions
            if pos != pos1 and pos // 5 != row1 and pos % 5 != col1
        ]

        if valid_pos2:
            pos2 = random.choice(valid_pos2)
            urplus_positions = [pos1, pos2]
            valid_urplus_positions = True

    # Place UR+ cards in the selected positions
    for i, pos in enumerate(urplus_positions):
        board[pos] = selected_urplus[i]

    # Track which rows and columns have high-rarity cards (SSR or UR+)
    rows_with_high_rarity = set()
    cols_with_high_rarity = set()

    # Add rows and columns with UR+ cards
    for pos in urplus_positions:
        rows_with_high_rarity.add(pos // 5)
        cols_with_high_rarity.add(pos % 5)

    # Add the center row and column (which has a FREE card)
    rows_with_high_rarity.add(2)  # Center row
    cols_with_high_rarity.add(2)  # Center column

    # Remove the UR+ positions from available positions
    available_positions = [pos for pos in all_positions if pos not in urplus_positions and pos != 12]

    # Combine all remaining selected characters
    remaining_chars = selected_r + selected_sr + selected_ssr

    # Sort remaining characters by rarity for strategic placement
    # We want to place SSR cards first to ensure every row and column has at least one high-rarity card
    remaining_chars.sort(key=lambda x: 0 if x["rarity"] == "SSR" else 1)

    # First, place SSR cards in rows and columns that don't have high-rarity cards yet
    ssr_chars_to_place = [c for c in remaining_chars if c["rarity"] == "SSR"]
    other_chars_to_place = [c for c in remaining_chars if c["rarity"] != "SSR"]

    # Calculate rows and columns that need high-rarity cards
    rows_needing_high_rarity = set(range(5)) - rows_with_high_rarity
    cols_needing_high_rarity = set(range(5)) - cols_with_high_rarity

    # Place SSR cards strategically to cover rows and columns without high-rarity cards
    for row in rows_needing_high_rarity:
        if not ssr_chars_to_place:
            break

        # Find positions in this row that are available
        row_positions = [pos for pos in available_positions if pos // 5 == row]

        if row_positions:
            # Prefer positions that also cover columns needing high-rarity cards
            priority_positions = [pos for pos in row_positions if pos % 5 in cols_needing_high_rarity]

            if priority_positions:
                pos = random.choice(priority_positions)
            else:
                pos = random.choice(row_positions)

            # Place an SSR card here
            board[pos] = ssr_chars_to_place.pop(0)
            available_positions.remove(pos)

            # Update tracking sets
            rows_with_high_rarity.add(pos // 5)
            cols_with_high_rarity.add(pos % 5)

    # Now handle any columns that still need high-rarity cards
    cols_still_needing = set(range(5)) - cols_with_high_rarity
    for col in cols_still_needing:
        if not ssr_chars_to_place:
            break

        # Find positions in this column that are available
        col_positions = [pos for pos in available_positions if pos % 5 == col]

        if col_positions:
            pos = random.choice(col_positions)

            # Place an SSR card here
            board[pos] = ssr_chars_to_place.pop(0)
            available_positions.remove(pos)

            # Update tracking sets
            rows_with_high_rarity.add(pos // 5)
            cols_with_high_rarity.add(pos % 5)

    # Add any remaining SSR cards back to the pool
    other_chars_to_place.extend(ssr_chars_to_place)

    # Shuffle the remaining characters for better dispersion
    random.shuffle(other_chars_to_place)

    # Calculate point values for each row and column to balance the board
    row_points = [0] * 5
    col_points = [0] * 5

    # Add points for already placed cards (UR+, FREE, and strategically placed SSR)
    for pos, char in enumerate(board):
        if char is not None:
            row, col = pos // 5, pos % 5
            row_points[row] += RARITY_POINTS[char["rarity"]]
            col_points[col] += RARITY_POINTS[char["rarity"]]

    # Place the remaining characters with point balancing
    # Sort available positions by how balanced they would make the board
    while available_positions and other_chars_to_place:
        # Calculate a score for each position based on how balanced it would make the board
        position_scores = []
        for pos in available_positions:
            row, col = pos // 5, pos % 5
            # Lower score is better (means more balanced)
            score = row_points[row] + col_points[col]
            position_scores.append((pos, score))

        # Sort positions by score (ascending)
        position_scores.sort(key=lambda x: x[1])

        # Choose one of the most balanced positions (with some randomness)
        # Take the top 3 positions or all if fewer than 3 are available
        top_n = min(3, len(position_scores))
        chosen_pos, _ = random.choice(position_scores[:top_n])

        # Place the next character
        char = other_chars_to_place.pop(0)
        board[chosen_pos] = char

        # Update points and available positions
        row, col = chosen_pos // 5, chosen_pos % 5
        row_points[row] += RARITY_POINTS[char["rarity"]]
        col_points[col] += RARITY_POINTS[char["rarity"]]
        available_positions.remove(chosen_pos)

    # Verify that every row and column has at least one high-rarity card
    for i in range(5):
        row_has_high_rarity = any(board[i*5 + j] is not None and board[i*5 + j]["rarity"] in ["SSR", "UR+"] for j in range(5))
        col_has_high_rarity = any(board[i + j*5] is not None and board[i + j*5]["rarity"] in ["SSR", "UR+"] for j in range(5))

        if not row_has_high_rarity or not col_has_high_rarity:
            # This should not happen with our algorithm, but just in case
            print(f"Warning: Row or column {i} does not have a high-rarity card!")

    # Calculate the final rarity distribution (for debugging purposes)
    _ = get_rarity_distribution(board)

    # Return the board with the slot numbers
    for i, char in enumerate(board):
        char["slot"] = i + 1  # 1-indexed slots

    return board


def save_board_to_json(board: List[Dict[str, Any]], filename: str) -> None:
    """
    Save a bingo board to a JSON file.

    Args:
        board: The bingo board to save
        filename: The name of the file to save to
    """
    with open(filename, 'w') as f:
        json.dump(board, f, indent=2)


def load_board_from_json(filename: str) -> List[Dict[str, Any]]:
    """
    Load a bingo board from a JSON file.

    Args:
        filename: The name of the file to load from

    Returns:
        The loaded bingo board
    """
    with open(filename, 'r') as f:
        return json.load(f)


def calculate_board_points(board: List[Dict[str, Any]]) -> int:
    """
    Calculate the total points for a bingo board.

    Args:
        board: The bingo board to calculate points for

    Returns:
        The total points for the board
    """
    return sum(RARITY_POINTS[char["rarity"]] for char in board)


def get_rarity_distribution(board: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Get the distribution of rarities on a bingo board.

    Args:
        board: The bingo board to analyze

    Returns:
        A dictionary mapping rarity to count
    """
    return {
        "FREE": sum(1 for char in board if char["rarity"] == "FREE"),
        "R": sum(1 for char in board if char["rarity"] == "R"),
        "SR": sum(1 for char in board if char["rarity"] == "SR"),
        "SSR": sum(1 for char in board if char["rarity"] == "SSR"),
        "UR+": sum(1 for char in board if char["rarity"] == "UR+")
    }


def analyze_high_rarity_distribution(board: List[Dict[str, Any]]) -> Dict[str, List[int]]:
    """
    Analyze the distribution of high-rarity cards (SSR and UR+) in rows and columns.

    Args:
        board: The bingo board to analyze

    Returns:
        A dictionary with keys 'rows' and 'cols', each containing a list of counts
        of high-rarity cards in each row or column
    """
    # Sort the board by slot number to ensure correct ordering
    sorted_board = sorted(board, key=lambda x: x["slot"])

    # Initialize counters
    row_high_rarity = [0] * 5
    col_high_rarity = [0] * 5

    # Count high-rarity cards in each row and column
    for i in range(5):
        for j in range(5):
            idx = i * 5 + j
            char = sorted_board[idx]
            if char["rarity"] in ["SSR", "UR+"]:
                row_high_rarity[i] += 1
                col_high_rarity[j] += 1

    # Calculate row and column point totals
    row_points = [0] * 5
    col_points = [0] * 5

    for i in range(5):
        for j in range(5):
            idx = i * 5 + j
            char = sorted_board[idx]
            row_points[i] += RARITY_POINTS[char["rarity"]]
            col_points[j] += RARITY_POINTS[char["rarity"]]

    return {
        "rows_high_rarity": row_high_rarity,
        "cols_high_rarity": col_high_rarity,
        "row_points": row_points,
        "col_points": col_points
    }


def print_board(board: List[Dict[str, Any]]) -> None:
    """
    Print a bingo board in a 5x5 grid with distribution analysis.

    Args:
        board: The bingo board to print
    """
    # Sort the board by slot number
    sorted_board = sorted(board, key=lambda x: x["slot"])

    # Get high rarity distribution
    distribution = analyze_high_rarity_distribution(board)
    row_high_rarity = distribution["rows_high_rarity"]
    col_high_rarity = distribution["cols_high_rarity"]
    row_points = distribution["row_points"]
    col_points = distribution["col_points"]

    # Print column high rarity counts and points
    print("\nColumn High Rarity (SSR/UR+) Counts:")
    print("  ".join([f"Col {j+1}: {col_high_rarity[j]}" for j in range(5)]))

    print("\nColumn Point Totals:")
    print("  ".join([f"Col {j+1}: {col_points[j]}" for j in range(5)]))

    print("\nBingo Board:")
    for i in range(5):
        row = []
        for j in range(5):
            idx = i * 5 + j
            char = sorted_board[idx]
            row.append(f"{char['rarity']} - {char['Name']}")

        # Add row high rarity count and points
        row_info = f"| Row {i+1}: {row_high_rarity[i]} high, {row_points[i]} pts"
        print("  ".join(row) + " " + row_info)

    # Verify the high-rarity rule
    all_rows_have_high = all(count > 0 for count in row_high_rarity)
    all_cols_have_high = all(count > 0 for count in col_high_rarity)

    if all_rows_have_high and all_cols_have_high:
        print("\n✅ All rows and columns have at least one high-rarity card (SSR or UR+)")
    else:
        missing_rows = [i+1 for i, count in enumerate(row_high_rarity) if count == 0]
        missing_cols = [j+1 for j, count in enumerate(col_high_rarity) if count == 0]

        if missing_rows:
            print(f"\n❌ Rows missing high-rarity cards: {missing_rows}")
        if missing_cols:
            print(f"\n❌ Columns missing high-rarity cards: {missing_cols}")
