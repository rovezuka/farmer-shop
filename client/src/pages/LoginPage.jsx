import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const data = await login(email, password);
      // Перенаправление в зависимости от роли
      if (data.role === 'farmer') navigate('/farmer/dashboard');
      else if (data.role === 'admin') navigate('/admin');
      else navigate('/catalog');
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка входа');
    }
  };

  return (
    <div className="login-page">
      <h1>Вход в систему</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="email" placeholder="Email" required
          value={email} onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password" placeholder="Пароль" required minLength={6}
          value={password} onChange={(e) => setPassword(e.target.value)}
        />
        {error && <p className="error">{error}</p>}
        <button type="submit">Войти</button>
      </form>
    </div>
  );
}