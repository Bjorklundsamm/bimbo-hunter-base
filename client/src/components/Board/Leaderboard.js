import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Leaderboard = () => {
  const navigate = useNavigate();
  // State for leaderboard data
  const [leaderboardData, setLeaderboardData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch leaderboard data
  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        setLoading(true);

        const response = await fetch('http://localhost:5000/api/leaderboard');

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        setLeaderboardData(data);
      } catch (err) {
        console.error('Error fetching leaderboard:', err);
        setError('Failed to load leaderboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchLeaderboard();

    // Set up polling to refresh leaderboard data
    const intervalId = setInterval(fetchLeaderboard, 30000); // Refresh every 30 seconds

    return () => clearInterval(intervalId); // Clean up on unmount
  }, []);

  // Sort data by score in descending order
  const sortedData = [...leaderboardData].sort((a, b) => b.score - a.score);

  // Find the maximum score for scaling
  const maxScore = Math.max(...sortedData.map(user => user.score || 0), 1); // Ensure we don't divide by zero

  // Truncate display name to max 16 characters
  const truncateDisplayName = (displayName) => {
    if (displayName.length <= 16) {
      return displayName;
    }
    return displayName.substring(0, 16) + '...';
  };

  // Handle clicking on a leaderboard entry to view their board
  const handleViewUserBoard = (displayName) => {
    navigate(`/boards/${encodeURIComponent(displayName)}`);
  };

  if (loading) {
    return (
      <div className="leaderboard-section">
        <h2>Leaderboard</h2>
        <div className="loading-message">Loading leaderboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="leaderboard-section">
        <h2>Leaderboard</h2>
        <div className="error-message">{error}</div>
      </div>
    );
  }

  return (
    <div className="leaderboard-section">
      <h2>Leaderboard</h2>
      <div className="leaderboard-container">
        {sortedData.length > 0 ? (
          sortedData.map((user, index) => (
            <div
              key={index}
              className="leaderboard-entry"
              onClick={() => handleViewUserBoard(user.display_name)}
              title={`View ${user.display_name}'s board`}
            >
              <div className="user-rank">{index + 1}</div>
              <div
                className="user-name"
                title={user.display_name} // Show full name on hover
              >
                {truncateDisplayName(user.display_name)}
              </div>
              <div className="score-number">{user.score}</div>
            </div>
          ))
        ) : (
          <div className="no-data-message">No scores yet. Be the first to score!</div>
        )}
      </div>
    </div>
  );
};

export default Leaderboard;
