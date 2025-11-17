import React, { useState } from 'react';
import config from '../constants/config';

const LoginPage = ({ onLogin }) => {
    const [activeTab, setActiveTab] = useState('login'); // 'login' or 'register'
    const [credentials, setCredentials] = useState({
        identifier: '', // email or phone
        password: ''
    });
    const [registerData, setRegisterData] = useState({
        staffName: '',
        position: '',
        phone: '',
        email: '',
        address: '',
        managerID: '',
        salary: '',
        password: ''
    });
    const [error, setError] = useState('');

    const handleChange = (e) => {
        setCredentials({
            ...credentials,
            [e.target.name]: e.target.value
        });
    };

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            // Dev fallback: admin/admin
            if (credentials.identifier === 'admin' && credentials.password === 'admin') {
                const mockUser = {
                    staffID: 'ADMIN001',
                    staffName: 'Administrator',
                    position: 'Admin',
                    token: 'dev-token'
                };
                onLogin(mockUser);
                return;
            }

            // Call backend login for staff: send identifier and password
            const resp = await fetch(`${config.API_BASE_URL}${config.API_ENDPOINTS.LOGIN_STAFF}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ identifier: credentials.identifier, password: credentials.password })
            });

            if (!resp.ok) {
                const errJson = await resp.json().catch(() => ({}));
                throw new Error(errJson.detail || errJson.message || 'Sai email/số điện thoại hoặc mật khẩu');
            }

            const data = await resp.json();
            // Backend returns { message: 'Login successful', staff: { ... } }
            const staff = data.staff || data;
            // Pass staff object up to App; App will store it in localStorage
            onLogin(staff);
        } catch (err) {
            setError(err.message);
        }
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        try {
            // Prepare payload: convert empty strings for optional numeric fields to null/number
            const payload = {
                staffName: registerData.staffName || undefined,
                position: registerData.position || undefined,
                phone: registerData.phone || undefined,
                email: registerData.email || undefined,
                address: registerData.address || undefined,
                managerID: registerData.managerID === '' ? null : (registerData.managerID ?? null),
                salary: registerData.salary === '' ? null : (registerData.salary ? Number(registerData.salary) : null),
                password: registerData.password || undefined
            };

            const response = await fetch(`${config.API_BASE_URL}${config.API_ENDPOINTS.REGISTER_STAFF}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                // Try to parse JSON error body (FastAPI returns detailed validation errors for 422)
                let errBody = null;
                try {
                    errBody = await response.json();
                } catch (parseErr) {
                    // non-json response
                    console.warn('Could not parse error body', parseErr);
                }

                if (response.status === 422 && errBody && Array.isArray(errBody.detail)) {
                    // Collect readable messages from Pydantic validation errors
                    const msgs = errBody.detail.map(d => {
                        if (d.loc && d.msg) {
                            return `${d.loc.slice(1).join('.')} - ${d.msg}`;
                        }
                        return d.msg || JSON.stringify(d);
                    });
                    throw new Error(msgs.join('; '));
                }

                // Fallback: use detail/message if available
                const msg = (errBody && (errBody.detail || errBody.message)) || 'Đăng ký thất bại';
                throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
            }

            // Đăng ký thành công - chuyển về tab đăng nhập
            setActiveTab('login');
            setError('Đăng ký thành công! Vui lòng đăng nhập.');
        } catch (err) {
            console.error('Register error:', err);
            setError(err.message || 'Đăng ký thất bại');
        }
    };

    const handleRegisterChange = (e) => {
        const { name, value } = e.target;
        setRegisterData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
            <div className="sm:mx-auto sm:w-full sm:max-w-md">
                <div className="flex justify-center space-x-4 mb-6">
                    <button
                        onClick={() => { setActiveTab('login'); setError(''); }}
                        className={`px-4 py-2 font-medium rounded-t-lg ${activeTab === 'login'
                            ? 'bg-indigo-600 text-white'
                            : 'text-gray-500 hover:text-gray-700'
                            }`}
                    >
                        Đăng nhập
                    </button>
                    <button
                        onClick={() => { setActiveTab('register'); setError(''); }}
                        className={`px-4 py-2 font-medium rounded-t-lg ${activeTab === 'register'
                            ? 'bg-indigo-600 text-white'
                            : 'text-gray-500 hover:text-gray-700'
                            }`}
                    >
                        Đăng ký
                    </button>
                </div>
            </div>

            <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
                <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
                    {activeTab === 'login' ? (
                        <form className="space-y-6" onSubmit={handleLogin}>
                            <div>
                                <label htmlFor="identifier" className="block text-sm font-medium text-gray-700">
                                    Email hoặc Số điện thoại
                                </label>
                                <input
                                    id="identifier"
                                    name="identifier"
                                    type="text"
                                    required
                                    placeholder="email@example.com hoặc 0123456789"
                                    value={credentials.identifier}
                                    onChange={handleChange}
                                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                                />
                            </div>

                            <div>
                                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                                    Mật khẩu
                                </label>
                                <input
                                    id="password"
                                    name="password"
                                    type="password"
                                    required
                                    value={credentials.password}
                                    onChange={handleChange}
                                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                                />
                            </div>

                            {error && (
                                <div className="text-red-600 text-sm">
                                    {error}
                                </div>
                            )}

                            <button
                                type="submit"
                                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                            >
                                Đăng nhập
                            </button>
                        </form>
                    ) : (
                        <form className="space-y-6" onSubmit={handleRegister}>
                            <div>
                                <label htmlFor="staffName" className="block text-sm font-medium text-gray-700">
                                    Tên nhân viên
                                </label>
                                <input
                                    id="staffName"
                                    name="staffName"
                                    type="text"
                                    required
                                    value={registerData.staffName}
                                    onChange={handleRegisterChange}
                                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                                />
                            </div>

                            <div>
                                <label htmlFor="position" className="block text-sm font-medium text-gray-700">
                                    Chức vụ
                                </label>
                                <select
                                    id="position"
                                    name="position"
                                    required
                                    value={registerData.position}
                                    onChange={handleRegisterChange}
                                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                                >
                                    <option value="">Chọn chức vụ</option>
                                    <option value="Manager">Manager</option>
                                    <option value="Sales">Sales</option>
                                    <option value="Inventory">Inventory</option>
                                    <option value="Cashier">Cashier</option>
                                </select>
                            </div>

                            <div>
                                <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
                                    Số điện thoại
                                </label>
                                <input
                                    id="phone"
                                    name="phone"
                                    type="tel"
                                    required
                                    value={registerData.phone}
                                    onChange={handleRegisterChange}
                                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                                />
                            </div>

                            <div>
                                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                                    Email
                                </label>
                                <input
                                    id="email"
                                    name="email"
                                    type="email"
                                    required
                                    value={registerData.email}
                                    onChange={handleRegisterChange}
                                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                                />
                            </div>

                            <div>
                                <label htmlFor="address" className="block text-sm font-medium text-gray-700">
                                    Địa chỉ
                                </label>
                                <input
                                    id="address"
                                    name="address"
                                    type="text"
                                    required
                                    value={registerData.address}
                                    onChange={handleRegisterChange}
                                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                                />
                            </div>

                            <div>
                                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                                    Mật khẩu
                                </label>
                                <input
                                    id="password"
                                    name="password"
                                    type="password"
                                    required
                                    value={registerData.password}
                                    onChange={handleRegisterChange}
                                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                                />
                            </div>

                            {error && (
                                <div className={`text-sm ${error.includes('thành công') ? 'text-green-600' : 'text-red-600'}`}>
                                    {error}
                                </div>
                            )}

                            <button
                                type="submit"
                                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                            >
                                Đăng ký
                            </button>
                        </form>
                    )}
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
