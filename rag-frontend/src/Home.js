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
        <div>
            {!activeAccount ? (
                <>
                    <label htmlFor="role-select">Select Role: </label>
                    <select id="role-select" value={role} onChange={handleRoleChange}>
                        <option value="Public">Public</option>
                        <option value="Employee">Employee</option>
                        <option value="Admin">Admin</option>
                    </select>
                    <br />
                    <button onClick={handleLogin}>Login with Microsoft</button>
                </>
            ) : (
                <>
                    <p>Welcome, {activeAccount.name}</p>
                    <p>Selected Role: {role}</p>
                    <label htmlFor="role-select">Change Role: </label>
                    <select id="role-select" value={role} onChange={handleRoleChange}>
                        <option value="Public">Public</option>
                        <option value="Employee">Employee</option>
                        <option value="Admin">Admin</option>
                    </select>
                    <br />
                    <button onClick={handleLogout}>Logout</button>
                    <button onClick={() => navigate('/query', { state: { role } })}>
                        Go to Query Form
                    </button>
                </>
            )}
        </div>
    );
}

export default Home;