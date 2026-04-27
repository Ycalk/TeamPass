import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { authApi } from "../api/auth";
import { Menu, MenuButton, MenuItem, MenuItems, Transition } from '@headlessui/react';
import { Fragment } from 'react';

export function MainLayout() {
    const navigate = useNavigate();

    const handleLogout = async () => {
        try {
            await authApi.logout();
            toast.success("Вы успешно вышли из системы");
            navigate("/");
        } catch (error) {
            toast.error("Ошибка при выходе из системы");
            console.error(error);
        }
    };

    return (
        <div className="bg-background text-on-surface min-h-screen font-body flex">
            <aside className="fixed left-0 top-0 h-screen flex flex-col p-6 w-72 bg-surface-container-lowest z-50">
                <div className="mb-10 px-4">
                    <div className="h-16 flex items-center">
                        <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center mr-3 shadow-md shadow-primary/20">
                            <span className="material-symbols-outlined text-on-primary">school</span>
                        </div>
                        <span className="text-2xl font-black text-primary tracking-tighter font-headline">
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

                    {/* Меню Headless UI */}
                    <Menu as="div" className="relative w-full">
                        {({ open }) => (
                            <>
                                <MenuButton
                                    className={`w-full flex items-center px-4 py-3 font-medium transition-colors rounded-xl focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 ${open
                                        ? "bg-primary/10 text-primary"
                                        : "text-on-surface-variant hover:bg-surface-container hover:text-primary"
                                        }`}
                                >
                                    <span className="material-symbols-outlined mr-3">settings</span>
                                    <span className="font-label text-md">Настройки</span>
                                </MenuButton>

                                <Transition
                                    as={Fragment}
                                    enter="transition ease-out duration-150"
                                    enterFrom="transform opacity-0 translate-y-2 scale-95"
                                    enterTo="transform opacity-100 translate-y-0 scale-100"
                                    leave="transition ease-in duration-100"
                                    leaveFrom="transform opacity-100 translate-y-0 scale-100"
                                    leaveTo="transform opacity-0 translate-y-1 scale-95"
                                >
                                    <MenuItems className="absolute bottom-full left-0 mb-2 w-full origin-bottom bg-surface-container-lowest rounded-xl shadow-lg shadow-primary/5 border border-outline-variant/15 p-1.5 focus:outline-none z-50">
                                        <div className="px-3 py-2 text-[11px] font-bold text-outline uppercase tracking-wider mb-1">
                                            Аккаунт
                                        </div>
                                        <MenuItem>
                                            {({ focus }) => (
                                                <button
                                                    onClick={handleLogout}
                                                    className={`w-full flex items-center px-3 py-2.5 rounded-lg transition-colors group focus:outline-none ${focus ? 'bg-error/10 text-error' : 'text-error/80'
                                                        }`}
                                                >
                                                    <span className="material-symbols-outlined mr-3 text-[20px] group-hover:-translate-x-0.5 transition-transform">
                                                        logout
                                                    </span>
                                                    <span className="font-label text-sm font-medium">Выйти из профиля</span>
                                                </button>
                                            )}
                                        </MenuItem>
                                    </MenuItems>
                                </Transition>
                            </>
                        )}
                    </Menu>

                    <button className="w-full flex items-center px-4 py-3 text-on-surface-variant font-medium hover:bg-surface-container hover:text-primary transition-colors rounded-xl group focus:outline-none">
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
                `flex items-center px-4 py-3 font-medium transition-colors group outline-none focus-visible:ring-2 focus-visible:ring-primary/50 ${isActive
                    ? "text-primary font-extrabold border-r-4 border-secondary bg-secondary/10 rounded-l-xl"
                    : "text-on-surface-variant hover:bg-surface-container hover:text-primary rounded-xl"
                }`
            }
        >
            <span className="material-symbols-outlined mr-3">{icon}</span>
            <span className="font-label text-md">{label}</span>
        </NavLink>
    );
}