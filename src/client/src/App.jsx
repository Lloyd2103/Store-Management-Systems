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
  const [customer, setCustomer] = useState(null);
  const [cart, setCart] = useState([]);

  useEffect(() => {
    const savedCustomer = sessionStorage.getItem("customer");
    const savedCart = sessionStorage.getItem("cart");

    if (savedCustomer) setCustomer(JSON.parse(savedCustomer));
    if (savedCart) setCart(JSON.parse(savedCart));
  }, []);

  useEffect(() => {
    if (customer) {
      sessionStorage.setItem("customer", JSON.stringify(customer));
    }
  }, [customer]);

  useEffect(() => {
    sessionStorage.setItem("cart", JSON.stringify(cart));
  }, [cart]);

  const handleLoginSuccess = (user) => {
    setCustomer(user);
    sessionStorage.setItem("customer", JSON.stringify(user));
  };

  const handleLogout = () => {
    setCustomer(null);
    sessionStorage.clear();
  };

  const isLoggedIn = customer !== null;

  return (
    <Router>
      <Routes>
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

        <Route path="/register" element={<RegisterView />} />

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

        <Route
          path="/order-history"
          element={isLoggedIn ? <OrderHistory /> : <Navigate to="/login" />}
        />
      </Routes>
    </Router>
  );
}
