import axiosClient from "../api/axiosClient";

const AUTH_URL = "/auth";

const authService = {

    login: async (data) => {
        const res = await axiosClient.post(`${AUTH_URL}/login`, data);
        return res.data;
    },

    register: async (data) => {
        const res = await axiosClient.post(`${AUTH_URL}/register`, data);
        return res.data;
    },

    verifyOtp: async (data) => {
        const res = await axiosClient.post(`${AUTH_URL}/verify`, data);
        return res.data;
    },

    resendOtp: async (data) => {
        const res = await axiosClient.post(`${AUTH_URL}/resend-otp`, data);
        return res.data;
    },

    logout: async () => {
        await axiosClient.post(`${AUTH_URL}/logout`);
        window.location.href = "/login";
    },

    refreshToken: async () => {
        const res = await axiosClient.post(`${AUTH_URL}/refresh-token`);
        return res.data;
    }
};

export default authService;