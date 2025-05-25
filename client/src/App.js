import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, Link } from 'react-router-dom';
import './App.css';

// Import components
import { UserProvider, useUser } from './components/Auth/UserContext';
import Login from './components/Auth/Login';
import UserDashboard from './components/Dashboard/UserDashboard';
import BoardViewer from './components/Board/BoardViewer';
import HowToPlay from './components/HowToPlay/HowToPlay';

// Protected Route component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useUser();

  // If still loading, show loading indicator
  if (loading) {
    return <div className="loading-message">Loading...</div>;
  }

  // If not logged in, redirect to login page
  if (!user) {
    return <Navigate to="/" replace />;
  }

  // If logged in, render the protected component
  return children;
};

// Rules component
export const Rules = () => {
  return (
    <div className="rules-container">
      <div id="rules" className="rules-section">
        <h2>Rules</h2>
        <p>Please follow these important guidelines for a fun and respectful experience:</p>
        <ol>
          <li>Cosplay is NOT consent - always ask for permission before taking photos.</li>
          <li>You must be featured in the photo (at least a hand) to claim a square.</li>
          <li>Teams can have as many members as you'd like, but there will still only be a single prize per team.</li>
          <li>You can refresh to get a new board, but you will lose all your current progress.</li>
          <li>Each player receives a unique bingo board with characters of different rarities.</li>
          <li>Characters are ranked by rarity: FREE, R, SR, SSR, and UR+.</li>
          <li>Higher rarity characters are worth more points, but are harder to find.</li>
        </ol>
        <p>Good luck, and happy hunting!</p>
      </div>
    </div>
  );
};

// Header component with location awareness
const AppHeader = () => {
  const location = useLocation();
  const { user } = useUser();

  // Show links on all protected routes (when user is logged in and not on the standalone rules page)
  const isProtectedRoute = user && location.pathname !== '/rules' && location.pathname !== '/';

  return (
    <header className="app-header">
      <div className="logo-container">
        <img src={`${process.env.PUBLIC_URL}/title-logo.png`} alt="Bimbo Hunter Logo" className="title-logo" />
      </div>
      <p>
        Thank you for competing in Official 2025 Bimbo Hunt!
        {isProtectedRoute && (
          <span className="header-links">
            Check out <Link to="/how-to-play">How to Play</Link> and <a href="#rules">Rules</a> below
          </span>
        )}
      </p>
    </header>
  );
};

// Main App component
const AppContent = () => {
  return (
    <Router>
      <AppRoutes />
    </Router>
  );
};

// Routes component with header
const AppRoutes = () => {
  return (
    <div className="app-container">
      <AppHeader />

        <Routes>
          {/* Public routes */}
          <Route path="/" element={<Login />} />
          <Route path="/rules" element={<div className="standalone-rules-page"><Rules /></div>} />

          {/* Protected routes */}
          <Route
            path="/how-to-play"
            element={
              <ProtectedRoute>
                <HowToPlay />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <UserDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/boards/:displayName"
            element={
              <ProtectedRoute>
                <BoardViewer />
              </ProtectedRoute>
            }
          />

          {/* Fallback route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>

        <footer className="app-footer">
          <p>Enjoy the game!</p>
        </footer>
      </div>
  );
};

// Wrap the app with the UserProvider
const App = () => {
  return (
    <UserProvider>
      <AppContent />
    </UserProvider>
  );
};

export default App;
