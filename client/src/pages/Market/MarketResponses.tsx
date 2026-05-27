import { useEffect, useState } from 'react';

import {
  completeDeal,
  createDealReport,
  getDealReport,
  getMyResponses,
  getResponseDeal,
  updateDealReport,
} from '../../api/market';

import { DealReportEditor } from './components/DealReportEditor';

export function MarketResponses() {
  const [items, setItems] = useState<
    any[]
  >([]);

  const load = async () => {
    const res =
      await getMyResponses();

    const mapped = await Promise.all(
      res.data.map(
        async (response: any) => {
          if (
            response.status !==
            'accepted'
          ) {
            return response;
          }

          const deal =
            await getResponseDeal(
              response.id
            );

          return {
            ...response,
            deal: deal.data,
          };
        }
      )
    );

    setItems(mapped);
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-8">
      {items.map((item) => (
        <div
          key={item.id}
          className="bg-white rounded-3xl p-6"
        >
          <div className="font-bold text-2xl">
            {item.team.name}
          </div>

          <div className="mt-2">
            Статус: {item.status}
          </div>

          {item.deal?.status ===
            'in_progress' && (
            <DealBlock
              dealId={item.deal.id}
            />
          )}

          {item.deal?.status ===
            'completed' && (
            <div className="mt-4 text-green-700 font-bold">
              Завершено
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function DealBlock({
  dealId,
}: {
  dealId: string;
}) {
  const [data, setData] =
    useState<any>();

  useEffect(() => {
    load();
  }, []);

  const load = async () => {
    try {
      const res =
        await getDealReport(dealId);

      setData(res.data);
    } catch {}
  };

  const save = async (content: any) => {
    try {
      await updateDealReport(
        dealId,
        content
      );
    } catch {
      await createDealReport(
        dealId,
        content
      );
    }
  };

  return (
    <div className="mt-6">
      <DealReportEditor
        data={data}
        onChange={(content) => {
          setData(content);

          save(content);
        }}
      />

      <button
        onClick={async () => {
          await completeDeal(dealId);

          alert(
            'Отчет отправлен'
          );
        }}
        className="mt-5 bg-indigo-900 text-white px-5 py-3 rounded-2xl"
      >
        Отправить отчет
      </button>
    </div>
  );
}