import { Link, Outlet, useLocation } from 'react-router-dom';

const tabs = [
    { label: 'Все запросы', path: '/knowledge', icon: 'explore' },
    { label: 'Мои запросы', path: '/knowledge/my', icon: 'assignment' },
    { label: 'Отклики', path: '/knowledge/responses', icon: 'reply_all' },
];

export function Knowledge() {
    const location = useLocation();

    return (
        <div className="space-y-8">
            <div className="bg-surface-container-lowest rounded-[2rem] shadow-2xl shadow-primary/5 border border-outline-variant/15 p-8 relative overflow-hidden">
                <div className="absolute top-[-30%] right-[-5%] w-[250px] h-[250px] bg-primary/5 rounded-full blur-[60px] pointer-events-none" />
                <div className="absolute bottom-[-20%] left-[-5%] w-[180px] h-[180px] bg-secondary-fixed/8 rounded-full blur-[50px] pointer-events-none" />

                <div className="relative z-10">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center">
                            <span className="material-symbols-outlined text-primary">swap_horizontal_circle</span>
                        </div>
                        <h1 className="text-3xl font-black text-on-surface font-headline tracking-tight">
                            Биржа знаний
                        </h1>
                    </div>

                    <div className="flex gap-2">
                        {tabs.map((tab) => {
                            const active = location.pathname === tab.path;

                            return (
                                <Link
                                    key={tab.path}
                                    to={tab.path}
                                    className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm transition-all ${active
                                            ? 'bg-primary text-on-primary shadow-md shadow-primary/20'
                                            : 'text-on-surface-variant hover:bg-surface-container hover:text-primary'
                                        }`}
                                >
                                    <span className="material-symbols-outlined text-[18px]">{tab.icon}</span>
                                    {tab.label}
                                </Link>
                            );
                        })}
                    </div>
                </div>
            </div>

            <Outlet />
        </div>
    );
}
