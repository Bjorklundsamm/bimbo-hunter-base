import React from 'react';

const BingoSquare = ({ character, isMarked, onClick, onPortraitClick, index, isReadOnly }) => {
  // Determine the border color based on rarity
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
        return '#FFFFFF'; // White
    }
  };

  // Get the local file path for the thumbnail
  const getThumbnailUrl = (thumbnailPath) => {
    if (!thumbnailPath) return null;

    // Extract just the filename from the path
    const filename = thumbnailPath.split('/').pop();

    // Construct the URL to the thumbnail in the public folder
    return `${process.env.PUBLIC_URL}/thumbnails/${filename}`;
  };

  // Get the thumbnail URL using the thumbnail path
  const thumbnailUrl = getThumbnailUrl(character.Thumbnail);

  // Handle click on the thumbnail to show portrait
  const handleThumbnailClick = (e) => {
    e.stopPropagation(); // Prevent the square's onClick from firing

    // Get the position of the clicked thumbnail for zoom effect
    const rect = e.currentTarget.getBoundingClientRect();
    const position = {
      x: rect.left + rect.width / 2,
      y: rect.top + rect.height / 2
    };

    // Pass the character, position, and index to the parent component
    onPortraitClick(character, position, index);
  };

  // Add 'free' class if this is the FREE square
  const isFreeSquare = character.rarity === 'FREE';

  return (
    <div
      className={`bingo-square ${isMarked ? 'marked' : ''} ${isFreeSquare ? 'free' : ''} ${isReadOnly ? 'read-only' : ''}`}
      onClick={isReadOnly ? null : onClick}
      style={{
        borderColor: getRarityColor(character.rarity),
        backgroundColor: 'transparent',
        position: 'relative',
        cursor: isReadOnly ? 'default' : 'pointer'
      }}
    >
      <div className="thumbnail-container" onClick={handleThumbnailClick}>
        <img
          src={thumbnailUrl}
          alt={character.Name}
          className="character-thumbnail"
        />
      </div>
    </div>
  );
};

export default BingoSquare;
