import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import LoginPage from './pages/LoginPage'
import CatalogPage from './pages/CatalogPage'
import ProductDetailPage from './pages/ProductDetailPage'
import FarmerDashboardPage from './pages/FarmerDashboardPage'
import CustomerOrdersPage from './pages/CustomerOrdersPage'

function PrivateRoute({ children, role }) {
  const { user, loading } = useAuth()
  if (loading) return <p>Загрузка...</p>
  if (!user) return <Navigate to="/login" replace />
  if (role && user.role !== role) return <Navigate to="/catalog" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/catalog" element={<CatalogPage />} />
      <Route path="/products/:id" element={<ProductDetailPage />} />
      <Route
        path="/orders"
        element={
          <PrivateRoute role="customer">
            <CustomerOrdersPage />
          </PrivateRoute>
        }
      />
      <Route
        path="/farmer/dashboard"
        element={
          <PrivateRoute role="farmer">
            <FarmerDashboardPage />
          </PrivateRoute>
        }
      />
      <Route path="/" element={<Navigate to="/catalog" replace />} />
      <Route path="*" element={<Navigate to="/catalog" replace />} />
    </Routes>
  )
}
