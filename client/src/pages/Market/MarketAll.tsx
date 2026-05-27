import { useEffect, useState } from 'react';

import {
  createListing,
  createResponse,
  getListings,
  getTokens,
} from '../../api/market';

import { ListingCard } from './components/ListingCard';

export function MarketAll() {
  const [listings, setListings] =
    useState<any[]>([]);

  const [tokens, setTokens] =
    useState<any>(null);

  const [title, setTitle] = useState('');

  const [description, setDescription] =
    useState('');

  const load = async () => {
    const listingsRes =
      await getListings();

    const tokensRes = await getTokens();

    setListings(listingsRes.data);

    setTokens(tokensRes.data);
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-8">
      <div className="bg-white rounded-3xl p-6">
        <div className="text-xl font-bold">
          Токены команды
        </div>

        <div className="mt-3">
          Свободно: {tokens?.free_tokens}
        </div>

        <div>
          Зарезервировано:{' '}
          {tokens?.reserved_tokens}
        </div>
      </div>

      <div className="bg-white rounded-3xl p-6">
        <h2 className="text-2xl font-bold mb-5">
          Создать запрос
        </h2>

        <input
          value={title}
          onChange={(e) =>
            setTitle(e.target.value)
          }
          placeholder="Название"
          className="w-full border rounded-2xl px-4 py-3 mb-4"
        />

        <textarea
          value={description}
          onChange={(e) =>
            setDescription(
              e.target.value
            )
          }
          placeholder="Описание"
          className="w-full border rounded-2xl px-4 py-3"
        />

        <button
          onClick={async () => {
            await createListing(
              title,
              description
            );

            setTitle('');
            setDescription('');

            load();
          }}
          className="mt-5 bg-indigo-900 text-white px-5 py-3 rounded-2xl"
        >
          Создать
        </button>
      </div>

      <div className="space-y-5">
        {listings.map((listing) => (
          <ListingCard
            key={listing.id}
            listing={listing}
            onRespond={async () => {
              await createResponse(
                listing.id
              );

              alert(
                'Отклик отправлен'
              );
            }}
          />
        ))}
      </div>
    </div>
  );
}