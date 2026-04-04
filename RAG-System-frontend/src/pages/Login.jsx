import React, { useState } from "react";
import authService from "../services/authService";
import "../App.css";

function Login() {

    const [credentials, setCredentials] = useState({ username: "", password: "" });
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setCredentials({ ...credentials, [e.target.name]: e.target.value });
    };

    const handleLogin = async (e) => {

        e.preventDefault();
        setLoading(true);
        setError("");

        try {

            await authService.login(credentials);
            window.location.href = "/";

        } catch (err) {

            console.error("Lỗi đăng nhập:", err);
            setError("Tên đăng nhập hoặc mật khẩu không đúng!");

        } finally {

            setLoading(false);

        }

    };

    return (
        <div className="login-container">

            <form className="login-form" onSubmit={handleLogin}>

                <h2>Đăng nhập RAG System</h2>

                {error && <p className="error-msg">{error}</p>}

                <div className="input-group">
                    <label>Username</label>
                    <input
                        type="text"
                        name="username"
                        value={credentials.username}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="input-group">
                    <label>Password</label>
                    <input
                        type="password"
                        name="password"
                        value={credentials.password}
                        onChange={handleChange}
                        required
                    />
                </div>

                <button type="submit" disabled={loading} className="login-btn">
                    {loading ? "Đang xác thực..." : "Đăng nhập"}
                </button>

                <p className="register-link">
                    Chưa có tài khoản? <a href="/register">Đăng ký</a>
                </p>

            </form>

        </div>
    );
}

export default Login;