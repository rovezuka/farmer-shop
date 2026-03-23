import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import styles from './FarmerDashboard.module.css'

const STATUS_LABELS = { new: 'Новый', confirmed: 'Подтверждён', ready: 'Готов', delivered: 'Выдан', cancelled: 'Отменён' }
const NEXT_STATUS = { new: 'confirmed', confirmed: 'ready', ready: 'delivered' }
const NEXT_LABEL = { new: 'Подтвердить', confirmed: 'Готов к выдаче', ready: 'Выдан' }

export default function FarmerDashboardPage() {
  const [tab, setTab] = useState('orders')
  const [orders, setOrders] = useState([])
  const [products, setProducts] = useState([])
  const [analytics, setAnalytics] = useState(null)
  const [period, setPeriod] = useState('month')
  const [categories, setCategories] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: '', description: '', price: '', unit: 'кг', quantity: '', category_id: '', image_url: '' })
  const [loading, setLoading] = useState(true)
  const { user } = useAuth()

  useEffect(() => {
    if (!user) return
    if (tab === 'orders') api.get('/orders/farmer').then(r => setOrders(r.data.items)).finally(() => setLoading(false))
    if (tab === 'products') {
      setLoading(true)
      Promise.all([api.get('/products'), api.get('/categories')])
        .then(([pr, cr]) => { setProducts(pr.data.items); setCategories(cr.data) })
        .finally(() => setLoading(false))
    }
    if (tab === 'analytics') {
      setLoading(true)
      api.get(`/analytics/sales?period=${period}`).then(r => setAnalytics(r.data)).finally(() => setLoading(false))
    }
  }, [tab, period])

  const updateStatus = async (orderId, newStatus) => {
    try {
      await api.patch(`/orders/${orderId}/status`, { status: newStatus })
      setOrders(prev => prev.map(o => o.id === orderId ? {...o, status: newStatus} : o))
    } catch (e) { alert(e.response?.data?.detail || 'Ошибка') }
  }

  const cancelOrder = async (orderId) => {
    if (!confirm('Отменить заказ?')) return
    try {
      await api.patch(`/orders/${orderId}/status`, { status: 'cancelled', reason: 'Отменено фермером' })
      setOrders(prev => prev.map(o => o.id === orderId ? {...o, status: 'cancelled'} : o))
    } catch (e) { alert(e.response?.data?.detail || 'Ошибка') }
  }

  const deleteProduct = async (id) => {
    if (!confirm('Удалить товар?')) return
    await api.delete(`/products/${id}`)
    setProducts(prev => prev.filter(p => p.id !== id))
  }

  const setF = k => e => setForm(f => ({...f, [k]: e.target.value}))

  const handleCreateProduct = async e => {
    e.preventDefault()
    try {
      await api.post('/products', { ...form, price: parseFloat(form.price), quantity: parseFloat(form.quantity), category_id: parseInt(form.category_id) })
      setShowForm(false)
      const { data } = await api.get('/products')
      setProducts(data.items)
    } catch (e) { alert(e.response?.data?.detail || 'Ошибка') }
  }

  return (
    <div className={styles.page}>
      <h2>Личный кабинет фермера</h2>
      <div className={styles.tabs}>
        {['orders','products','analytics'].map(t => (
          <button key={t} className={tab===t ? styles.activeTab : styles.tab} onClick={() => { setTab(t); setLoading(true) }}>
            {t==='orders'?'📦 Заказы':t==='products'?'🥕 Мои товары':'📊 Аналитика'}
          </button>
        ))}
      </div>

      {loading && <div className={styles.loading}>Загрузка...</div>}

      {!loading && tab === 'orders' && (
        <div className={styles.list}>
          {orders.length === 0 ? <p>Заказов пока нет</p> : orders.map(order => (
            <div key={order.id} className={styles.card}>
              <div className={styles.cardHead}>
                <span>Заказ #{order.id}</span>
                <span className={styles.status}>{STATUS_LABELS[order.status]}</span>
                <span className={styles.date}>{new Date(order.order_date).toLocaleDateString('ru-RU')}</span>
              </div>
              <div className={styles.items}>
                {order.items?.map(i => (
                  <div key={i.id} className={styles.orderItem}>
                    <span>{i.product_name || `Товар #${i.product_id}`}</span>
                    <span>{i.quantity} × {i.price_at_order} ₽</span>
                  </div>
                ))}
              </div>
              <div className={styles.cardFoot}>
                <strong>{parseFloat(order.total_amount).toFixed(2)} ₽</strong>
                <div className={styles.actions}>
                  {NEXT_STATUS[order.status] && (
                    <button className={styles.btnConfirm} onClick={() => updateStatus(order.id, NEXT_STATUS[order.status])}>
                      {NEXT_LABEL[order.status]}
                    </button>
                  )}
                  {['new','confirmed'].includes(order.status) && (
                    <button className={styles.btnCancel} onClick={() => cancelOrder(order.id)}>Отменить</button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && tab === 'products' && (
        <div>
          <button className={styles.addBtn} onClick={() => setShowForm(s => !s)}>
            {showForm ? '✕ Отмена' : '+ Добавить товар'}
          </button>
          {showForm && (
            <form className={styles.productForm} onSubmit={handleCreateProduct}>
              <h3>Новый товар</h3>
              <div className={styles.formGrid}>
                <label>Название <input value={form.name} onChange={setF('name')} required /></label>
                <label>Цена (₽) <input type="number" step="0.01" value={form.price} onChange={setF('price')} required /></label>
                <label>Количество <input type="number" step="0.1" value={form.quantity} onChange={setF('quantity')} required /></label>
                <label>Единица
                  <select value={form.unit} onChange={setF('unit')}>
                    <option value="KG">кг</option>
                    <option value="LITER">л</option>
                    <option value="PIECE">шт</option>
                  </select>
                </label>
                <label>Категория
                  <select value={form.category_id} onChange={setF('category_id')} required>
                    <option value="">Выберите...</option>
                    {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </label>
                <label>URL изображения <input value={form.image_url} onChange={setF('image_url')} placeholder="https://..." /></label>
              </div>
              <label>Описание
                <textarea value={form.description} onChange={setF('description')} rows={3} />
              </label>
              <button type="submit" className={styles.submitBtn}>Сохранить товар</button>
            </form>
          )}
          <div className={styles.productGrid}>
            {products.map(p => (
              <div key={p.id} className={styles.productCard}>
                <strong>{p.name}</strong>
                <span>{p.price} ₽/{p.unit}</span>
                <span>Остаток: {p.quantity}</span>
                <button className={styles.delBtn} onClick={() => deleteProduct(p.id)}>Удалить</button>
              </div>
            ))}
          </div>
        </div>
      )}

      {!loading && tab === 'analytics' && analytics && (
        <div className={styles.analytics}>
          <div className={styles.periodSelector}>
            {['week','month','quarter'].map(p => (
              <button key={p} className={period===p ? styles.activePeriod : styles.periodBtn} onClick={() => setPeriod(p)}>
                {p==='week'?'Неделя':p==='month'?'Месяц':'Квартал'}
              </button>
            ))}
          </div>
          <div className={styles.statsGrid}>
            <div className={styles.stat}><span>💰 Выручка</span><strong>{analytics.total_revenue.toFixed(2)} ₽</strong></div>
            <div className={styles.stat}><span>📦 Заказов</span><strong>{analytics.total_orders}</strong></div>
            <div className={styles.stat}><span>🥕 Продано</span><strong>{analytics.total_items_sold.toFixed(1)} ед.</strong></div>
          </div>
          <h3>Топ-5 товаров</h3>
          <div className={styles.topList}>
            {analytics.top_products.length === 0 ? <p>Нет данных за период</p> : analytics.top_products.map((p, i) => (
              <div key={i} className={styles.topItem}>
                <span className={styles.topNum}>{i+1}</span>
                <span className={styles.topName}>{p.name}</span>
                <span>{p.quantity_sold.toFixed(1)} ед.</span>
                <span className={styles.topRevenue}>{p.revenue.toFixed(2)} ₽</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
