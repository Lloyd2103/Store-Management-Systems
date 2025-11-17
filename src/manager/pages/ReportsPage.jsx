import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Package, DollarSign, Loader2, Users } from 'lucide-react';
import config from '../constants/config';
import dayjs from 'dayjs'; // Import dayjs

const LoadingSpinner = () => (
    <div className="flex items-center justify-center p-8 text-indigo-600">
        <Loader2 className="w-8 h-8 animate-spin mr-2" />
        <span>Đang tải dữ liệu...</span>
    </div>
);

const ReportsPage = () => {
    const [summary, setSummary] = useState(null);
    const [revenueData, setRevenueData] = useState([]);
    const [topProducts, setTopProducts] = useState([]);
    const [inventoryReport, setInventoryReport] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    // THAY ĐỔI: Sử dụng state timeRange để chọn lọc
    const [timeRange, setTimeRange] = useState('month'); // Mặc định là 'month'
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');

    // THAY ĐỔI: Logic tính toán startDate và endDate từ timeRange
    useEffect(() => {
        const calculateDates = (range) => {
            const now = dayjs();
            let start, end = now.format('YYYY-MM-DD');

            switch (range) {
                case 'week':
                    // 7 ngày gần nhất (từ 7 ngày trước đến hôm nay)
                    start = now.subtract(7, 'day').format('YYYY-MM-DD');
                    break;
                case 'month':
                    // Từ đầu tháng đến hôm nay
                    start = now.startOf('month').format('YYYY-MM-DD');
                    break;
                case 'quarter':
                    // Từ đầu quý đến hôm nay
                    start = now.startOf('quarter').format('YYYY-MM-DD');
                    break;
                case 'year':
                    // Từ đầu năm đến hôm nay
                    start = now.startOf('year').format('YYYY-MM-DD');
                    break;
                default:
                    start = '';
                    end = '';
            }
            setStartDate(start);
            setEndDate(end);
        };

        calculateDates(timeRange);
    }, [timeRange]); // Chạy lại khi timeRange thay đổi

    // Giữ nguyên: Chạy các hàm load khi startDate/endDate thay đổi
    useEffect(() => {
        // isLoading được set lại ở loadSummary
        setIsLoading(true);
        loadSummary();
        loadRevenueReport();
        loadTopProducts();
        // loadInventoryReport không cần tham số ngày
        loadInventoryReport();
    }, [startDate, endDate]);


    const loadSummary = async () => {
        try {
            const response = await fetch(`${config.API_BASE_URL}${config.API_ENDPOINTS.REPORTS_SUMMARY}`);
            if (response.ok) {
                const data = await response.json();
                setSummary(data);
            }
        } catch (err) {
            console.error('Error loading summary:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const loadRevenueReport = async () => {
        try {
            const params = new URLSearchParams();
            if (startDate) params.append('start_date', startDate);
            if (endDate) params.append('end_date', endDate);

            const response = await fetch(`${config.API_BASE_URL}${config.API_ENDPOINTS.REPORTS_REVENUE}?${params}`);
            if (response.ok) {
                const data = await response.json();
                setRevenueData(data);
            }
        } catch (err) {
            console.error('Error loading revenue report:', err);
        }
    };

    const loadTopProducts = async () => {
        try {
            const params = new URLSearchParams();
            params.append('limit', '10');
            if (startDate) params.append('start_date', startDate);
            if (endDate) params.append('end_date', endDate);

            const response = await fetch(`${config.API_BASE_URL}${config.API_ENDPOINTS.REPORTS_TOP_PRODUCTS}?${params}`);
            if (response.ok) {
                const data = await response.json();
                setTopProducts(data);
            }
        } catch (err) {
            console.error('Error loading top products:', err);
        }
    };

    const loadInventoryReport = async () => {
        try {
            const response = await fetch(`${config.API_BASE_URL}${config.API_ENDPOINTS.REPORTS_INVENTORY}`);
            if (response.ok) {
                const data = await response.json();
                setInventoryReport(data);
            }
        } catch (err) {
            console.error('Error loading inventory report:', err);
        }
    };

    if (isLoading) {
        return <LoadingSpinner />;
    }

    const formatCurrency = (amount) => {
        if (amount === null || amount === undefined || amount === '') return '';
        const num = typeof amount === 'string' ? parseFloat(amount) : amount;
        if (isNaN(num)) return amount;
        // Định dạng tiền tệ Việt Nam với dấu phẩy phân cách hàng nghìn
        return num.toLocaleString('vi-VN');
    };

    const formatNumber = (num) => {
        return new Intl.NumberFormat('vi-VN').format(num || 0);
    };

    return (
        <div className="p-4 space-y-6">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold text-gray-800">Báo cáo & Thống kê</h2>

                {/* THAY ĐỔI: Sử dụng Select Box thay cho Input Date */}
                <div className="flex gap-2">
                    <select
                        value={timeRange}
                        onChange={(e) => setTimeRange(e.target.value)}
                        className="border border-gray-300 rounded px-3 py-2 text-sm"
                    >
                        <option value="week">Tuần này</option>
                        <option value="month">Tháng này</option>
                        <option value="quarter">Quý này</option>
                        <option value="year">Năm này</option>
                    </select>
                </div>
            </div>

            {/* Summary Cards */}
            {summary && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="bg-white rounded-lg shadow p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Tổng Khách hàng</p>
                                <p className="text-2xl font-bold text-indigo-600">{formatNumber(summary.totalCustomers)}</p>
                            </div>
                            <Users className="w-8 h-8 text-indigo-400" />
                        </div>
                    </div>
                    <div className="bg-white rounded-lg shadow p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Tổng Sản phẩm</p>
                                <p className="text-2xl font-bold text-green-600">{formatNumber(summary.totalProducts)}</p>
                            </div>
                            <Package className="w-8 h-8 text-green-400" />
                        </div>
                    </div>
                    <div className="bg-white rounded-lg shadow p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Tổng Doanh thu</p>
                                <p className="text-2xl font-bold text-blue-600">{formatCurrency(summary.totalRevenue)} đ</p>
                            </div>
                            <DollarSign className="w-8 h-8 text-blue-400" />
                        </div>
                    </div>
                    <div className="bg-white rounded-lg shadow p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Tổng Công nợ</p>
                                <p className="text-2xl font-bold text-red-600">{formatCurrency(summary.totalDebts)} đ</p>
                            </div>
                            <TrendingUp className="w-8 h-8 text-red-400" />
                        </div>
                    </div>
                </div>
            )}

            {/* Revenue Report (Báo cáo Doanh thu - Đã có sẵn) */}
            <div className="bg-white rounded-lg shadow p-4">
                <h3 className="text-lg font-semibold mb-4 flex items-center text-gray-700">
                    <BarChart3 className="w-5 h-5 mr-2 text-indigo-600" /> {/* Màu icon giữ nguyên */}
                    Báo cáo Doanh thu
                </h3>
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-4 py-2 text-left text-xs font-medium text-blue-500">Ngày</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-blue-500">Số đơn</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-blue-500">Tổng doanh thu</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-blue-500">Đã thanh toán</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-blue-500">Chưa thanh toán</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {revenueData.length > 0 ? (
                                revenueData.map((item, index) => (
                                    <tr key={index}>
                                        <td className="px-4 py-2 text-sm text-black">{item.date}</td>
                                        <td className="px-4 py-2 text-sm text-black">{formatNumber(item.orderCount)}</td>
                                        <td className="px-4 py-2 text-sm font-semibold text-blue-700">{formatCurrency(item.totalRevenue)} đ</td>
                                        <td className="px-4 py-2 text-sm font-semibold text-green-600 ">{formatCurrency(item.paidAmount)} đ</td>
                                        <td className="px-4 py-2 text-sm font-semibold text-red-600">{formatCurrency(item.unpaidAmount)} đ</td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="5" className="px-4 py-4 text-center text-gray-500">Không có dữ liệu</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Top Products (Sản phẩm Bán chạy - Đã có sẵn) */}
            <div className="bg-white rounded-lg shadow p-4">
                <h3 className="text-lg font-semibold mb-4 flex items-center text-gray-700">
                    <TrendingUp className="w-5 h-5 mr-2 text-indigo-600" />
                    Sản phẩm Bán chạy
                </h3>
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-4 py-2 text-left text-xs font-medium text-blue-500">Mã SP</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-blue-500">Tên sản phẩm</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-blue-500">Danh mục</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-blue-500">Số lượng bán</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-blue-500">Doanh thu</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {topProducts.length > 0 ? (
                                topProducts.map((product, index) => (
                                    <tr key={index}>
                                        <td className="px-4 py-2 text-sm text-black">{product.productID}</td>
                                        <td className="px-4 py-2 text-sm text-black">{product.productName}</td>
                                        <td className="px-4 py-2 text-sm text-black">{product.productLine}</td>
                                        <td className="px-4 py-2 text-sm text-black">{formatNumber(product.totalQuantitySold)}</td>
                                        <td className="px-4 py-2 text-sm font-semibold text-blue-600">{formatCurrency(product.totalRevenue)} đ</td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="5" className="px-4 py-4 text-center text-gray-500">Không có dữ liệu</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Inventory Report (Báo cáo Tồn kho - Đã có sẵn) */}
            <div className="bg-white rounded-lg shadow p-4">
                <h3 className="text-lg font-semibold mb-4 flex items-center text-gray-700">
                    <Package className="w-5 h-5 mr-2 text-indigo-600" />
                    Báo cáo Tồn kho
                </h3>
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-4 py-2 text-left text-xs font-medium text-blue-500">Kho</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-blue-500">Sản phẩm</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-blue-500">Số lượng</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-blue-500">Giá trị</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-blue-500">Trạng thái</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {inventoryReport.length > 0 ? (
                                inventoryReport.map((item, index) => (
                                    <tr key={index}>
                                        <td className="px-4 py-2 text-sm text-black">{item.warehouse}</td>
                                        <td className="px-4 py-2 text-sm text-black">{item.productName || 'N/A'}</td>
                                        <td className="px-4 py-2 text-sm text-black">{formatNumber(item.stockQuantity)}</td>
                                        <td className="px-4 py-2 text-sm text-black">{formatCurrency(item.totalValue)} đ</td>
                                        <td className="px-4 py-2 text-sm text-black">
                                            <span className={`px-2 py-1 rounded text-xs ${item.status === 'Out of Stock' ? 'bg-red-100 text-red-800' :
                                                item.status === 'Low Stock' ? 'bg-yellow-100 text-yellow-800' :
                                                    'bg-green-100 text-green-800'
                                                }`}>
                                                {item.status}
                                            </span>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="5" className="px-4 py-4 text-center text-gray-500">Không có dữ liệu</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default ReportsPage;
