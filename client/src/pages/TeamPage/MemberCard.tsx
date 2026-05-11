import {
  removeMember,
  transferCaptaincy,
} from "../../api/teams";

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
  const isCurrentCaptain =
    member.id === captainId;

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
        <div className="flex gap-2">
          <button
            onClick={async () => {
              await transferCaptaincy(
                member.id
              );

              onReload();
            }}
            className="px-3 py-1 rounded-lg bg-yellow-500 text-white"
          >
            Передать капитанство
          </button>

          <button
            onClick={async () => {
              await removeMember(member.id);

              onReload();
            }}
            className="px-3 py-1 rounded-lg bg-red-500 text-white"
          >
            Удалить
          </button>
        </div>
      )}
    </div>
  );
};