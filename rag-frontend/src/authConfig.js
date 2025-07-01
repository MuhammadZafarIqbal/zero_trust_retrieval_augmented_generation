export const msalConfig = {
    auth: {
        clientId: "6e3a0f77-a606-43cd-83ab-6b9181b1222f",
        authority: "https://login.microsoftonline.com/trusteq.de",
        redirectUri: "http://localhost:3000",
    },
    cache: {
        cacheLocation: "localStorage",
        storeAuthStateInCookie: false,
    },
};
