import React, { useState, useEffect } from 'react';

const PointsDisplay = ({ characters, markedCells, onRefreshClick, isReadOnly, score }) => {
  const [groupPoints, setGroupPoints] = useState(0);

  // Fetch group points
  useEffect(() => {
    const fetchGroupPoints = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/group-points');
        if (response.ok) {
          const data = await response.json();
          setGroupPoints(data.total_points);
        }
      } catch (error) {
        console.error('Error fetching group points:', error);
      }
    };

    fetchGroupPoints();

    // Set up polling to refresh group points every 30 seconds
    const intervalId = setInterval(fetchGroupPoints, 30000);

    return () => clearInterval(intervalId); // Clean up on unmount
  }, []);

  // Also update group points when the individual score changes
  useEffect(() => {
    const fetchGroupPoints = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/group-points');
        if (response.ok) {
          const data = await response.json();
          setGroupPoints(data.total_points);
        }
      } catch (error) {
        console.error('Error fetching group points:', error);
      }
    };

    // Only fetch if we have a score (to avoid unnecessary calls on initial load)
    if (score !== undefined) {
      fetchGroupPoints();
    }
  }, [score]);

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

  // Calculate the percentage for the meter using GROUP POINTS (0-500 points)
  const MAX_POINTS = 500; // Updated to 500 as per requirements
  const fillPercentage = Math.min((groupPoints / MAX_POINTS) * 100, 100);

  // Milestone definitions - updated as per requirements
  const milestones = [
    { points: 150, reward: "Champagne Toast!" },
    { points: 250, reward: "Mystery Prize" },
    { points: 350, reward: "Seafood Boil" }
  ];

  // Determine the next reward based on current group points
  const getNextReward = () => {
    for (const milestone of milestones) {
      if (groupPoints < milestone.points) {
        return `${milestone.points} pts - ${milestone.reward}`;
      }
    }
    return "All rewards unlocked!";
  };

  return (
    <div className="points-section-wrapper">
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

            {/* Render milestone markers (without tooltips) */}
            {milestones.map((milestone, index) => (
              <div
                key={index}
                className="milestone-marker"
                style={{ left: `${(milestone.points / MAX_POINTS) * 100}%` }}
              >
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

      {/* Next Reward Section - now on its own row */}
      <div className="next-reward-section">
        <div className="next-reward-label">Next Reward:</div>
        <div className="next-reward-text">{getNextReward()}</div>
      </div>
    </div>
  );
};

export default PointsDisplay;
