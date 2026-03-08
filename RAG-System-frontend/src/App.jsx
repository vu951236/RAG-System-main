import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import "./App.css";
import UploadBox from "./components/UploadBox.jsx";
import ChatBox from "./components/ChatBox.jsx";
import ragService from "./services/ragService";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import Login from "./pages/Login.jsx";
import authService from "./services/authService.js";

function MainLayout() {

    const [conversations, setConversations] = useState([]);
    const [selectedConvId, setSelectedConvId] = useState(null);

    const fetchSidebar = async () => {
        try {

            const res = await ragService.getConversations();

            setConversations(Array.isArray(res.data) ? res.data : []);

        } catch (error) {

            console.error("Lỗi lấy danh sách hội thoại:", error);
            setConversations([]);

        }
    };

    useEffect(() => {

        const loadSidebar = async () => {

            try {

                const res = await ragService.getConversations();

                setConversations(Array.isArray(res.data) ? res.data : []);

            } catch (error) {

                console.error("Lỗi lấy danh sách hội thoại:", error);
                setConversations([]);

            }

        };

        loadSidebar();

    }, []);

    const handleNewChat = async () => {

        try {

            const res = await ragService.createNewConversation();

            setSelectedConvId(res.data);

            await fetchSidebar();

        } catch (error) {

            console.error(error);
            alert("Không thể tạo cuộc trò chuyện mới");

        }

    };

    const handleLogout = async () => {

        try {

            await authService.logout();

        } catch (error) {

            console.error("Logout error:", error);

        }

    };

    return (
        <div className="main-container">

            <div className="sidebar">

                <button className="new-chat-btn" onClick={handleNewChat}>
                    <span>+</span> New Chat
                </button>

                <div className="conv-list">

                    {conversations.map((conv) => (

                        <div
                            key={conv.id}
                            className={`conv-item ${selectedConvId === conv.id ? "active" : ""}`}
                            onClick={() => setSelectedConvId(conv.id)}
                        >
                            {conv.title}
                        </div>

                    ))}

                </div>

                <div className="sidebar-footer">

                    <UploadBox />

                    <button className="logout-btn" onClick={handleLogout}>
                        Đăng xuất
                    </button>

                </div>

            </div>

            <div className="chat-area">

                {selectedConvId ? (

                    <>
                        <div className="chat-header">
                            Hội thoại #{selectedConvId}
                        </div>

                        <ChatBox
                            convId={selectedConvId}
                            onUpdateSidebar={fetchSidebar}
                        />
                    </>

                ) : (

                    <div className="welcome-screen">
                        <h1>RAG System</h1>
                        <p>Chọn một cuộc trò chuyện hoặc tạo mới để bắt đầu</p>
                    </div>

                )}

            </div>

        </div>
    );
}

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<Login />} />

                <Route
                    path="/"
                    element={
                        <ProtectedRoute>
                            <MainLayout />
                        </ProtectedRoute>
                    }
                />

                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;