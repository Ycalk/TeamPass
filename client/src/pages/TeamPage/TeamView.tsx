import { leaveTeam } from '../../api/teams';
import { CaptainPanel } from './CaptainPanel';
import { MemberCard } from './MemberCard';
import { Menu, MenuButton, MenuItem, MenuItems, Transition } from '@headlessui/react';
import { Fragment } from 'react';

type Props = {
    team: any;
    isCaptain: boolean;
    onReload: () => void;
};

export const TeamView = ({ team, isCaptain, onReload }: Props) => {
    // Сортировка: капитан всегда первый
    const sortedMembers = [...team.members]
        .filter((member: any, index: number, arr: any[]) => arr.findIndex((m) => m.id === member.id) === index)
        .sort((a, b) => {
            if (String(a.id) === String(team.captain.id)) return -1;
            if (String(b.id) === String(team.captain.id)) return 1;
            return 0;
        });

    return (
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
            <div className="xl:col-span-2 space-y-6">
                <div className="bg-surface-container-lowest border border-outline-variant/20 rounded-3xl p-8 shadow-sm">
                    <div className="flex justify-between items-start mb-8">
                        <div>
                            <span className="text-sm font-bold text-primary uppercase tracking-wider mb-1 block">Ваша команда</span>
                            <h1 className="text-4xl font-black text-on-surface font-headline">
                                {team.name}
                            </h1>
                        </div>

                        <Menu as="div" className="relative">
                            <MenuButton className="w-10 h-10 flex items-center justify-center rounded-xl text-on-surface-variant hover:bg-surface-container hover:text-primary transition-colors focus:outline-none">
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
                                <MenuItems className="absolute right-0 mt-2 w-56 origin-top-right bg-surface-container-lowest border border-outline-variant/20 rounded-xl shadow-lg p-1.5 focus:outline-none z-10">
                                    <MenuItem>
                                        {({ focus }) => (
                                            <button
                                                onClick={async () => {
                                                    if (window.confirm("Вы уверены, что хотите покинуть команду?")) {
                                                        await leaveTeam();
                                                        window.location.reload();
                                                    }
                                                }}
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
                        <h2 className="text-lg font-bold mb-4 text-on-surface">
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

            {isCaptain && (
                <div className="xl:col-span-1">
                    <CaptainPanel team={team} onReload={onReload} />
                </div>
            )}
        </div>
    );
};