import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { CartProvider } from './context/CartContext'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import CatalogPage from './pages/CatalogPage'
import ProductDetailPage from './pages/ProductDetailPage'
import CustomerOrdersPage from './pages/CustomerOrdersPage'
import FarmerDashboardPage from './pages/FarmerDashboardPage'
import CartPage from './pages/CartPage'
import Navbar from './components/Navbar'
import { useAuth } from './context/AuthContext'

function PrivateRoute({ children, role }) {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" />
  if (role && user.role !== role) return <Navigate to="/" />
  return children
}

function AppRoutes() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<CatalogPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/products/:id" element={<ProductDetailPage />} />
        <Route path="/cart" element={<PrivateRoute role="customer"><CartPage /></PrivateRoute>} />
        <Route path="/orders" element={<PrivateRoute role="customer"><CustomerOrdersPage /></PrivateRoute>} />
        <Route path="/farmer" element={<PrivateRoute role="farmer"><FarmerDashboardPage /></PrivateRoute>} />
      </Routes>
    </>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </CartProvider>
    </AuthProvider>
  )
}
