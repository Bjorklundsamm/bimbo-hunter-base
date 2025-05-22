import React from 'react';

const PointsDisplay = ({ characters, markedCells, onRefreshClick, isReadOnly, score }) => {
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

  // Use the score from props if provided, otherwise calculate it
  const displayScore = score !== undefined ? score : totalPoints;

  // Calculate the percentage for the meter (0-500 points)
  const MAX_POINTS = 500; // Updated to 500 as per requirements
  const fillPercentage = Math.min((displayScore / MAX_POINTS) * 100, 100);

  // Milestone definitions - updated as per requirements
  const milestones = [
    { points: 150, reward: "Toast in L.A. Live!" },
    { points: 250, reward: "Mystery prize!" },
    { points: 350, reward: "Yakitori!" }
  ];

  return (
    <div className="points-controls-container">
      <div className="points-meter-container">
        <div className="points-meter">
          <div
            className="points-meter-fill"
            style={{ width: `${fillPercentage}%` }}
          ></div>

          {/* Add the progress text with negative coloring effect */}
          <div className="progress-text">
            GROUP POINTS
          </div>

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

      <div className="controls-wrapper">
        <div className="points-display">
          <div className="score-label">Score</div>
          <div className="score-value">{displayScore}</div>
        </div>
        {!isReadOnly && (
          <button 
            className="refresh-button" 
            onClick={onRefreshClick} 
            title="Refresh Board"
          >
            ↻
          </button>
        )}
      </div>
    </div>
  );
};

export default PointsDisplay;
