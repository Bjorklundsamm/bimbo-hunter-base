import React from 'react';

const BingoSquare = ({ character, isMarked, onPortraitClick, index, isReadOnly, userImage }) => {
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

  // Get the number of stars based on rarity
  const getRarityStars = (rarity) => {
    switch (rarity) {
      case 'FREE':
        return 1; // Green - 1 star
      case 'R':
        return 2; // Blue - 2 stars
      case 'SR':
        return 3; // Purple - 3 stars
      case 'SSR':
        return 4; // Orange - 4 stars
      case 'UR+':
        return 5; // Red - 5 stars
      default:
        return 0;
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

  // Get the thumbnail URL using the thumbnail path or user image
  const thumbnailUrl = (isMarked && userImage)
    ? `${process.env.PUBLIC_URL}${userImage}`
    : getThumbnailUrl(character.Thumbnail);

  // Handle click on the thumbnail to show portrait
  const handleThumbnailClick = (e) => {
    // No need to stop propagation since we're removing the square's onClick handler

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

  // Get the number of stars for this rarity
  const starCount = getRarityStars(character.rarity);

  // Get the color for the stars (same as border color)
  const starColor = getRarityColor(character.rarity);

  return (
    <div
      className={`bingo-square ${isMarked ? 'marked' : ''} ${isFreeSquare ? 'free' : ''} ${isReadOnly ? 'read-only' : ''}`}
      style={{
        borderColor: starColor,
        backgroundColor: 'transparent',
        position: 'relative',
        cursor: 'default' // Border area is not clickable
      }}
    >
      <div className="thumbnail-container" onClick={handleThumbnailClick}>
        <img
          src={thumbnailUrl}
          alt={character.Name}
          className="character-thumbnail"
        />
        {/* Star rating system - only show on thumbnails, not portraits */}
        <div className="rarity-stars">
          {[...Array(starCount)].map((_, i) => {
            // Calculate if this is the center star
            const isCenterStar = i === Math.floor(starCount / 2);

            // For even numbers of stars, make the two middle stars slightly larger
            const isMiddlePair = starCount % 2 === 0 && (i === starCount / 2 - 1 || i === starCount / 2);

            // Calculate distance from center for graduated sizing
            const distanceFromCenter = Math.abs(i - (starCount - 1) / 2);
            // Increase the size difference between center and outer stars
            const sizeMultiplier = 1 - (distanceFromCenter * 0.25);

            return (
              <span
                key={i}
                className={`star ${isCenterStar ? 'center-star' : ''} ${isMiddlePair ? 'middle-pair' : ''}`}
                style={{
                  color: starColor,
                  fontSize: `${sizeMultiplier * 100}%`,
                  transform: `scale(${sizeMultiplier})`
                }}
              >
                ★
              </span>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default BingoSquare;
