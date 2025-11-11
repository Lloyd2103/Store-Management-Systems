// Định nghĩa các vị trí nhân viên
export const STAFF_POSITIONS = {
    ADMIN: 'Admin',
    MANAGER: 'Manager',
    SALES: 'Sales',
    INVENTORY: 'Inventory',
    CASHIER: 'Cashier'
};

// Định nghĩa quyền cho từng vị trí
export const POSITION_PERMISSIONS = {
    Admin: {
        customers: ['view', 'create', 'edit', 'delete'],
        products: ['view', 'create', 'edit', 'delete'],
        orders: ['view', 'create', 'edit', 'delete'],
        payments: ['view', 'create', 'edit', 'delete'],
        staff: ['view', 'create', 'edit', 'delete'],
        vendors: ['view', 'create', 'edit', 'delete'],
        inventory: ['view', 'create', 'edit', 'delete'],
        reports: ['view']
    },
    Manager: {
        customers: ['view', 'create', 'edit'],
        products: ['view', 'edit'],
        orders: ['view', 'create', 'edit'],
        payments: ['view'],
        staff: ['view'],
        vendors: ['view', 'create', 'edit'],
        inventory: ['view', 'edit'],
        reports: ['view']
    },
    Sales: {
        customers: ['view', 'create', 'edit'],
        products: ['view'],
        orders: ['view', 'create'],
        payments: ['view', 'create'],
        staff: ['view'],
        vendors: ['view'],
        inventory: ['view']
    },
    Inventory: {
        products: ['view', 'edit'],
        orders: ['view'],
        vendors: ['view'],
        inventory: ['view', 'create', 'edit']
    },
    Cashier: {
        customers: ['view'],
        orders: ['view'],
        payments: ['view', 'create', 'edit'],
        products: ['view']
    }
};

// Hàm kiểm tra quyền
export const checkPermission = (position, module, action) => {
    if (!position || !POSITION_PERMISSIONS[position]) return false;
    if (!POSITION_PERMISSIONS[position][module]) return false;
    return POSITION_PERMISSIONS[position][module].includes(action);
};