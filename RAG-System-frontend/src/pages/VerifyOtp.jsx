import React, { useState } from "react";
import authService from "../services/authService";
import { useLocation, useNavigate } from "react-router-dom";

function VerifyOtp() {

    const location = useLocation();
    const navigate = useNavigate();

    const email = location.state?.email || "";

    const [otp, setOtp] = useState("");
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");

    const handleVerify = async (e) => {

        e.preventDefault();

        try {

            const res = await authService.verifyOtp({
                email,
                otp
            });

            setMessage(res.message || "Xác thực thành công");

            setTimeout(() => {
                navigate("/login");
            }, 1500);

        } catch (err) {

            setError("OTP không hợp lệ");

        }
    };

    const handleResend = async () => {

        try {

            await authService.resendOtp({ email });

            setMessage("Đã gửi lại OTP");

        } catch {

            setError("Không thể gửi lại OTP");

        }

    };

    return (
        <div className="login-container">

            <form className="login-form" onSubmit={handleVerify}>

                <h2>Xác thực OTP</h2>

                <p>Email: {email}</p>

                {error && <p className="error-msg">{error}</p>}
                {message && <p className="success-msg">{message}</p>}

                <div className="input-group">
                    <label>OTP</label>
                    <input
                        type="text"
                        value={otp}
                        onChange={(e) => setOtp(e.target.value)}
                        required
                    />
                </div>

                <button type="submit" className="login-btn">
                    Xác thực
                </button>

                <button
                    type="button"
                    onClick={handleResend}
                    style={{marginTop:"10px"}}
                >
                    Gửi lại OTP
                </button>

            </form>

        </div>
    );
}

export default VerifyOtp;