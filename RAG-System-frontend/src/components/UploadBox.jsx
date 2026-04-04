import React, { useState } from "react";
import ragService from "../services/ragService";
import "../styles/upload.css";

function UploadBox({ convId }) {

    const [file, setFile] = useState(null);
    const [status, setStatus] = useState("");
    const [loading, setLoading] = useState(false);

    const handleFileChange = (e) => {
        const selected = e.target.files[0];
        if (!selected) return;

        if (selected.type !== "application/pdf") {
            setStatus("Chỉ được upload file PDF");
            setFile(null);
            return;
        }

        setFile(selected);
        setStatus("");
    };

    const handleUpload = async () => {
        // Kiểm tra xem đã có file và ID hội thoại chưa
        if (!file) {
            setStatus("Vui lòng chọn file");
            return;
        }
        if (!convId) {
            setStatus("Không tìm thấy ID hội thoại!");
            return;
        }

        try {
            setLoading(true);
            setStatus("Đang upload...");

            const response = await ragService.uploadFile(convId, file);

            console.log("Server trả về:", response.data);
            setStatus(`Upload thành công: ${response.data.fileName || "File đã lưu"}`);

            setFile(null);
        } catch (error) {
            console.error("Chi tiết lỗi upload:", error);
            setStatus("Upload thất bại! Kiểm tra kết nối hoặc CORS.");
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
                    File chuẩn bị gửi: <strong>{file.name}</strong>
                </p>
            )}

            <button
                onClick={handleUpload}
                disabled={loading || !file}
                className="upload-btn"
            >
                {loading ? "Đang xử lý..." : "Bắt đầu Upload"}
            </button>

            {loading && (
                <div className="spinner-wrapper">
                    <div className="spinner"></div>
                </div>
            )}

            {status && <p className={`status ${status.includes("thành công") ? "success" : "error"}`}>
                {status}
            </p>}
        </div>
    );
}

export default UploadBox;