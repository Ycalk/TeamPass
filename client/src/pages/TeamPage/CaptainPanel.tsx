import { useEffect, useState } from "react";
import {
    changeTeamName, deleteTeamInvitation, getTeamInvitations,
    searchUsers, sendInvitation,
} from "../../api/teams";

type Props = { team: any; onReload: () => void; };

export const CaptainPanel = ({ team, onReload }: Props) => {
    const [name, setName] = useState(team.name);
    const [query, setQuery] = useState("");
    const [users, setUsers] = useState<any[]>([]);
    const [selectedUser, setSelectedUser] = useState<any>(null);
    const [invites, setInvites] = useState<any[]>([]);
    const [isSaving, setIsSaving] = useState(false);

    useEffect(() => { loadInvites(); }, []);

    const loadInvites = async () => {
        try {
            const res = await getTeamInvitations();
            setInvites(res.data);
        } catch (e) {
            setInvites([]);
        }
    };

    useEffect(() => {
        if (!query || selectedUser) {
            setUsers([]);
            return;
        }
        const timeout = setTimeout(async () => {
            try {
                const res = await searchUsers(query);
                setUsers(res.data);
            } catch {
                setUsers([]);
            }
        }, 300);
        return () => clearTimeout(timeout);
    }, [query, selectedUser]);

    return (
        <aside className="bg-surface-container border border-outline-variant/20 rounded-3xl p-6 h-fit">
            <h2 className="text-xl font-bold mb-6 flex items-center text-on-surface">
                <span className="material-symbols-outlined mr-2 text-primary">admin_panel_settings</span>
                Управление
            </h2>

            <div className="mb-6">
                <label className="text-xs font-bold text-on-surface-variant uppercase tracking-wider mb-2 block">
                    Название команды
                </label>
                <div className="flex gap-2">
                    <input
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        className="w-full rounded-xl px-4 py-2.5 bg-surface-container-lowest border border-outline-variant/30 focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all text-sm"
                    />
                    <button
                        onClick={async () => {
                            if (name === team.name) return;
                            setIsSaving(true);
                            await changeTeamName(name);
                            setIsSaving(false);
                            onReload();
                        }}
                        disabled={name === team.name || isSaving}
                        className="bg-primary text-on-primary px-3 rounded-xl hover:bg-primary/90 disabled:opacity-50 transition-colors flex items-center justify-center shrink-0"
                    >
                        <span className="material-symbols-outlined text-[20px]">
                            {isSaving ? 'sync' : 'save'}
                        </span>
                    </button>
                </div>
            </div>

            <div className="mb-8 relative">
                <label className="text-xs font-bold text-on-surface-variant uppercase tracking-wider mb-2 block">
                    Пригласить участника
                </label>
                <div className="relative">
                    <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant">search</span>
                    <input
                        value={query}
                        onChange={(e) => {
                            setQuery(e.target.value);
                            setSelectedUser(null);
                        }}
                        placeholder="ФИО или номер..."
                        className="w-full rounded-xl pl-10 pr-4 py-2.5 bg-surface-container-lowest border border-outline-variant/30 focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all text-sm"
                    />
                </div>

                {users.length > 0 && !selectedUser && (
                    <div className="absolute top-full left-0 right-0 mt-2 bg-surface-container-lowest border border-outline-variant/20 rounded-xl shadow-lg max-h-48 overflow-y-auto z-20">
                        {users.map((user) => {
                            const fullName = `${user.student.last_name} ${user.student.first_name} ${user.student.patronymic || ""}`.trim();
                            return (
                                <button
                                    key={user.id}
                                    onClick={() => {
                                        setSelectedUser(user);
                                        setQuery(fullName);
                                        setUsers([]);
                                    }}
                                    className="w-full text-left px-4 py-3 hover:bg-surface-container text-sm text-on-surface border-b border-outline-variant/10 last:border-0 transition-colors"
                                >
                                    {fullName}
                                </button>
                            );
                        })}
                    </div>
                )}

                <button
                    disabled={!selectedUser}
                    onClick={async () => {
                        try {
                            await sendInvitation(selectedUser.id);
                            setQuery("");
                            setSelectedUser(null);
                            await loadInvites();
                        } catch (e: any) {
                            if (e.response?.status === 409) {
                                alert("Пользователь уже приглашен или состоит в команде");
                            } else {
                                alert("Ошибка отправки приглашения");
                            }
                        }
                    }}
                    className="w-full mt-3 bg-primary/10 text-primary hover:bg-primary hover:text-on-primary py-2.5 rounded-xl font-bold text-sm transition-colors disabled:opacity-50 disabled:hover:bg-primary/10 disabled:hover:text-primary flex items-center justify-center"
                >
                    <span className="material-symbols-outlined mr-2 text-[18px]">send</span>
                    Отправить
                </button>
            </div>

            <div>
                <h3 className="text-xs font-bold text-on-surface-variant uppercase tracking-wider mb-3">
                    Отправленные приглашения
                </h3>
                {invites.length === 0 ? (
                    <div className="text-sm text-on-surface-variant/70 text-center py-4">Нет активных приглашений</div>
                ) : (
                    <div className="space-y-2">
                        {invites.map((invite) => {
                            const fullName = `${invite.user.student.last_name} ${invite.user.student.first_name}`;
                            return (
                                <div key={invite.id} className="flex items-center justify-between bg-surface-container-lowest p-2.5 rounded-xl border border-outline-variant/20">
                                    <div className="text-sm font-medium truncate pr-2">{fullName}</div>
                                    {!invite.accepted_at && (
                                        <button
                                            onClick={async () => {
                                                try {
                                                    await deleteTeamInvitation(invite.id);
                                                    loadInvites();
                                                } catch (e: any) {
                                                    alert("Ошибка удаления приглашения");
                                                }
                                            }}
                                            className="text-on-surface-variant hover:text-error transition-colors p-1 rounded-lg hover:bg-error/10"
                                        >
                                            <span className="material-symbols-outlined text-[18px]">close</span>
                                        </button>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </aside>
    );
};