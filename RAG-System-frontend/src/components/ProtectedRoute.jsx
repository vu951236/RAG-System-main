import React, { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import ragService from "../services/ragService";

const ProtectedRoute = ({ children }) => {

    const [isAuth, setIsAuth] = useState(null);

    useEffect(() => {

        const checkAuth = async () => {

            try {

                await ragService.getConversations();

                setIsAuth(true);

            } catch (error) {

                if (error.response?.status === 401) {
                    setIsAuth(false);
                } else {
                    setIsAuth(false);
                }

            }

        };

        checkAuth();

    }, []);

    if (isAuth === null) {
        return <div>Loading...</div>;
    }

    if (!isAuth) {
        return <Navigate to="/login" replace />;
    }

    return children;
};

export default ProtectedRoute;