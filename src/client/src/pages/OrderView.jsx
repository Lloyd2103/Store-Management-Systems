import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { API_BASE_URL } from "../config";

export default function OrderView({ customer, cart: cartFromProps, setCart }) {
  const navigate = useNavigate();
  const location = useLocation();

  const { cart: cartFromNavigation, product } = location.state || {};

  const cart =
    cartFromNavigation ||
    (product ? [{ ...product, quantity: 1 }] : cartFromProps);

  const [orderItems, setOrderItems] = useState(
    cart.map((item) => ({
      ...item,
      orderQuantity: item.quantity
    }))
  );

  const updateQuantity = (productID, newQty) => {
    if (newQty < 1) newQty = 1;

    setOrderItems((prev) =>
      prev.map((item) =>
        item.productID === productID
          ? { ...item, orderQuantity: newQty }
          : item
      )
    );
  };

  const totalPrice = orderItems.reduce(
    (sum, item) => sum + item.orderQuantity * Number(item.priceEach),
    0
  );

  const paymentOptions = ["Cash", "BankTransfer", "Card", "Voucher"];
  const [paymentMethod, setPaymentMethod] = useState("");

  const handleOrder = async () => {
    if (!paymentMethod) {
      alert("Vui lòng chọn phương thức thanh toán!");
      return;
    }

    if (!customer) {
      alert("Vui lòng đăng nhập lại!");
      navigate("/login");
      return;
    }

    try {
      let pickupMethod = "";
      let paymentStatus = "";
      let orderStatus = "Confirmed";

      if (paymentMethod === "Cash" || paymentMethod === "Card") {
        pickupMethod = "StorePickup";
        paymentStatus = "Unpaid";
      } else {
        pickupMethod = "Ship";
        paymentStatus = "Paid";
      }

      const productList = orderItems.map((item) => ({
        productID: item.productID,
        quantity: item.orderQuantity,
        priceEach: Number(item.priceEach),
      }));

      const res = await fetch(`${API_BASE_URL}/order/checkout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customerID: customer.customerID,
          staffID: 1,
          paymentMethod: paymentMethod,
          products: productList,
          pickupMethod,
          orderStatus,
          paymentStatus,
          shippedStatus: "In Process",
          shippedDate: null,
        }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Checkout failed");

      const updatedCart = cartFromProps
        .map((item) => {
          const ordered = orderItems.find(
            (oi) => oi.productID === item.productID
          );
          if (!ordered) return item;

          if (ordered.orderQuantity < item.quantity) {
            return {
              ...item,
              quantity: item.quantity - ordered.orderQuantity,
            };
          }
          return null;
        })
        .filter(Boolean);

      setCart(updatedCart);
      localStorage.setItem("cart", JSON.stringify(updatedCart));

      alert("✅ Đặt hàng thành công!");
      navigate("/");

    } catch (err) {
      console.error(err);
      alert("❌ Lỗi đặt hàng: " + err.message);
    }
  };

  if (!orderItems.length) {
    return <div className="p-8 text-center text-gray-500">Không có sản phẩm để đặt hàng.</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-indigo-600 text-white px-8 py-4">
        <h1 onClick={() => navigate("/")} className="text-2xl font-bold cursor-pointer">
          🛍️ Cửa hàng Online
        </h1>
      </header>

      <main className="flex-1 p-8 max-w-3xl mx-auto bg-white rounded-2xl shadow">
        <h2 className="text-xl font-semibold mb-6">Xác nhận đơn hàng</h2>

        <div className="space-y-4 mb-6">
          {orderItems.map((item) => (
            <div key={item.productID} className="border rounded-xl p-4 flex justify-between items-center">
              <div>
                <p className="font-semibold">{item.productName}</p>
                <p className="text-sm text-gray-500">Giá: {Number(item.priceEach).toLocaleString()}₫</p>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={() => updateQuantity(item.productID, item.orderQuantity - 1)}
                  className="w-8 h-8 bg-gray-200 rounded-full text-lg font-bold"
                >
                  -
                </button>

                <span className="px-3">{item.orderQuantity}</span>

                <button
                  onClick={() => updateQuantity(item.productID, item.orderQuantity + 1)}
                  className="w-8 h-8 bg-gray-200 rounded-full text-lg font-bold"
                >
                  +
                </button>
              </div>

              <p className="font-bold text-indigo-600">
                {(item.orderQuantity * Number(item.priceEach)).toLocaleString()}₫
              </p>
            </div>
          ))}
        </div>

        <h3 className="font-medium mb-2">Chọn phương thức thanh toán</h3>
        <div className="grid grid-cols-2 gap-3 mb-6">
          {paymentOptions.map((method) => (
            <button
              key={method}
              onClick={() => setPaymentMethod(method)}
              className={`border rounded-xl py-2 ${
                paymentMethod === method ? "bg-orange-500 text-white" : "bg-gray-100 hover:bg-gray-200"
              }`}
            >
              {method}
            </button>
          ))}
        </div>

        <div className="flex justify-between">
          <p className="font-semibold text-lg">
            Tổng: <span className="text-orange-500">{totalPrice.toLocaleString()}₫</span>
          </p>

          <button
            disabled={!paymentMethod}
            onClick={handleOrder}
            className={`px-6 py-2 rounded-xl text-white font-semibold ${
              paymentMethod ? "bg-orange-500 hover:bg-orange-600" : "bg-gray-400"
            }`}
          >
            Đặt hàng
          </button>
        </div>
      </main>
    </div>
  );
}
