import { Dialog, DialogBackdrop, DialogPanel, Transition, TransitionChild } from '@headlessui/react';
import { Fragment } from 'react';

type Props = {
    open: boolean;
    onClose: () => void;
    onConfirm: () => void;
    title: string;
    description?: string;
    confirmText?: string;
    cancelText?: string;
    variant?: 'danger' | 'primary';
    icon?: string;
    loading?: boolean;
};

export const ConfirmModal = ({
    open,
    onClose,
    onConfirm,
    title,
    description,
    confirmText = 'Подтвердить',
    cancelText = 'Отмена',
    variant = 'primary',
    icon,
    loading = false,
}: Props) => {
    const isDanger = variant === 'danger';

    return (
        <Transition show={open} as={Fragment}>
            <Dialog onClose={onClose} className="relative z-[100]">
                <TransitionChild
                    as={Fragment}
                    enter="ease-out duration-200"
                    enterFrom="opacity-0"
                    enterTo="opacity-100"
                    leave="ease-in duration-150"
                    leaveFrom="opacity-100"
                    leaveTo="opacity-0"
                >
                    <DialogBackdrop className="fixed inset-0 bg-black/30 backdrop-blur-sm" />
                </TransitionChild>

                <div className="fixed inset-0 flex items-center justify-center p-4">
                    <TransitionChild
                        as={Fragment}
                        enter="ease-out duration-200"
                        enterFrom="opacity-0 scale-95 translate-y-4"
                        enterTo="opacity-100 scale-100 translate-y-0"
                        leave="ease-in duration-150"
                        leaveFrom="opacity-100 scale-100 translate-y-0"
                        leaveTo="opacity-0 scale-95 translate-y-4"
                    >
                        <DialogPanel className="w-full max-w-md bg-surface-container-lowest rounded-3xl shadow-2xl shadow-primary/10 border border-outline-variant/15 p-8">
                            {icon && (
                                <div className={`w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-5 ${isDanger ? 'bg-error/10 text-error' : 'bg-primary/10 text-primary'
                                    }`}>
                                    <span className="material-symbols-outlined text-[28px]">{icon}</span>
                                </div>
                            )}

                            <h3 className="text-xl font-bold text-on-surface text-center font-headline mb-2">
                                {title}
                            </h3>

                            {description && (
                                <p className="text-on-surface-variant text-sm text-center mb-8">
                                    {description}
                                </p>
                            )}

                            {!description && <div className="mb-8" />}

                            <div className="flex gap-3">
                                <button
                                    onClick={onClose}
                                    disabled={loading}
                                    className="flex-1 px-4 py-3 rounded-xl font-bold text-sm text-on-surface-variant hover:bg-surface-container transition-colors disabled:opacity-50"
                                >
                                    {cancelText}
                                </button>
                                <button
                                    onClick={onConfirm}
                                    disabled={loading}
                                    className={`flex-1 px-4 py-3 rounded-xl font-bold text-sm transition-all disabled:opacity-50 ${isDanger
                                            ? 'bg-error text-on-error hover:bg-error/90 shadow-md shadow-error/20'
                                            : 'bg-primary text-on-primary hover:bg-primary/90 shadow-md shadow-primary/20'
                                        }`}
                                >
                                    {loading ? (
                                        <span className="material-symbols-outlined animate-spin text-[20px] mx-auto block">progress_activity</span>
                                    ) : (
                                        confirmText
                                    )}
                                </button>
                            </div>
                        </DialogPanel>
                    </TransitionChild>
                </div>
            </Dialog>
        </Transition>
    );
};
