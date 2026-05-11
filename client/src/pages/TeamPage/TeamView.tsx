import { leaveTeam } from '../../api/teams';
import { CaptainPanel } from './CaptainPanel';
import { MemberCard } from './MemberCard';

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
  return (
    <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
      <div className="xl:col-span-2">
        <div className="bg-white rounded-3xl p-8">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-4xl font-bold">
              {team.name}
            </h1>

            <button
              onClick={async () => {
                await leaveTeam();
                window.location.reload();
              }}
              className="text-red-500"
            >
              Выйти
            </button>
          </div>

          <div className="space-y-4">
            {team.members.map((member: any) => (
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