import { removeMember, transferCaptaincy } from "../../api/teams";
import { Menu, MenuButton, MenuItem, MenuItems, Transition } from '@headlessui/react';
import { Fragment } from 'react';

type Props = {
    member: any;
    captainId: string;
    isCaptain: boolean;
    onReload: () => void;
};

export const MemberCard = ({ member, captainId, isCaptain, onReload }: Props) => {
    const isCurrentCaptain = String(member.id) === String(captainId);
    const firstName = member.student.first_name || "";
    const lastName = member.student.last_name || "";
    const fullName = `${lastName} ${firstName} ${member.student.patronymic || ""}`.trim();
    const initials = (firstName.charAt(0) + (lastName.charAt(0) || "")).toUpperCase() || "С";

    return (
        <div className="flex justify-between items-center bg-surface-container-lowest border border-outline-variant/20 rounded-2xl p-4 hover:border-primary/30 transition-colors">
            <div className="flex items-center">
                <div className="w-12 h-12 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-lg mr-4 shrink-0">
                    {initials}
                </div>
                <div>
                    <div className="font-bold text-on-surface mb-0.5">{fullName}</div>
                    <div className="flex items-center">
                        {isCurrentCaptain ? (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-secondary/10 text-secondary">
                                <span className="material-symbols-outlined text-[14px] mr-1">stars</span>
                                Капитан
                            </span>
                        ) : (
                            <span className="text-sm text-on-surface-variant">Участник</span>
                        )}
                    </div>
                </div>
            </div>

            {isCaptain && !isCurrentCaptain && (
                <Menu as="div" className="relative">
                    <MenuButton className="p-2 rounded-xl text-on-surface-variant hover:bg-surface-container hover:text-primary transition-colors focus:outline-none">
                        <span className="material-symbols-outlined">more_vert</span>
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
                                            try {
                                                await transferCaptaincy(member.id);
                                                onReload();
                                            } catch {
                                                alert("Ошибка передачи капитанства");
                                            }
                                        }}
                                        className={`w-full flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${focus ? 'bg-surface-container text-primary' : 'text-on-surface'
                                            }`}
                                    >
                                        <span className="material-symbols-outlined mr-2 text-[18px]">manage_accounts</span>
                                        Передать капитанство
                                    </button>
                                )}
                            </MenuItem>
                            <div className="h-px bg-outline-variant/20 my-1 mx-2" />
                            <MenuItem>
                                {({ focus }) => (
                                    <button
                                        onClick={async () => {
                                            try {
                                                await removeMember(member.id);
                                                onReload();
                                            } catch {
                                                alert("Ошибка удаления участника");
                                            }
                                        }}
                                        className={`w-full flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${focus ? 'bg-error/10 text-error' : 'text-error/80'
                                            }`}
                                    >
                                        <span className="material-symbols-outlined mr-2 text-[18px]">person_remove</span>
                                        Удалить из команды
                                    </button>
                                )}
                            </MenuItem>
                        </MenuItems>
                    </Transition>
                </Menu>
            )}
        </div>
    );
};