import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { ordersAPI } from '../services/api'

const STATUS_LABELS = {
  new: 'Новый',
  confirmed: 'Подтверждён',
  ready: 'Готов к выдаче',
  delivered: 'Доставлен',
  cancelled: 'Отменён',
}

export default function CustomerOrdersPage() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    ordersAPI.getMy()
      .then((res) => setOrders(res.data.items))
      .catch(() => setError('Не удалось загрузить заказы'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p>Загрузка...</p>
  if (error) return <p style={{ color: 'red' }}>{error}</p>

  return (
    <div style={{ maxWidth: 700, margin: '0 auto', padding: 20 }}>
      <h1>Мои заказы</h1>
      <Link to="/catalog">← В каталог</Link>

      {orders.length === 0 && <p style={{ marginTop: 16 }}>У вас пока нет заказов</p>}

      {orders.map((order) => (
        <div key={order.id} style={{ border: '1px solid #ddd', borderRadius: 8, padding: 16, marginTop: 12 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <strong>Заказ #{order.id}</strong>
            <span style={{ background: '#f0f0f0', padding: '2px 8px', borderRadius: 4 }}>
              {STATUS_LABELS[order.status] || order.status}
            </span>
          </div>
          <p>Дата: {new Date(order.order_date).toLocaleDateString('ru-RU')}</p>
          <p>Сумма: {order.total_amount} ₽</p>
          <p>Оплата: {order.payment_method}</p>
          <div>
            <strong>Позиции:</strong>
            <ul style={{ margin: '4px 0', paddingLeft: 20 }}>
              {order.items.map((item) => (
                <li key={item.id}>
                  Товар #{item.product_id} — {item.quantity} × {item.price_at_order} ₽
                </li>
              ))}
            </ul>
          </div>
        </div>
      ))}
    </div>
  )
}
