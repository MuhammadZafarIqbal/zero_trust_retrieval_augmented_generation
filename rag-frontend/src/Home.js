import React from 'react';
import { useMsal } from '@azure/msal-react';
import QueryForm from './QueryForm';

function Home() {
    const { instance, accounts } = useMsal();
    const activeAccount = accounts[0];

    const handleLogin = () => {
        if (accounts.length === 0) {
            instance.loginPopup({
                scopes: ["user.read"]
            }).catch(e => console.error(e));
        } else {
            console.log('User already logged in:', accounts[0]);
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
                    <QueryForm user={activeAccount} />
                </>
            )}
        </div>
    );
}

export default Home;