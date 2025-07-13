import React from 'react';
import { useMsal } from '@azure/msal-react';
import { useNavigate } from 'react-router-dom';

function Home() {
    const { instance, accounts } = useMsal();
    const activeAccount = accounts[0];
    const navigate = useNavigate();

    const handleLogin = () => {
        if (accounts.length === 0) {
            instance.loginPopup({
                scopes: ["user.read"]
            }).then(() => {
                // Login successful, navigate to QueryForm page
                navigate('/query');
            }).catch(e => console.error(e));
        } else {
            console.log('User already logged in:', accounts[0]);
            navigate('/query');
        }
    };

    const handleLogout = () => {
        instance.logoutPopup();
    };

    return (
        <div>
            {!activeAccount ? (
                <button onClick={handleLogin}>Login with Microsoft</button>
            ) : (
                <>
                    <p>Welcome, {activeAccount.name}</p>
                    <button onClick={handleLogout}>Logout</button>
                    <button onClick={() => navigate('/query')}>Go to Query Form</button>
                </>
            )}
        </div>
    );
}

export default Home;