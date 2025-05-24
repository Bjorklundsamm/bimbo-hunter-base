import React, { useState, useEffect } from 'react';

const PortraitOverlay = ({ character, onClose, onClaim, sourcePosition, isClaimed, isReadOnly }) => {
  // Get the portrait URL from the portrait path
  const getPortraitUrl = (portraitPath) => {
    if (!portraitPath) return null;
    return `${process.env.PUBLIC_URL}${portraitPath}`;
  };

  const portraitUrl = getPortraitUrl(character.Portrait);

  // Get the frame overlay URL based on character rarity
  const getFrameOverlayUrl = (rarity) => {
    if (!rarity || rarity === 'FREE') return null; // No frame for FREE characters
    return `${process.env.PUBLIC_URL}/frames/${rarity} - Portrait.png`;
  };

  const frameOverlayUrl = getFrameOverlayUrl(character.rarity);

  // Use state to control animation classes and details visibility
  const [isVisible, setIsVisible] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  // Apply the animation after component mounts
  useEffect(() => {
    // Small delay to ensure the component is rendered before animation starts
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, 50);

    return () => clearTimeout(timer);
  }, []);

  // Handle closing with animation
  const handleClose = () => {
    setIsVisible(false);
    setShowDetails(false);
    // Wait for animation to complete before actually closing
    setTimeout(onClose, 300);
  };

  // Handle claiming with animation
  const handleClaim = () => {
    if (isReadOnly) return; // Disable claiming for read-only mode

    setIsVisible(false);
    setShowDetails(false);
    // Wait for animation to complete before actually claiming
    setTimeout(onClaim, 300);
  };

  // Handle showing/hiding details
  const handleToggleDetails = () => {
    setShowDetails(!showDetails);
  };

  // Get rarity value text
  const getRarityValue = (rarity) => {
    switch (rarity) {
      case 'FREE':
        return 'FREE (1 pt)';
      case 'R':
        return 'R (2 pts)';
      case 'SR':
        return 'SR (3 pts)';
      case 'SSR':
        return 'SSR (4 pts)';
      case 'UR+':
        return 'UR+ (6 pts)';
      default:
        return 'Unknown';
    }
  };

  // Get rarity color for details button
  const getRarityColor = (rarity) => {
    switch (rarity) {
      case 'FREE':
        return '#4CAF50'; // Green
      case 'R':
        return '#2196F3'; // Blue
      case 'SR':
        return '#9C27B0'; // Purple
      case 'SSR':
        return '#FF9800'; // Orange
      case 'UR+':
        return '#F44336'; // Red
      default:
        return '#2196F3'; // Default blue
    }
  };

  return (
    <div className={`portrait-overlay ${isVisible ? 'visible' : ''}`}>
      <div
        className={`portrait-container ${isVisible ? 'visible' : ''}`}
        style={sourcePosition ? {
          // If we have source position, use it for initial transform origin
          transformOrigin: `${sourcePosition.x}px ${sourcePosition.y}px`
        } : {}}
      >
        <button className="close-button" onClick={handleClose}>×</button>
        <div className="portrait-image-container">
          <img
            src={portraitUrl}
            alt={character.Name}
            className="character-portrait"
          />
          {frameOverlayUrl && (
            <img
              src={frameOverlayUrl}
              alt={`${character.rarity} frame`}
              className="portrait-frame-overlay"
            />
          )}
        </div>
        <div className="portrait-buttons">
          {!isReadOnly && (
            <button
              className={`claim-button ${isClaimed ? 'unclaim' : ''}`}
              onClick={handleClaim}
            >
              {isClaimed ? 'Unclaim' : 'Claim!'}
            </button>
          )}
          <button
            className="details-button"
            onClick={handleToggleDetails}
            style={{
              backgroundColor: getRarityColor(character.rarity),
              boxShadow: `0 0 20px ${getRarityColor(character.rarity)}80, 0 4px 6px rgba(0, 0, 0, 0.1)`
            }}
          >
            Details
          </button>
        </div>

        {showDetails && (
          <div
            className="character-details-overlay"
            onClick={() => setShowDetails(false)}
          >
            <div
              className="character-details-content"
              onClick={(e) => e.stopPropagation()} // Prevent clicks on content from closing
            >
              <p><strong>Name:</strong><br />{character.Name}</p>
              <p><strong>Source:</strong><br />{character.Source}</p>
              <p><strong>Value:</strong><br />{getRarityValue(character.rarity)}</p>
              <p><strong>What to look for:</strong><br />{character.description || "No description available"}</p>
              <p><strong>Special conditions:</strong><br />{character.conditions || "None"}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PortraitOverlay;
