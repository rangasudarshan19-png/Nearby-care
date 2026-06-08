const TOKEN_KEY = 'token';
const USER_KEY = 'user';
const LOGOUT_EVENT_KEY = 'nearbycare:logout';

export const getAuthToken = () => sessionStorage.getItem(TOKEN_KEY);

export const getStoredUser = () => {
  const userData = sessionStorage.getItem(USER_KEY);
  if (!userData) return null;

  try {
    return JSON.parse(userData);
  } catch (error) {
    sessionStorage.removeItem(USER_KEY);
    return null;
  }
};

export const setAuthSession = (token, user) => {
  sessionStorage.setItem(TOKEN_KEY, token);
  sessionStorage.setItem(USER_KEY, JSON.stringify(user));
};

export const updateStoredUser = (user) => {
  sessionStorage.setItem(USER_KEY, JSON.stringify(user));
};

export const clearAuthSession = ({ broadcast = false } = {}) => {
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(USER_KEY);

  if (broadcast) {
    localStorage.setItem(LOGOUT_EVENT_KEY, String(Date.now()));
  }
};

export const subscribeToLogout = (callback) => {
  const handler = (event) => {
    if (event.key === LOGOUT_EVENT_KEY) {
      clearAuthSession();
      callback();
    }
  };

  window.addEventListener('storage', handler);
  return () => window.removeEventListener('storage', handler);
};
