import React, { useState, useEffect, useRef } from "react";
import ragService from "../services/ragService";

function ChatBox({ convId, onUpdateSidebar }) {

    const [question, setQuestion] = useState("");
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);

    const messagesEndRef = useRef(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const loadMessages = async () => {

        try {

            const res = await ragService.getMessagesByConv(convId);

            const history = res.data.flatMap(m => [
                {
                    type: "user",
                    text: m.question
                },
                {
                    type: "bot",
                    pdf: m.pdfPath
                }
            ]);

            setMessages(history);

        } catch (error) {

            console.error("Lỗi tải tin nhắn:", error);

        }

    };

    useEffect(() => {

        if (convId) {
            loadMessages();
        }

    }, [convId]);


    const handleAsk = async () => {

        if (loading) return;

        if (!question.trim() || question.trim().split(/\s+/).length < 3) {
            alert("Câu hỏi phải dài hơn 2 từ");
            return;
        }

        const currentQuestion = question;

        setMessages(prev => [
            ...prev,
            { type: "user", text: currentQuestion }
        ]);

        setQuestion("");
        setLoading(true);

        try {

            await ragService.askQuestion(convId, currentQuestion);

            await loadMessages();

            onUpdateSidebar?.();

        } catch (error) {

            console.error("Lỗi khi gọi AI:", error);

            let message = "Có lỗi xảy ra";

            if (error.response?.data?.message) {
                message = error.response.data.message;
            }

            setMessages(prev => [
                ...prev,
                { type: "bot", error: message }
            ]);

        } finally {

            setLoading(false);

        }

    };


    return (

        <div className="chat-box-container">

            <div className="messages-container">

                {messages.length === 0 && (
                    <div style={{
                        textAlign: "center",
                        color: "#8e8ea0",
                        marginTop: "20px"
                    }}>
                        Hãy bắt đầu bằng một câu hỏi...
                    </div>
                )}

                {messages.map((msg, index) => (

                    <div key={index} className={`message-row ${msg.type}`}>

                        <div className="message-content">

                            {msg.type === "user" && msg.text}

                            {msg.type === "bot" && msg.pdf && (
                                <button
                                    onClick={() => ragService.downloadPdf(convId, msg.pdf)}
                                >
                                    📄 Tải PDF
                                </button>
                            )}

                            {msg.error && (
                                <span style={{ color: "red" }}>
                                    {msg.error}
                                </span>
                            )}

                        </div>

                    </div>

                ))}

                {loading && (
                    <div className="message-row bot">
                        <div className="message-content italic">
                            AI đang suy nghĩ...
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef}></div>

            </div>


            <div className="input-container">

                <div className="input-wrapper">

                    <input
                        className="chat-input"
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleAsk()}
                        placeholder="Nhập câu hỏi..."
                        disabled={loading}
                    />

                    <button
                        className="send-btn"
                        onClick={handleAsk}
                        disabled={loading || !question.trim()}
                    >
                        {loading ? "..." : "Gửi"}
                    </button>

                </div>

            </div>

        </div>

    );

}

export default ChatBox;