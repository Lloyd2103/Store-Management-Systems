import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { API_BASE_URL } from "../config";

export default function AccountView({ customer, onLogout, setCustomer }) {
  const navigate = useNavigate();
  const [formData, setFormData] = useState(customer || {});
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    const stored = JSON.parse(localStorage.getItem("customer"));
    
    if (!stored) {
      navigate("/login");
      return;
    }

    setFormData(stored);
    setCustomer(stored);

    if (stored.customerID) {
      fetch(`${API_BASE_URL}/customers/${stored.customerID}`)
        .then((res) => res.json())
        .then((data) => {
          if (data && data.customerID) {
            setFormData(data);
            setCustomer(data);
            localStorage.setItem("customer", JSON.stringify(data));
          }
        })
        .catch((err) => console.error("Lỗi khi tải thông tin:", err));
    }
  }, [navigate, setCustomer]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSave = async () => {
    if (!formData.customerID) {
      setErrorMsg("Không tìm thấy ID khách hàng để cập nhật!");
      return;
    }

    setLoading(true);
    setErrorMsg("");
    setSuccessMsg("");

    try {
      const res = await fetch(
        `${API_BASE_URL}/customers/${formData.customerID}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            customerName: formData.customerName,
            phone: formData.phone,
            email: formData.email,
            address: formData.address,
            postalCode: formData.postalCode,
          }),
        }
      );

      const data = await res.json();

      if (!res.ok || !data.customerID) {
        throw new Error("Cập nhật thất bại hoặc server không trả dữ liệu hợp lệ!");
      }

      setFormData(data);
      setCustomer(data);
      localStorage.setItem("customer", JSON.stringify(data));
      setSuccessMsg("✅ Cập nhật thông tin thành công!");
    } catch (err) {
      console.error(err);
      setErrorMsg("❌ Không thể cập nhật thông tin!");
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => navigate("/");

  if (!formData) return null;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center py-10">
      <div className="bg-white rounded-2xl shadow-xl w-[480px] p-8">
        <h2 className="text-2xl font-bold text-indigo-600 text-center mb-6">
          👤 Thông tin tài khoản
        </h2>

        {errorMsg && <p className="text-red-500 text-sm text-center mb-3">{errorMsg}</p>}
        {successMsg && <p className="text-green-600 text-sm text-center mb-3">{successMsg}</p>}

        <div className="mb-4">
          <label className="block text-gray-600 font-semibold mb-1">Mã khách hàng</label>
          <input
            value={formData.customerID || ""}
            disabled
            className="w-full border rounded-xl px-3 py-2 bg-gray-100 text-gray-600"
          />
        </div>

        <div className="mb-4">
          <label className="block text-gray-600 font-semibold mb-1">Họ và tên</label>
          <input
            name="customerName"
            value={formData.customerName || ""}
            onChange={handleChange}
            className="w-full border rounded-xl px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
          />
        </div>

        <div className="mb-4">
          <label className="block text-gray-600 font-semibold mb-1">Số điện thoại</label>
          <input
            name="phone"
            value={formData.phone || ""}
            onChange={handleChange}
            className="w-full border rounded-xl px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
          />
        </div>

        <div className="mb-4">
          <label className="block text-gray-600 font-semibold mb-1">Email</label>
          <input
            name="email"
            value={formData.email || ""}
            onChange={handleChange}
            className="w-full border rounded-xl px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
          />
        </div>

        <div className="mb-4">
          <label className="block text-gray-600 font-semibold mb-1">Địa chỉ</label>
          <input
            name="address"
            value={formData.address || ""}
            onChange={handleChange}
            className="w-full border rounded-xl px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
          />
        </div>

        <div className="mb-6">
          <label className="block text-gray-600 font-semibold mb-1">Mã bưu điện</label>
          <input
            name="postalCode"
            value={formData.postalCode || ""}
            onChange={handleChange}
            className="w-full border rounded-xl px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
          />
        </div>

        <div className="flex justify-between items-center">
          <button
            onClick={handleBack}
            className="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded-xl font-semibold"
          >
            ⏪ Quay lại
          </button>
          <button
            onClick={handleSave}
            disabled={loading}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-xl font-semibold disabled:opacity-50"
          >
            {loading ? "Đang lưu..." : "💾 Lưu thay đổi"}
          </button>
        </div>

        <div className="text-center mt-6">
          <button
            onClick={() => onLogout(navigate)}
            className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-xl font-semibold"
          >
            Đăng xuất
          </button>
        </div>
      </div>
    </div>
  );
}
