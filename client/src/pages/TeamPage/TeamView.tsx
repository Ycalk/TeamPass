import { useState } from 'react';
import { leaveTeam } from '../../api/teams';
import { CaptainPanel } from './CaptainPanel';
import { MemberCard } from './MemberCard';
import { ConfirmModal } from '../../components/ConfirmModal';
import { Menu, MenuButton, MenuItem, MenuItems, Transition } from '@headlessui/react';
import { Fragment } from 'react';

type Props = {
    team: any;
    isCaptain: boolean;
    onReload: () => void;
};

export const TeamView = ({ team, isCaptain, onReload }: Props) => {
    const [showLeaveModal, setShowLeaveModal] = useState(false);
    const [leaving, setLeaving] = useState(false);

    const sortedMembers = [...team.members]
        .filter((member: any, index: number, arr: any[]) => arr.findIndex((m) => m.id === member.id) === index)
        .sort((a, b) => {
            if (String(a.id) === String(team.captain.id)) return -1;
            if (String(b.id) === String(team.captain.id)) return 1;
            return 0;
        });

    const handleLeave = async () => {
        setLeaving(true);
        try {
            await leaveTeam();
            setShowLeaveModal(false);
            onReload();
        } finally {
            setLeaving(false);
        }
    };

    return (
        <>
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                <div className="xl:col-span-2 space-y-6">
                    <div className="bg-surface-container-lowest rounded-[2rem] shadow-2xl shadow-primary/5 border border-outline-variant/15 p-8 relative">
                        <div className="absolute top-[-15%] right-[-5%] w-[200px] h-[200px] bg-primary/5 rounded-full blur-[60px] pointer-events-none" />

                        <div className="relative z-10">
                            <div className="flex justify-between items-start mb-8">
                                <div>
                                    <span className="text-xs font-bold text-primary uppercase tracking-widest mb-1.5 block">Ваша команда</span>
                                    <h1 className="text-4xl font-black text-on-surface font-headline tracking-tight">
                                        {team.name}
                                    </h1>
                                </div>

                                <Menu as="div" className="relative">
                                    <MenuButton className="w-10 h-10 flex items-center justify-center rounded-xl text-on-surface-variant hover:bg-surface-container hover:text-primary transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/50">
                                        <span className="material-symbols-outlined">more_horiz</span>
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
                                        <MenuItems className="absolute right-0 mt-2 w-56 origin-top-right bg-surface-container-lowest border border-outline-variant/15 rounded-xl shadow-lg shadow-primary/5 p-1.5 focus:outline-none z-10">
                                            <MenuItem>
                                                {({ focus }) => (
                                                    <button
                                                        onClick={() => setShowLeaveModal(true)}
                                                        className={`w-full flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${focus ? 'bg-error/10 text-error' : 'text-error/80'
                                                            }`}
                                                    >
                                                        <span className="material-symbols-outlined mr-2 text-[18px]">logout</span>
                                                        Покинуть команду
                                                    </button>
                                                )}
                                            </MenuItem>
                                        </MenuItems>
                                    </Transition>
                                </Menu>
                            </div>

                            <div>
                                <h2 className="text-lg font-bold mb-4 text-on-surface font-headline flex items-center gap-2">
                                    <span className="material-symbols-outlined text-primary/70 text-[22px]">group</span>
                                    Участники ({sortedMembers.length})
                                </h2>
                                <div className="grid gap-3">
                                    {sortedMembers.map((member: any) => (
                                        <MemberCard
                                            key={member.id}
                                            member={member}
                                            isCaptain={isCaptain}
                                            captainId={team.captain.id}
                                            onReload={onReload}
                                        />
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {isCaptain && (
                    <div className="xl:col-span-1">
                        <CaptainPanel team={team} onReload={onReload} />
                    </div>
                )}
            </div>

            <ConfirmModal
                open={showLeaveModal}
                onClose={() => setShowLeaveModal(false)}
                onConfirm={handleLeave}
                title="Покинуть команду?"
                description="Вы уверены, что хотите покинуть команду? Это действие нельзя отменить."
                confirmText="Покинуть"
                cancelText="Отмена"
                variant="danger"
                icon="logout"
                loading={leaving}
            />
        </>
    );
};
