import React, { useState, useEffect } from 'react';
import './App.css';

// Portrait Overlay component
const PortraitOverlay = ({ character, onClose, onClaim, sourcePosition, isClaimed }) => {
  // Get the portrait URL from the portrait path
  const getPortraitUrl = (portraitPath) => {
    if (!portraitPath) return null;
    return `${process.env.PUBLIC_URL}${portraitPath}`;
  };

  const portraitUrl = getPortraitUrl(character.Portrait);

  // Use state to control animation classes and details visibility
  const [isVisible, setIsVisible] = React.useState(false);
  const [showDetails, setShowDetails] = React.useState(false);

  // Apply the animation after component mounts
  React.useEffect(() => {
    // Small delay to ensure the component is rendered before animation starts
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, 50);

    return () => clearTimeout(timer);
  }, []);

  // Handle closing with animation
  const handleClose = () => {
    setIsVisible(false);
    setShowDetails(false);
    // Wait for animation to complete before actually closing
    setTimeout(onClose, 300);
  };

  // Handle claiming with animation
  const handleClaim = () => {
    setIsVisible(false);
    setShowDetails(false);
    // Wait for animation to complete before actually claiming
    setTimeout(onClaim, 300);
  };

  // Handle showing/hiding details
  const handleToggleDetails = () => {
    // Debug: Log the character object to see if it has a description field
    console.log('Character in details:', character);
    setShowDetails(!showDetails);
  };

  // Get rarity value text
  const getRarityValue = (rarity) => {
    switch (rarity) {
      case 'FREE':
        return 'FREE (1 pt)';
      case 'R':
        return 'R (2 pts)';
      case 'SR':
        return 'SR (3 pts)';
      case 'SSR':
        return 'SSR (4 pts)';
      case 'UR+':
        return 'UR+ (6 pts)';
      default:
        return 'Unknown';
    }
  };

  return (
    <div className={`portrait-overlay ${isVisible ? 'visible' : ''}`}>
      <div
        className={`portrait-container ${isVisible ? 'visible' : ''}`}
        style={sourcePosition ? {
          // If we have source position, use it for initial transform origin
          transformOrigin: `${sourcePosition.x}px ${sourcePosition.y}px`
        } : {}}
      >
        <button className="close-button" onClick={handleClose}>×</button>
        <img
          src={portraitUrl}
          alt={character.Name}
          className="character-portrait"
        />
        <div className="portrait-buttons">
          <button
            className={`claim-button ${isClaimed ? 'unclaim' : ''}`}
            onClick={handleClaim}
          >
            {isClaimed ? 'Unclaim' : 'Claim!'}
          </button>
          <button className="details-button" onClick={handleToggleDetails}>Details</button>
        </div>

        {showDetails && (
          <div
            className="character-details-overlay"
            onClick={() => setShowDetails(false)}
          >
            <div
              className="character-details-content"
              onClick={(e) => e.stopPropagation()} // Prevent clicks on content from closing
            >
              <p><strong>Name:</strong><br />{character.Name}</p>
              <p><strong>Source:</strong><br />{character.Source}</p>
              <p><strong>Value:</strong><br />{getRarityValue(character.rarity)}</p>
              <p><strong>What to look for:</strong><br />{character.description || "No description available"}</p>
              <p><strong>Special conditions:</strong><br />{character.conditions || "None"}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Represents a single square on the bingo board
const BingoSquare = ({ character, isMarked, onClick, onPortraitClick, index }) => {
  // Determine the border color based on rarity
  const getRarityColor = (rarity) => {
    switch (rarity) {
      case 'FREE':
        return '#4CAF50'; // Green
      case 'R':
        return '#2196F3'; // Blue
      case 'SR':
        return '#9C27B0'; // Purple
      case 'SSR':
        return '#FF9800'; // Orange
      case 'UR+':
        return '#F44336'; // Red
      default:
        return '#FFFFFF'; // White
    }
  };

  // Get the local file path for the thumbnail
  const getThumbnailUrl = (thumbnailPath) => {
    if (!thumbnailPath) return null;

    // Extract just the filename from the path
    const filename = thumbnailPath.split('/').pop();

    // Construct the URL to the thumbnail in the public folder
    return `${process.env.PUBLIC_URL}/thumbnails/${filename}`;
  };

  // Get the thumbnail URL using the thumbnail path
  const thumbnailUrl = getThumbnailUrl(character.Thumbnail);

  // Handle click on the thumbnail to show portrait
  const handleThumbnailClick = (e) => {
    e.stopPropagation(); // Prevent the square's onClick from firing

    // Get the position of the clicked thumbnail for zoom effect
    const rect = e.currentTarget.getBoundingClientRect();
    const position = {
      x: rect.left + rect.width / 2,
      y: rect.top + rect.height / 2
    };

    // Pass the character, position, and index to the parent component
    onPortraitClick(character, position, index);
  };

  // Add 'free' class if this is the FREE square
  const isFreeSquare = character.rarity === 'FREE';

  return (
    <div
      className={`bingo-square ${isMarked ? 'marked' : ''} ${isFreeSquare ? 'free' : ''}`}
      onClick={onClick}
      style={{
        borderColor: getRarityColor(character.rarity),
        backgroundColor: 'transparent',
        position: 'relative'
      }}
    >
      <div className="thumbnail-container" onClick={handleThumbnailClick}>
        <img
          src={thumbnailUrl}
          alt={character.Name}
          className="character-thumbnail"
        />
      </div>
    </div>
  );
};

// Confirmation Modal component
const ConfirmationModal = ({ onCancel, onConfirm }) => {
  return (
    <div className="confirmation-modal-overlay">
      <div className="confirmation-modal">
        <h3>Warning!</h3>
        <p>
          If you refresh your board, you will lose all your current progress and claimed squares.
          Are you sure you want to generate a new board?
        </p>
        <div className="confirmation-modal-buttons">
          <button className="cancel-button" onClick={onCancel}>
            Cancel
          </button>
          <button className="confirm-button" onClick={onConfirm}>
            Generate New Board
          </button>
        </div>
      </div>
    </div>
  );
};

// Points Display component with refresh button and points meter
const PointsDisplay = ({ characters, markedCells, onRefreshClick }) => {
  // Point values for each rarity
  const RARITY_POINTS = {
    "FREE": 1,
    "R": 2,
    "SR": 3,
    "SSR": 4,
    "UR+": 6
  };

  // Calculate points from marked cells
  const calculateBasePoints = () => {
    let totalPoints = 0;
    markedCells.forEach(index => {
      if (index >= 0 && index < characters.length) {
        const character = characters[index];
        totalPoints += RARITY_POINTS[character.rarity];
      }
    });
    return totalPoints;
  };

  // Check if there's a bingo (5 in a row, column, or diagonal)
  const checkForBingos = () => {
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
  };

  const basePoints = calculateBasePoints();
  const bingoPoints = checkForBingos();
  const totalPoints = basePoints + bingoPoints;

  // Calculate the percentage for the meter (0-350 points)
  const MAX_POINTS = 350;
  const fillPercentage = Math.min((totalPoints / MAX_POINTS) * 100, 100);

  // Milestone definitions
  const milestones = [
    { points: 150, reward: "Champagne Toast in LA Live" },
    { points: 250, reward: "Mystery prize" },
    { points: 350, reward: "Yakitori on the beach!" }
  ];

  return (
    <div className="points-controls-container">
      <div className="points-meter-container">
        <div className="points-meter">
          <div
            className="points-meter-fill"
            style={{ width: `${fillPercentage}%` }}
          ></div>

          {/* Render milestones */}
          {milestones.map((milestone, index) => (
            <div
              key={index}
              className="milestone"
              style={{ left: `${(milestone.points / MAX_POINTS) * 100}%` }}
            >
              <div className="milestone-tooltip">
                {milestone.reward}
              </div>
              <div className="milestone-value">{milestone.points}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="points-display">
        <div className="score-label">Score</div>
        <div className="score-value">{totalPoints}</div>
      </div>
      <button className="refresh-button" onClick={onRefreshClick} title="Refresh Board">
        ↻
      </button>
    </div>
  );
};

// Represents the 5x5 Bingo Board
const BingoBoard = () => {
  const [characters, setCharacters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [markedCells, setMarkedCells] = useState(new Set());
  const [selectedCharacter, setSelectedCharacter] = useState(null);
  const [sourcePosition, setSourcePosition] = useState(null);
  const [showRefreshConfirmation, setShowRefreshConfirmation] = useState(false);

  // Function to fetch characters and generate a board
  const fetchCharactersAndGenerateBoard = async () => {
    try {
      setLoading(true);

      // Step 1: Fetch the characters data from the backend
      const charactersResponse = await fetch('http://localhost:5000/api/characters');

      if (!charactersResponse.ok) {
        throw new Error(`HTTP error! Status: ${charactersResponse.status}`);
      }

      const charactersData = await charactersResponse.json();

      // Step 2: Send the characters data to the backend to generate a balanced bingo board
      const boardResponse = await fetch('http://localhost:5000/api/generate-board', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ characters: charactersData }),
      });

      if (!boardResponse.ok) {
        throw new Error(`HTTP error! Status: ${boardResponse.status}`);
      }

      const boardData = await boardResponse.json();

      // Sort the characters by slot number
      const sortedCharacters = [...boardData].sort((a, b) => a.slot - b.slot);

      setCharacters(sortedCharacters);

      // Pre-mark the FREE space
      const freeIndex = sortedCharacters.findIndex(char => char.rarity === 'FREE');
      if (freeIndex !== -1) {
        const newMarkedCells = new Set();
        newMarkedCells.add(freeIndex);
        setMarkedCells(newMarkedCells);
      }

      setLoading(false);
    } catch (error) {
      console.error('Error generating board:', error);
      setError(error.message);
      setLoading(false);
    }
  };

  // Fetch the character data and generate a bingo board on initial load
  useEffect(() => {
    fetchCharactersAndGenerateBoard();
  }, []); // Empty dependency array ensures this runs only once on mount

  // Handle refresh button click
  const handleRefreshClick = () => {
    setShowRefreshConfirmation(true);
  };

  // Handle cancel refresh
  const handleCancelRefresh = () => {
    setShowRefreshConfirmation(false);
  };

  // Handle confirm refresh
  const handleConfirmRefresh = () => {
    // Reset state
    setMarkedCells(new Set());
    setSelectedCharacter(null);
    setSourcePosition(null);
    setShowRefreshConfirmation(false);

    // Generate a new board
    fetchCharactersAndGenerateBoard();
  };

  // Handles clicking on a square to mark/unmark it
  const handleSquareClick = (index) => {
    const character = characters[index];

    // Cannot unmark the "FREE" space
    if (character.rarity === 'FREE') {
      return;
    }

    const newMarkedCells = new Set(markedCells);
    if (newMarkedCells.has(index)) {
      newMarkedCells.delete(index); // Unmark if already marked
    } else {
      newMarkedCells.add(index); // Mark if not marked
    }
    setMarkedCells(newMarkedCells);
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
  const handleClaimCharacter = () => {
    if (selectedCharacter && selectedCharacter.index !== undefined) {
      const index = selectedCharacter.index;
      const newMarkedCells = new Set(markedCells);

      // Toggle the claim status (except for FREE square)
      if (characters[index].rarity === 'FREE') {
        // FREE square should always remain claimed
        newMarkedCells.add(index);
      } else if (newMarkedCells.has(index)) {
        // Unclaim if already claimed
        newMarkedCells.delete(index);
      } else {
        // Claim if not claimed
        newMarkedCells.add(index);
      }

      setMarkedCells(newMarkedCells);
    }

    // Close the overlay
    setSelectedCharacter(null);
  };

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
            onClick={() => handleSquareClick(index)}
            onPortraitClick={handlePortraitClick}
          />
        ))}
      </div>

      <PointsDisplay
        characters={characters}
        markedCells={markedCells}
        onRefreshClick={handleRefreshClick}
      />

      {selectedCharacter && (
        <PortraitOverlay
          character={selectedCharacter}
          onClose={handleClosePortrait}
          onClaim={handleClaimCharacter}
          sourcePosition={sourcePosition}
          isClaimed={selectedCharacter.index !== undefined && markedCells.has(selectedCharacter.index)}
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

// Main App component
const App = () => {
  return (
    <div className="app-container">
      <header className="app-header">
        <div className="logo-container">
          <img src={`${process.env.PUBLIC_URL}/title-logo.png`} alt="Bimbo Hunter Logo" className="title-logo" />
        </div>
        <p>Thank you for competing in Official 2025 Bimbo Hunt! Please read our <a href="#how-to-play">#how to play</a> and <a href="#rules">#rules</a> before starting your game.</p>
      </header>
      <BingoBoard />
      <div id="how-to-play" className="rules-section">
        <h2>How to Play</h2>
        <p>Ready to start hunting? Here's what to do:</p>
        <ol>
          <li>Find people wearing the cosplays on your board and ask to get a picture with them.</li>
          <li>Upload your picture to claim the slot and accumulate points.</li>
          <li>If you're too shy to ask for a picture, remember how excited you feel when someone recognizes your cosplay and think about how nice it is to offer that to them!</li>
          <li>Prizes will be awarded to the first and second place winners, as well as the person who earned the most overall points.</li>
        </ol>
        <p>Remember, cosplayers love to be recognized and appreciated for their hard work!</p>
      </div>
      <div id="rules" className="rules-section">
        <h2>Rules</h2>
        <p>Please follow these important guidelines for a fun and respectful experience:</p>
        <ol>
          <li>Cosplay is NOT consent - always ask for permission before taking photos.</li>
          <li>You must be featured in the photo (at least a hand) to claim a square.</li>
          <li>Teams can have as many members as you'd like, but there will still only be a single prize per team.</li>
          <li>You can refresh to get a new board, but you will lose all your current progress.</li>
          <li>Each player receives a unique bingo board with characters of different rarities.</li>
          <li>Characters are ranked by rarity: FREE, R, SR, SSR, and UR+.</li>
          <li>Higher rarity characters are worth more points, but are harder to find.</li>
        </ol>
        <p>Good luck, and happy hunting!</p>
      </div>
      <footer className="app-footer">
        <p>Enjoy the game!</p>
      </footer>
    </div>
  );
};

export default App;
