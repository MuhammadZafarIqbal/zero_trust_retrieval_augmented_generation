import React, { useState } from 'react';
import axios from 'axios';

function QueryForm() {
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState('');
    const [loading, setLoading] = useState(false);

    const handleQuery = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const formData = new FormData();
            formData.append('question', question);
            const res = await axios.post('http://localhost:8000/query', formData, {
                withCredentials: true,
            });
            setAnswer(res.data.answer);
        } catch (err) {
            let errorMsg = err.message;
            if (err.response?.data?.detail) {
                // detail could be string or object, handle both
                errorMsg = typeof err.response.data.detail === 'string'
                    ? err.response.data.detail
                    : JSON.stringify(err.response.data.detail, null, 2);
            }
            setAnswer("Error: " + errorMsg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ margin: "2rem" }}>
            <h2>Ask the RAG System</h2>
            <form onSubmit={handleQuery}>
                <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Type your question..."
                    style={{ width: "60%", padding: "0.5rem" }}
                />
                <button type="submit" disabled={loading} style={{ marginLeft: "1rem" }}>
                    {loading ? 'Asking...' : 'Ask'}
                </button>
            </form>
            {answer && (
                <div style={{ marginTop: "1rem" }}>
                    <strong>Answer:</strong> <p>{answer}</p>
                </div>
            )}
        </div>
    );
}

export default QueryForm;
