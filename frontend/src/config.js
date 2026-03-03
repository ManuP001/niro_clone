// Determine backend URL based on environment
// Always use REACT_APP_BACKEND_URL env var (set in Render for each environment)
// Falls back to localhost for local development

export const getBackendUrl = () => {
  return process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
};

// Export as a constant for backwards compatibility, but also export the function
export const BACKEND_URL = getBackendUrl();
