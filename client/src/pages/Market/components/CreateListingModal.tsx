import { Dialog, DialogBackdrop, DialogPanel, Transition, TransitionChild } from '@headlessui/react';
import { Fragment, useEffect, useState } from 'react';

type Props = {
    open: boolean;
    onClose: () => void;
    onSubmit: (title: string, description: string) => void;
    loading?: boolean;
};

export const CreateListingModal = ({ open, onClose, onSubmit, loading = false }: Props) => {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');

    useEffect(() => {
        if (open) {
            setTitle('');
            setDescription('');
        }
    }, [open]);

    const handleSubmit = () => {
        if (!title.trim() || !description.trim()) return;
        onSubmit(title.trim(), description.trim());
    };

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
                        <DialogPanel className="w-full max-w-lg bg-surface-container-lowest rounded-3xl shadow-2xl shadow-primary/10 border border-outline-variant/15 p-8">
                            <div className="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-5 bg-primary/10 text-primary">
                                <span className="material-symbols-outlined text-[28px]">post_add</span>
                            </div>

                            <h3 className="text-xl font-bold text-on-surface text-center font-headline mb-6">
                                Новый запрос
                            </h3>

                            <div className="space-y-4 mb-6">
                                <div>
                                    <label className="text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-2 block">
                                        Название
                                    </label>
                                    <input
                                        value={title}
                                        onChange={(e) => setTitle(e.target.value)}
                                        placeholder="Что вам нужно?"
                                        className="w-full rounded-xl px-4 py-3 bg-surface-container-low border border-outline-variant/30 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all text-sm text-on-surface"
                                    />
                                </div>

                                <div>
                                    <label className="text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-2 block">
                                        Описание
                                    </label>
                                    <textarea
                                        value={description}
                                        onChange={(e) => setDescription(e.target.value)}
                                        placeholder="Опишите задачу подробнее..."
                                        rows={4}
                                        className="w-full rounded-xl px-4 py-3 bg-surface-container-low border border-outline-variant/30 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all text-sm text-on-surface resize-none"
                                    />
                                </div>
                            </div>

                            <div className="flex gap-3">
                                <button
                                    onClick={onClose}
                                    disabled={loading}
                                    className="flex-1 px-4 py-3 rounded-xl font-bold text-sm text-on-surface-variant hover:bg-surface-container transition-colors disabled:opacity-50"
                                >
                                    Отмена
                                </button>
                                <button
                                    onClick={handleSubmit}
                                    disabled={!title.trim() || !description.trim() || loading}
                                    className="flex-1 px-4 py-3 rounded-xl font-bold text-sm bg-primary text-on-primary hover:bg-primary/90 shadow-md shadow-primary/20 transition-all disabled:opacity-50 disabled:shadow-none"
                                >
                                    {loading ? (
                                        <span className="material-symbols-outlined animate-spin text-[20px] mx-auto block">progress_activity</span>
                                    ) : (
                                        'Создать запрос'
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
