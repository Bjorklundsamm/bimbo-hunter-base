import React, { useState, useEffect } from 'react';
import { useUser } from '../Auth/UserContext';
import { useNavigate } from 'react-router-dom';
import { Rules } from '../../App';
import { getApiUrl } from '../../config/api';

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
  const [showAgreementModal, setShowAgreementModal] = useState(false);
  const [hasAgreedToTerms, setHasAgreedToTerms] = useState(false);

  // Fetch all users and check if current user has a board on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch all users
        const usersResponse = await fetch(getApiUrl('/api/users'));

        if (!usersResponse.ok) {
          throw new Error(`HTTP error! Status: ${usersResponse.status}`);
        }

        const usersData = await usersResponse.json();
        setUsers(usersData);

        // Check if user has a board
        if (user) {
          const boardResponse = await fetch(getApiUrl(`/api/users/${user.id}/board`), {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          });

          if (boardResponse.ok) {
            const boardData = await boardResponse.json();
            setUserBoard(boardData);
            // If user has a board, redirect them to their board immediately
            navigate(`/boards/${encodeURIComponent(user.display_name)}`);
            return; // Exit early since we're redirecting
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
  }, [user, navigate]);

  // Handle logout
  const handleLogout = () => {
    logout();
    navigate('/');
  };

  // Navigate to another user's board
  const viewUserBoard = (displayName) => {
    navigate(`/boards/${encodeURIComponent(displayName)}`);
  };

  // Show the agreement modal
  const handleStartPlayingClick = () => {
    setShowAgreementModal(true);
  };

  // Handle agreement modal confirmation
  const handleAgreementConfirm = () => {
    if (!hasAgreedToTerms) {
      setError('Please agree to review the How to Play section and Rules before starting.');
      return;
    }
    setShowAgreementModal(false);
    createNewBoard();
  };

  // Handle agreement modal cancellation
  const handleAgreementCancel = () => {
    setShowAgreementModal(false);
    setHasAgreedToTerms(false);
  };

  // Create a new board for the current user
  const createNewBoard = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(getApiUrl(`/api/users/${user.id}/board`), {
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

  // Handle cancel refresh
  const handleCancelRefresh = () => {
    setShowRefreshConfirmation(false);
  };

  // Handle confirm refresh
  const handleConfirmRefresh = async () => {
    try {
      setLoading(true);
      setShowRefreshConfirmation(false);

      const response = await fetch(getApiUrl(`/api/users/${user.id}/board`), {
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
        ) : !userBoard ? (
          <div className="board-creation-section">
            <h2>Ready to Start Playing?</h2>
            <button
              onClick={handleStartPlayingClick}
              className="start-playing-button enabled"
              disabled={loading}
            >
              Start Playing!
            </button>
          </div>
        ) : null}
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

      {/* Agreement modal */}
      {showAgreementModal && (
        <div className="confirmation-overlay">
          <div className="agreement-modal">
            <h3>Before You Start Playing</h3>
            <div className="agreement-text">
              <p>
                Before playing or making any complaints, you must read the <a href="/how-to-play" target="_blank" rel="noopener noreferrer">How to Play</a> section and the <a href="#rules">Rules</a> to understand the game mechanics, scoring system, and proper etiquette.
              </p>
            </div>
            <div className="agreement-checkbox-section">
              <label className="agreement-checkbox">
                <input
                  type="checkbox"
                  checked={hasAgreedToTerms}
                  onChange={(e) => setHasAgreedToTerms(e.target.checked)}
                />
                I promise
              </label>
            </div>
            <div className="confirmation-buttons">
              <button onClick={handleAgreementCancel} className="cancel-button">
                Cancel
              </button>
              <button
                onClick={handleAgreementConfirm}
                className={`confirm-button ${hasAgreedToTerms ? 'enabled' : 'disabled'}`}
                disabled={!hasAgreedToTerms}
              >
                Start Playing!
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
