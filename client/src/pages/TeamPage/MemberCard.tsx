import {
  removeMember,
  transferCaptaincy,
} from "../../api/teams";
import { useState } from 'react';

type Props = {
  member: any;
  captainId: string;
  isCaptain: boolean;
  onReload: () => void;
};

export const MemberCard = ({
  member,
  captainId,
  isCaptain,
  onReload,
}: Props) => {
    const [menuOpen, setMenuOpen] = useState(false);

    const isCurrentCaptain =
        String(member.id) === String(captainId);

    const fullName = `
        ${member.student.last_name}
        ${member.student.first_name}
        ${member.student.patronymic}
    `;

  return (
    <div className="flex justify-between items-center border rounded-2xl p-4">
      <div>
        <div className="font-semibold">
          {fullName}
        </div>

        <div className="text-sm text-gray-500">
          {isCurrentCaptain
            ? "Капитан"
            : "Участник"}
        </div>
      </div>

    {isCaptain && !isCurrentCaptain && (
        <div className="relative">
            <button
            onClick={() =>
                setMenuOpen(!menuOpen)
            }
            className="text-2xl"
            >
            ⚙
            </button>

            {menuOpen && (
            <div className="absolute right-0 mt-2 bg-white border rounded-xl shadow-lg p-2 z-10 min-w-[220px]">
                <button
                onClick={async () => {
                    try {
                    await transferCaptaincy(
                        member.id
                    );

                    onReload();
                    } catch {
                    alert(
                        "Ошибка передачи капитанства"
                    );
                    }
                }}
                className="block w-full text-left px-3 py-2 hover:bg-gray-100 rounded-lg"
                >
                Передать капитанство
                </button>

                <button
                onClick={async () => {
                    try {
                    await removeMember(
                        member.id
                    );

                    onReload();
                    } catch {
                    alert(
                        "Ошибка удаления участника"
                    );
                    }
                }}
                className="block w-full text-left px-3 py-2 hover:bg-gray-100 rounded-lg text-red-500"
                >
                Удалить из команды
                </button>
            </div>
            )}
        </div>
        )}
    </div>
  );
};