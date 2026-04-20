import { Routes, Route, Navigate } from "react-router-dom";
import { MainLayout } from "./layouts/MainLayout";
import { Login } from "./pages/Login";
import { Register } from "./pages/Register";
import { Dashboard } from "./pages/Dashboard";
import { Team } from "./pages/Team";
import { Profile } from "./pages/Profile";
import { Knowledge } from "./pages/Knowledge";
import { Challenges } from "./pages/Challenges";
import { Leaderboard } from "./pages/Leaderboard";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { PublicRoute } from "./components/PublicRoute";

export default function App() {
    return (
        <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />

            <Route element={<PublicRoute />}>
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
            </Route>

            <Route element={<ProtectedRoute />}>
                <Route element={<MainLayout />}>
                    <Route path="/app" element={<Navigate to="/dashboard" replace />} />
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/team" element={<Team />} />
                    <Route path="/knowledge" element={<Knowledge />} />
                    <Route path="/challenges" element={<Challenges />} />
                    <Route path="/leaderboard" element={<Leaderboard />} />
                    <Route path="/profile" element={<Profile />} />
                </Route>
            </Route>

            <Route path="*" element={<div className="p-10 text-center">Страница не найдена</div>} />
        </Routes>
    );
}