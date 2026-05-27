import { useEffect, useState } from 'react';

import {
  createDeal,
  getListingDeal,
  getListingResponses,
  getMyListings,
} from '../../api/market';

import { ListingCard } from './components/ListingCard';
import { ResponseCard } from './components/ResponseCard';

export function MarketMyListings() {
  const [items, setItems] = useState<
    any[]
  >([]);

  const load = async () => {
    const res =
      await getMyListings();

    const listings = res.data;

    const mapped = await Promise.all(
      listings.map(async (listing: any) => {
        const responses =
          await getListingResponses(
            listing.id
          );

        const accepted =
          responses.data.find(
            (r: any) =>
              r.status === 'accepted'
          );

        let deal = null;

        if (accepted) {
          try {
            const dealRes =
              await getListingDeal(
                listing.id
              );

            deal = dealRes.data;
          } catch {}
        }

        return {
          ...listing,
          responses: responses.data,
          deal,
        };
      })
    );

    setItems(mapped);
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-8">
      {items.map((listing) => (
        <div
          key={listing.id}
          className="space-y-4"
        >
          <ListingCard
            listing={listing}
          />

          <div className="space-y-3">
            {listing.responses.map(
              (response: any) => (
                <ResponseCard
                  key={response.id}
                  response={response}
                  onAccept={
                    response.status ===
                    'pending'
                      ? async () => {
                          await createDeal(
                            response.id
                          );

                          load();
                        }
                      : undefined
                  }
                />
              )
            )}
          </div>

          {listing.deal && (
            <div className="bg-green-100 p-4 rounded-2xl">
              Сделка:{' '}
              {listing.deal.status}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}