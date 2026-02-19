import React from "react";
import UploadBox from "./components/UploadBox.jsx";
import ChatBox from "./components/ChatBox.jsx";

function App() {
    return (
        <div style={{ maxWidth: 600, margin: "auto", marginTop: 40 }}>
            <h2>RAG Chat System</h2>
            <UploadBox />
            <ChatBox />
        </div>
    );
}

export default App;
