import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import styles from './AuthPage.module.css'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const nav = useNavigate()

  const handleSubmit = async e => {
    e.preventDefault()
    setLoading(true); setError('')
    try {
      const { data } = await api.post('/auth/login', { email, password })
      login(data)
      console.log('localStorage after login:', localStorage.getItem('access_token'))  
      nav(data.role === 'farmer' ? '/farmer' : '/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка входа')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.container}>
      <form className={styles.form} onSubmit={handleSubmit}>
        <h2>Вход в систему</h2>
        {error && <div className={styles.error}>{error}</div>}
        <label>Email
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
        </label>
        <label>Пароль
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
        </label>
        <button type="submit" disabled={loading}>{loading ? 'Вход...' : 'Войти'}</button>
        <p>Нет аккаунта? <Link to="/register">Зарегистрироваться</Link></p>
        <p className={styles.hint}>
          Тест: buyer@example.com / buyer123<br/>
          Фермер: ivanov@ferma.ru / farmer123
        </p>
      </form>
    </div>
  )
}
