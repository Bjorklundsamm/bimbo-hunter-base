import React, { useState, useEffect } from 'react';
import { useUser } from '../Auth/UserContext';
import { useNavigate } from 'react-router-dom';
import { Rules } from '../../App';

const UserDashboard = () => {
  // Get user context and navigation
  const { user, logout } = useUser();
  const navigate = useNavigate();

  // State for users list and user's board
  const [users, setUsers] = useState([]);
  const [userBoard, setUserBoard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showRefreshConfirmation, setShowRefreshConfirmation] = useState(false);

  // Fetch all users and check if current user has a board on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch all users
        const usersResponse = await fetch('http://localhost:5000/api/users');

        if (!usersResponse.ok) {
          throw new Error(`HTTP error! Status: ${usersResponse.status}`);
        }

        const usersData = await usersResponse.json();
        setUsers(usersData);

        // Check if user has a board
        if (user) {
          const boardResponse = await fetch(`http://localhost:5000/api/users/${user.id}/board`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          });

          if (boardResponse.ok) {
            const boardData = await boardResponse.json();
            setUserBoard(boardData);
          } else if (boardResponse.status !== 404) {
            // Only throw error if it's not a 404 (no board found)
            throw new Error(`HTTP error! Status: ${boardResponse.status}`);
          }
        }
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user]);

  // Handle logout
  const handleLogout = () => {
    logout();
    navigate('/');
  };

  // Navigate to current user's board
  const viewMyBoard = () => {
    navigate(`/boards/${encodeURIComponent(user.display_name)}`);
  };

  // Navigate to another user's board
  const viewUserBoard = (displayName) => {
    navigate(`/boards/${encodeURIComponent(displayName)}`);
  };

  // Create a new board for the current user
  const createNewBoard = async () => {
    try {
      setLoading(true);

      const response = await fetch(`http://localhost:5000/api/users/${user.id}/board`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      // Update local state with the new board
      const boardData = await response.json();
      setUserBoard(boardData);

      // Navigate to the new board
      navigate(`/boards/${encodeURIComponent(user.display_name)}`);
    } catch (err) {
      console.error('Error creating new board:', err);
      setError('Failed to create new board. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Handle refresh board button click
  const handleRefreshClick = () => {
    setShowRefreshConfirmation(true);
  };

  // Handle cancel refresh
  const handleCancelRefresh = () => {
    setShowRefreshConfirmation(false);
  };

  // Handle confirm refresh
  const handleConfirmRefresh = async () => {
    try {
      setLoading(true);
      setShowRefreshConfirmation(false);

      const response = await fetch(`http://localhost:5000/api/users/${user.id}/board`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      // Update local state with the new board
      const boardData = await response.json();
      setUserBoard(boardData);

      // Navigate to the new board
      navigate(`/boards/${encodeURIComponent(user.display_name)}`);
    } catch (err) {
      console.error('Error refreshing board:', err);
      setError('Failed to refresh board. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // If user is not logged in, redirect to login page
  if (!user) {
    navigate('/');
    return null;
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Welcome, {user.display_name}!</h1>
        <button onClick={handleLogout} className="logout-button">Logout</button>
      </div>

      <div className="dashboard-actions">
        {loading ? (
          <div className="loading-message">Loading...</div>
        ) : userBoard ? (
          <button onClick={viewMyBoard} className="action-button">
            View My Board
          </button>
        ) : (
          <button onClick={createNewBoard} className="action-button">
            Generate a Board
          </button>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="users-section">
        <h2>Other Players</h2>
        {loading ? (
          <div className="loading-message">Loading users...</div>
        ) : (
          <div className="users-list">
            {users
              .filter(u => u.id !== user.id) // Filter out current user
              .map(u => (
                <div key={u.id} className="user-item">
                  <span className="user-name">{u.display_name}</span>
                  <button
                    onClick={() => viewUserBoard(u.display_name)}
                    className="view-board-button"
                  >
                    View Board
                  </button>
                </div>
              ))}
            {users.length <= 1 && (
              <div className="no-users-message">
                No other players yet. Invite your friends!
              </div>
            )}
          </div>
        )}
      </div>

      {/* Refresh confirmation dialog */}
      {showRefreshConfirmation && (
        <div className="confirmation-overlay">
          <div className="confirmation-dialog">
            <h3>Warning!</h3>
            <p>
              Refreshing your board will delete your previous one and restart your progress.
              Are you sure you want to continue?
            </p>
            <div className="confirmation-buttons">
              <button onClick={handleCancelRefresh} className="cancel-button">
                Cancel
              </button>
              <button onClick={handleConfirmRefresh} className="confirm-button">
                Yes, Refresh My Board
              </button>
            </div>
          </div>
        </div>
      )}

      {/* How to Play and Rules sections */}
      <div className="dashboard-info-sections">
        <Rules />
      </div>
    </div>
  );
};

export default UserDashboard;
