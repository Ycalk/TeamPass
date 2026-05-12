import { leaveTeam } from '../../api/teams';
import { CaptainPanel } from './CaptainPanel';
import { MemberCard } from './MemberCard';
import { useState } from 'react';

type Props = {
  team: any;
  isCaptain: boolean;
  onReload: () => void;
};

export const TeamView = ({
  team,
  isCaptain,
  onReload,
}: Props) => {
    const [menuOpen, setMenuOpen] = useState(false);

    return (
    <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
      <div className="xl:col-span-2">
        <div className="bg-white rounded-3xl p-8">
          <div className="flex justify-between items-start mb-6">
            <h1 className="text-4xl font-bold">
                {team.name}
            </h1>

            <div className="relative">
                <button
                onClick={() =>
                    setMenuOpen(!menuOpen)
                }
                className="text-3xl leading-none"
                >
                ☰
                </button>

                {menuOpen && (
                <div className="absolute right-0 mt-2 bg-white border rounded-xl shadow-lg p-2 z-10">
                    <button
                    onClick={async () => {
                        await leaveTeam();

                        window.location.reload();
                    }}
                    className="text-red-500 whitespace-nowrap"
                    >
                    Выйти из команды
                    </button>
                </div>
                )}
            </div>
            </div>

          <div className="space-y-4">
            {team.members
                .filter(
                (
                    member: any,
                    index: number,
                    arr: any[]
                ) =>
                    arr.findIndex(
                    (m) => m.id === member.id
                    ) === index
                )
                .map((member: any) => (
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

      {isCaptain && (
        <CaptainPanel
          team={team}
          onReload={onReload}
        />
      )}
    </div>
  );
};