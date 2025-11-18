import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { API_BASE_URL } from "../config";

export default function RegisterView({ onSwitchToLogin }) {
  const [formData, setFormData] = useState({
    customerName: "",
    phone: "",
    email: "",
    address: "",
    postalCode: "",
    password: "",
  });
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  // Nếu onSwitchToLogin không có, dùng navigate để chuyển
  const switchToLogin = () => {
    if (typeof onSwitchToLogin === "function") {
      onSwitchToLogin();
    } else {
      navigate("/login");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg("");
    setSuccessMsg("");
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE_URL}/register/customer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      // đọc body trả về (await hợp lệ vì handleSubmit là async)
      const data = await res.json();

      if (!res.ok) {
        // backend có thể trả { error: "..." } hoặc tương tự
        setErrorMsg(data.error || "Đăng ký thất bại!");
      } else {
        // Nếu backend trả về customer hoặc customerID, bạn có thể log để kiểm tra
        if (data.customerID) {
          setSuccessMsg(`Đăng ký thành công! Mã khách hàng của bạn: ${data.customerID}`);
        } else {
          setSuccessMsg("Đăng ký thành công! Vui lòng đăng nhập.");
        }

        // Chờ 1s rồi chuyển sang trang đăng nhập
        setTimeout(() => {
          switchToLogin();
        }, 1000);
      }
    } catch (err) {
      console.error("Lỗi khi đăng ký:", err);
      setErrorMsg("Không thể kết nối tới máy chủ!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white shadow-xl rounded-2xl p-8 w-[420px]">
        <h2 className="text-2xl font-bold text-indigo-600 text-center mb-6">
          Tạo tài khoản mới
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            name="customerName"
            placeholder="Họ và tên"
            value={formData.customerName}
            onChange={handleChange}
            required
            className="w-full border rounded-xl px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
          />
          <input
            name="phone"
            placeholder="Số điện thoại"
            value={formData.phone}
            onChange={handleChange}
            required
            className="w-full border rounded-xl px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
          />
          <input
            name="email"
            placeholder="Email (tùy chọn)"
            value={formData.email}
            onChange={handleChange}
            className="w-full border rounded-xl px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
          />
          <input
            name="address"
            placeholder="Địa chỉ"
            value={formData.address}
            onChange={handleChange}
            required
            className="w-full border rounded-xl px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
          />
          <input
            name="postalCode"
            placeholder="Mã bưu điện"
            value={formData.postalCode}
            onChange={handleChange}
            required
            className="w-full border rounded-xl px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
          />
          <input
            type="password"
            name="password"
            placeholder="Mật khẩu"
            value={formData.password}
            onChange={handleChange}
            required
            className="w-full border rounded-xl px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
          />

          {errorMsg && <p className="text-red-500 text-sm text-center">{errorMsg}</p>}
          {successMsg && <p className="text-green-600 text-sm text-center">{successMsg}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-2 rounded-xl hover:bg-indigo-700 transition font-semibold"
          >
            {loading ? "Đang xử lý..." : "Đăng ký"}
          </button>
        </form>

        <p className="text-sm text-center mt-4 text-gray-600">
          Đã có tài khoản? {" "}
          <button
            onClick={switchToLogin}
            className="text-indigo-600 font-semibold hover:underline"
          >
            Đăng nhập ngay
          </button>
        </p>
      </div>
    </div>
  );
}
