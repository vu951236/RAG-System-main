import React, { useState } from "react";
import authService from "../services/authService";
import { useNavigate } from "react-router-dom";

function Register() {

    const navigate = useNavigate();

    const [form, setForm] = useState({
        username: "",
        email: "",
        password: ""
    });

    const [message, setMessage] = useState("");
    const [error, setError] = useState("");

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleRegister = async (e) => {
        e.preventDefault();

        try {

            const res = await authService.register(form);

            setMessage(res.message || "Đăng ký thành công! Vui lòng kiểm tra OTP");

            navigate("/verify", {
                state: { email: form.email }
            });

        } catch (err) {

            setError("Đăng ký thất bại");

        }
    };

    return (
        <div className="login-container">

            <form className="login-form" onSubmit={handleRegister}>

                <h2>Đăng ký tài khoản</h2>

                {error && <p className="error-msg">{error}</p>}
                {message && <p className="success-msg">{message}</p>}

                <div className="input-group">
                    <label>Username</label>
                    <input
                        type="text"
                        name="username"
                        value={form.username}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="input-group">
                    <label>Email</label>
                    <input
                        type="email"
                        name="email"
                        value={form.email}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="input-group">
                    <label>Password</label>
                    <input
                        type="password"
                        name="password"
                        value={form.password}
                        onChange={handleChange}
                        required
                    />
                </div>

                <button type="submit" className="login-btn">
                    Đăng ký
                </button>

                <p style={{marginTop:"10px"}}>
                    Đã có tài khoản? <a href="/login">Đăng nhập</a>
                </p>

            </form>

        </div>
    );
}

export default Register;