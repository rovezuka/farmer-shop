import { useState, useEffect } from 'react'
import { ordersAPI } from '../services/api'

const STATUS_LABELS = {
  new: 'Новый',
  confirmed: 'Подтверждён',
  ready: 'Готов к выдаче',
  delivered: 'Доставлен',
  cancelled: 'Отменён',
}

const STATUS_ACTIONS = {
  new: [
    { label: 'Подтвердить', status: 'confirmed' },
    { label: 'Отменить', status: 'cancelled' },
  ],
  confirmed: [
    { label: 'Готов к выдаче', status: 'ready' },
    { label: 'Отменить', status: 'cancelled' },
  ],
  ready: [
    { label: 'Доставлен', status: 'delivered' },
  ],
}

export default function FarmerDashboardPage() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [statusFilter, setStatusFilter] = useState('')

  const loadOrders = async () => {
    setLoading(true)
    setError(null)
    try {
      const params = statusFilter ? { status_filter: statusFilter } : {}
      const res = await ordersAPI.getFarmerOrders(params)
      setOrders(res.data.items)
    } catch {
      setError('Не удалось загрузить заказы')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadOrders() }, [statusFilter])

  const handleStatusChange = async (orderId, newStatus) => {
    try {
      await ordersAPI.updateStatus(orderId, { status: newStatus })
      loadOrders()
    } catch (err) {
      alert(err.response?.data?.detail || 'Ошибка при обновлении статуса')
    }
  }

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: 20 }}>
      <h1>Дашборд фермера</h1>

      <div style={{ marginBottom: 16 }}>
        <label>Фильтр по статусу: </label>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="">Все</option>
          {Object.entries(STATUS_LABELS).map(([val, label]) => (
            <option key={val} value={val}>{label}</option>
          ))}
        </select>
      </div>

      {loading && <p>Загрузка...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {!loading && orders.length === 0 && <p>Заказов нет</p>}

      {orders.map((order) => (
        <div key={order.id} style={{ border: '1px solid #ddd', borderRadius: 8, padding: 16, marginBottom: 12 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <strong>Заказ #{order.id}</strong>
            <span style={{ background: '#f0f0f0', padding: '2px 8px', borderRadius: 4 }}>
              {STATUS_LABELS[order.status] || order.status}
            </span>
          </div>
          <p>Дата: {new Date(order.order_date).toLocaleDateString('ru-RU')}</p>
          <p>Сумма: {order.total_amount} ₽</p>
          <div>
            <strong>Позиции:</strong>
            <ul style={{ margin: '4px 0', paddingLeft: 20 }}>
              {order.items.map((item) => (
                <li key={item.id}>
                  {item.product_name || `Товар #${item.product_id}`} — {item.quantity} × {item.price_at_order} ₽
                </li>
              ))}
            </ul>
          </div>
          <div style={{ marginTop: 8, display: 'flex', gap: 8 }}>
            {(STATUS_ACTIONS[order.status] || []).map((action) => (
              <button
                key={action.status}
                onClick={() => handleStatusChange(order.id, action.status)}
                style={{
                  background: action.status === 'cancelled' ? '#ff4d4f' : '#52c41a',
                  color: 'white',
                  border: 'none',
                  borderRadius: 4,
                  padding: '4px 12px',
                  cursor: 'pointer',
                }}
              >
                {action.label}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
