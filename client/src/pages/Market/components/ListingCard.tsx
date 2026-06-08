import { Menu, MenuButton, MenuItem, MenuItems, Transition } from '@headlessui/react';
import { Fragment } from 'react';

type Props = {
    listing: any;
    onRespond?: () => void;
    showMenu?: boolean;
    menuItems?: { label: string; icon: string; onClick: () => void; variant?: 'default' | 'danger' }[];
    statusBadge?: { label: string; color: string };
    children?: React.ReactNode;
};

export function ListingCard({ listing, onRespond, showMenu, menuItems, statusBadge, children }: Props) {
    const date = new Date(listing.created_at * 1000);
    const formatted = date.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });

    return (
        <div className="bg-surface-container-lowest border border-outline-variant/15 rounded-2xl p-6 hover:shadow-md hover:shadow-primary/5 transition-all relative group">
            <div className="flex justify-between items-start gap-4 mb-4">
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2 flex-wrap">
                        <h3 className="text-lg font-bold text-on-surface font-headline truncate">
                            {listing.title}
                        </h3>
                        {statusBadge && (
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-lg text-xs font-bold ${statusBadge.color}`}>
                                {statusBadge.label}
                            </span>
                        )}
                    </div>

                    <div className="flex items-center gap-3 text-sm text-on-surface-variant">
                        <span className="flex items-center gap-1">
                            <span className="material-symbols-outlined text-[16px]">group</span>
                            {listing.team?.name || 'Неизвестная команда'}
                        </span>
                        <span className="text-outline-variant">·</span>
                        <span className="flex items-center gap-1">
                            <span className="material-symbols-outlined text-[16px]">schedule</span>
                            {formatted}
                        </span>
                    </div>
                </div>

                {showMenu && menuItems && menuItems.length > 0 && (
                    <Menu as="div" className="relative shrink-0">
                        <MenuButton className="w-9 h-9 flex items-center justify-center rounded-xl text-on-surface-variant hover:bg-surface-container hover:text-primary transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/50">
                            <span className="material-symbols-outlined text-[20px]">more_vert</span>
                        </MenuButton>
                        <Transition
                            as={Fragment}
                            enter="transition ease-out duration-100"
                            enterFrom="transform opacity-0 scale-95"
                            enterTo="transform opacity-100 scale-100"
                            leave="transition ease-in duration-75"
                            leaveFrom="transform opacity-100 scale-100"
                            leaveTo="transform opacity-0 scale-95"
                        >
                            <MenuItems className="absolute right-0 mt-2 w-52 origin-top-right bg-surface-container-lowest border border-outline-variant/15 rounded-xl shadow-lg shadow-primary/5 p-1.5 focus:outline-none z-50">
                                {menuItems.map((item, i) => (
                                    <MenuItem key={i}>
                                        {({ focus }) => (
                                            <button
                                                onClick={item.onClick}
                                                className={`w-full flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${item.variant === 'danger'
                                                        ? (focus ? 'bg-error/10 text-error' : 'text-error/80')
                                                        : (focus ? 'bg-surface-container text-primary' : 'text-on-surface')
                                                    }`}
                                            >
                                                <span className="material-symbols-outlined mr-2 text-[18px]">{item.icon}</span>
                                                {item.label}
                                            </button>
                                        )}
                                    </MenuItem>
                                ))}
                            </MenuItems>
                        </Transition>
                    </Menu>
                )}
            </div>

            <p className="text-on-surface-variant text-sm leading-relaxed whitespace-pre-wrap mb-4">
                {listing.description}
            </p>

            {onRespond && (
                <button
                    onClick={onRespond}
                    className="bg-gradient-to-r from-primary to-primary-container text-on-primary px-5 py-2.5 rounded-xl font-bold text-sm shadow-md shadow-primary/20 hover:scale-[0.98] active:scale-95 transition-all flex items-center gap-2"
                >
                    <span className="material-symbols-outlined text-[18px]">reply</span>
                    Откликнуться
                </button>
            )}

            {children}
        </div>
    );
}
