import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, Link } from 'react-router-dom';
import './App.css';

// Import components
import { UserProvider, useUser } from './components/Auth/UserContext';
import Login from './components/Auth/Login';
import UserDashboard from './components/Dashboard/UserDashboard';
import BoardViewer from './components/Board/BoardViewer';
import Leaderboard from './components/Board/Leaderboard';
import Cards from './components/Cards/Cards';
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

// Header component with logo and thank you message in same row
const AppHeader = () => {
  return (
    <header className="app-header">
      <div className="header-row">
        <div className="logo-container">
          <img src={`${process.env.PUBLIC_URL}/title-logo.png`} alt="Bimbo Hunter Logo" className="title-logo" />
        </div>
        <div className="thank-you-message">
          <p>Thank you for competing in Official 2025 Bimbo Hunt!</p>
        </div>
      </div>
    </header>
  );
};

// Navigation component
const Navigation = () => {
  const location = useLocation();
  const { user } = useUser();

  // Only show navigation for logged-in users
  if (!user) return null;

  const navItems = [
    { path: '/dashboard', label: 'Your Board' },
    { path: '/leaderboard', label: 'Leader Board' },
    { path: '/cards', label: 'Cards' },
    { path: '/how-to-play', label: 'How to Play' },
    { path: '/rules', label: 'Rules' }
  ];

  return (
    <nav className="main-navigation">
      <div className="nav-container">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
          >
            {item.label}
          </Link>
        ))}
      </div>
    </nav>
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
      <Navigation />

        <Routes>
          {/* Public routes */}
          <Route path="/" element={<Login />} />
          <Route path="/rules" element={<div className="standalone-rules-page"><Rules /></div>} />

          {/* Protected routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <UserDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/leaderboard"
            element={
              <ProtectedRoute>
                <Leaderboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/cards"
            element={
              <ProtectedRoute>
                <Cards />
              </ProtectedRoute>
            }
          />
          <Route
            path="/how-to-play"
            element={
              <ProtectedRoute>
                <HowToPlay />
              </ProtectedRoute>
            }
          />
          <Route
            path="/rules"
            element={
              <ProtectedRoute>
                <div className="standalone-rules-page"><Rules /></div>
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
