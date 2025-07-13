import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { useMsal } from '@azure/msal-react';
import './Chat.css';
import { loginRequest } from './authConfig';

function QueryForm() {
    const [question, setQuestion] = useState('');
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const chatEndRef = useRef(null);

    const { instance, accounts } = useMsal();

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

            const res = await axios.post('http://localhost:8000/query', { question }, {
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
        <div className="chat-container">
            <div className="chat-box">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`message ${msg.type}`}>
                        <div className="avatar">{msg.type === 'user' ? '🧑' : '🤖'}</div>
                        <div className="bubble">
                            <div>{msg.text}</div>
                            <div className="timestamp">{msg.timestamp}</div>
                        </div>
                    </div>
                ))}
                <div ref={chatEndRef} />
            </div>

            <form className="chat-form" onSubmit={handleQuery}>
                <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Ask something..."
                    disabled={loading}
                />
                <button type="submit" disabled={loading || !question.trim()}>
                    {loading ? '...' : 'Send'}
                </button>
            </form>
        </div>
    );
}

export default QueryForm;