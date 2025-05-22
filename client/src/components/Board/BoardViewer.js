import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useUser } from '../Auth/UserContext';

// Import components from App.js (we'll extract these later)
import BingoBoard from './BingoBoard';
import Leaderboard from './Leaderboard';
import { Rules } from '../../App';

const BoardViewer = () => {
  // Get user ID from URL params
  const { userId } = useParams();
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
  const isOwnBoard = user && parseInt(userId) === user.id;

  // Fetch board data and owner info
  useEffect(() => {
    const fetchBoardData = async () => {
      try {
        setLoading(true);

        // Fetch all users to find the board owner
        const usersResponse = await fetch('http://localhost:5000/api/users');

        if (!usersResponse.ok) {
          throw new Error(`HTTP error! Status: ${usersResponse.status}`);
        }

        const usersData = await usersResponse.json();
        const owner = usersData.find(u => u.id === parseInt(userId));

        if (!owner) {
          throw new Error('User not found');
        }

        setBoardOwner(owner);

        // Fetch the user's board
        const boardResponse = await fetch(`http://localhost:5000/api/users/${userId}/board`);

        if (!boardResponse.ok) {
          throw new Error(`HTTP error! Status: ${boardResponse.status}`);
        }

        const boardData = await boardResponse.json();
        setBoard(boardData);

        // Fetch the board progress
        const progressResponse = await fetch(`http://localhost:5000/api/users/${userId}/boards/${boardData.id}/progress`);

        if (!progressResponse.ok) {
          throw new Error(`HTTP error! Status: ${progressResponse.status}`);
        }

        const progressData = await progressResponse.json();
        setProgress(progressData);

      } catch (err) {
        console.error('Error fetching board data:', err);
        setError('Failed to load board data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchBoardData();
  }, [userId]);

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

      {board && progress && (
        <BingoBoard
          boardData={board.board_data}
          progressData={progress}
          isReadOnly={!isOwnBoard}
          userId={parseInt(userId)}
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
