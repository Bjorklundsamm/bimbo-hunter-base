import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useUser } from '../Auth/UserContext';

// Import components from App.js (we'll extract these later)
import BingoBoard from './BingoBoard';
import Leaderboard from './Leaderboard';
import { Rules } from '../../App';

const BoardViewer = () => {
  // Get display name from URL params
  const { displayName } = useParams();
  const navigate = useNavigate();

  // Get current user from context
  const { user } = useUser();

  // State for board data and owner info
  const [boardOwner, setBoardOwner] = useState(null);
  const [board, setBoard] = useState(null);
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Determine if this is the current user's board
  const isOwnBoard = user && displayName.toLowerCase() === user.display_name.toLowerCase();

  // Fetch board data and owner info
  useEffect(() => {
    const fetchBoardData = async () => {
      try {
        setLoading(true);

        // Fetch the user's board by display name
        const boardResponse = await fetch(`http://localhost:5000/api/boards/${encodeURIComponent(displayName)}`);

        if (!boardResponse.ok) {
          if (boardResponse.status === 404) {
            throw new Error('User not found or no board exists for this user');
          }
          throw new Error(`HTTP error! Status: ${boardResponse.status}`);
        }

        const boardData = await boardResponse.json();
        setBoard(boardData.board);
        setBoardOwner(boardData.user);

        // Fetch the board progress
        const progressResponse = await fetch(`http://localhost:5000/api/boards/${encodeURIComponent(displayName)}/progress`);

        if (!progressResponse.ok) {
          throw new Error(`HTTP error! Status: ${progressResponse.status}`);
        }

        const progressData = await progressResponse.json();
        setProgress(progressData);

      } catch (err) {
        console.error('Error fetching board data:', err);
        setError(err.message || 'Failed to load board data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchBoardData();
  }, [displayName]);

  // Handle back to dashboard button
  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  // If loading, show loading message
  if (loading) {
    return <div className="loading-message">Loading board...</div>;
  }

  // If error, show error message
  if (error) {
    return (
      <div className="error-container">
        <div className="error-message">{error}</div>
        <button onClick={handleBackToDashboard} className="back-button">
          Back to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="board-viewer-container">
      <div className="board-viewer-header">
        <h1 className={`board-title ${isOwnBoard ? 'your-board-title' : ''}`}>
          {isOwnBoard ? 'Your Board' : `${boardOwner.display_name}'s Board`}
        </h1>
      </div>

      {board && progress && boardOwner && (
        <BingoBoard
          boardData={board.board_data}
          progressData={progress}
          isReadOnly={!isOwnBoard}
          userId={boardOwner.id}
          boardId={board.id}
        />
      )}

      <Leaderboard />

      <button onClick={handleBackToDashboard} className="back-button">
        Back to Dashboard
      </button>

      {/* How to Play and Rules sections */}
      <div className="dashboard-info-sections">
        <Rules />
      </div>
    </div>
  );
};

export default BoardViewer;
