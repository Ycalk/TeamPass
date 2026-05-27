type Props = {
  listing: any;
  onRespond?: () => void;
};

export function ListingCard({
  listing,
  onRespond,
}: Props) {
  return (
    <div className="bg-white rounded-3xl p-6 border">
      <div className="flex justify-between">
        <div>
          <h2 className="text-2xl font-bold text-indigo-900">
            {listing.title}
          </h2>

          <p className="text-gray-500 mt-1">
            {listing.team.name}
          </p>
        </div>

        <div className="text-sm text-gray-400">
          {new Date(
            listing.created_at * 1000
          ).toLocaleString()}
        </div>
      </div>

      <p className="mt-5 whitespace-pre-wrap">
        {listing.description}
      </p>

      {onRespond && (
        <button
          onClick={onRespond}
          className="mt-6 bg-indigo-900 text-white px-5 py-3 rounded-2xl"
        >
          Откликнуться
        </button>
      )}
    </div>
  );
}