import { useState, useEffect, useCallback } from 'react'
import api from '../services/api'
import ProductCard from '../components/ProductCard'
import { CartProvider } from '../context/CartContext'
import styles from './CatalogPage.module.css'

export default function CatalogPage() {
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({ search: '', category_id: '', min_price: '', max_price: '', sort_by: 'name' })

  const perPage = 12

  const fetchProducts = useCallback(async () => {
    setLoading(true)
    try {
      const params = { page, per_page: perPage, ...Object.fromEntries(Object.entries(filters).filter(([,v]) => v !== '')) }
      const { data } = await api.get('/products', { params })
      setProducts(data.items); setTotal(data.total)
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }, [page, filters])

  useEffect(() => { fetchProducts() }, [fetchProducts])

  useEffect(() => {
    api.get('/categories').then(r => setCategories(r.data)).catch(() => {})
  }, [])

  const setF = k => e => { setFilters(f => ({...f, [k]: e.target.value})); setPage(1) }

  return (
    <CartProvider>
    <div className={styles.page}>
      <div className={styles.sidebar}>
        <h3>Фильтры</h3>
        <label>Поиск
          <input placeholder="Найти товар..." value={filters.search} onChange={setF('search')} />
        </label>
        <label>Категория
          <select value={filters.category_id} onChange={setF('category_id')}>
            <option value="">Все категории</option>
            {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </label>
        <label>Цена от
          <input type="number" min="0" value={filters.min_price} onChange={setF('min_price')} placeholder="0" />
        </label>
        <label>Цена до
          <input type="number" min="0" value={filters.max_price} onChange={setF('max_price')} placeholder="∞" />
        </label>
        <label>Сортировка
          <select value={filters.sort_by} onChange={setF('sort_by')}>
            <option value="name">По названию</option>
            <option value="price">По цене</option>
            <option value="created_at">Новинки</option>
          </select>
        </label>
      </div>

      <div className={styles.main}>
        <div className={styles.header}>
          <h2>Каталог товаров</h2>
          <span>{total} товаров</span>
        </div>
        {loading ? <div className={styles.loading}>Загрузка...</div> : (
          <>
            <div className={styles.grid}>
              {products.map(p => <ProductCard key={p.id} product={p} />)}
              {products.length === 0 && <p className={styles.empty}>Товары не найдены</p>}
            </div>
            {total > perPage && (
              <div className={styles.pagination}>
                <button disabled={page === 1} onClick={() => setPage(p => p - 1)}>← Назад</button>
                <span>Стр. {page} / {Math.ceil(total / perPage)}</span>
                <button disabled={page >= Math.ceil(total / perPage)} onClick={() => setPage(p => p + 1)}>Вперёд →</button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
    </CartProvider>
  )
}
