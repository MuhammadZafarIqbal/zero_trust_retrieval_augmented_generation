import React, { useState } from 'react';
import { useMsal } from '@azure/msal-react';
import { useNavigate } from 'react-router-dom';
import { loginRequest } from './authConfig';

function Home() {
    const { instance, accounts } = useMsal();
    const activeAccount = accounts[0];
    const navigate = useNavigate();

    const [role, setRole] = useState('Public');

    const handleLogin = () => {
        if (accounts.length === 0) {
            instance.loginPopup(loginRequest)
                .then(() => {
                    // Login successful, navigate to QueryForm page
                    navigate('/query', { state: { role } });
                }).catch(e => console.error(e));
        } else {
            console.log('User already logged in:', accounts[0]);
            navigate('/query', { state: { role } });
        }
    };

    const handleLogout = () => {
        instance.logoutPopup();
    };

    const handleRoleChange = (e) => {
        setRole(e.target.value);
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
            <div className="bg-white shadow-lg rounded-2xl p-8 w-full max-w-md space-y-6">
                {/* Branding */}
                <div className="flex justify-center items-center gap-4 mb-2">
                    <img src="/Logo_of_the_Technical_University_of_Munich.svg" alt="TUM" className="h-10" />
                    <img src="/trusteq-light.01680954.svg" alt="TrustEQ" className="h-10" />
                </div>

                {/* Title */}
                <h1 className="text-2xl font-semibold text-center text-gray-800">
                    Zero Trust AI Security Portal
                </h1>
                <p className="text-center text-gray-500 text-sm">
                    Collaboration between TUM & TrustEQ
                </p>

                {/* Auth Area */}
                {!activeAccount ? (
                    <>
                        <div>
                            <label htmlFor="role-select" className="block text-sm font-medium text-gray-700 mb-1">
                                Select Role
                            </label>
                            <select
                                id="role-select"
                                value={role}
                                onChange={handleRoleChange}
                                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="Public">Public</option>
                                <option value="Employee">Employee</option>
                                <option value="Admin">Admin</option>
                            </select>
                        </div>
                        <button
                            onClick={handleLogin}
                            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition"
                        >
                            Login with Microsoft
                        </button>
                    </>
                ) : (
                    <>
                        <div className="text-center space-y-1">
                            <p className="text-lg font-medium text-gray-700">
                                Welcome, {activeAccount.name}
                            </p>
                            <p className="text-sm text-gray-500">Role: {role}</p>
                        </div>

                        <div>
                            <label htmlFor="role-select" className="block text-sm font-medium text-gray-700 mb-1">
                                Change Role
                            </label>
                            <select
                                id="role-select"
                                value={role}
                                onChange={handleRoleChange}
                                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="Public">Public</option>
                                <option value="Employee">Employee</option>
                                <option value="Admin">Admin</option>
                            </select>
                        </div>

                        <div className="flex gap-3">
                            <button
                                onClick={handleLogout}
                                className="w-1/2 bg-gray-200 text-gray-800 py-2 px-4 rounded-md hover:bg-gray-300 transition"
                            >
                                Logout
                            </button>
                            <button
                                onClick={() => navigate('/query', { state: { role } })}
                                className="w-1/2 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition"
                            >
                                Go to Query
                            </button>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}

export default Home;