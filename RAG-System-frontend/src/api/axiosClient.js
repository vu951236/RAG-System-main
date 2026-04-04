import axios from "axios";
import authService from "../services/authService";

const axiosClient = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    withCredentials: true
});

axiosClient.interceptors.response.use(
    (response) => response,
    async (error) => {

        const originalRequest = error.config;

        if (
            error.response?.status === 401 &&
            !originalRequest._retry &&
            !originalRequest.url.includes("/auth/login") &&
            !originalRequest.url.includes("/auth/refresh-token")
        ) {

            originalRequest._retry = true;

            try {

                await authService.refreshToken();

                return axiosClient(originalRequest);

            } catch (refreshError) {

                console.error("Refresh token thất bại:", refreshError);

                window.location.href = "/login";
                return Promise.reject(refreshError);

            }

        }

        return Promise.reject(error);
    }
);

export default axiosClient;