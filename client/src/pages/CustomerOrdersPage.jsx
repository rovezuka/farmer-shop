import { useState, useEffect } from 'react'
import api from '../services/api'
import styles from './OrdersPage.module.css'

const STATUS_LABELS = { new: 'Новый', confirmed: 'Подтверждён', ready: 'Готов к выдаче', delivered: 'Выдан', cancelled: 'Отменён' }
const STATUS_COLORS = { new: '#3498db', confirmed: '#2ecc71', ready: '#f39c12', delivered: '#27ae60', cancelled: '#e74c3c' }

export default function CustomerOrdersPage() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/orders/my').then(r => setOrders(r.data.items)).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className={styles.loading}>Загрузка заказов...</div>

  return (
    <div className={styles.page}>
      <h2>Мои заказы</h2>
      {orders.length === 0 ? <p className={styles.empty}>У вас пока нет заказов</p> : (
        <div className={styles.list}>
          {orders.map(order => (
            <div key={order.id} className={styles.card}>
              <div className={styles.cardHead}>
                <span className={styles.orderId}>Заказ #{order.id}</span>
                <span className={styles.badge} style={{background: STATUS_COLORS[order.status]}}>{STATUS_LABELS[order.status]}</span>
                <span className={styles.date}>{new Date(order.order_date).toLocaleDateString('ru-RU')}</span>
              </div>
              <div className={styles.items}>
                {order.items.map(item => (
                  <div key={item.id} className={styles.item}>
                    <span>Товар #{item.product_id}</span>
                    <span>{item.quantity} шт × {item.price_at_order} ₽</span>
                  </div>
                ))}
              </div>
              <div className={styles.total}>Итого: <strong>{parseFloat(order.total_amount).toFixed(2)} ₽</strong></div>
              <div className={styles.meta}>
                Оплата: {order.payment_method} | {order.payment_status ? '✅ Оплачен' : '⏳ Ожидает оплаты'}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
