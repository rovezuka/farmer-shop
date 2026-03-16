import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Восстановление сессии из localStorage
    const token = localStorage.getItem('access_token');
    const role = localStorage.getItem('role');
    const userId = localStorage.getItem('user_id');
    if (token && role) {
      setUser({ token, role, userId: parseInt(userId) });
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const res = await authAPI.login({ email, password });
    const { access_token, refresh_token, role, user_id } = res.data;
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    localStorage.setItem('role', role);
    localStorage.setItem('user_id', user_id);
    setUser({ token: access_token, role, userId: user_id });
    return res.data;
  };

  const register = async (data) => {
    const res = await authAPI.register(data);
    const { access_token, refresh_token, role, user_id } = res.data;
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    localStorage.setItem('role', role);
    localStorage.setItem('user_id', user_id);
    setUser({ token: access_token, role, userId: user_id });
    return res.data;
  };

  const logout = () => {
    localStorage.clear();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);