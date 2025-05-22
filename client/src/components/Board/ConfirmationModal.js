import React from 'react';

const ConfirmationModal = ({ onCancel, onConfirm }) => {
  return (
    <div className="confirmation-overlay">
      <div className="confirmation-dialog">
        <h3>Warning!</h3>
        <p>
          Refreshing your board will delete your previous one and restart your progress.
          Are you sure you want to continue?
        </p>
        <div className="confirmation-buttons">
          <button className="cancel-button" onClick={onCancel}>
            Cancel
          </button>
          <button className="confirm-button" onClick={onConfirm}>
            Yes, Refresh My Board
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationModal;
