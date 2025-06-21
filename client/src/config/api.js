/**
 * API Configuration
 * Handles the base URL for API calls in different environments
 */

// Determine the API base URL based on the environment
const getApiBaseUrl = () => {
  // In development, use the full localhost URL
  if (process.env.NODE_ENV === 'development') {
    return 'http://localhost:5000';
  }
  
  // In production, use relative URLs since the API is served from the same server
  return '';
};

export const API_BASE_URL = getApiBaseUrl();

/**
 * Helper function to construct full API URLs
 * @param {string} endpoint - The API endpoint (e.g., '/api/characters')
 * @returns {string} - The full API URL
 */
export const getApiUrl = (endpoint) => {
  // Ensure endpoint starts with /
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${API_BASE_URL}${cleanEndpoint}`;
};

const apiConfig = {
  API_BASE_URL,
  getApiUrl
};

export default apiConfig;
