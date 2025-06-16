import React, { useState, useEffect } from 'react';
import PortraitOverlay from '../Board/PortraitOverlay';

const Cards = () => {
  const [characters, setCharacters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCharacter, setSelectedCharacter] = useState(null);

  // Fetch all characters
  useEffect(() => {
    const fetchCharacters = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:5000/api/characters');
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        setCharacters(data);
      } catch (err) {
        console.error('Error fetching characters:', err);
        setError('Failed to load characters');
      } finally {
        setLoading(false);
      }
    };

    fetchCharacters();
  }, []);

  const handleCharacterClick = (character, index) => {
    setSelectedCharacter(character);
  };

  const handleCloseOverlay = () => {
    setSelectedCharacter(null);
  };

  if (loading) {
    return (
      <div className="cards-container">
        <h1>All Available Cards</h1>
        <div className="loading-message">Loading cards...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="cards-container">
        <h1>All Available Cards</h1>
        <div className="error-message">{error}</div>
      </div>
    );
  }

  // Group characters by rarity
  const groupedCharacters = characters.reduce((groups, character) => {
    const rarity = character.rarity || 'R';
    if (!groups[rarity]) {
      groups[rarity] = [];
    }
    groups[rarity].push(character);
    return groups;
  }, {});

  // Define rarity order and colors (matching the official rarity colors used in BingoSquare)
  const rarityOrder = ['FREE', 'R', 'SR', 'SSR', 'UR+'];
  const rarityColors = {
    'FREE': '#4CAF50', // Green
    'R': '#2196F3',    // Blue
    'SR': '#9C27B0',   // Purple
    'SSR': '#FF9800',  // Orange
    'UR+': '#F44336'   // Red
  };

  return (
    <div className="cards-container">
      <h1>All Available Cards</h1>
      <div className="cards-content">
        {rarityOrder.map(rarity => {
          const rarityCharacters = groupedCharacters[rarity] || [];
          if (rarityCharacters.length === 0) return null;

          return (
            <div key={rarity} className="rarity-section">
              <h2 className="rarity-title" style={{ color: rarityColors[rarity] }}>
                {rarity} ({rarityCharacters.length} cards)
              </h2>
              <div className="cards-grid">
                {rarityCharacters.map((character, index) => (
                  <div
                    key={`${rarity}-${index}`}
                    className="card-item"
                    onClick={() => handleCharacterClick(character, index)}
                  >
                    <div className="card-image-container">
                      <img
                        src={`${process.env.PUBLIC_URL}${character.Thumbnail}`}
                        alt={character.Name}
                        className="card-thumbnail"
                        onError={(e) => {
                          console.error('Failed to load thumbnail:', character.Thumbnail);
                          e.target.style.display = 'none';
                        }}
                      />
                      {character.rarity !== 'FREE' && (
                        <img
                          src={`${process.env.PUBLIC_URL}/frames/${character.rarity}.png`}
                          alt={`${character.rarity} frame`}
                          className="card-frame"
                          onError={(e) => {
                            console.error('Failed to load frame:', `/frames/${character.rarity}.png`);
                            e.target.style.display = 'none';
                          }}
                        />
                      )}
                    </div>
                    <div className="card-info">
                      <h3 className="card-name">{character.Name}</h3>
                      <p className="card-source">{character.Source}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {selectedCharacter && (
        <PortraitOverlay
          character={selectedCharacter}
          onClose={handleCloseOverlay}
          onClaim={() => {}} // No claim functionality in cards view
          isClaimed={false}
          isReadOnly={true} // Make it read-only so no claim button shows
        />
      )}
    </div>
  );
};

export default Cards;
