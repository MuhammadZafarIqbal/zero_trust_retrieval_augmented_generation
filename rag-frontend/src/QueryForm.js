import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './Chat.css'; // we'll create this next

function QueryForm() {
    const [question, setQuestion] = useState('');
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const chatEndRef = useRef(null);

    const scrollToBottom = () => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleQuery = async (e) => {
        e.preventDefault();
        if (!question.trim()) return;

        const userMessage = { type: 'user', text: question, timestamp: new Date() };
        setMessages((prev) => [...prev, userMessage]);
        setLoading(true);
        setQuestion('');

        try {
            const formData = new FormData();
            formData.append('question', question);
            const res = await axios.post('http://localhost:8000/query', formData);
            const answer = res.data.answer;

            const botMessage = { type: 'bot', text: answer, timestamp: new Date() };
            setMessages((prev) => [...prev, botMessage]);
        } catch (err) {
            const errorText =
                typeof err.response?.data?.detail === 'string'
                    ? err.response.data.detail
                    : JSON.stringify(err.response?.data?.detail || err.message);
            setMessages((prev) => [...prev, { type: 'bot', text: 'Error: ' + errorText }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chat-container">
            <div className="chat-box">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`message ${msg.type}`}>
                        <div className="message-content">{msg.text}</div>
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