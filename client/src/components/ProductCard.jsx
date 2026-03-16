import { Link } from 'react-router-dom'
import { useCart } from '../context/CartContext'
import { useAuth } from '../context/AuthContext'
import styles from './ProductCard.module.css'

export default function ProductCard({ product }) {
  const { addItem } = useCart()
  const { user } = useAuth()

  return (
    <div className={styles.card}>
      {product.image_url
        ? <img src={product.image_url} alt={product.name} className={styles.img} onError={e => { e.target.style.display='none' }} />
        : <div className={styles.noImg}>🥦</div>
      }
      <div className={styles.body}>
        <span className={styles.category}>{product.category_name}</span>
        <Link to={`/products/${product.id}`} className={styles.name}>{product.name}</Link>
        <p className={styles.farmer}>🏡 {product.farmer_name}</p>
        {product.avg_rating && <p className={styles.rating}>⭐ {product.avg_rating}</p>}
        {product.distance_km && <p className={styles.dist}>📍 {product.distance_km} км</p>}
        <div className={styles.footer}>
          <span className={styles.price}>{product.price} ₽/{product.unit}</span>
          {user?.role === 'customer' && (
            <button className={styles.addBtn} onClick={() => addItem(product)}>+ В корзину</button>
          )}
        </div>
      </div>
    </div>
  )
}
