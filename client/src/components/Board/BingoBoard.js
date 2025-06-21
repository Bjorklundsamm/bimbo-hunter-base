import React, { useState, useEffect, useCallback } from 'react';

// Import sub-components (we'll extract these later)
import BingoSquare from './BingoSquare';
import PointsDisplay from './PointsDisplay';
import PortraitOverlay from './PortraitOverlay';
import ConfirmationModal from './ConfirmationModal';

const BingoBoard = ({ boardData, progressData, isReadOnly, userId, boardId }) => {
  const [characters, setCharacters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [markedCells, setMarkedCells] = useState(new Set());
  const [userImages, setUserImages] = useState({});
  const [selectedCharacter, setSelectedCharacter] = useState(null);
  const [sourcePosition, setSourcePosition] = useState(null);
  const [showRefreshConfirmation, setShowRefreshConfirmation] = useState(false);
  const [score, setScore] = useState(0);

  // Initialize board with data
  useEffect(() => {
    if (boardData && progressData) {
      try {
        // Sort the characters by slot number
        const sortedCharacters = [...boardData].sort((a, b) => a.slot - b.slot);
        setCharacters(sortedCharacters);

        // Set marked cells from progress data
        const markedSet = new Set(progressData.marked_cells);
        setMarkedCells(markedSet);

        // Set user images from progress data
        setUserImages(progressData.user_images || {});

        // Set score from progress data
        setScore(progressData.score);

        setLoading(false);
      } catch (error) {
        console.error('Error initializing board:', error);
        setError(error.message);
        setLoading(false);
      }
    }
  }, [boardData, progressData]);

  // Save progress when marked cells change
  useEffect(() => {
    const saveProgress = async () => {
      if (!isReadOnly && userId && boardId && characters.length > 0) {
        try {
          // Calculate score
          const newScore = calculateTotalPoints();
          
          // Save to backend
          await fetch(`http://localhost:5000/api/users/${userId}/boards/${boardId}/progress`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              marked_cells: Array.from(markedCells),
              user_images: userImages,
              score: newScore
            }),
          });
          
          // Update local score state
          setScore(newScore);
        } catch (error) {
          console.error('Error saving progress:', error);
        }
      }
    };

    // Only save if we have marked cells and it's not read-only
    if (markedCells.size > 0 && !isReadOnly) {
      saveProgress();
    }
  }, [markedCells, userImages, isReadOnly, userId, boardId, characters, calculateTotalPoints]);

  // Function to fetch characters and generate a new board
  const fetchCharactersAndGenerateBoard = async () => {
    try {
      setLoading(true);

      // Create a new board for the user
      const response = await fetch(`http://localhost:5000/api/users/${userId}/board`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const newBoardData = await response.json();

      // Sort the characters by slot number
      const sortedCharacters = [...newBoardData.board_data].sort((a, b) => a.slot - b.slot);
      setCharacters(sortedCharacters);

      // Get the new progress (should have FREE space marked)
      const progressResponse = await fetch(`http://localhost:5000/api/users/${userId}/boards/${newBoardData.id}/progress`);
      
      if (!progressResponse.ok) {
        throw new Error(`HTTP error! Status: ${progressResponse.status}`);
      }
      
      const newProgressData = await progressResponse.json();
      
      // Set marked cells from new progress data
      const markedSet = new Set(newProgressData.marked_cells);
      setMarkedCells(markedSet);

      // Set user images from new progress data
      setUserImages(newProgressData.user_images || {});

      // Set score from new progress data
      setScore(newProgressData.score);

      setLoading(false);
    } catch (error) {
      console.error('Error generating board:', error);
      setError(error.message);
      setLoading(false);
    }
  };

  // Handle refresh button click
  const handleRefreshClick = () => {
    if (isReadOnly) return; // Disable refresh for read-only mode
    setShowRefreshConfirmation(true);
  };

  // Handle cancel refresh
  const handleCancelRefresh = () => {
    setShowRefreshConfirmation(false);
  };

  // Handle confirm refresh
  const handleConfirmRefresh = () => {
    // Close any open overlays
    setSelectedCharacter(null);
    setSourcePosition(null);
    setShowRefreshConfirmation(false);

    // Generate a new board (this will handle all state updates)
    fetchCharactersAndGenerateBoard();
  };

  // Handle clicking on a thumbnail to show the portrait
  const handlePortraitClick = (character, position, index) => {
    setSourcePosition(position);
    setSelectedCharacter({...character, index});
  };

  // Handle closing the portrait overlay
  const handleClosePortrait = () => {
    setSelectedCharacter(null);
    setSourcePosition(null);
  };

  // Handle claiming or unclaiming a character
  const handleClaimCharacter = (imagePath = null) => {
    if (isReadOnly) return; // Disable claiming for read-only mode

    if (selectedCharacter && selectedCharacter.index !== undefined) {
      const index = selectedCharacter.index;
      const newMarkedCells = new Set(markedCells);
      const newUserImages = { ...userImages };

      // Toggle the claim status (except for FREE square)
      if (characters[index].rarity === 'FREE') {
        // FREE square should always remain claimed
        newMarkedCells.add(index);
      } else if (newMarkedCells.has(index) && imagePath === null) {
        // Unclaim if already claimed and no new image provided
        newMarkedCells.delete(index);
        delete newUserImages[index];
      } else if (imagePath) {
        // Claim with uploaded image
        newMarkedCells.add(index);
        newUserImages[index] = imagePath;
      } else {
        // This shouldn't happen with the new upload flow, but keep for safety
        newMarkedCells.add(index);
      }

      setMarkedCells(newMarkedCells);
      setUserImages(newUserImages);
    }

    // Close the overlay
    setSelectedCharacter(null);
  };

  // Point values for each rarity
  const RARITY_POINTS = {
    "FREE": 1,
    "R": 2,
    "SR": 3,
    "SSR": 4,
    "UR+": 6
  };

  // Calculate points from marked cells
  const calculateBasePoints = useCallback(() => {
    let totalPoints = 0;
    markedCells.forEach(index => {
      if (index >= 0 && index < characters.length) {
        const character = characters[index];
        totalPoints += RARITY_POINTS[character.rarity];
      }
    });
    return totalPoints;
  }, [markedCells, characters]);

  // Check if there's a bingo (5 in a row, column, or diagonal)
  const checkForBingos = useCallback(() => {
    const bingoBonus = 5; // Bonus points for each bingo
    let bingoCount = 0;

    // Convert markedCells set to a 5x5 grid for easier checking
    const grid = Array(5).fill().map(() => Array(5).fill(false));
    markedCells.forEach(index => {
      const row = Math.floor(index / 5);
      const col = index % 5;
      grid[row][col] = true;
    });

    // Check rows
    for (let row = 0; row < 5; row++) {
      if (grid[row].every(cell => cell)) {
        bingoCount++;
      }
    }

    // Check columns
    for (let col = 0; col < 5; col++) {
      if (grid.every(row => row[col])) {
        bingoCount++;
      }
    }

    // Check main diagonal (top-left to bottom-right)
    if (grid[0][0] && grid[1][1] && grid[2][2] && grid[3][3] && grid[4][4]) {
      bingoCount++;
    }

    // Check other diagonal (top-right to bottom-left)
    if (grid[0][4] && grid[1][3] && grid[2][2] && grid[3][1] && grid[4][0]) {
      bingoCount++;
    }

    return bingoCount * bingoBonus;
  }, [markedCells]);

  // Calculate total points
  const calculateTotalPoints = useCallback(() => {
    const basePoints = calculateBasePoints();
    const bingoPoints = checkForBingos();
    return basePoints + bingoPoints;
  }, [calculateBasePoints, checkForBingos]);

  if (loading) {
    return <div className="loading-message">Loading board...</div>;
  }

  if (error) {
    return <div className="error-message">Error: {error}</div>;
  }

  return (
    <>
      <div className="bingo-board">
        {characters.map((character, index) => (
          <BingoSquare
            key={index}
            index={index}
            character={character}
            isMarked={markedCells.has(index)}
            onPortraitClick={handlePortraitClick}
            isReadOnly={isReadOnly}
            userImage={userImages[index]}
          />
        ))}
      </div>

      <PointsDisplay
        characters={characters}
        markedCells={markedCells}
        onRefreshClick={handleRefreshClick}
        isReadOnly={isReadOnly}
        score={score}
      />

      {selectedCharacter && (
        <PortraitOverlay
          character={selectedCharacter}
          onClose={handleClosePortrait}
          onClaim={handleClaimCharacter}
          sourcePosition={sourcePosition}
          isClaimed={selectedCharacter.index !== undefined && markedCells.has(selectedCharacter.index)}
          isReadOnly={isReadOnly}
          userId={userId}
          boardId={boardId}
          squareIndex={selectedCharacter.index}
          userImage={userImages[selectedCharacter.index]}
        />
      )}

      {showRefreshConfirmation && (
        <ConfirmationModal
          onCancel={handleCancelRefresh}
          onConfirm={handleConfirmRefresh}
        />
      )}
    </>
  );
};

export default BingoBoard;
