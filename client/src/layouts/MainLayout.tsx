import { NavLink, Outlet } from "react-router-dom";

export function MainLayout() {
    return (
        <div className="bg-background text-on-surface min-h-screen font-body flex">
            <aside className="fixed left-0 top-0 h-screen flex flex-col p-6 w-72 bg-slate-50 z-50">
                <div className="mb-10 px-4">
                    <div className="h-16 flex items-center">
                        <div className="w-10 h-10 bg-indigo-950 rounded-xl flex items-center justify-center mr-3 shadow-md">
                            <span className="material-symbols-outlined text-white">school</span>
                        </div>
                        <span className="text-2xl font-black text-indigo-950 tracking-tighter font-headline">
                            TeamPass
                        </span>
                    </div>
                </div>

                <nav className="flex-1 space-y-2">
                    <SidebarLink to="/dashboard" icon="dashboard" label="Панель управления" />
                    <SidebarLink to="/team" icon="group" label="Команда" />
                    <SidebarLink to="/knowledge" icon="swap_horizontal_circle" label="Биржа знаний" />
                    <SidebarLink to="/challenges" icon="emoji_events" label="Вызовы" />
                    <SidebarLink to="/leaderboard" icon="leaderboard" label="Рейтинги" />
                    <SidebarLink to="/profile" icon="account_circle" label="Профиль" />
                </nav>

                <div className="mt-auto space-y-2 pt-6">
                    <button className="w-full flex items-center px-4 py-3 text-indigo-400 font-medium hover:bg-indigo-100 transition-colors rounded-xl group">
                        <span className="material-symbols-outlined mr-3">settings</span>
                        <span className="font-label text-md">Настройки</span>
                    </button>
                    <button className="w-full flex items-center px-4 py-3 text-indigo-400 font-medium hover:bg-indigo-100 transition-colors rounded-xl group">
                        <span className="material-symbols-outlined mr-3">help</span>
                        <span className="font-label text-md">Поддержка</span>
                    </button>
                </div>
            </aside>
            <main className="w-full ml-72 py-10 px-10 max-w-7xl mx-auto min-h-screen">
                <Outlet />
            </main>
        </div>
    );
}

function SidebarLink({ to, icon, label }: { to: string; icon: string; label: string }) {
    return (
        <NavLink
            to={to}
            className={({ isActive }) =>
                `flex items-center px-4 py-3 font-medium transition-colors group ${isActive
                    ? "text-indigo-900 font-extrabold border-r-4 border-teal-500 bg-indigo-50/50 rounded-l-xl"
                    : "text-indigo-400 hover:bg-indigo-100 rounded-xl"
                }`
            }
        >
            <span className="material-symbols-outlined mr-3">{icon}</span>
            <span className="font-label text-md">{label}</span>
        </NavLink>
    );
}