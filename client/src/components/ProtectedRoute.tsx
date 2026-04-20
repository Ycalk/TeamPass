import { useEffect, useState } from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { usersApi } from "../api/users";
import { getAccessToken, refreshAccessToken } from "../api/client";

export function ProtectedRoute() {
    const [isChecking, setIsChecking] = useState(true);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const location = useLocation();

    useEffect(() => {
        const verifyAuth = async () => {
            try {
                if (!getAccessToken()) {
                    await refreshAccessToken();
                }
                await usersApi.getMe();
                setIsAuthenticated(true);
            } catch (error) {
                setIsAuthenticated(false);
            } finally {
                setIsChecking(false);
            }
        };

        verifyAuth();
    }, []);

    if (isChecking) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <span className="material-symbols-outlined animate-spin text-4xl text-primary">
                    progress_activity
                </span>
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    return <Outlet />;
}