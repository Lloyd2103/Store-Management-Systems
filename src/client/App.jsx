import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import LoginView from "./pages/LoginView";
import RegisterView from "./pages/RegisterView";
import CustomerView from "./pages/CustomerView";
import CartView from "./pages/CartView";
import OrderView from "./pages/OrderView";
import AccountView from "./pages/AccountView";
import OrderHistory from "./pages/OrderHistory";

export default function App() {
  // ===== SESSION LOGIN STATE =====
  const [customer, setCustomer] = useState(null);
  const [cart, setCart] = useState([]);

  // Khi app load lại (reload), lấy customer từ sessionStorage
  useEffect(() => {
    const savedCustomer = sessionStorage.getItem("customer");
    const savedCart = sessionStorage.getItem("cart");

    if (savedCustomer) setCustomer(JSON.parse(savedCustomer));
    if (savedCart) setCart(JSON.parse(savedCart));
  }, []);

  // Lưu lại customer và cart vào sessionStorage mỗi khi thay đổi
  useEffect(() => {
    if (customer) {
      sessionStorage.setItem("customer", JSON.stringify(customer));
    }
  }, [customer]);

  useEffect(() => {
    sessionStorage.setItem("cart", JSON.stringify(cart));
  }, [cart]);

  // ===== LOGIN SUCCESS =====
  const handleLoginSuccess = (user) => {
    setCustomer(user);
    sessionStorage.setItem("customer", JSON.stringify(user));
  };

  // ===== LOGOUT =====
  const handleLogout = () => {
    setCustomer(null);
    sessionStorage.clear();
  };

  const isLoggedIn = customer !== null;

  return (
    <Router>
      <Routes>
        {/* LOGIN */}
        <Route
          path="/login"
          element={
            !isLoggedIn ? (
              <LoginView onLoginSuccess={handleLoginSuccess} />
            ) : (
              <Navigate to="/" />
            )
          }
        />

        {/* REGISTER */}
        <Route path="/register" element={<RegisterView />} />

        {/* HOME / PRODUCT LIST */}
        <Route
          path="/"
          element={
            isLoggedIn ? (
              <CustomerView customer={customer} cart={cart} setCart={setCart} />
            ) : (
              <Navigate to="/login" />
            )
          }
        />

        {/* CART */}
        <Route
          path="/cart"
          element={
            isLoggedIn ? (
              <CartView cart={cart} setCart={setCart} customer={customer} />
            ) : (
              <Navigate to="/login" />
            )
          }
        />

        {/* ORDER */}
        <Route
          path="/order"
          element={
            isLoggedIn ? (
              <OrderView customer={customer} cart={cart} setCart={setCart} />
            ) : (
              <Navigate to="/login" />
            )
          }
        />

        {/* ACCOUNT */}
        <Route
          path="/account"
          element={
            isLoggedIn ? (
              <AccountView
                customer={customer}
                setCustomer={setCustomer}
                onLogout={handleLogout}
              />
            ) : (
              <Navigate to="/login" />
            )
          }
        />

        {/* ORDER HISTORY */}
        <Route
          path="/order-history"
          element={isLoggedIn ? <OrderHistory /> : <Navigate to="/login" />}
        />
      </Routes>
    </Router>
  );
}
