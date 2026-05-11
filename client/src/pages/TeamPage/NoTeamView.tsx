import {
  acceptInvitation,
  declineInvitation,
  createTeam,
} from '../../api/teams';

type Props = {
  invitations: any[];
  onReload: () => void;
};

export const NoTeamView = ({
  invitations,
  onReload,
}: Props) => {
  const handleCreate = async () => {
    const name = prompt("Название команды");

    if (!name) return;

    await createTeam(name);

    onReload();
  };

  return (
    <div className="space-y-6">
      <button
        onClick={handleCreate}
        className="bg-blue-600 text-white px-4 py-2 rounded-xl"
      >
        Создать команду
      </button>

      <div>
        <h2 className="text-2xl font-bold mb-4">
          Приглашения
        </h2>

        <div className="space-y-3">
          {invitations.map((invite: any) => (
            <div
              key={invite.id}
              className="p-4 rounded-2xl border flex items-center justify-between"
            >
              <div>
                {invite.team.name}
              </div>

              <div className="flex gap-2">
                <button
                  onClick={async () => {
                    await acceptInvitation(invite.id);
                    onReload();
                  }}
                  className="bg-green-600 text-white px-3 py-1 rounded-lg"
                >
                  Принять
                </button>

                <button
                  onClick={async () => {
                    await declineInvitation(invite.id);
                    onReload();
                  }}
                  className="bg-red-600 text-white px-3 py-1 rounded-lg"
                >
                  Отклонить
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};