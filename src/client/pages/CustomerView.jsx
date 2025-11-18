import React, { useState, useEffect } from "react";
import { ShoppingCart, Search, User, Clock } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { API_BASE_URL } from "../config";

export default function CustomerView({ cart, setCart }) {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const navigate = useNavigate();

  // ====== FILTERS ======
  const [filterBrand, setFilterBrand] = useState("");
  const [filterName, setFilterName] = useState("");
  const [filterPrice, setFilterPrice] = useState(["", ""]); // from – to

  // 🔹 Load sản phẩm
  useEffect(() => {
    fetch(`${API_BASE_URL}/products`)
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) setProducts(data);
      });
  }, []);

  // 🔹 Filter logic hoàn chỉnh
  const filteredProducts = products.filter((p) => {
    const nameMatch = p.productName
      .toLowerCase()
      .includes(filterName.toLowerCase());

    const brandMatch =
      filterBrand === "" || p.productBrand === filterBrand;

    // Giá
    const price = Number(p.MSRP);
    const min = filterPrice[0] === "" ? 0 : Number(filterPrice[0]);
    const max = filterPrice[1] === "" ? Infinity : Number(filterPrice[1]);
    const priceMatch = price >= min && price <= max;

    return nameMatch && brandMatch && priceMatch;
  });

  // 🔹 Mở popup chọn số lượng
  const openPopup = (product) => {
    setSelectedProduct(product);
    setQuantity(1);
  };

  const closePopup = () => setSelectedProduct(null);

  // 🔹 Thêm vào giỏ hàng
  const handleAddToCart = (product, qty) => {
    setCart((prev) => {
      const exist = prev.find((i) => i.productID === product.productID);
      if (exist) {
        return prev.map((i) =>
          i.productID === product.productID
            ? { ...i, quantity: i.quantity + qty }
            : i
        );
      }
      return [...prev, { ...product, quantity: qty }];
    });

    closePopup();
  };

  // 🔹 Đặt hàng ngay
  const handleDirectOrder = (product) => {
    navigate("/order", { state: { cart: [{ ...product, quantity: 1 }] } });
  };

  // Danh sách thương hiệu
  const brandList = [...new Set(products.map((p) => p.productBrand))];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* HEADER */}
      <header className="bg-indigo-600 shadow px-8 py-4 flex justify-between items-center">
        <h1
          onClick={() => navigate("/")}
          className="text-2xl font-bold text-white cursor-pointer"
        >
          🛒 Cửa hàng đồ điện tử
        </h1>

        {/* Ô tìm kiếm */}
        <div className="flex items-center bg-white rounded-xl px-4 py-2 w-96">
          <input
            type="text"
            placeholder="Nhập tên sản phẩm..."
            value={filterName}
            onChange={(e) => setFilterName(e.target.value)}
            className="flex-1 bg-transparent outline-none text-sm"
          />
          <Search className="w-5 h-5 text-gray-500" />
        </div>

        <div className="flex items-center gap-4">

          <button
            onClick={() => navigate("/order-history")}
            className="flex items-center gap-2 bg-white text-indigo-600 px-4 py-2 rounded-xl hover:bg-gray-100 font-semibold"
          >
            <Clock className="w-5 h-5" /> Lịch sử
          </button>

          <button
            onClick={() => navigate("/cart")}
            className="flex items-center gap-2 bg-white text-indigo-600 px-4 py-2 rounded-xl hover:bg-gray-100 font-semibold"
          >
            <ShoppingCart className="w-5 h-5" />
            Giỏ hàng ({cart.length})
          </button>

          <button
            onClick={() => navigate("/account")}
            className="flex items-center gap-2 bg-white text-indigo-600 px-4 py-2 rounded-xl hover:bg-gray-100 font-semibold"
          >
            <User className="w-5 h-5" />
            Tài khoản
          </button>
        </div>
      </header>

      {/* MAIN */}
      <main className="flex p-8 gap-6">
        {/* SIDEBAR */}
        <div className="w-64 bg-white rounded-2xl shadow p-5 h-fit sticky top-5">
          <h2 className="text-lg font-bold mb-4">🔎 Bộ lọc tìm kiếm</h2>

          {/* Thương hiệu */}
          <div className="mb-6">
            <p className="font-semibold mb-2">Thương hiệu</p>

            <select
              className="w-full border px-3 py-2 rounded-xl"
              value={filterBrand}
              onChange={(e) => setFilterBrand(e.target.value)}
            >
              <option value="">Tất cả</option>
              {brandList.map((b, i) => (
                <option key={i} value={b}>
                  {b}
                </option>
              ))}
            </select>
          </div>

          {/* Giá */}
          <div className="mb-6">
            <p className="font-semibold mb-2">Khoảng giá</p>

            <input
              type="number"
              placeholder="Từ..."
              className="w-full mb-2 border px-3 py-2 rounded-xl"
              value={filterPrice[0]}
              onChange={(e) => {
                const v = e.target.value;
                setFilterPrice([v === "" ? "" : Number(v), filterPrice[1]]);
              }}
            />

            <input
              type="number"
              placeholder="Đến..."
              className="w-full border px-3 py-2 rounded-xl"
              value={filterPrice[1]}
              onChange={(e) => {
                const v = e.target.value;
                setFilterPrice([filterPrice[0], v === "" ? "" : Number(v)]);
              }}
            />
          </div>
        </div>

        {/* PRODUCT LIST */}
        <div className="flex-1">
          <h2 className="text-xl font-semibold mb-4">Danh sách sản phẩm</h2>

          <div className="grid grid-cols-4 gap-6">
            {filteredProducts.map((p) => (
              <div
                key={p.productID}
                className="bg-white rounded-2xl shadow hover:shadow-lg transition p-4 flex flex-col justify-between"
              >
                <div>
                  <div className="h-32 bg-gray-100 rounded-xl mb-3 flex items-center justify-center text-gray-400 text-sm">
                    Ảnh sản phẩm
                  </div>

                  <h3 className="font-semibold text-gray-800">
                    {p.productName}
                  </h3>

                  <p className="text-indigo-600 font-bold mt-1">
                    {Number(p.MSRP).toLocaleString()}₫
                  </p>
                </div>

                <button
                  onClick={() => openPopup(p)}
                  className="mt-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl py-2 transition"
                >
                  Thêm vào giỏ
                </button>

                <button
                  onClick={() => handleDirectOrder(p)}
                  className="mt-2 bg-orange-500 hover:bg-orange-600 text-white rounded-xl py-2 transition font-medium"
                >
                  Đặt hàng
                </button>
              </div>
            ))}
          </div>
        </div>
      </main>

      {/* POPUP SỐ LƯỢNG */}
      {selectedProduct && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
          <div className="bg-white rounded-2xl shadow-xl p-6 w-96 relative">
            <button
              onClick={closePopup}
              className="absolute top-3 right-3 text-gray-500 hover:text-black text-xl"
            >
              ✕
            </button>

            <h2 className="text-lg font-semibold text-gray-800 mb-4 text-center">
              {selectedProduct.productName}
            </h2>

            <div className="flex justify-center items-center gap-4 mb-6">
              <button
                onClick={() => setQuantity(Math.max(1, quantity - 1))}
                className="w-8 h-8 bg-gray-200 rounded-full text-xl font-bold hover:bg-gray-300"
              >
                −
              </button>

              <span className="text-xl font-semibold w-10 text-center">
                {quantity}
              </span>

              <button
                onClick={() => setQuantity(quantity + 1)}
                className="w-8 h-8 bg-gray-200 rounded-full text-xl font-bold hover:bg-gray-300"
              >
                +
              </button>
            </div>

            <button
              onClick={() => handleAddToCart(selectedProduct, quantity)}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded-xl font-semibold"
            >
              Thêm vào giỏ hàng
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
