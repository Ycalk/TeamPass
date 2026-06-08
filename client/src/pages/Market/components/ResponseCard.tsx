type Props = {
    response: any;
    onAccept?: () => void;
    showStatus?: boolean;
    children?: React.ReactNode;
};

const statusConfig: Record<string, { label: string; color: string; icon: string }> = {
    pending: {
        label: 'Ожидает',
        color: 'bg-tertiary-container/10 text-on-tertiary-container',
        icon: 'hourglass_empty',
    },
    accepted: {
        label: 'Принят',
        color: 'bg-secondary/10 text-secondary',
        icon: 'check_circle',
    },
    rejected: {
        label: 'Отклонён',
        color: 'bg-error/10 text-error',
        icon: 'cancel',
    },
};

export function ResponseCard({ response, onAccept, showStatus = true, children }: Props) {
    const status = statusConfig[response.status] || statusConfig.pending;

    return (
        <div className="bg-surface-container-low border border-outline-variant/10 rounded-xl p-4 flex items-center justify-between gap-4 hover:border-primary/15 transition-all">
            <div className="flex items-center gap-3 min-w-0">
                <div className="w-10 h-10 rounded-full bg-secondary/10 text-secondary flex items-center justify-center shrink-0">
                    <span className="material-symbols-outlined text-[20px]">group</span>
                </div>
                <div className="min-w-0">
                    <div className="font-bold text-on-surface text-sm truncate">
                        {response.team?.name || 'Неизвестная команда'}
                    </div>
                    {showStatus && (
                        <div className="flex items-center gap-1.5 mt-0.5">
                            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-bold ${status.color}`}>
                                <span className="material-symbols-outlined text-[12px]">{status.icon}</span>
                                {status.label}
                            </span>
                        </div>
                    )}
                </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
                {onAccept && (
                    <button
                        onClick={onAccept}
                        className="bg-secondary text-on-secondary px-4 py-2 rounded-xl font-bold text-sm shadow-md shadow-secondary/20 hover:scale-[0.98] active:scale-95 transition-all flex items-center gap-1.5"
                    >
                        <span className="material-symbols-outlined text-[16px]">person_add</span>
                        Назначить
                    </button>
                )}
                {children}
            </div>
        </div>
    );
}
