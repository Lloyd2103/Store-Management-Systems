import React from "react";
import { useNavigate } from "react-router-dom";
import { ShoppingCart } from "lucide-react";

export default function CartView({ cart, setCart, customer }) {
  const navigate = useNavigate();

  // ✅ Tính tổng tiền
  const totalPrice = cart.reduce(
    (sum, item) => sum + Number(item.priceEach || 0) * item.quantity,
    0
  );

  // ✅ Xóa một sản phẩm khỏi giỏ
  const handleRemove = (productID) => {
    const updated = cart.filter((item) => item.productID !== productID);
    setCart(updated);
    localStorage.setItem("cart", JSON.stringify(updated));
  };

  // ✅ Thanh toán
  const handleCheckout = () => {
    if (cart.length === 0) return;
    navigate("/order", { state: { cart } });
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* HEADER */}
      <header className="bg-indigo-600 text-white px-8 py-4 flex justify-between items-center">
        <h1
          className="text-2xl font-bold cursor-pointer"
          onClick={() => navigate("/")}
        >
          🛍️ Cửa hàng Online
        </h1>

        <button
          onClick={() => navigate("/cart")}
          className="flex items-center gap-2 text-white font-semibold"
        >
          <ShoppingCart className="w-5 h-5" /> Giỏ hàng ({cart.length})
        </button>
      </header>

      {/* MAIN */}
      <main className="flex-1 p-8 grid grid-cols-3 gap-6">
        {/* DANH SÁCH SẢN PHẨM */}
        <section className="col-span-2">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">
            Sản phẩm trong giỏ hàng
          </h2>

          {cart.length === 0 ? (
            <p className="text-gray-500 italic">Chưa có sản phẩm nào.</p>
          ) : (
            <div className="space-y-4">
              {cart.map((item) => (
                <div
                  key={item.productID}
                  className="bg-white rounded-xl shadow p-4 flex justify-between items-center"
                >
                  <div>
                    <h3 className="font-medium">{item.productName}</h3>

                    <p className="text-sm font-semibold text-indigo-600">
                      Số lượng: {" "}
                      <span className="text-black">{item.quantity}</span>
                    </p>

                    <p className="text-sm text-gray-700">
                      Đơn giá: {Number(item.priceEach).toLocaleString()}₫
                    </p>

                    <p className="text-sm text-gray-700 font-semibold">
                      Thành tiền: {(item.quantity * Number(item.priceEach)).toLocaleString()}₫
                    </p>
                  </div>

                  {/* NÚT XÓA */}
                  <button
                    onClick={() => handleRemove(item.productID)}
                    className="text-red-500 hover:text-red-700 text-sm"
                  >
                    Xóa
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* PANEL TỔNG TIỀN */}
        <aside className="bg-white rounded-xl shadow p-6 h-fit sticky top-6">
          <h2 className="text-lg font-bold text-gray-800 mb-4">
            Tổng thanh toán
          </h2>

          <p className="text-gray-700 mb-3">
            Tổng: {" "}
            <span className="text-orange-500 font-bold">
              {totalPrice.toLocaleString()}₫
            </span>
          </p>

          <button
            onClick={handleCheckout}
            disabled={!cart.length}
            className="w-full bg-orange-500 hover:bg-orange-600 text-white py-2 rounded-xl transition disabled:opacity-50"
          >
            Thanh toán
          </button>
        </aside>
      </main>
    </div>
  );
}
