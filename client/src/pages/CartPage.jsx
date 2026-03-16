import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCart } from '../context/CartContext'
import api from '../services/api'
import styles from './CartPage.module.css'

export default function CartPage() {
  const { items, removeItem, updateQty, clear, total } = useCart()
  const [pickupPoints, setPickupPoints] = useState([])
  const [pickupId, setPickupId] = useState('')
  const [payMethod, setPayMethod] = useState('card')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const nav = useNavigate()

  useEffect(() => {
    api.get('/pickup-points').then(r => { setPickupPoints(r.data); if (r.data.length) setPickupId(r.data[0].id) })
  }, [])

  const handleOrder = async () => {
    if (!pickupId || items.length === 0) return
    setLoading(true)
    try {
      await api.post('/orders', {
        pickup_point_id: Number(pickupId),
        payment_method: payMethod,
        items: items.map(i => ({ product_id: i.product.id, quantity: i.quantity }))
      })
      clear(); setSuccess(true)
      setTimeout(() => nav('/orders'), 2000)
    } catch (e) {
      alert(e.response?.data?.detail || 'Ошибка при оформлении заказа')
    } finally { setLoading(false) }
  }

  if (success) return <div className={styles.success}>✅ Заказ оформлен! Перенаправляем...</div>

  if (items.length === 0) return (
    <div className={styles.empty}>
      <p>Корзина пуста</p>
      <button onClick={() => nav('/')}>Перейти в каталог</button>
    </div>
  )

  return (
    <div className={styles.page}>
      <h2>Корзина</h2>
      <div className={styles.layout}>
        <div className={styles.list}>
          {items.map(({ product, quantity }) => (
            <div key={product.id} className={styles.item}>
              <div className={styles.itemInfo}>
                <span className={styles.itemName}>{product.name}</span>
                <span className={styles.itemPrice}>{product.price} ₽/{product.unit}</span>
              </div>
              <div className={styles.itemCtrl}>
                <button onClick={() => updateQty(product.id, quantity - 1)}>−</button>
                <span>{quantity}</span>
                <button onClick={() => updateQty(product.id, quantity + 1)}>+</button>
                <span className={styles.itemTotal}>{(product.price * quantity).toFixed(2)} ₽</span>
                <button className={styles.del} onClick={() => removeItem(product.id)}>✕</button>
              </div>
            </div>
          ))}
        </div>
        <div className={styles.summary}>
          <h3>Оформление заказа</h3>
          <label>Точка выдачи
            <select value={pickupId} onChange={e => setPickupId(e.target.value)}>
              {pickupPoints.map(p => <option key={p.id} value={p.id}>{p.name} — {p.address}</option>)}
            </select>
          </label>
          <label>Способ оплаты
            <select value={payMethod} onChange={e => setPayMethod(e.target.value)}>
              <option value="card">Банковская карта</option>
              <option value="cash">Наличные</option>
            </select>
          </label>
          <div className={styles.total}>Итого: <strong>{total.toFixed(2)} ₽</strong></div>
          <button className={styles.orderBtn} onClick={handleOrder} disabled={loading}>
            {loading ? 'Оформляем...' : 'Оформить заказ'}
          </button>
        </div>
      </div>
    </div>
  )
}
