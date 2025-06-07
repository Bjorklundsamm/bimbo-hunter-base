import React, { useState, useEffect, useRef } from 'react';

const PortraitOverlay = ({ character, onClose, onClaim, sourcePosition, isClaimed, isReadOnly, userId, boardId, squareIndex }) => {
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
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const fileInputRef = useRef(null);

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

  // Handle file selection
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setShowUpload(true);
    }
  };

  // Handle file upload
  const handleUpload = async () => {
    if (!selectedFile || !userId || !boardId || squareIndex === undefined) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`http://localhost:5000/api/users/${userId}/boards/${boardId}/upload/${squareIndex}`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        // Call onClaim with the uploaded image path
        onClaim(result.image_path);
        setIsVisible(false);
        setShowDetails(false);
        setShowUpload(false);
      } else {
        console.error('Upload failed');
        alert('Failed to upload image. Please try again.');
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload image. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  // Handle claiming with animation (for unclaiming)
  const handleClaim = () => {
    if (isReadOnly) return; // Disable claiming for read-only mode

    if (isClaimed) {
      // If already claimed, just unclaim
      setIsVisible(false);
      setShowDetails(false);
      setTimeout(() => onClaim(null), 300);
    } else {
      // If not claimed, show upload interface
      setShowUpload(true);
    }
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
          {!isReadOnly && !showUpload && (
            <button
              className={`claim-button ${isClaimed ? 'unclaim' : ''}`}
              onClick={handleClaim}
            >
              {isClaimed ? 'Unclaim' : 'Claim!'}
            </button>
          )}
          {!showUpload && (
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
          )}
        </div>

        {/* Upload Interface Overlay */}
        {showUpload && !isReadOnly && (
          <div
            className="character-details-overlay"
            onClick={() => {
              setShowUpload(false);
              setSelectedFile(null);
            }}
          >
            <div
              className="character-details-content upload-overlay-content"
              onClick={(e) => e.stopPropagation()} // Prevent clicks on content from closing
            >
              <h3 className="upload-title">Upload Your Photo</h3>
              <p className="upload-description">Upload a photo of yourself with this cosplayer to claim this square!</p>

              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileSelect}
                accept="image/*"
                style={{ display: 'none' }}
              />

              <div className="upload-buttons">
                <button
                  className="details-button upload-select-button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploading}
                  style={{
                    backgroundColor: getRarityColor(character.rarity),
                    boxShadow: `0 0 20px ${getRarityColor(character.rarity)}80, 0 4px 6px rgba(0, 0, 0, 0.1)`
                  }}
                >
                  {selectedFile ? 'Change Photo' : 'Select Photo'}
                </button>

                {selectedFile && (
                  <div className="selected-file-info">
                    <p><strong style={{ color: getRarityColor(character.rarity) }}>Selected:</strong><br />{selectedFile.name}</p>
                    <div className="upload-actions">
                      <button
                        className="details-button upload-confirm-button"
                        onClick={handleUpload}
                        disabled={uploading}
                        style={{
                          backgroundColor: '#4CAF50',
                          boxShadow: '0 0 20px #4CAF5080, 0 4px 6px rgba(0, 0, 0, 0.1)'
                        }}
                      >
                        {uploading ? 'Uploading...' : 'Upload & Claim'}
                      </button>
                      <button
                        className="details-button upload-cancel-button"
                        onClick={() => {
                          setShowUpload(false);
                          setSelectedFile(null);
                        }}
                        disabled={uploading}
                        style={{
                          backgroundColor: '#f44336',
                          boxShadow: '0 0 20px #f4433680, 0 4px 6px rgba(0, 0, 0, 0.1)'
                        }}
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}

                {/* Cancel button always visible */}
                {!selectedFile && (
                  <button
                    className="details-button upload-cancel-button"
                    onClick={() => {
                      setShowUpload(false);
                      setSelectedFile(null);
                    }}
                    disabled={uploading}
                    style={{
                      backgroundColor: '#f44336',
                      boxShadow: '0 0 20px #f4433680, 0 4px 6px rgba(0, 0, 0, 0.1)'
                    }}
                  >
                    Cancel
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {showDetails && (
          <div
            className="character-details-overlay"
            onClick={() => setShowDetails(false)}
          >
            <div
              className="character-details-content"
              onClick={(e) => e.stopPropagation()} // Prevent clicks on content from closing
            >
              <p><strong style={{ color: getRarityColor(character.rarity) }}>Name:</strong><br />{character.Name}</p>
              <p><strong style={{ color: getRarityColor(character.rarity) }}>Source:</strong><br />{character.Source}</p>
              <p><strong style={{ color: getRarityColor(character.rarity) }}>Value:</strong><br />{getRarityValue(character.rarity)}</p>
              <p><strong style={{ color: getRarityColor(character.rarity) }}>What to look for:</strong><br />{character.description || "No description available"}</p>
              <p><strong style={{ color: getRarityColor(character.rarity) }}>Special conditions:</strong><br />{character.conditions || "None"}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PortraitOverlay;
