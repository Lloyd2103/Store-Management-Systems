/**
 * File cấu hình cho frontend
 * Thay đổi các tham số tại đây để cấu hình kết nối với backend
 */

const config = {
    // Địa chỉ API backend (không có dấu / ở cuối)
    // Ví dụ: "http://localhost:6868" hoặc "http://192.168.2.1:6868"
    API_BASE_URL: "http://192.168.2.50:6868",

    // Các endpoint API
    API_ENDPOINTS: {
        LOGIN_STAFF: "/login/staff",
        LOGIN_CUSTOMER: "/login/customer",
        REGISTER_STAFF: "/register/staff",
        REGISTER_CUSTOMER: "/register/customer",
        CUSTOMERS: "/customers",
        PRODUCTS: "/products",
        ORDERS: "/orders",
        PAYMENTS: "/payments",
        STAFFS: "/staffs",
        VENDORS: "/vendors",
        INVENTORIES: "/inventories",
        REQUESTS: "/requests",
        STORES: "/stores",
        SUPPLIES: "/supplies",
        CATEGORIES: "/categories",
        DEBTS: "/debts",
        INVENTORY_IMPORT: "/inventory/import",
        INVENTORY_EXPORT: "/inventory/export",
        INVENTORY_STOCKTAKING: "/inventory/stocktaking",
        REPORTS_REVENUE: "/reports/revenue",
        REPORTS_TOP_PRODUCTS: "/reports/top-products",
        REPORTS_INVENTORY: "/reports/inventory",
        REPORTS_SUMMARY: "/reports/summary"
    }
};

export default config;
