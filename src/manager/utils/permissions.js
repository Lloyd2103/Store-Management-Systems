// Định nghĩa các vị trí nhân viên
export const STAFF_POSITIONS = {
    ADMIN: 'Admin',
    MANAGER: 'Manager',
    SALES: 'Sales',
    INVENTORY: 'Inventory',
    CASHIER: 'Cashier'
};

export const POSITION_PERMISSIONS = {
    Admin: {
        customers: ['view', 'create', 'edit', 'delete'],
        products: ['view', 'create', 'edit', 'delete'],
        orders: ['view', 'create', 'edit', 'delete'],
        payments: ['view', 'create', 'edit', 'delete'],
        staffs: ['view', 'create', 'edit', 'delete'],
        vendors: ['view', 'create', 'edit', 'delete'],
        inventories: ['view', 'create', 'edit', 'delete'],
        reports: ['view']
    },
    Manager: {
        customers: ['view', 'create', 'edit', 'delete'],
        products: ['view', 'create', 'edit', 'delete'],
        orders: ['view', 'create', 'edit', 'delete'],
        payments: ['view', 'create', 'edit', 'delete'],
        staffs: ['view', 'create', 'edit', 'delete'],
        vendors: ['view', 'create', 'edit', 'delete'],
        inventories: ['view', 'create', 'edit', 'delete'],
        reports: ['view']
    },
    Sales: {
        customers: ['view', 'create', 'edit'],
        products: ['view'],
        orders: ['view', 'create'],
        payments: ['view', 'create'],
        staffs: ['view'],
        vendors: ['view'],
        inventories: ['view']
    },
    Inventory: {
        products: ['view', 'edit'],
        orders: ['view'],
        vendors: ['view'],
        inventories: ['view', 'create', 'edit']
    },
    Cashier: {
        customers: ['view'],
        orders: ['view'],
        payments: ['view', 'create', 'edit'],
        products: ['view']
    }
};

export const checkPermission = (position, module, action) => {
    if (!position || !POSITION_PERMISSIONS[position]) return false;
    if (!POSITION_PERMISSIONS[position][module]) return false;
    return POSITION_PERMISSIONS[position][module].includes(action);
};