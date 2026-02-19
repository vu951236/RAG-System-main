import React, { useState } from "react";
import ragService from "../services/ragService";
import "../styles/upload.css";

function UploadBox() {

    const [file, setFile] = useState(null);
    const [status, setStatus] = useState("");
    const [loading, setLoading] = useState(false);

    const handleUpload = async () => {

        if (!file) return;

        try {
            setLoading(true);
            setStatus("");

            await ragService.uploadFile(file);

            setStatus("Upload thành công!");
        } catch (error) {
            setStatus("Upload thất bại!");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="upload-container">

            <h3>Upload tài liệu</h3>

            <input
                type="file"
                accept="application/pdf"
                onChange={(e) => setFile(e.target.files[0])}
            />

            <button
                onClick={handleUpload}
                disabled={loading}
                className="upload-btn"
            >
                {loading ? "Đang upload..." : "Upload"}
            </button>

            {loading && <div className="spinner"></div>}

            <p>{status}</p>

        </div>
    );
}

export default UploadBox;
