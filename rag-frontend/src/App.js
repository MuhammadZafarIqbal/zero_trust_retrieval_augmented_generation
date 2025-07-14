import React from 'react';
import { MsalProvider } from '@azure/msal-react';
import { PublicClientApplication } from '@azure/msal-browser';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate
} from 'react-router-dom';

import { msalConfig } from './authConfig';
import Home from './Home';
import QueryForm from './QueryForm';

const msalInstance = new PublicClientApplication(msalConfig);

function App() {
  return (
    <MsalProvider instance={msalInstance}>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/query" element={<QueryForm />} />
          {/* Fallback route */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Router>
    </MsalProvider>
  );
}

export default App;