import { createContext, useContext, useState } from 'react'


const CartContext = createContext({
  items: [],
  addItem: () => {},
  removeItem: () => {},
  updateQty: () => {},
  clear: () => {},
  total: 0
})
export function CartProvider({ children }) {
  const [items, setItems] = useState([])  // [{product, quantity}]

  const addItem = (product, qty = 1) => {
    setItems(prev => {
      const ex = prev.find(i => i.product.id === product.id)
      if (ex) return prev.map(i => i.product.id === product.id ? {...i, quantity: i.quantity + qty} : i)
      return [...prev, { product, quantity: qty }]
    })
  }

  const removeItem = (productId) => setItems(prev => prev.filter(i => i.product.id !== productId))

  const updateQty = (productId, qty) => {
    if (qty <= 0) return removeItem(productId)
    setItems(prev => prev.map(i => i.product.id === productId ? {...i, quantity: qty} : i))
  }

  const clear = () => setItems([])

  const total = items.reduce((s, i) => s + i.product.price * i.quantity, 0)

  return (
    <CartContext.Provider value={{ items, addItem, removeItem, updateQty, clear, total }}>
      {children}
    </CartContext.Provider>
  )
}

export const useCart = () => useContext(CartContext)
