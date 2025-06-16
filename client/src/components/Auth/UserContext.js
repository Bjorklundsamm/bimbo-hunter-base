import React, { createContext, useState, useEffect, useContext } from 'react';

// Create the user context
const UserContext = createContext();

// Custom hook to use the user context
export const useUser = () => useContext(UserContext);

// User provider component
export const UserProvider = ({ children }) => {
  // State for user data
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check for existing user session on mount
  useEffect(() => {
    const checkUserSession = async () => {
      try {
        // Check if user data exists in local storage
        const storedUser = localStorage.getItem('user');
        
        if (storedUser) {
          const userData = JSON.parse(storedUser);
          
          // Verify the user still exists in the database
          const response = await fetch(`http://localhost:5000/api/auth/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ pin: userData.pin }),
          });
          
          if (response.ok) {
            const data = await response.json();
            if (data.success) {
              setUser(data.user);
            } else {
              // Clear invalid session
              localStorage.removeItem('user');
              setUser(null);
            }
          } else {
            // Clear invalid session
            localStorage.removeItem('user');
            setUser(null);
          }
        }
      } catch (err) {
        console.error('Error checking user session:', err);
        setError('Failed to restore user session');
      } finally {
        setLoading(false);
      }
    };

    checkUserSession();
  }, []);

  // Login function
  const login = async (pin) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('http://localhost:5000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pin }),
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        // Save user data to state and local storage
        setUser(data.user);
        localStorage.setItem('user', JSON.stringify(data.user));
        return { success: true, user: data.user };
      } else {
        setError(data.error || 'Invalid PIN');
        return { success: false, error: data.error || 'Invalid PIN' };
      }
    } catch (err) {
      console.error('Login error:', err);
      setError('Failed to login. Please try again.');
      return { success: false, error: 'Failed to login. Please try again.' };
    } finally {
      setLoading(false);
    }
  };

  // Register function
  const register = async (pin, displayName) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('http://localhost:5000/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pin, display_name: displayName }),
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        // Save user data to state and local storage
        setUser(data.user);
        localStorage.setItem('user', JSON.stringify(data.user));
        return { success: true };
      } else {
        setError(data.error || 'Failed to register');
        return { success: false, error: data.error || 'Failed to register' };
      }
    } catch (err) {
      console.error('Registration error:', err);
      setError('Failed to register. Please try again.');
      return { success: false, error: 'Failed to register. Please try again.' };
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('user');
    setUser(null);
  };

  // Context value
  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
  };

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
};

export default UserContext;
