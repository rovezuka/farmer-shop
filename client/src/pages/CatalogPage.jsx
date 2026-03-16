/**
 * Страница каталога товаров (SRS раздел 5.1 — Каталог товаров).
 * Поддерживает фильтрацию, поиск, геосортировку.
 */
import { useState, useEffect } from 'react';
import { productsAPI } from '../services/api';
import ProductCard from '../components/ProductCard';

export default function CatalogPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [categoryId, setCategoryId] = useState(null);
  const [sortBy, setSortBy] = useState('name');
  const [userLocation, setUserLocation] = useState(null);

  // Определение геолокации (UC-2)
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => setUserLocation({
          lat: pos.coords.latitude,
          lon: pos.coords.longitude,
        }),
        () => console.log('Геолокация недоступна')
      );
    }
  }, []);

  // Загрузка товаров
  useEffect(() => {
    loadProducts();
  }, [search, categoryId, sortBy, userLocation]);

  const loadProducts = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        search: search || undefined,
        category_id: categoryId || undefined,
        sort_by: sortBy,
        user_lat: userLocation?.lat,
        user_lon: userLocation?.lon,
      };
      const res = await productsAPI.getAll(params);
      setProducts(res.data.items);
    } catch (err) {
      console.error('Ошибка загрузки товаров:', err);
      setError('Не удалось загрузить товары. Проверьте подключение к серверу.');
    }
    setLoading(false);
  };

  return (
    <div className="catalog-page">
      <h1>Каталог фермерских продуктов</h1>

      {/* Панель фильтров */}
      <div className="filters">
        <input
          type="text"
          placeholder="Поиск по названию..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="search-input"
        />
        <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
          <option value="name">По названию</option>
          <option value="price">По цене</option>
          <option value="distance">Рядом со мной</option>
          <option value="created_at">Новинки</option>
        </select>
      </div>

      {/* Сетка товаров */}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {loading ? (
        <p>Загрузка...</p>
      ) : (
        <div className="products-grid">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
          {products.length === 0 && <p>Товары не найдены</p>}
        </div>
      )}
    </div>
  );
}