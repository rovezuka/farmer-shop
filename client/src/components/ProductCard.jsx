/**
 * Карточка товара для каталога (SRS раздел 5.1).
 */
import { Link } from 'react-router-dom';

export default function ProductCard({ product }) {
  return (
    <div className="product-card">
      <img
        src={product.image_url || '/placeholder.jpg'}
        alt={product.name}
        className="product-image"
      />
      <div className="product-info">
        <h3>{product.name}</h3>
        <p className="price">{product.price} ₽/{product.unit}</p>
        <p className="farmer">🌾 {product.farmer_name}</p>
        {product.avg_rating && (
          <p className="rating">⭐ {product.avg_rating}</p>
        )}
        {product.distance_km && (
          <p className="distance">📍 {product.distance_km} км</p>
        )}
        <Link to={`/products/${product.id}`} className="btn">
          Подробнее
        </Link>
      </div>
    </div>
  );
}