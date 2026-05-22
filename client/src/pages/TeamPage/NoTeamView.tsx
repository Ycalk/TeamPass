import { acceptInvitation, declineInvitation, createTeam } from '../../api/teams';

type Props = {
    invitations: any[];
    onReload: () => void;
};

export const NoTeamView = ({ invitations, onReload }: Props) => {
    const handleCreate = async () => {
        const name = prompt("Введите название новой команды:");
        if (!name || !name.trim()) return;
        await createTeam(name.trim());
        onReload();
    };

    return (
        <div className="max-w-3xl mx-auto mt-10">
            <div className="bg-surface-container-lowest border border-outline-variant/20 rounded-3xl p-10 text-center mb-8 shadow-sm">
                <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                    <span className="material-symbols-outlined text-4xl text-primary">group_add</span>
                </div>
                <h1 className="text-3xl font-black text-on-surface mb-3 font-headline">Вы не состоите в команде</h1>
                <p className="text-on-surface-variant mb-8 max-w-md mx-auto">
                    Создайте собственную команду, чтобы стать капитаном, или примите одно из приглашений ниже.
                </p>
                <button
                    onClick={handleCreate}
                    className="bg-primary text-on-primary px-6 py-3 rounded-xl font-bold flex items-center mx-auto hover:bg-primary/90 transition-colors shadow-md shadow-primary/20"
                >
                    <span className="material-symbols-outlined mr-2 text-[20px]">add</span>
                    Создать команду
                </button>
            </div>

            {invitations.length > 0 && (
                <div>
                    <h2 className="text-xl font-bold mb-4 flex items-center text-on-surface">
                        <span className="material-symbols-outlined mr-2 text-primary">mail</span>
                        Входящие приглашения ({invitations.length})
                    </h2>
                    <div className="grid gap-4">
                        {invitations.map((invite: any) => (
                            <div
                                key={invite.id}
                                className="bg-surface-container-lowest border border-outline-variant/20 p-5 rounded-2xl flex items-center justify-between shadow-sm hover:shadow-md transition-shadow"
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
                                        className="bg-primary/10 text-primary hover:bg-primary hover:text-on-primary px-4 py-2 rounded-xl font-medium transition-colors"
                                    >
                                        Принять
                                    </button>
                                    <button
                                        onClick={async () => {
                                            await declineInvitation(invite.id);
                                            onReload();
                                        }}
                                        className="bg-error/10 text-error hover:bg-error hover:text-on-error px-4 py-2 rounded-xl font-medium transition-colors"
                                    >
                                        Отклонить
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};