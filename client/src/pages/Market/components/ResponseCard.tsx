type Props = {
  response: any;
  onAccept?: () => void;
};

export function ResponseCard({
  response,
  onAccept,
}: Props) {
  return (
    <div className="bg-white rounded-2xl p-5 border">
      <div className="flex justify-between items-center">
        <div>
          <div className="font-bold text-indigo-900">
            {response.team.name}
          </div>

          <div className="text-sm text-gray-500">
            {response.status}
          </div>
        </div>

        {onAccept && (
          <button
            onClick={onAccept}
            className="bg-green-600 text-white px-4 py-2 rounded-xl"
          >
            Назначить
          </button>
        )}
      </div>
    </div>
  );
}