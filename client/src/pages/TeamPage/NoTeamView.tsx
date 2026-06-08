import { useState } from 'react';
import { acceptInvitation, declineInvitation, createTeam } from '../../api/teams';
import { PromptModal } from '../../components/PromptModal';

type Props = {
    invitations: any[];
    onReload: () => void;
};

export const NoTeamView = ({ invitations, onReload }: Props) => {
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [creating, setCreating] = useState(false);

    const handleCreate = async (name: string) => {
        setCreating(true);
        try {
            await createTeam(name);
            setShowCreateModal(false);
            onReload();
        } finally {
            setCreating(false);
        }
    };

    return (
        <div className="max-w-3xl mx-auto mt-10">
            <div className="bg-surface-container-lowest overflow-hidden rounded-[2rem] shadow-2xl shadow-primary/5 border border-outline-variant/15 p-10 text-center mb-8 relative">
                <div className="absolute top-[-20%] right-[-10%] w-[200px] h-[200px] bg-primary/5 rounded-full blur-[60px] pointer-events-none" />
                <div className="absolute bottom-[-15%] left-[-10%] w-[180px] h-[180px] bg-secondary-fixed/10 rounded-full blur-[50px] pointer-events-none" />

                <div className="relative z-10">
                    <div className="w-20 h-20 bg-primary/10 rounded-[1.5rem] flex items-center justify-center mx-auto mb-6 shadow-inner border border-primary/20">
                        <span className="material-symbols-outlined text-4xl text-primary">group_add</span>
                    </div>
                    <h1 className="text-3xl font-black text-on-surface mb-3 font-headline">Вы не состоите в команде</h1>
                    <p className="text-on-surface-variant mb-8 max-w-md mx-auto leading-relaxed">
                        Создайте собственную команду, чтобы стать капитаном, или примите одно из приглашений ниже.
                    </p>
                    <button
                        onClick={() => setShowCreateModal(true)}
                        className="bg-gradient-to-r from-primary to-primary-container text-on-primary px-8 py-3.5 rounded-xl font-bold flex items-center mx-auto hover:scale-[0.98] active:scale-95 transition-all shadow-lg shadow-primary/20"
                    >
                        <span className="material-symbols-outlined mr-2 text-[20px]">add</span>
                        Создать команду
                    </button>
                </div>
            </div>

            {invitations.length > 0 && (
                <div>
                    <h2 className="text-xl font-bold mb-4 flex items-center text-on-surface font-headline">
                        <span className="material-symbols-outlined mr-2 text-primary">mail</span>
                        Входящие приглашения ({invitations.length})
                    </h2>
                    <div className="grid gap-4">
                        {invitations.map((invite: any) => (
                            <div
                                key={invite.id}
                                className="bg-surface-container-lowest border border-outline-variant/15 p-5 rounded-2xl flex items-center justify-between shadow-sm hover:shadow-md hover:shadow-primary/5 transition-all"
                            >
                                <div className="flex items-center">
                                    <div className="w-12 h-12 bg-secondary/10 rounded-xl flex items-center justify-center mr-4 text-secondary">
                                        <span className="material-symbols-outlined">flag</span>
                                    </div>
                                    <div>
                                        <div className="font-bold text-lg text-on-surface">{invite.team.name}</div>
                                        <div className="text-sm text-on-surface-variant">Приглашение в команду</div>
                                    </div>
                                </div>
                                <div className="flex gap-2">
                                    <button
                                        onClick={async () => {
                                            await acceptInvitation(invite.id);
                                            onReload();
                                        }}
                                        className="bg-primary/10 text-primary hover:bg-primary hover:text-on-primary px-5 py-2.5 rounded-xl font-bold text-sm transition-all"
                                    >
                                        Принять
                                    </button>
                                    <button
                                        onClick={async () => {
                                            await declineInvitation(invite.id);
                                            onReload();
                                        }}
                                        className="bg-error/10 text-error hover:bg-error hover:text-on-error px-5 py-2.5 rounded-xl font-bold text-sm transition-all"
                                    >
                                        Отклонить
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <PromptModal
                open={showCreateModal}
                onClose={() => setShowCreateModal(false)}
                onSubmit={handleCreate}
                title="Новая команда"
                label="Название команды"
                placeholder="Введите название..."
                confirmText="Создать"
                icon="group_add"
                loading={creating}
            />
        </div>
    );
};
