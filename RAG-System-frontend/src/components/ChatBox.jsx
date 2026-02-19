import React, { useState } from "react";
import ragService from "../services/ragService";

function ChatBox() {

    const [question, setQuestion] = useState("");
    const [messages, setMessages] = useState([]);

    const handleAsk = async () => {

        if (!question) return;

        setMessages(prev => [
            ...prev,
            { type: "user", text: question }
        ]);

        try {

            const response = await ragService.askQuestion(question);

            const url = window.URL.createObjectURL(
                new Blob([response.data])
            );

            const link = document.createElement("a");
            link.href = url;
            link.setAttribute("download", "ket_qua_rag.pdf");
            document.body.appendChild(link);
            link.click();

            setMessages(prev => [
                ...prev,
                { type: "bot", text: "Đã tạo file PDF kết quả." }
            ]);

        } catch (error) {
            setMessages(prev => [
                ...prev,
                { type: "bot", text: "Có lỗi xảy ra." }
            ]);
        }

        setQuestion("");
    };

    return (
        <div style={{ marginTop: 20 }}>

            <h3>Chat hỏi đáp</h3>

            {/* KHUNG CHAT */}
            <div
                style={{
                    border: "1px solid #ccc",
                    borderRadius: 10,
                    height: 300,
                    overflowY: "auto",
                    padding: 10,
                    marginBottom: 10
                }}
            >
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        style={{
                            textAlign: msg.type === "user" ? "right" : "left",
                            marginBottom: 8
                        }}
                    >
            <span
                style={{
                    background: msg.type === "user" ? "#4CAF50" : "#eee",
                    color: msg.type === "user" ? "white" : "black",
                    padding: "8px 12px",
                    borderRadius: 12,
                    display: "inline-block",
                    maxWidth: "70%"
                }}
            >
              {msg.text}
            </span>
                    </div>
                ))}
            </div>

            {/* INPUT */}
            <div style={{ display: "flex", gap: 10 }}>
                <input
                    style={{ flex: 1, padding: 8 }}
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Nhập câu hỏi..."
                />
                <button onClick={handleAsk}>Gửi</button>
            </div>

        </div>
    );
}

export default ChatBox;
