// Authentication service
const TOKEN_KEY = 'auth_token';
const USER_ROLE_KEY = 'user_role';
const USER_ID_KEY = 'user_id';
const USERNAME_KEY = 'username';

export const saveAuthData = (authData) => {
  localStorage.setItem(TOKEN_KEY, authData.token);
  localStorage.setItem(USER_ROLE_KEY, authData.role);
  localStorage.setItem(USER_ID_KEY, authData.userId);
  localStorage.setItem(USERNAME_KEY, authData.username);
};

export const getAuthToken = () => {
  return localStorage.getItem(TOKEN_KEY);
};

export const getUserRole = () => {
  return localStorage.getItem(USER_ROLE_KEY);
};

export const getUserId = () => {
  return localStorage.getItem(USER_ID_KEY);
};

export const getUsername = () => {
  return localStorage.getItem(USERNAME_KEY);
};

export const isAuthenticated = () => {
  return !!getAuthToken();
};

export const isAdmin = () => {
  return getUserRole() === 'ADMIN';
};

export const isEditor = () => {
  const role = getUserRole();
  return role === 'EDITOR' || role === 'ADMIN';
};

export const logout = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_ROLE_KEY);
  localStorage.removeItem(USER_ID_KEY);
  localStorage.removeItem(USERNAME_KEY);
};