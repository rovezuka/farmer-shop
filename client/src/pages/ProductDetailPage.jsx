import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../services/api'
import { useCart } from '../context/CartContext'
import { useAuth } from '../context/AuthContext'
import styles from './ProductDetailPage.module.css'

export default function ProductDetailPage() {
  const { id } = useParams()
  const [product, setProduct] = useState(null)
  const [qty, setQty] = useState(1)
  const { addItem } = useCart()
  const { user } = useAuth()
  const nav = useNavigate()

  useEffect(() => {
    api.get(`/products/${id}`).then(r => setProduct(r.data)).catch(() => nav('/'))
  }, [id])

  if (!product) return <div className={styles.loading}>Загрузка...</div>

  const handleAdd = () => { addItem(product, qty); nav('/cart') }

  return (
    <div className={styles.page}>
      <button className={styles.back} onClick={() => nav(-1)}>← Назад</button>
      <div className={styles.card}>
        {product.image_url
          ? <img src={product.image_url} alt={product.name} className={styles.img} onError={e => e.target.style.display='none'} />
          : <div className={styles.noImg}>🥦</div>
        }
        <div className={styles.info}>
          <span className={styles.cat}>{product.category_name}</span>
          <h1>{product.name}</h1>
          <p className={styles.farmer}>🏡 {product.farmer_name}</p>
          {product.avg_rating && <p>⭐ Рейтинг: {product.avg_rating} / 5</p>}
          <p className={styles.desc}>{product.description}</p>
          <div className={styles.meta}>
            <span>Количество: {product.quantity} {product.unit}</span>
            {product.expiration_date && <span>Срок годности: {product.expiration_date}</span>}
          </div>
          <div className={styles.buy}>
            <span className={styles.price}>{product.price} ₽/{product.unit}</span>
            {user?.role === 'customer' && (
              <div className={styles.qty}>
                <button onClick={() => setQty(q => Math.max(1, q - 1))}>−</button>
                <span>{qty}</span>
                <button onClick={() => setQty(q => Math.min(product.quantity, q + 1))}>+</button>
                <button className={styles.addBtn} onClick={handleAdd}>В корзину</button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
