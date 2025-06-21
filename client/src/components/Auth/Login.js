import React, { useState } from 'react';
import { useUser } from './UserContext';
import { useNavigate } from 'react-router-dom';
import { getApiUrl } from '../../config/api';

const Login = () => {
  // State for form inputs
  const [pin, setPin] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);
  const [formError, setFormError] = useState('');

  // Get user context and navigation
  const { login, register, loading } = useUser();
  const navigate = useNavigate();

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');

    if (isRegistering) {
      // Validate registration inputs
      if (!pin || !displayName) {
        setFormError('Please enter both PIN and display name');
        return;
      }

      // Register new user
      const result = await register(pin, displayName);

      if (result.success) {
        // Redirect to dashboard on success (new users won't have boards yet)
        navigate('/dashboard');
      } else {
        setFormError(result.error);
      }
    } else {
      // Validate login input
      if (!pin) {
        setFormError('Please enter your PIN');
        return;
      }

      // Login existing user
      const result = await login(pin);

      if (result.success) {
        // Check if user is admin
        if (result.user && result.user.is_admin) {
          navigate('/admin');
          return;
        }

        // Check if user has a board and redirect accordingly
        try {
          const boardResponse = await fetch(getApiUrl(`/api/users/${result.user?.id || JSON.parse(localStorage.getItem('user')).id}/board`), {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          });

          if (boardResponse.ok) {
            // User has a board, redirect to their board
            const userData = JSON.parse(localStorage.getItem('user'));
            navigate(`/boards/${encodeURIComponent(userData.display_name)}`);
          } else {
            // User doesn't have a board, redirect to dashboard
            navigate('/dashboard');
          }
        } catch (err) {
          console.error('Error checking user board:', err);
          // Fallback to dashboard
          navigate('/dashboard');
        }
      } else {
        setFormError(result.error);
      }
    }
  };

  // Toggle between login and registration forms
  const toggleForm = () => {
    setIsRegistering(!isRegistering);
    setFormError('');
  };

  return (
    <div className="auth-container">
      <div className="auth-form-container">
        <h2>{isRegistering ? 'Create Account' : 'Login'}</h2>

        {formError && <div className="auth-error">{formError}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="pin">PIN</label>
            <input
              type="text"
              id="pin"
              value={pin}
              onChange={(e) => setPin(e.target.value)}
              placeholder="Enter your PIN"
              disabled={loading}
            />
          </div>

          {isRegistering && (
            <div className="form-group">
              <label htmlFor="displayName">Display Name</label>
              <input
                type="text"
                id="displayName"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="Enter your display name"
                disabled={loading}
              />
            </div>
          )}

          <button type="submit" className="auth-button" disabled={loading}>
            {loading ? 'Processing...' : isRegistering ? 'Register' : 'Login'}
          </button>
        </form>

        <div className="auth-toggle">
          <button onClick={toggleForm} className="toggle-button" disabled={loading}>
            {isRegistering ? 'Already have an account? Login' : 'New user? Create account'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Login;
