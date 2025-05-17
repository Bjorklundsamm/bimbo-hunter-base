import React, { useState, useEffect } from 'react';
import './App.css';

// Represents a single square on the bingo board
const BingoSquare = ({ number, isMarked, onClick }) => {
  return (
    <div
      className={`bingo-square ${isMarked ? 'marked' : ''}`}
      onClick={onClick}
    >
      {number}
    </div>
  );
};

// Represents the 5x5 Bingo Board
const BingoBoard = () => {
  const [board, setBoard] = useState([]);
  const [markedCells, setMarkedCells] = useState(new Set());

  // Initialize the board with numbers (e.g., 1-25 for a simple demo)
  // In a real bingo game, these would be random and within specific ranges per column.
  useEffect(() => {
    const initialBoard = [];
    for (let i = 0; i < 5; i++) {
      const row = [];
      for (let j = 0; j < 5; j++) {
        // For a 5x5 board, the center square (2,2) is often "FREE"
        if (i === 2 && j === 2) {
          row.push('FREE');
        } else {
          // Placeholder numbers; a real game would have specific ranges
          row.push(i * 5 + j + 1);
        }
      }
      initialBoard.push(row);
    }
    setBoard(initialBoard);

    // Pre-mark the "FREE" space if it exists
    // The key for a cell is calculated as rowIndex * numCols + colIndex.
    // For a 5x5 board, numCols is 5.
    // The center square is at rowIndex = 2, colIndex = 2.
    // So, the key for the "FREE" space is 2 * 5 + 2 = 12.
    const newMarkedCells = new Set();
    if (initialBoard[2][2] === 'FREE') {
        newMarkedCells.add(12); // Directly use the calculated key for the FREE space
        setMarkedCells(newMarkedCells);
    }
  }, []); // Empty dependency array ensures this runs only once on mount

  // Handles clicking on a square
  const handleSquareClick = (rowIndex, colIndex) => {
    const cellValue = board[rowIndex][colIndex];
    const cellKey = rowIndex * 5 + colIndex; // Unique key for the cell

    // Cannot unmark the "FREE" space
    if (cellValue === 'FREE') {
        return;
    }

    const newMarkedCells = new Set(markedCells);
    if (newMarkedCells.has(cellKey)) {
      newMarkedCells.delete(cellKey); // Unmark if already marked
    } else {
      newMarkedCells.add(cellKey); // Mark if not marked
    }
    setMarkedCells(newMarkedCells);
  };

  if (board.length === 0) {
    return <div className="loading-message">Loading board...</div>;
  }

  return (
    <div className="bingo-board">
      {board.map((row, rowIndex) =>
        row.map((number, colIndex) => (
          <BingoSquare
            key={`${rowIndex}-${colIndex}`}
            number={number}
            isMarked={markedCells.has(rowIndex * 5 + colIndex)}
            onClick={() => handleSquareClick(rowIndex, colIndex)}
          />
        ))
      )}
    </div>
  );
};

// Main App component
const App = () => {
  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Bimbo Hunter</h1>
        <p>Thank you for competing in Official 2025 Bimbo Hunt! Please read our <a href="#rules">#rules</a> before starting your game.</p>
      </header>
      <BingoBoard />
      <div id="rules" className="rules-section">
        <h2>Rules</h2>
        <p>[RULES WILL GO HERE]</p>
      </div>
      <footer className="app-footer">
        <p>Enjoy the game!</p>
      </footer>
    </div>
  );
};

export default App;
