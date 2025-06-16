import React, { useState, useEffect } from 'react';
import { useUser } from '../Auth/UserContext';
import { useNavigate } from 'react-router-dom';
import './AdminPanel.css';

const AdminPanel = () => {
  const { user, logout } = useUser();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState(''); // 'success' or 'error'

  // State for different admin operations
  const [players, setPlayers] = useState([]);
  const [boards, setBoards] = useState([]);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [selectedBoard, setSelectedBoard] = useState(null);
  const [editingDisplayName, setEditingDisplayName] = useState(null);
  const [newDisplayName, setNewDisplayName] = useState('');
  const [editingBoard, setEditingBoard] = useState(null);
  const [boardProgress, setBoardProgress] = useState(null);

  // Fetch players and boards on component mount
  useEffect(() => {
    // Only fetch if user is admin
    if (user && user.is_admin) {
      fetchPlayers();
      fetchBoards();
    }
  }, [user]);

  // Check if user is admin - moved after hooks
  if (!user || !user.is_admin) {
    return <div className="admin-error">Access denied. Admin privileges required.</div>;
  }

  const showMessage = (msg, type = 'success') => {
    setMessage(msg);
    setMessageType(type);
    setTimeout(() => {
      setMessage('');
      setMessageType('');
    }, 5000);
  };

  const fetchPlayers = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/users');
      if (response.ok) {
        const data = await response.json();
        setPlayers(data);
      }
    } catch (error) {
      console.error('Error fetching players:', error);
    }
  };

  const fetchBoards = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/admin/boards');
      if (response.ok) {
        const data = await response.json();
        setBoards(data);
      }
    } catch (error) {
      console.error('Error fetching boards:', error);
    }
  };

  const restartServer = async () => {
    if (!window.confirm('Are you sure you want to restart the server? This will disconnect all users.')) {
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/admin/restart-server', {
        method: 'POST',
      });
      
      if (response.ok) {
        showMessage('Server restart initiated. Please wait for reconnection.');
      } else {
        showMessage('Failed to restart server', 'error');
      }
    } catch (error) {
      showMessage('Error restarting server', 'error');
    }
    setLoading(false);
  };

  const deleteAllBoards = async () => {
    if (!window.confirm('Are you sure you want to delete ALL boards? This action cannot be undone.')) {
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/admin/delete-all-boards', {
        method: 'DELETE',
      });
      
      if (response.ok) {
        const data = await response.json();
        showMessage(data.message);
        fetchBoards(); // Refresh boards list
      } else {
        showMessage('Failed to delete all boards', 'error');
      }
    } catch (error) {
      showMessage('Error deleting all boards', 'error');
    }
    setLoading(false);
  };

  const deleteAllPlayers = async () => {
    if (!window.confirm('Are you sure you want to delete ALL players? This action cannot be undone.')) {
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/admin/delete-all-players', {
        method: 'DELETE',
      });
      
      if (response.ok) {
        const data = await response.json();
        showMessage(data.message);
        fetchPlayers(); // Refresh players list
        fetchBoards(); // Refresh boards list
      } else {
        showMessage('Failed to delete all players', 'error');
      }
    } catch (error) {
      showMessage('Error deleting all players', 'error');
    }
    setLoading(false);
  };

  const deletePlayer = async (playerId, playerName) => {
    if (!window.confirm(`Are you sure you want to delete player "${playerName}"? This action cannot be undone.`)) {
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:5000/api/admin/delete-player/${playerId}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        const data = await response.json();
        showMessage(data.message);
        fetchPlayers(); // Refresh players list
        fetchBoards(); // Refresh boards list
      } else {
        showMessage('Failed to delete player', 'error');
      }
    } catch (error) {
      showMessage('Error deleting player', 'error');
    }
    setLoading(false);
  };

  const deleteBoard = async (userId, playerName) => {
    if (!window.confirm(`Are you sure you want to delete the board for "${playerName}"? This action cannot be undone.`)) {
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:5000/api/admin/delete-board/${userId}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        const data = await response.json();
        showMessage(data.message);
        fetchBoards(); // Refresh boards list
      } else {
        showMessage('Failed to delete board', 'error');
      }
    } catch (error) {
      showMessage('Error deleting board', 'error');
    }
    setLoading(false);
  };

  const updateDisplayName = async (userId, currentName) => {
    if (!newDisplayName.trim()) {
      showMessage('Please enter a new display name', 'error');
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:5000/api/admin/update-display-name/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ display_name: newDisplayName }),
      });
      
      if (response.ok) {
        const data = await response.json();
        showMessage(data.message);
        fetchPlayers(); // Refresh players list
        fetchBoards(); // Refresh boards list
        setEditingDisplayName(null);
        setNewDisplayName('');
      } else {
        const data = await response.json();
        showMessage(data.error || 'Failed to update display name', 'error');
      }
    } catch (error) {
      showMessage('Error updating display name', 'error');
    }
    setLoading(false);
  };

  return (
    <div className="admin-panel">
      <div className="admin-header">
        <h1>Admin Panel</h1>
        <div className="admin-header-info">
          <p>Welcome, {user.display_name}</p>
          <button
            onClick={() => {
              logout();
              navigate('/');
            }}
            className="admin-button secondary small"
          >
            Logout
          </button>
        </div>
      </div>

      {message && (
        <div className={`admin-message ${messageType}`}>
          {message}
        </div>
      )}

      <div className="admin-sections">
        {/* Server Management */}
        <div className="admin-section">
          <h2>Server Management</h2>
          <button 
            onClick={restartServer} 
            disabled={loading}
            className="admin-button danger"
          >
            Restart Server
          </button>
        </div>

        {/* Bulk Operations */}
        <div className="admin-section">
          <h2>Bulk Operations</h2>
          <button 
            onClick={deleteAllBoards} 
            disabled={loading}
            className="admin-button danger"
          >
            Delete All Boards
          </button>
          <button 
            onClick={deleteAllPlayers} 
            disabled={loading}
            className="admin-button danger"
          >
            Delete All Players
          </button>
        </div>

        {/* Player Management */}
        <div className="admin-section">
          <h2>Player Management</h2>
          <div className="player-list">
            {players.map(player => (
              <div key={player.id} className="player-item">
                <div className="player-info">
                  <span className="player-name">{player.display_name}</span>
                  <span className="player-pin">PIN: {player.pin}</span>
                </div>
                <div className="player-actions">
                  <button
                    onClick={() => deletePlayer(player.id, player.display_name)}
                    disabled={loading}
                    className="admin-button small danger"
                  >
                    Delete Player
                  </button>
                  {editingDisplayName === player.id ? (
                    <div className="edit-name-form">
                      <input
                        type="text"
                        value={newDisplayName}
                        onChange={(e) => setNewDisplayName(e.target.value)}
                        placeholder="New display name"
                      />
                      <button
                        onClick={() => updateDisplayName(player.id, player.display_name)}
                        disabled={loading}
                        className="admin-button small"
                      >
                        Save
                      </button>
                      <button
                        onClick={() => {
                          setEditingDisplayName(null);
                          setNewDisplayName('');
                        }}
                        className="admin-button small secondary"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => {
                        setEditingDisplayName(player.id);
                        setNewDisplayName(player.display_name);
                      }}
                      disabled={loading}
                      className="admin-button small"
                    >
                      Edit Name
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Board Management */}
        <div className="admin-section">
          <h2>Board Management</h2>
          <div className="board-list">
            {boards.map(board => (
              <div key={board.id} className="board-item">
                <div className="board-info">
                  <span className="board-player">{board.display_name}</span>
                  <span className="board-created">Created: {new Date(board.created_at).toLocaleDateString()}</span>
                </div>
                <div className="board-actions">
                  <button
                    onClick={() => deleteBoard(board.user_id, board.display_name)}
                    disabled={loading}
                    className="admin-button small danger"
                  >
                    Delete Board
                  </button>
                  <button
                    onClick={() => setEditingBoard(board)}
                    disabled={loading}
                    className="admin-button small"
                  >
                    Edit Board
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Board Editor Modal */}
      {editingBoard && (
        <BoardEditor
          board={editingBoard}
          onClose={() => setEditingBoard(null)}
          onUpdate={() => {
            fetchBoards();
            setEditingBoard(null);
            showMessage('Board updated successfully');
          }}
        />
      )}
    </div>
  );
};

// Board Editor Component
const BoardEditor = ({ board, onClose, onUpdate }) => {
  const [boardProgress, setBoardProgress] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchBoardProgress();
  }, [board]);

  const fetchBoardProgress = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/boards/${encodeURIComponent(board.display_name)}/progress`);
      if (response.ok) {
        const data = await response.json();
        setBoardProgress(data);
      }
    } catch (error) {
      console.error('Error fetching board progress:', error);
    }
  };

  const toggleSquare = async (squareIndex) => {
    if (!boardProgress) return;

    setLoading(true);
    try {
      const markedCells = [...boardProgress.marked_cells];
      const userImages = { ...boardProgress.user_images };

      if (markedCells.includes(squareIndex)) {
        // Unclaim the square
        const index = markedCells.indexOf(squareIndex);
        markedCells.splice(index, 1);
        delete userImages[squareIndex];
      } else {
        // Claim the square
        markedCells.push(squareIndex);
      }

      // Calculate new score
      let newScore = 0;
      markedCells.forEach(cellIndex => {
        const character = board.board_data[cellIndex];
        if (character) {
          switch (character.rarity) {
            case 'FREE': newScore += 1; break;
            case 'R': newScore += 2; break;
            case 'SR': newScore += 3; break;
            case 'SSR': newScore += 4; break;
            case 'UR+': newScore += 6; break;
            default: newScore += 1; break;
          }
        }
      });

      // Check for completed rows/columns and add bonus points
      const completedLines = checkCompletedLines(markedCells);
      newScore += completedLines * 5;

      const response = await fetch(`http://localhost:5000/api/admin/boards/${board.user_id}/progress`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          marked_cells: markedCells,
          user_images: userImages,
          score: newScore
        }),
      });

      if (response.ok) {
        const updatedProgress = await response.json();
        setBoardProgress(updatedProgress);
      }
    } catch (error) {
      console.error('Error updating board progress:', error);
    }
    setLoading(false);
  };

  const checkCompletedLines = (markedCells) => {
    let completedLines = 0;

    // Check rows
    for (let row = 0; row < 5; row++) {
      let rowComplete = true;
      for (let col = 0; col < 5; col++) {
        if (!markedCells.includes(row * 5 + col)) {
          rowComplete = false;
          break;
        }
      }
      if (rowComplete) completedLines++;
    }

    // Check columns
    for (let col = 0; col < 5; col++) {
      let colComplete = true;
      for (let row = 0; row < 5; row++) {
        if (!markedCells.includes(row * 5 + col)) {
          colComplete = false;
          break;
        }
      }
      if (colComplete) completedLines++;
    }

    return completedLines;
  };

  if (!boardProgress) {
    return (
      <div className="board-editor-overlay">
        <div className="board-editor">
          <div>Loading board...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="board-editor-overlay">
      <div className="board-editor">
        <div className="board-editor-header">
          <h3>Editing Board for {board.display_name}</h3>
          <button onClick={onClose} className="admin-button secondary">Close</button>
        </div>

        <div className="board-editor-content">
          <div className="board-grid">
            {board.board_data.map((character, index) => (
              <div
                key={index}
                className={`board-square ${boardProgress.marked_cells.includes(index) ? 'claimed' : ''} ${character.rarity === 'FREE' ? 'free' : ''}`}
                onClick={() => toggleSquare(index)}
                style={{ cursor: loading ? 'not-allowed' : 'pointer' }}
              >
                {character.rarity === 'FREE' ? 'FREE' : character.name}
              </div>
            ))}
          </div>

          <div className="board-stats">
            <p>Score: {boardProgress.score}</p>
            <p>Claimed Squares: {boardProgress.marked_cells.length}/25</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;
