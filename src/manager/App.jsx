/* eslint-disable no-dupe-keys */
import React, { useState, useEffect, useCallback } from 'react';
import { Users, Package, ShoppingCart, Truck, ClipboardList, Package2, Loader2, Plus, X, BarChart3, Search, Filter, Edit, Trash2, Eye } from 'lucide-react';
import LoginPage from './pages/LoginPage';
import ReportsPage from './pages/ReportsPage';
import { POSITION_PERMISSIONS } from './utils/permissions';
import config from './constants/config';

const API_BASE_URL = config.API_BASE_URL;
const TABS = {
    customers: { label: 'Khách hàng', icon: Users, endpoint: '/customers' },
    products: { label: 'Sản phẩm', icon: Package, endpoint: '/products' },
    orders: { label: 'Đơn hàng', icon: ShoppingCart, endpoint: '/orders' },
    payments: { label: 'Thanh toán', icon: Package2, endpoint: '/payments' },
    staffs: { label: 'Nhân viên', icon: ClipboardList, endpoint: '/staffs' },
    vendors: { label: 'Nhà cung cấp', icon: Truck, endpoint: '/vendors' },
    inventories: { label: 'Kho', icon: Package2, endpoint: '/inventories' },
    reports: { label: 'Báo cáo', icon: BarChart3, endpoint: '/reports' },
};



const LoadingSpinner = () => (
    <div className="flex items-center justify-center p-8 text-indigo-600">
        <Loader2 className="w-8 h-8 animate-spin mr-2" />
        <span>Đang tải dữ liệu...</span>
    </div>
);

// Hàm format số tiền với dấu chấm mỗi 3 chữ số
const formatCurrency = (value) => {
    if (value === null || value === undefined || value === '') return '';
    const num = typeof value === 'string' ? parseFloat(value) : value;
    if (isNaN(num)) return value;
    return num.toLocaleString('vi-VN');
};

// Hàm kiểm tra xem cột có phải là số tiền không
const isCurrencyColumn = (columnName) => {
    const currencyColumns = [
        'priceEach', 'MSRP', 'totalAmount', 'salary', 'transactionAmount',
        'unitCost', 'paidAmount', 'unpaidAmount', 'debtAmount', 'totalDebt',
        'totalRevenue', 'totalValue', 'totalInventoryValue', 'paymentAmount'
    ];
    const columnLower = columnName.toLowerCase();
    return currencyColumns.includes(columnName) ||
        columnLower.includes('price') ||
        columnLower.includes('amount') ||
        columnLower.includes('cost') ||
        columnLower.includes('salary') ||
        columnLower.includes('revenue') ||
        columnLower.includes('value');
};

const getColumnDisplayName = (columnName) => {
    const displayNames = {
        // Khách hàng
        customerID: 'Mã KH',
        customerName: 'Tên khách hàng',
        customerType: 'Loại KH',
        phone: 'Điện thoại',
        email: 'Email',
        address: 'Địa chỉ',
        postalCode: 'Mã bưu chính',
        loyalLevel: 'Cấp độ',
        loyalPoint: 'Điểm tích lũy',

        // Nhân viên
        staffID: 'Mã NV',
        staffName: 'Tên nhân viên',
        position: 'Chức vụ',
        managerID: 'Mã người quản lý',
        salary: 'Lương',

        // Sản phẩm
        productID: 'Mã Sản Phẩm',
        productName: 'Tên sản phẩm',
        priceEach: 'Giá Nhập',
        productLine: 'Dòng sản phẩm',
        productScale: 'Quy mô',
        productBrand: 'Thương hiệu',
        productDiscription: 'Mô tả',
        warrantyPeriod: 'Thời gian bảo hành',
        MSRP: 'Giá Đề Xuất',


        // Đơn hàng
        orderID: 'Mã đơn',
        orderDate: 'Ngày đặt',
        totalAmount: 'Tổng tiền',
        orderStatus: 'Trạng thái Đơn hàng',
        paymentStatus: 'Trạng thái Thanh toán',
        pickupMethod: 'Phương thức nhận hàng',
        shippedDate: 'Ngày giao hàng',
        shippedStatus: 'Trạng thái giao hàng',

        // Thanh toán
        paymentID: 'Mã TT',
        orderID: 'Mã đơn',
        transactionAmount: 'Số tiền',
        paymentMethod: 'Phương thức',
        transactionDate: 'Ngày giao dịch',
        transactionStatus: 'Trạng thái giao dịch',

        // Tồn kho
        inventoryID: 'Mã kho',
        warehouse: 'Kho',
        warehouseID: 'Mã kho chứa',
        maxStockLevel: 'Tồn tối đa',
        stockQuantity: 'Số lượng',
        unitCost: 'Đơn giá',
        lastUpdate: 'Cập nhật',
        inventoryNote: 'Ghi chú',
        inventoryStatus: 'Trạng thái',
        productCount: 'Số sản phẩm',

        // Nhà cung cấp
        vendorID: 'Mã NCC',
        vendorName: 'Tên NCC',
        contactName: 'Người liên hệ',
        vendorType: 'Loại NCC',
        paymentTerms: 'Điều khoản TT',
        vendorStatus: 'Trạng thái'
    };
    return displayNames[columnName] || columnName.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase());
};

const ActionButtons = ({ onEdit, onDelete, onView, activeTab }) => {
    // For orders, vendors, inventory: show View, Edit, Delete
    // For others: show Edit, Delete
    const needsView = ['orders', 'vendors', 'inventories'].includes(activeTab);

    return (
        <div className="flex gap-2">
            {needsView && onView && (
                <button
                    onClick={(e) => {
                        e.stopPropagation();
                        onView();
                    }}
                    className="p-1.5 rounded text-gray-600 hover:bg-blue-50 bg-white transition-colors"
                    title="Xem chi tiết"
                >
                    <Eye className="w-4 h-4" />
                </button>
            )}
            <button
                onClick={(e) => {
                    e.stopPropagation();
                    onEdit();
                }}
                className="p-1.5 rounded text-blue-600 hover:bg-blue-50 bg-white transition-colors"
                title="Sửa"
            >
                <Edit className="w-4 h-4" />
            </button>
            <button
                onClick={(e) => {
                    e.stopPropagation();
                    onDelete();
                }}
                className="p-1.5 rounded text-red-600 hover:bg-red-50 bg-white transition-colors"
                title="Xóa"
            >
                <Trash2 className="w-4 h-4" />
            </button>
        </div>
    );
};

const DataTable = ({ data, onRowClick, onItemEdit, onItemDelete, selectedRows, onSelectRow, activeTab }) => {
    const handleEdit = useCallback((item) => {
        if (onItemEdit) {
            onItemEdit(item);
        } else {
            // Fallback for old behavior
            onRowClick(item);
        }
    }, [onItemEdit, onRowClick]);

    const handleDelete = useCallback((item) => {
        if (onItemDelete) {
            onItemDelete(item);
        }
    }, [onItemDelete]);

    if (!data || data.length === 0) {
        return <div className="p-4 text-gray-500 text-center">Không có dữ liệu để hiển thị.</div>;
    }

    const columns = Object.keys(data[0]);
    const idKey = columns.find((c) => c.toLowerCase().endsWith("id")) || columns[0];

    return (
        <div className="overflow-x-auto bg-white rounded shadow-lg">
            <table className="min-w-full divide-y divide-blue-900">
                <thead className="bg-blue-100 sticky top-0">
                    <tr>
                        <th className="px-2 py-1">
                            <input
                                type="checkbox"
                                onChange={(e) => onSelectRow(e.target.checked ? data.map((item) => item[idKey]) : [])}
                                checked={selectedRows.length === data.length}
                                className="w-3 h-3"
                            />
                        </th>
                        {columns.map((col) => (
                            <th key={col} className="px-3 py-2 text-left text-xs font-medium text-blue-800 tracking-wider">
                                {getColumnDisplayName(col)}
                            </th>
                        ))}
                        <th className="px-3 py-2 text-left text-xs font-medium text-blue-800 tracking-wider">
                            {/* Action column - no header text as requested */}
                        </th>
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-blue-200">
                    {data.map((item, index) => (
                        <tr
                            key={index}
                            className={`transition duration-150 ${selectedRows.includes(item[idKey]) ? 'bg-indigo-50' : 'hover:bg-gray-100'}`}
                        >
                            <td className="px-2 py-1">
                                <input
                                    type="checkbox"
                                    className="w-3 h-3"
                                    checked={selectedRows.includes(item[idKey])} onChange={(e) => {
                                        onSelectRow(
                                            e.target.checked
                                                ? [...selectedRows, item[idKey]]
                                                : selectedRows.filter((id) => id !== item[idKey])
                                        );
                                    }}
                                />
                            </td>
                            {columns.map((col) => {
                                const value = item[col];
                                const displayValue = isCurrencyColumn(col) ? formatCurrency(value) : value;
                                return (
                                    <td key={col} className="px-3 py-1 whitespace-nowrap text-xs text-gray-900">
                                        {displayValue}
                                    </td>
                                );
                            })}
                            <td className="px-3 py-1 whitespace-nowrap text-xs text-gray-900">
                                <ActionButtons
                                    onEdit={() => handleEdit(item)}
                                    onDelete={() => handleDelete(item)}
                                    onView={() => onRowClick(item)}
                                    activeTab={activeTab}
                                />
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

// Relations Modal Component
const RelationsModal = ({ data, type, onClose, onEdit, onDelete, activeTab, selectedItem, user }) => {
    const [isEditing, setIsEditing] = useState(false);
    const [editData, setEditData] = useState(selectedItem || {});

    

    const getTitle = () => {
        if (isEditing) {
            return activeTab === 'vendors' ? 'Chỉnh sửa Nhà cung cấp' : 'Chỉnh sửa Kho';
        }
        switch (type) {
            case 'product-relations':
                return 'Quan hệ Sản phẩm';
            case 'vendor-products':
                return 'Sản phẩm được cung cấp';
            case 'inventory-products':
                return 'Sản phẩm trong kho';
            case 'order-details':
                return 'Chi tiết Đơn hàng';
            default:
                return 'Quan hệ';
        }
    };

    const handleEditChange = (e) => {
        const { name, value, inputType } = e.target;
        let processedValue = value;
        if (inputType === 'number') {
            processedValue = value === '' ? '' : Number(value);
        }
        setEditData({ ...editData, [name]: processedValue });
    };

    const handleSaveEdit = async () => {
        try {
            const endpoint = `${API_BASE_URL}${TABS[activeTab].endpoint}/${editData[Object.keys(editData)[0]]}`;
            const response = await fetch(endpoint, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${user.token}`,
                },
                body: JSON.stringify(editData)
            });

            if (!response.ok) throw new Error('Lỗi khi cập nhật dữ liệu');
            setIsEditing(false);
            onEdit(); // Trigger refresh in parent
            alert('Cập nhật thành công!');
        } catch (err) {
            alert('Lỗi khi cập nhật: ' + err.message);
        }
    };

    const getInputType = (key) => {
        const k = key.toLowerCase();
        if (k === 'password') return 'password';
        if (k.includes('email')) return 'email';
        if (k.includes('phone')) return 'tel';
        if (k.includes('date')) return 'date';
        if (k.includes('point') || k.includes('quantity') || k.includes('warranty')) return 'number';
        if (k.includes('price') || k.includes('amount') || k.includes('cost') || k.includes('salary')) return 'number';
        if (k === 'position') return 'select';
        if (k.includes('status') || k.includes('method') || k.includes('type')) return 'select';
        return 'text';
    };

    const getSelectOptions = (key) => {
        const options = {
            orderStatus: ['Pending', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled'],
            pickupMethod: ['Ship', 'StorePickup'],
            shippedStatus: ['Shipped', 'Cancelled', 'On Hold', 'In Process'],
            paymentStatus: ['Unpaid', 'Partial', 'Paid', 'Refunded'],
            paymentMethod: ['Cash', 'Credit Card', 'Bank Transfer', 'E-Wallet', 'Check'],
            customerType: ['Individual', 'Corporate', 'Partner', 'Reseller'],
            loyalLevel: ['New', 'Bronze', 'Silver', 'Gold', 'Platinum'],
            inventoryStatus: ['Active', 'Inactive', 'Low Stock', 'Out of Stock'],
            roleStore: ['Import', 'Export', 'Stocktaking', 'Manual', 'Initial', 'Update'],
            vendorStatus: ['Active', 'Inactive', 'Pending', 'Blacklisted'],
            transactionStatus: ['Pending', 'Completed', 'Failed', 'Refunded']
        };
        if (key === 'position') return ['Manager', 'Sales', 'Inventory'];
        return options[key] || [];
    };

    if (isEditing) {
        // Edit mode - show form to edit selectedItem
        return (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-2 z-50">
                <div className="bg-white rounded p-4 w-full max-w-md shadow-xl relative max-h-[90vh] overflow-hidden">
                    <button onClick={() => setIsEditing(false)} className="absolute top-2 right-2 text-gray-400 hover:text-red-600">
                        <X className="w-4 h-4" />
                    </button>
                    <h2 className="text-lg font-bold text-indigo-700 mb-3">{getTitle()}</h2>
                    <form onSubmit={(e) => { e.preventDefault(); handleSaveEdit(); }} className="space-y-2 max-h-[70vh] overflow-y-auto">
                        {Object.entries(editData)
                            .filter(([key]) => {
                                const hiddenFields = ['lastedUpdate', 'orderDate', 'shippedDate'];
                                return !hiddenFields.includes(key) && !key.toLowerCase().includes('id');
                            })
                            .map(([key]) => {
                                const inputType = getInputType(key);
                                return (
                                    <div key={key}>
                                        <label className="block text-xs font-medium text-blue-600 mb-1">
                                            {getColumnDisplayName(key)}
                                        </label>
                                        {inputType === 'select' ? (
                                            <select
                                                name={key}
                                                value={editData[key] ?? ''}
                                                onChange={handleEditChange}
                                                className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                                            >
                                                <option value="">Chọn {getColumnDisplayName(key)}</option>
                                                {getSelectOptions(key).map(option => (
                                                    <option key={option} value={option}>{option}</option>
                                                ))}
                                            </select>
                                        ) : (
                                            <input
                                                name={key}
                                                type={inputType}
                                                value={editData[key] ?? ''}
                                                onChange={handleEditChange}
                                                className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                                                min={inputType === 'number' ? 0 : undefined}
                                                step={inputType === 'number' ? 'any' : undefined}
                                            />
                                        )}
                                    </div>
                                );
                            })}
                        <button type="submit" className="w-full bg-indigo-600 text-white py-1.5 rounded text-sm">
                            Lưu thay đổi
                        </button>
                    </form>
                </div>
            </div>
        );
    }

    const getTableConfig = (relationType) => {
        const configs = {
            // 1. Cấu hình cho bảng Supplies (khi bấm vào Vendor)
            'supplies': {
                columns: [
                    { key: 'productID', label: 'Mã sản phẩm', className: 'text-black' },
                    { key: 'quantitySupplier', label: 'SL Cung cấp', className: 'text-black', formatter: formatCurrency },
                    { key: 'supplyDate', label: 'Ngày cung cấp', className: 'text-black', formatter: (v) => v ? new Date(v).toLocaleDateString('vi-VN') : '' },
                    { key: 'handledBy', label: 'Người phụ trách', className: 'text-black' }
                ],
                emptyMessage: 'Nhà cung cấp này chưa cung cấp sản phẩm nào'
            },

            // 2. Cấu hình cho bảng Requests (khi bấm vào Order)
            'request': { // Lưu ý: modalType bên App truyền sang là 'request' (số ít)
                columns: [
                    { key: 'orderID', label: 'Mã đơn', className: 'text-black' },
                    { key: 'productID', label: 'Mã sản phẩm', className: 'text-black' },
                    { key: 'quantityOrdered', label: 'Số lượng Đặt', className: 'text-black', formatter: formatCurrency },
                    { key: 'discount', label: 'Giảm giá', className: 'text-black' },
                    { key: 'note', label: 'Ghi chú', className: 'text-black' }
                ],
                emptyMessage: 'Đơn hàng này chưa có yêu cầu chi tiết'
            },

            // 3. Cấu hình cho bảng Stores (khi bấm vào Inventory)
            'stores': {
                columns: [
                    { key: 'productID', label: 'Mã sản phẩm', className: 'text-black' },
                    { key: 'quantityStore', label: 'Số lượng', className: 'text-black', formatter: formatCurrency },
                    { key: 'storeDate', label: 'Ngày nhập kho', className: 'text-black', formatter: (v) => v ? new Date(v).toLocaleDateString('vi-VN') : '' },
                    { key: 'roleStore', label: 'Loại giao dịch', className: 'text-black' }
                ],
                emptyMessage: 'Kho này chưa có lịch sử lưu trữ'
            },
            
        };
        return configs[relationType];
    };

    const renderGenericTable = () => {
        const config = getTableConfig(type);
        if (!config) return <div className="text-center text-gray-500 py-8">Không có dữ liệu</div>;

        return (
            <>
                {data.length > 0 ? (
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50 sticky top-0">
                                <tr>
                                    {config.columns.map((col) => (
                                        <th key={col.key} className={`px-3 py-2 text-left text-xs font-medium tracking-wider ${col.className.replace('text-black', 'text-gray-500')}`}>
                                            {col.label}
                                        </th>
                                    ))}
                                    {config.extraColumn && (
                                        <th className={`px-3 py-2 text-left text-xs font-medium tracking-wider ${config.extraColumn.className || 'text-gray-500'}`}>
                                            {config.extraColumn.label}
                                        </th>
                                    )}
                                    <th className="px-3 py-2 text-left text-xs font-medium tracking-wider text-gray-500">Hành động</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {data.map((item, index) => (
                                    <tr key={index} className="hover:bg-gray-50">
                                        {config.columns.map((col) => (
                                            <td key={col.key} className={`px-3 py-2 whitespace-nowrap text-xs ${col.className}`}>
                                                {col.formatter ? col.formatter(item[col.key]) : item[col.key]}
                                            </td>
                                        ))}
                                        {config.extraColumn && (() => {
                                            const extraData = config.extraColumn.calculate(item);
                                            return (
                                                <td className={`px-3 py-2 whitespace-nowrap text-xs ${extraData.className || 'text-gray-900'}`}>
                                                    {extraData.display}
                                                </td>
                                            );
                                        })()}
                                        <td className="px-3 py-1 whitespace-nowrap text-xs text-gray-900">
                                            <ActionButtons
                                                onEdit={() => onEdit(item)}
                                                onDelete={() => onDelete(item)}
                                                activeTab={activeTab}
                                            />
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div className="text-center text-gray-500 py-8">{config.emptyMessage}</div>
                )}
            </>
        );
    };


    const modalSize = type === 'order-details' ? 'w-full max-w-6xl' : 'w-full max-w-4xl';

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-2 z-50">
            <div className={`bg-white rounded p-4 ${modalSize} shadow-xl relative max-h-[90vh] overflow-hidden flex flex-col`}>
                <button onClick={onClose} className="absolute top-2 right-2 text-black hover:text-black z-10 bg-white p-2">
                    <X className="w-5 h-5" />
                </button>
                <h2 className="text-lg font-bold text-indigo-700 mb-3">{getTitle()}</h2>

                <div className="flex-1 overflow-auto">
                    {renderGenericTable()}
                </div>
            </div>
        </div>
    );
};

const FormModal = ({ data, onSave, onCancel, mode = 'edit' }) => {
    const [formData, setFormData] = useState(data || {});

    const handleChange = (e) => {
        const { name, value, type } = e.target;
        let processedValue = value;

        // Handle special input types
        if (type === 'number') {
            processedValue = value === '' ? null : Number(value);
        }

        setFormData({ ...formData, [name]: processedValue });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        onSave(formData);
    };

    const title = mode === 'edit' ? 'Chỉnh sửa thông tin' : 'Thêm mới';

    const getInputType = (key) => {
        // Determine input type based on field name
        const k = key.toLowerCase();
        if (k === 'password') return 'password';
        if (k.includes('email')) return 'email';
        if (k.includes('phone')) return 'tel';
        if (k.includes('date')) return 'date';
        if (k.includes('point') || k.includes('quantity') || k.includes('warranty')) return 'number';
        if (k.includes('price') || k.includes('amount') || k.includes('cost') || k.includes('salary')) return 'number';
        if (k.toLowerCase().endsWith('id')) return 'number';
        if (k === 'position') return 'select';
        if (k.includes('status') || k.includes('method') || k.includes('type')) return 'select';
        return 'text';
    };

    const getSelectOptions = (key) => {
        const options = {
            orderStatus: ['Pending', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled'],
            pickupMethod: ['Ship', 'StorePickup'],
            shippedStatus: ['Shipped', 'Cancelled', 'On Hold', 'In Process'],
            paymentStatus: ['Unpaid', 'Partial', 'Paid', 'Refunded'],
            paymentMethod: ['Cash', 'Credit Card', 'Bank Transfer', 'E-Wallet', 'Check'],
            customerType: ['Individual', 'Corporate', 'Partner', 'Reseller'],
            loyalLevel: ['New', 'Bronze', 'Silver', 'Gold', 'Platinum'],
            inventoryStatus: ['Active', 'Inactive', 'Low Stock', 'Out of Stock'],
            roleStore: ['Import', 'Export', 'Stocktaking', 'Manual', 'Initial', 'Update'],
            vendorStatus: ['Active', 'Inactive', 'Pending', 'Blacklisted'],
            transactionStatus: ['Pending', 'Completed', 'Failed', 'Refunded']
        };
        // special-case: position selection for staff accounts
        if (key === 'position') return ['Manager', 'Sales', 'Inventory',];
        return options[key] || [];
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-2 z-50">
            <div className="bg-white rounded p-4 w-full max-w-md shadow-xl relative">
                <button onClick={onCancel} className="absolute top-2 right-2 text-gray-400 hover:text-red-600">
                    <X className="w-4 h-4" />
                </button>
                <h2 className="text-lg font-bold text-indigo-700 mb-3 ">{title}</h2>
                <form onSubmit={handleSubmit} className="space-y-2 max-h-[70vh] overflow-y-auto">
                    {Object.entries(mode === 'edit' ? formData : data)
                        .filter(([key]) => {
                            const hiddenFields = ['lastedUpdate', 'orderDate', 'shippedDate', 'paymentDate'];
                            return !hiddenFields.includes(key);
                        })
                        .map(([key]) => {
                            const inputType = getInputType(key);
                            return (
                                <div key={key}>
                                    <label className="block text-xs font-medium text-blue-600 mb-1 ">
                                        {getColumnDisplayName(key)}
                                    </label>
                                    {inputType === 'select' ? (
                                        <select
                                            name={key}
                                            value={formData[key] ?? ''}
                                            onChange={handleChange}
                                            className="w-full border border-gray-300 rounded px-2 py-1 text-sm "
                                        >
                                            <option value="">Chọn {getColumnDisplayName(key)}</option>
                                            {getSelectOptions(key).map(option => (
                                                <option key={option} value={option}>{option}</option>
                                            ))}
                                        </select>

                                    ) : (
                                        <input
                                            name={key}
                                            type={inputType}
                                            value={formData[key] ?? ''}
                                            onChange={handleChange}
                                            className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                                            min={inputType === 'number' ? 0 : undefined}
                                            step={inputType === 'number' ? 'any' : undefined}
                                        />
                                    )}
                                </div>
                            );
                        })}
                    <button type="submit" className="w-full bg-indigo-600 text-white py-1.5 rounded text-sm">
                        {mode === 'edit' ? 'Lưu thay đổi' : 'Thêm mới'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default function App() {
    const [user, setUser] = useState(null);
    const [activeTab, setActiveTab] = useState('customers');
    const [data, setData] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const [modalMode, setModalMode] = useState('edit');
    const [selectedItem, setSelectedItem] = useState(null);
    const [selectedRows, setSelectedRows] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterCategory, setFilterCategory] = useState('');
    const [filterStatus, setFilterStatus] = useState('');

    const [showRelationsModal, setShowRelationsModal] = useState(false);
    const [relationsType, setRelationsType] = useState('');
    const [relationsData, setRelationsData] = useState([]);

    // --- NEW: State để lưu chính xác loại Resource đang thao tác ---
    const [currentResourceType, setCurrentResourceType] = useState('');

    const RESOURCE_CONFIG = {
        // ... Các bảng cũ giữ nguyên ...
        customers: { endpoint: '/customers', idKey: 'customerID' },
        products: { endpoint: '/products', idKey: 'productID' },
        orders: { endpoint: '/orders', idKey: 'orderID' },
        staffs: { endpoint: '/staffs', idKey: 'staffID' },
        inventories: { endpoint: '/inventories', idKey: 'inventoryID' },
        payments: { endpoint: '/payments', idKey: 'paymentID' },
        vendors: { endpoint: '/vendors', idKey: 'vendorID' },

        // --- SỬA LẠI ĐOẠN NÀY ---
        // Đổi 'idKeys' thành 'idKey'
        supplies: { endpoint: '/supplies', idKey: 'productID' },
        requests: { endpoint: '/requests', idKey: 'productID' },
        stores: { endpoint: '/stores', idKey: 'productID' },
    };

    const handleLogin = useCallback((userData) => {
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
        setActiveTab('customers');
    }, []);

    const handleLogout = useCallback(() => {
        setUser(null);
        localStorage.removeItem('user');
        setActiveTab('customers');
    }, []);

    useEffect(() => {
        const savedUser = localStorage.getItem('user');
        if (savedUser) {
            try {
                const userData = JSON.parse(savedUser);
                setUser(userData);
            } catch (err) {
                console.error('Error parsing user data:', err);
                localStorage.removeItem('user');
            }
        }
    }, []);


    const fetchData = useCallback(async (tabKey, search = '', category = '', status = '') => {
        if (!user || !tabKey) return;
        const tabInfo = TABS[tabKey];
        if (!tabInfo) return;

        setIsLoading(true);
        setError(null);

        try {
            const permissions = POSITION_PERMISSIONS[user.position]?.[tabKey];
            if (!permissions || !permissions.includes('view')) {
                throw new Error('Bạn không có quyền truy cập mục này');
            }

            const params = new URLSearchParams();
            if (search) params.append('search', search);
            if (category && tabKey === 'products') params.append('category', category);
            if (status && tabKey === 'orders') params.append('status', status);

            const url = `${API_BASE_URL}${tabInfo.endpoint}${params.toString() ? '?' + params.toString() : ''}`;

            const response = await fetch(url, {
                headers: { 'Authorization': `Bearer ${user.token}` },
            });

            if (!response.ok) {
                if (response.status === 401) {
                    handleLogout();
                    throw new Error('Phiên đăng nhập đã hết hạn');
                }
                throw new Error('Lỗi tải dữ liệu');
            }

            const result = await response.json();
            setData(result);
        } catch (err) {
            setError(err.message);
            if (err.message === 'Phiên đăng nhập đã hết hạn') handleLogout();
        } finally {
            setIsLoading(false);
        }
    }, [user, handleLogout]);

    useEffect(() => {
        if (user && activeTab && activeTab !== 'reports') {
            fetchData(activeTab, searchTerm, filterCategory, filterStatus);
        }
    }, [activeTab, fetchData, user, searchTerm, filterCategory, filterStatus]);

    useEffect(() => {
        setSearchTerm('');
        setFilterCategory('');
        setFilterStatus('');
    }, [activeTab]);

    const getDefaultSchema = (tabKey) => {
        // ... (Giữ nguyên logic getDefaultSchema cũ của bạn) ...
        const schemas = {
            customers: { customerID: '', customerName: '', customerType: 'Individual', phone: '', email: '', address: '', postalCode: '', loyalLevel: 'New', loyalPoint: 0 },
            products: { productID: '', productName: '', price: '', productLine: '', productScale: '', productBrand: '', productDescription: '' },
            payments: { paymentID: '', orderID: '', paymentDate: new Date().toISOString().split('T')[0], paymentAmount: '', paymentMethod: '', paymentStatus: 'Pending', transactionID: '', customerID: '', note: '' },
            orders: { orderID: '', orderDate: new Date().toISOString().split('T')[0], totalAmount: '', orderStatus: 'Pending', paymentStatus: 'Unpaid', pickupMethod: '', customerID: '', staffID: '' },
            staffs: { staffID: '', staffName: '', position: '', password: '', phone: '', email: '', address: '', managerID: '', salary: '' },
            inventories: { inventoryID: '', warehouse: '', productID: '', maxStockLevel: '', stockQuantity: '', unitCost: '', inventoryNote: '', inventoryStatus: 'Active' },
            vendors: { vendorID: '', vendorName: '', contactName: '', phone: '', email: '', address: '', vendorType: '', paymentTerms: '', vendorStatus: 'Active' }
        };
        return schemas[tabKey] || {};
    };

    // --- UPDATE: handleCreate (Thêm logic set Resource Type) ---
    const handleCreate = () => {
        const permissions = POSITION_PERMISSIONS[user.position]?.[activeTab];
        if (!permissions || !permissions.includes('create')) {
            alert('Bạn không có quyền thêm mới dữ liệu');
            return;
        }

        const schema = data.length > 0 ?
            Object.keys(data[0]).reduce((acc, key) => ({ ...acc, [key]: '' }), {}) :
            getDefaultSchema(activeTab);

        setSelectedItem(schema);
        setModalMode('create');

        // QUAN TRỌNG: Đang tạo mới cho Tab nào thì set type là Tab đó
        setCurrentResourceType(activeTab);

        setShowModal(true);
    };

    // --- UPDATE: handleItemEdit (Thêm logic set Resource Type) ---
    const handleItemEdit = useCallback((item) => {
        setSelectedItem(item);
        setModalMode('edit');

        // QUAN TRỌNG: Đang sửa item của Tab nào thì set type là Tab đó
        setCurrentResourceType(activeTab);

        setShowModal(true);
    }, [activeTab]);

    // --- UPDATE: handleRowClick (Logic quan trọng nhất) ---
    const handleRowClick = async (item) => {
        setSelectedItem(item);

        const RELATION_CONFIG = {
            orders: {
                getEndpoint: (row) => `/requests/${row.orderID}`,
                resourceName: 'requests',
                modalType: 'request'
            },
            vendors: {
                getEndpoint: (row) => `/supplies/${row.vendorID}`,
                resourceName: 'supplies',
                modalType: 'supplies'
            },
            inventories: { // Lưu ý tên tab là 'inventory' hay 'inventories' trong code của bạn
                getEndpoint: (row) => `/stores/${row.inventoryID}`,
                resourceName: 'stores',
                modalType: 'stores'
            },
            // Map thêm key 'inventory' nếu activeTab của bạn là số ít
            
        };

        const config = RELATION_CONFIG[activeTab];

        if (config) {
            try {
                // QUAN TRỌNG: Đánh dấu là đang làm việc với BẢNG CON
                setCurrentResourceType(config.resourceName);

                const endpoint = `${API_BASE_URL}${config.getEndpoint(item)}`;
                const response = await fetch(endpoint);

                if (!response.ok) throw new Error('Lỗi tải dữ liệu chi tiết');

                const childData = await response.json();

                // Gắn thêm _resource để dự phòng, nhưng logic chính sẽ dùng currentResourceType
                setRelationsData(childData.map(d => ({ ...d, _resource: config.resourceName })));
                setRelationsType(config.modalType);
                setShowRelationsModal(true);

            } catch (err) {
                console.error(`Error loading details for ${activeTab}:`, err);

                // Nếu lỗi API con, fallback về sửa bảng CHA
                setCurrentResourceType(activeTab);
                setModalMode('edit');
                setShowModal(true);
            }
        }
        else {
            // Không phải bảng có quan hệ -> Sửa bảng CHA
            setCurrentResourceType(activeTab);
            setModalMode('edit');
            setShowModal(true);
        }
    };

    const handleSave = async (formData) => {
        console.log("DEBUG handleSave - Config Type:", currentResourceType || activeTab);

        try {
            // 1. Kiểm tra quyền hạn
            const permissions = POSITION_PERMISSIONS[user.position]?.[activeTab];
            const action = modalMode === 'edit' ? 'edit' : 'create';
            if (!permissions || !permissions.includes(action)) {
                throw new Error(`Bạn không có quyền ${action === 'edit' ? 'chỉnh sửa' : 'thêm mới'} dữ liệu`);
            }

            // 2. Lấy cấu hình
            const typeKey = currentResourceType || activeTab;
            const config = RESOURCE_CONFIG[typeKey];

            if (!config) {
                throw new Error(`Lỗi cấu hình: Không tìm thấy config cho resource "${typeKey}"`);
            }

            // --- XỬ LÝ DỮ LIỆU (FIX LỖI 422) ---
            // Tạo bản sao để xử lý dữ liệu trước khi gửi
            const payload = { ...formData };

            // Tự động chuyển đổi các trường số sang Number để Backend không báo lỗi 422
            Object.keys(payload).forEach(key => {
                const k = key.toLowerCase();
                // Danh sách các từ khóa thường là số
                if (k.includes('id') || k.includes('price') || k.includes('cost') || k.includes('amount') || k.includes('quantity') || k.includes('stock') || k.includes('point')) {
                    if (payload[key] !== '' && payload[key] !== null) {
                        payload[key] = Number(payload[key]);
                    }
                }
            });

            // 3. Tạo Endpoint
            const isEdit = modalMode === 'edit';
            let endpoint = `${API_BASE_URL}${config.endpoint}`;

            if (isEdit) {
                // Ưu tiên 1: Dùng idKey (Single Key) -> Tạo URL dạng /resource/ID
                if (config.idKey) {
                    // Tìm key ID trong payload (bất kể hoa thường)
                    const actualIdKey = Object.keys(payload).find(k => k.toLowerCase() === config.idKey.toLowerCase());
                    const recordID = actualIdKey ? payload[actualIdKey] : null;

                    if (recordID) {
                        endpoint += `/${recordID}`;
                    } else {
                        console.error(`LỖI: Không tìm thấy ID (${config.idKey}) trong dữ liệu form.`);
                    }
                }
                // Ưu tiên 2: Dùng idKeys (Composite Key) -> Tạo URL dạng /resource?key=val
                else if (config.idKeys && Array.isArray(config.idKeys)) {
                    const params = new URLSearchParams();
                    config.idKeys.forEach(key => {
                        const actualKey = Object.keys(payload).find(k => k.toLowerCase() === key.toLowerCase());
                        if (actualKey && payload[actualKey]) params.append(key, payload[actualKey]);
                    });
                    if (params.toString()) endpoint += `?${params.toString()}`;
                }
            }

            console.log(`🚀 Sending ${isEdit ? 'PUT' : 'POST'} to: ${endpoint}`, payload);

            // 4. Gọi API
            const response = await fetch(endpoint, {
                method: isEdit ? 'PUT' : 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${user.token}`,
                },
                body: JSON.stringify(payload) // Gửi payload đã xử lý số liệu
            });

            if (!response.ok) {
                const errorText = await response.text();
                // Thử parse JSON lỗi nếu có để hiển thị đẹp hơn
                try {
                    const errJson = JSON.parse(errorText);
                    // Nếu lỗi là thiếu trường (ví dụ "Field required: note"), báo rõ ràng
                    if (errJson.detail && Array.isArray(errJson.detail)) {
                        const missingFields = errJson.detail.map(e => e.loc[1]).join(', ');
                        throw new Error(`Dữ liệu không hợp lệ: Kiểm tra trường [${missingFields}]`);
                    }
                    throw new Error(errJson.detail || errJson.message || `Lỗi ${response.status}`);
                } catch (err) {
                    console.error('Error parsing error response JSON:', err);
                    throw new Error(`Lỗi ${response.status}: ${errorText} `);
                }
            }

            setShowModal(false);
            fetchData(activeTab);
            alert("Lưu dữ liệu thành công!");

        } catch (err) {
            console.error(err);
            alert("Thất bại: " + err.message);
        }
    };

    const handleItemDelete = useCallback(async (item) => {
        const permissions = POSITION_PERMISSIONS[user.position]?.[activeTab];
        if (!permissions || !permissions.includes('delete')) {
            alert('Bạn không có quyền xóa dữ liệu');
            return;
        }

        const columns = Object.keys(item);
        const idKey = columns.find((c) => c.toLowerCase().endsWith("id")) || columns[0];
        const id = item[idKey];

        if (!window.confirm('Bạn có chắc muốn xóa bản ghi này?')) return;

        try {
            const endpoint = `${API_BASE_URL}${TABS[activeTab].endpoint}/${id}`;
            await fetch(endpoint, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${user.token}` },
            });
            fetchData(activeTab);
        } catch (err) {
            alert('Lỗi khi xóa: ' + err.message);
        }
    }, [user, activeTab, fetchData]);

    const handleDeleteSelected = async () => {
        const permissions = POSITION_PERMISSIONS[user.position]?.[activeTab];
        if (!permissions || !permissions.includes('delete')) {
            alert('Bạn không có quyền xóa dữ liệu');
            return;
        }

        if (selectedRows.length === 0) return;
        if (!window.confirm(`Bạn có chắc muốn xóa ${selectedRows.length} bản ghi?`)) return;

        try {
            for (const id of selectedRows) {
                const endpoint = `${API_BASE_URL}${TABS[activeTab].endpoint}/${id}`;
                await fetch(endpoint, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${user.token}` },
                });
            }
            setSelectedRows([]);
            fetchData(activeTab);
        } catch (err) {
            alert('Lỗi khi xóa: ' + err.message);
        }
    };

    if (!user) {
        return <LoginPage onLogin={handleLogin} />;
    }

    return (
        <div className="flex flex-col h-screen bg-gray-50 font-sans">
            <header className="bg-indigo-700 shadow-md p-2 text-white flex items-center justify-between h-12 flex-shrink-0">
                <h1 className="text-base font-extrabold tracking-tight md:text-lg">Hệ thống Quản lý Cửa hàng</h1>
                <div className="flex items-center space-x-4">
                    <span className="text-sm">
                        {user.staffName} ({user.position})
                    </span>
                    <button
                        onClick={handleLogout}
                        className="text-sm bg-indigo-800 px-2 py-1 rounded hover:bg-indigo-900"
                    >
                        Đăng xuất
                    </button>
                </div>
            </header>

            <div className="flex flex-1 overflow-hidden">
                <nav className="bg-white shadow-lg w-48 h-full p-2 md:p-3 overflow-y-auto flex-shrink-0">
                    <div className="flex flex-col space-y-1">
                        {Object.entries(TABS).map(([key, { label, icon }]) => (
                            <button key={key} onClick={() => setActiveTab(key)}
                                className={`flex items-center space-x-2 px-2 py-1.5 rounded text-sm font-medium transition duration-200 ${activeTab === key ? 'bg-indigo-100 text-indigo-700 shadow-inner' : 'bg-white text-gray-700 hover:bg-gray-100 hover:text-indigo-700'}`}>
                                {React.createElement(icon, { className: `w-4 h-4 ${activeTab === key ? 'text-indigo-600' : 'text-gray-500'}` })}
                                <span className="whitespace-nowrap">{label}</span>
                            </button>
                        ))}
                    </div>
                </nav>

                <main className="flex-1 bg-gray-50 p-3 overflow-auto">
                    {activeTab === 'reports' ? (
                        <ReportsPage />
                    ) : (
                        <div className="w-full h-full flex flex-col">
                            <div className="flex justify-between items-center mb-3 flex-shrink-0">
                                <h2 className="text-lg font-semibold text-gray-800 flex items-center space-x-2">
                                    {TABS[activeTab]?.icon && React.createElement(TABS[activeTab].icon, { className: 'w-5 h-5 text-indigo-600' })}
                                    <span>Quản lý {TABS[activeTab]?.label}</span>
                                </h2>
                                {activeTab !== 'reports' && (
                                    <div className="flex space-x-2">
                                        {selectedRows.length > 0 && (
                                            <button
                                                onClick={handleDeleteSelected}
                                                className="flex items-center bg-red-500 text-white px-2 py-1 rounded shadow-md hover:bg-red-600 transition duration-150 text-sm"
                                            >
                                                Xóa {selectedRows.length > 1 ? 'đã chọn' : 'mục này'}
                                            </button>
                                        )}
                                        <button
                                            onClick={handleCreate}
                                            className="flex items-center bg-green-500 text-white px-2 py-1 rounded shadow-md hover:bg-green-600 transition duration-150 text-sm"
                                        >
                                            <Plus className="w-4 h-4 mr-1" />
                                            Thêm {TABS[activeTab]?.label}
                                        </button>
                                    </div>
                                )}
                            </div>

                            {/* Search and Filters */}
                            <div className="mb-3 flex flex-wrap gap-2">
                                <div className="flex-1 min-w-[200px] ">
                                    <div className="relative">
                                        <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                                        <input
                                            type="text"
                                            placeholder="Tìm kiếm..."
                                            value={searchTerm}
                                            onChange={(e) => setSearchTerm(e.target.value)}
                                            className="w pl-8 pr-3 py-2 border border-blue-900   rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-200 text-black"
                                        />
                                    </div>
                                </div>
                                {activeTab === 'products' && (
                                    <select
                                        value={filterCategory}
                                        onChange={(e) => setFilterCategory(e.target.value)}
                                        className="px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                    >
                                        <option value="">Tất cả danh mục</option>
                                        <option value="CPU">CPU</option>
                                        <option value="GPU">GPU</option>
                                        <option value="RAM">RAM</option>
                                        <option value="Mainboard">Mainboard</option>
                                        <option value="Storage">Storage</option>
                                        <option value="PSU">PSU</option>
                                        <option value="Case">Case</option>
                                        <option value="Cooling">Cooling</option>
                                        <option value="Monitor">Monitor</option>
                                        <option value="Mouse">Mouse</option>
                                        <option value="Keyboard">Keyboard</option>
                                        <option value="Headset">Headset</option>
                                        <option value="Speaker">Speaker</option>
                                        <option value="Accessory">Accessory</option>


                                    </select>
                                )}
                                {activeTab === 'orders' && (
                                    <select
                                        value={filterStatus}
                                        onChange={(e) => setFilterStatus(e.target.value)}
                                        className="px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                    >
                                        <option value="">Tất cả trạng thái</option>
                                        <option value="Pending">Pending</option>
                                        <option value="Confirmed">Confirmed</option>
                                        <option value="Shipped">Shipped</option>
                                        <option value="Delivered">Delivered</option>
                                        <option value="Cancelled">Cancelled</option>
                                    </select>
                                )}
                            </div>

                            <div className="flex-1 overflow-auto">
                                {isLoading && <LoadingSpinner />}
                                {error && <div className="text-red-600 p-4 bg-red-50 rounded">{error}</div>}
                                {!isLoading && !error && (
                                    <DataTable
                                        data={data}
                                        onRowClick={handleRowClick}
                                        selectedRows={selectedRows}
                                        onSelectRow={setSelectedRows}
                                        onItemEdit={handleItemEdit}
                                        onItemDelete={handleItemDelete}
                                        activeTab={activeTab}
                                    />
                                )}
                            </div>
                        </div>
                    )}
                </main>
            </div>

            {showModal && selectedItem && (
                <FormModal
                    data={selectedItem}
                    onSave={handleSave}
                    onCancel={() => setShowModal(false)}
                    mode={modalMode}
                />
            )}

            {showRelationsModal && (
                <RelationsModal
                    data={relationsData}
                    type={relationsType}
                    onClose={() => {
                        setShowRelationsModal(false);
                        setRelationsData([]);
                        setRelationsType('');
                    }}
                    onEdit={(item) => {
                        setSelectedItem(item);
                        setModalMode('edit');
                        setShowModal(true);
                        setShowRelationsModal(false);
                    }}
                    onDelete={handleItemDelete}
                    activeTab={activeTab}
                    selectedItem={selectedItem}
                    user={user}
                    refreshData={() => fetchData(activeTab)}
                />
            )}
        </div>
    );
}
