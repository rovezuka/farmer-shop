import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import styles from './AuthPage.module.css'

export default function RegisterPage() {
  const [form, setForm] = useState({ email: '', password: '', role: 'customer', first_name: '', farm_name: '', phone: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const nav = useNavigate()

  const set = k => e => setForm(f => ({...f, [k]: e.target.value}))

  const handleSubmit = async e => {
    e.preventDefault(); setLoading(true); setError('')
    try {
      const { data } = await api.post('/auth/register', form)
      login(data)
      nav(data.role === 'farmer' ? '/farmer' : '/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка регистрации')
    } finally { setLoading(false) }
  }

  return (
    <div className={styles.container}>
      <form className={styles.form} onSubmit={handleSubmit}>
        <h2>Регистрация</h2>
        {error && <div className={styles.error}>{error}</div>}
        <label>Email <input type="email" value={form.email} onChange={set('email')} required /></label>
        <label>Пароль <input type="password" value={form.password} onChange={set('password')} required minLength={6} /></label>
        <label>Роль
          <select value={form.role} onChange={set('role')}>
            <option value="customer">Покупатель</option>
            <option value="farmer">Фермер</option>
          </select>
        </label>
        {form.role === 'customer' && (
          <label>Имя <input value={form.first_name} onChange={set('first_name')} required /></label>
        )}
        {form.role === 'farmer' && (
          <label>Название хозяйства <input value={form.farm_name} onChange={set('farm_name')} required /></label>
        )}
        <label>Телефон <input type="tel" value={form.phone} onChange={set('phone')} placeholder="+79001234567" /></label>
        <button type="submit" disabled={loading}>{loading ? 'Регистрация...' : 'Зарегистрироваться'}</button>
        <p>Есть аккаунт? <Link to="/login">Войти</Link></p>
      </form>
    </div>
  )
}
