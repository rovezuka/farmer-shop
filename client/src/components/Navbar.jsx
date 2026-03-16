import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'
import styles from './Navbar.module.css'

export default function Navbar() {
  const { user, logout } = useAuth()
  const cartContext = useCart()
  const items = cartContext?.items ?? []
  const nav = useNavigate()

  const handleLogout = () => { logout(); nav('/') }

  return (
    <nav className={styles.nav}>
      <Link to="/" className={styles.brand}>🌾 Фермерская лавка</Link>
      <div className={styles.links}>
        <Link to="/">Каталог</Link>
        {user?.role === 'customer' && (
          <>
            <Link to="/cart">🛒 Корзина {items.length > 0 && <span className={styles.badge}>{items.length}</span>}</Link>
            <Link to="/orders">Мои заказы</Link>
          </>
        )}
        {user?.role === 'farmer' && <Link to="/farmer">Личный кабинет</Link>}
        {user ? (
          <button onClick={handleLogout} className={styles.btn}>Выйти</button>
        ) : (
          <>
            <Link to="/login">Войти</Link>
            <Link to="/register" className={styles.btnPrimary}>Регистрация</Link>
          </>
        )}
      </div>
    </nav>
  )
}
