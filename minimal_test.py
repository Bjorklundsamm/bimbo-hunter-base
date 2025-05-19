"""
Minimal test script for the bingo board algorithm.
"""

import tools
import random
from typing import List, Dict, Any

# Create some mock characters for testing
mock_characters = []

# Add FREE characters
for i in range(5):
    mock_characters.append({
        "Name": f"FREE Character {i+1}",
        "rarity": "FREE",
        "Thumbnail": f"free_{i+1}.png"
    })

# Add R characters
for i in range(30):
    mock_characters.append({
        "Name": f"R Character {i+1}",
        "rarity": "R",
        "Thumbnail": f"r_{i+1}.png"
    })

# Add SR characters
for i in range(20):
    mock_characters.append({
        "Name": f"SR Character {i+1}",
        "rarity": "SR",
        "Thumbnail": f"sr_{i+1}.png"
    })

# Add SSR characters
for i in range(10):
    mock_characters.append({
        "Name": f"SSR Character {i+1}",
        "rarity": "SSR",
        "Thumbnail": f"ssr_{i+1}.png"
    })

# Add UR+ characters
for i in range(5):
    mock_characters.append({
        "Name": f"UR+ Character {i+1}",
        "rarity": "UR+",
        "Thumbnail": f"urplus_{i+1}.png"
    })

def test_with_mock_data():
    """Test the bingo board generation algorithm with mock data."""
    # Set a seed for reproducibility
    seed = 42
    
    print(f"Testing with seed {seed}")
    print("-" * 50)
    
    # Generate a board
    board = tools.generate_balanced_bingo_board(mock_characters, seed)
    
    # Print the board with distribution analysis
    tools.print_board(board)
    
    # Get the rarity distribution
    rarity_counts = tools.get_rarity_distribution(board)
    print("\nRarity distribution:")
    for rarity, count in rarity_counts.items():
        print(f"  {rarity}: {count} ({count * tools.RARITY_POINTS[rarity]} points)")
    
    # Calculate total points
    total_points = tools.calculate_board_points(board)
    print(f"Total points: {total_points}")
    
    # Analyze high-rarity distribution
    distribution = tools.analyze_high_rarity_distribution(board)
    row_high_rarity = distribution["rows_high_rarity"]
    col_high_rarity = distribution["cols_high_rarity"]
    
    # Check that every row has at least one high-rarity card
    all_rows_have_high = all(count > 0 for count in row_high_rarity)
    
    # Check that every column has at least one high-rarity card
    all_cols_have_high = all(count > 0 for count in col_high_rarity)
    
    print("\nHigh-rarity distribution check:")
    if all_rows_have_high and all_cols_have_high:
        print("✅ All rows and columns have at least one high-rarity card")
    else:
        missing_rows = [i+1 for i, count in enumerate(row_high_rarity) if count == 0]
        missing_cols = [j+1 for j, count in enumerate(col_high_rarity) if count == 0]
        
        if missing_rows:
            print(f"❌ Rows missing high-rarity cards: {missing_rows}")
        if missing_cols:
            print(f"❌ Columns missing high-rarity cards: {missing_cols}")
    
    return board

if __name__ == "__main__":
    test_with_mock_data()
