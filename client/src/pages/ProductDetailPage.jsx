import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { productsAPI, ordersAPI, pickupPointsAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function ProductDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()

  const [product, setProduct] = useState(null)
  const [pickupPoints, setPickupPoints] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [quantity, setQuantity] = useState(1)
  const [pickupPointId, setPickupPointId] = useState('')
  const [orderLoading, setOrderLoading] = useState(false)
  const [orderSuccess, setOrderSuccess] = useState(false)
  const [orderError, setOrderError] = useState(null)

  useEffect(() => {
    Promise.all([
      productsAPI.getById(id),
      pickupPointsAPI.getAll(),
    ])
      .then(([productRes, pointsRes]) => {
        setProduct(productRes.data)
        setPickupPoints(pointsRes.data)
        if (pointsRes.data.length > 0) {
          setPickupPointId(pointsRes.data[0].id)
        }
      })
      .catch(() => setError('Не удалось загрузить данные'))
      .finally(() => setLoading(false))
  }, [id])

  const handleOrder = async (e) => {
    e.preventDefault()
    if (!user) {
      navigate('/login')
      return
    }
    setOrderLoading(true)
    setOrderError(null)
    try {
      await ordersAPI.create({
        pickup_point_id: parseInt(pickupPointId),
        items: [{ product_id: parseInt(id), quantity: parseFloat(quantity) }],
      })
      setOrderSuccess(true)
    } catch (err) {
      setOrderError(err.response?.data?.detail || 'Ошибка при оформлении заказа')
    } finally {
      setOrderLoading(false)
    }
  }

  if (loading) return <p>Загрузка...</p>
  if (error) return <p style={{ color: 'red' }}>{error}</p>
  if (!product) return <p>Товар не найден</p>

  return (
    <div style={{ maxWidth: 600, margin: '0 auto', padding: 20 }}>
      <Link to="/catalog">← Назад в каталог</Link>

      <h1>{product.name}</h1>
      {product.image_url && (
        <img src={product.image_url} alt={product.name} style={{ maxWidth: '100%', marginBottom: 16 }} />
      )}
      <p>{product.description}</p>
      <p><strong>Цена:</strong> {product.price} ₽/{product.unit}</p>
      <p><strong>В наличии:</strong> {product.quantity} {product.unit}</p>
      <p><strong>Фермер:</strong> {product.farmer_name}</p>
      {product.avg_rating && <p><strong>Рейтинг:</strong> ⭐ {product.avg_rating}</p>}
      {product.distance_km && <p><strong>Расстояние:</strong> 📍 {product.distance_km} км</p>}

      <hr />

      {orderSuccess ? (
        <div>
          <p style={{ color: 'green' }}>✅ Заказ успешно оформлен!</p>
          <Link to="/orders">Мои заказы</Link>
        </div>
      ) : user?.role === 'customer' ? (
        <form onSubmit={handleOrder}>
          <h3>Оформить заказ</h3>
          <div>
            <label>Количество ({product.unit}):</label>
            <input
              type="number"
              min="0.1"
              max={product.quantity}
              step="0.1"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              required
              style={{ marginLeft: 8, width: 80 }}
            />
          </div>
          <div style={{ marginTop: 8 }}>
            <label>Пункт выдачи:</label>
            <select
              value={pickupPointId}
              onChange={(e) => setPickupPointId(e.target.value)}
              required
              style={{ marginLeft: 8 }}
            >
              {pickupPoints.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} — {p.address}
                </option>
              ))}
            </select>
          </div>
          {orderError && <p style={{ color: 'red' }}>{orderError}</p>}
          <button type="submit" disabled={orderLoading} style={{ marginTop: 12 }}>
            {orderLoading ? 'Оформляем...' : 'Заказать'}
          </button>
        </form>
      ) : !user ? (
        <p><Link to="/login">Войдите</Link>, чтобы оформить заказ</p>
      ) : null}
    </div>
  )
}
