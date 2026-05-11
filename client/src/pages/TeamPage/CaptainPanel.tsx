import { useEffect, useState } from "react";

import {
  changeTeamName,
  deleteTeamInvitation,
  getTeamInvitations,
  searchUsers,
  sendInvitation,
} from "../../api/teams";

type Props = {
  team: any;
  onReload: () => void;
};

export const CaptainPanel = ({
  team,
  onReload,
}: Props) => {
  const [name, setName] = useState(team.name);

  const [query, setQuery] = useState("");

  const [users, setUsers] = useState<any[]>([]);

  const [selectedUser, setSelectedUser] =
    useState<any>(null);

  const [invites, setInvites] = useState<any[]>(
    []
  );

  useEffect(() => {
    loadInvites();
  }, []);

  const loadInvites = async () => {
    try {
        const res =
        await getTeamInvitations();

        setInvites(res.data);
    } catch (e) {
        console.error(e);

        setInvites([]);
    }
    };

  useEffect(() => {
    if (!query) {
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
  }, [query]);

  return (
    <section className="bg-indigo-900 text-white rounded-[2rem] p-8">
      <h2 className="text-2xl font-bold mb-6">
        Панель капитана
      </h2>

      <div className="mb-8">
        <label className="text-xs uppercase">
          Название команды
        </label>

        <div className="flex gap-2 mt-2">
          <input
            value={name}
            onChange={(e) =>
              setName(e.target.value)
            }
            className="w-full rounded-xl px-4 py-3 text-black"
          />

          <button
            onClick={async () => {
              await changeTeamName(name);

              onReload();
            }}
            className="bg-yellow-400 text-black px-4 rounded-xl"
          >
            ✎
          </button>
        </div>
      </div>

      <div>
        <label className="text-xs uppercase">
          Пригласить в команду
        </label>

        <input
          value={query}
          onChange={(e) =>
            setQuery(e.target.value)
          }
          placeholder="ФИО или № студенческого"
          className="w-full mt-2 rounded-xl px-4 py-3 text-black"
        />

        {!!users.length && (
          <div className="bg-white rounded-xl mt-2 overflow-hidden">
            {users.map((user) => {
              const fullName = `
                ${user.student.last_name}
                ${user.student.first_name}
                ${user.student.patronymic}
              `;

              return (
                <button
                  key={user.id}
                  onClick={() => {
                    setSelectedUser(user);

                    setQuery(fullName);

                    setUsers([]);
                  }}
                  className="w-full text-left px-4 py-3 hover:bg-gray-100 text-black"
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
                await sendInvitation(
                selectedUser.id
                );

                setQuery("");

                setSelectedUser(null);

                await loadInvites();
            } catch (e: any) {
                console.error(e);

                if (e.response?.status === 409) {
                alert(
                    "Пользователь уже приглашен или состоит в команде"
                );

                return;
                }

                alert(
                "Ошибка отправки приглашения"
                );
            }
            }}
          className="w-full mt-4 bg-white text-indigo-900 py-4 rounded-2xl disabled:opacity-50"
        >
          Отправить приглашение
        </button>
      </div>

      <div className="mt-8">
        <h3 className="mb-4 font-bold">
          Приглашения
        </h3>

        <div className="space-y-3">
          {invites.map((invite) => {
            const fullName = `
              ${invite.user.student.last_name}
              ${invite.user.student.first_name}
              ${invite.user.student.patronymic}
            `;

            return (
              <div
                key={invite.id}
                className="flex items-center justify-between bg-white/10 p-3 rounded-xl"
              >
                <div>{fullName}</div>

                <button
                  onClick={async () => {
                    await deleteTeamInvitation(
                      invite.id
                    );

                    loadInvites();
                  }}
                  className="text-red-400"
                >
                  ✕
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};