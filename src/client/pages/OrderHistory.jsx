import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { API_BASE_URL } from "../config";

export default function OrderHistory() {
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  // ✅ Lấy thông tin người dùng từ localStorage
  const customer = JSON.parse(localStorage.getItem("customer"));

  // ✅ Nếu chưa đăng nhập → quay về login
  useEffect(() => {
    if (!customer || !customer.customerID) {
      navigate("/login");
    }
  }, [customer, navigate]);

  // ✅ Fetch danh sách đơn hàng
  useEffect(() => {
    if (!customer || !customer.customerID) return;

    const fetchOrders = async () => {
      try {
        // ✅ Sửa lại API đúng
        const res = await fetch(`${API_BASE_URL}/orders/${customer.customerID}`);
        const data = await res.json();

        if (!Array.isArray(data)) {
          console.error("Orders API trả về sai định dạng:", data);
          setLoading(false);
          return;
        }

        // ✅ Lấy danh sách sản phẩm cho từng đơn
        const ordersWithItems = await Promise.all(
          data.map(async (order) => {
            try {
              const req = await fetch(`${API_BASE_URL}/requests/${order.orderID}`);
              const reqData = await req.json();

              return {
                ...order,
                items: Array.isArray(reqData) ? reqData : [],
              };
            } catch (err) {
              console.error("Lỗi khi tải items:", err);
              return { ...order, items: [] };
            }
          })
        );

        setOrders(ordersWithItems);
      } catch (err) {
        console.error("Lỗi khi tải lịch sử đơn hàng:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, [customer]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-600 text-lg">
        Đang tải lịch sử đơn hàng...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      {/* HEADER */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-indigo-600">📜 Lịch sử đơn hàng</h1>
        <button
          onClick={() => navigate("/")}
          className="px-4 py-2 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700"
        >
          ⏪ Quay lại cửa hàng
        </button>
      </div>

      {orders.length === 0 ? (
        <p className="text-gray-600 italic">Bạn chưa có đơn hàng nào.</p>
      ) : (
        <div className="space-y-6">
          {orders.map((order) => (
            <div
              key={order.orderID}
              className="bg-white shadow rounded-2xl p-6 border border-gray-200"
            >
              <div className="flex justify-between mb-4">
                <h2 className="font-bold text-lg text-gray-800">
                  Đơn hàng #{order.orderID}
                </h2>
                <span className="text-sm text-gray-500">
                  {order.orderDate ? new Date(order.orderDate).toLocaleString() : ""}
                </span>
              </div>

              <div className="mb-2">
                <p>
                  <span className="font-semibold">Trạng thái đơn: </span>
                  {order.orderStatus || "Không có"}
                </p>
                <p>
                  <span className="font-semibold">Thanh toán: </span>
                  {order.paymentStatus}
                </p>
                <p>
                  <span className="font-semibold">Giao hàng: </span>
                  {order.shippedStatus}
                </p>
              </div>

              <h3 className="font-semibold mt-4 mb-2">Danh sách sản phẩm</h3>

              <div className="pl-4">
                {order.items.length > 0 ? (
                  order.items.map((item) => (
                    <div key={item.productID} className="mb-2">
                      <p className="text-gray-800">
                        • {item.productName} x {item.quantity}
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 italic">Không có sản phẩm.</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
