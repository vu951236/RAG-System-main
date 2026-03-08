import React, { useState } from "react";
import ragService from "../services/ragService";
import "../styles/upload.css";

function UploadBox() {

    const [file, setFile] = useState(null);
    const [status, setStatus] = useState("");
    const [loading, setLoading] = useState(false);

    const handleFileChange = (e) => {
        const selected = e.target.files[0];

        if (!selected) return;

        if (selected.type !== "application/pdf") {
            setStatus("Chỉ được upload file PDF");
            return;
        }

        setFile(selected);
        setStatus("");
    };

    const handleUpload = async () => {

        if (!file) {
            setStatus("Vui lòng chọn file");
            return;
        }

        try {

            setLoading(true);
            setStatus("Đang upload...");

            await ragService.uploadFile(file);

            setStatus("Upload thành công!");
            setFile(null);

        } catch (error) {

            console.error("Chi tiết lỗi upload:", error);
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
                onChange={handleFileChange}
                disabled={loading}
            />

            {file && (
                <p className="file-name">
                    File: {file.name}
                </p>
            )}

            <button
                onClick={handleUpload}
                disabled={loading || !file}
                className="upload-btn"
            >
                {loading ? "Đang upload..." : "Upload"}
            </button>

            {loading && (
                <div className="spinner-wrapper">
                    <div className="spinner"></div>
                </div>
            )}

            {status && <p className="status">{status}</p>}

        </div>
    );
}

export default UploadBox;