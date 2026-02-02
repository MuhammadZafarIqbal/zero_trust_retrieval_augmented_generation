import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { useMsal } from '@azure/msal-react';
import { useLocation } from 'react-router-dom';
import { loginRequest } from './authConfig';

function QueryForm() {
    const [question, setQuestion] = useState('');
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const chatEndRef = useRef(null);

    const { instance, accounts } = useMsal();
    const location = useLocation();
    const role = location.state?.role || 'Public'; // fallback to 'Public'

    const scrollToBottom = () => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const getTimestamp = () => {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    useEffect(() => {
        const welcomeMessage = {
            type: 'bot',
            text: "👋 Hello! Welcome to the HR Assistant Chatbot.\n"
                + "I'm here to help you quickly find answers to your HR-related questions, such as:\n\n"

                + "- 📄 Company policies and procedures\n"
                + "- 🧑‍💼 Employee benefits and compensation\n"
                + "- 🕒 Leave balances and time-off requests\n"
                + "- 🔒 Security and access policies\n"
                + "- 🗂️ Department and organizational details\n\n"

                + "Your queries are processed securely — we follow Zero Trust principles.\n\n"

                + "Feel free to ask me something like:\n"
                + "> What are the vacation policies and who is Alice Johnson's manager?\n"
                + "> What is the maternity leave policy?\n",
            timestamp: getTimestamp(),
        };
        setMessages([welcomeMessage]);
    }, []);

    const handleQuery = async (e) => {
        e.preventDefault();
        if (!question.trim()) return;

        const userMessage = {
            type: 'user',
            text: question,
            timestamp: getTimestamp(),
        };
        setMessages((prev) => [...prev, userMessage]);
        setLoading(true);
        setQuestion('');

        try {
            const tokenRequest = {
                scopes: ["api://6e3a0f77-a606-43cd-83ab-6b9181b1222f/access_as_user"],
                account: accounts[0],
            };

            const resToken = await instance.acquireTokenSilent(tokenRequest);
            const accessToken = resToken.accessToken;

            // Call backend API with Authorization header
            const res = await axios.post('http://localhost:8000/query', {
                question,
                role,
            }, {
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                    'Content-Type': 'application/json',
                },
            });

            const botMessage = {
                type: 'bot',
                text: res.data.answer,
                timestamp: getTimestamp(),
            };
            setMessages((prev) => [...prev, botMessage]);
        } catch (err) {
            setMessages((prev) => [
                ...prev,
                {
                    type: 'bot',
                    text: 'Error: Something went wrong.',
                    timestamp: getTimestamp(),
                },
            ]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-trusteq text-white flex flex-col items-center py-8 px-4">
            <div className="w-full bg-blue-50 max-w-2xl rounded-xl shadow-lg p-6 space-y-4">
                <h2 className="text-xl text-trusteq font-bold text-center">Chat with Zero Trust AI</h2>
                <div className="space-y-3 max-h-[60vh] overflow-y-auto pr-2">
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`flex items-start gap-3 ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                            {msg.type === 'bot' && <div className="text-2xl">🤖</div>}
                            <div className={`rounded-lg px-4 py-2 max-w-xs shadow-sm ${msg.type === 'user' ? 'bg-trusteq text-white' : 'bg-trusteq-light text-white'}`}>
                                <p className="whitespace-pre-wrap">{msg.text}</p>
                                <p className="text-xs text-gray-300 mt-1 text-right">{msg.timestamp}</p>
                            </div>
                            {msg.type === 'user' && <div className="text-2xl">🧑</div>}
                        </div>
                    ))}
                    <div ref={chatEndRef} />
                </div>
                <form className="flex gap-2" onSubmit={handleQuery}>
                    <input
                        type="text"
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        placeholder="Ask something..."
                        disabled={loading}
                        className="border border-gray-300 flex-1 px-4 py-2 rounded-lg bg-gray-100 text-black placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-trusteq"
                    />
                    <button
                        type="submit"
                        disabled={loading || !question.trim()}
                        className="bg-trusteq hover:bg-trusteq-light text-white px-4 py-2 rounded-lg transition"
                    >
                        {loading ? '...' : 'Send'}
                    </button>
                </form>
            </div>
        </div>
    );
}

export default QueryForm;