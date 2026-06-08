import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { createDeal, getDealReport, getListingDeal, getListingResponses, getMyListings } from '../../api/market';
import { ListingCard } from './components/ListingCard';
import { ResponseCard } from './components/ResponseCard';
import { DealReportView } from './components/DealReportView';

type ListingWithMeta = any & {
    responses: any[];
    deal: any | null;
    computedStatus: 'waiting' | 'in_progress' | 'completed';
};

export function MarketMyListings() {
    const [items, setItems] = useState<ListingWithMeta[]>([]);
    const [loading, setLoading] = useState(true);

    const load = async () => {
        setLoading(true);
        try {
            const res = await getMyListings();
            const listings = res.data;

            const mapped = await Promise.all(
                listings.map(async (listing: any) => {
                    const responsesRes = await getListingResponses(listing.id);
                    const responses = responsesRes.data;

                    const accepted = responses.find((r: any) => r.status === 'accepted');
                    let deal = null;

                    if (accepted) {
                        try {
                            const dealRes = await getListingDeal(listing.id);
                            deal = dealRes.data;
                        } catch { /* no deal yet */ }
                    }

                    let computedStatus: 'waiting' | 'in_progress' | 'completed' = 'waiting';
                    if (deal?.status === 'in_progress') computedStatus = 'in_progress';
                    else if (deal?.status === 'completed') computedStatus = 'completed';

                    return { ...listing, responses, deal, computedStatus };
                })
            );

            setItems(mapped);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { load(); }, []);

    const handleAssign = async (responseId: string) => {
        try {
            await createDeal(responseId);
            toast.success('Исполнитель назначен');
            await load();
        } catch {
            toast.error('Ошибка назначения исполнителя');
        }
    };

    const statusBadges: Record<string, { label: string; color: string }> = {
        waiting: { label: 'Ожидает исполнителя', color: 'bg-tertiary-container/10 text-on-tertiary-container' },
        in_progress: { label: 'В работе', color: 'bg-primary/10 text-primary' },
        completed: { label: 'Завершён', color: 'bg-secondary/10 text-secondary' },
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[40vh]">
                <span className="material-symbols-outlined animate-spin text-4xl text-primary">progress_activity</span>
            </div>
        );
    }

    if (items.length === 0) {
        return (
            <div className="bg-surface-container-lowest border border-outline-variant/15 rounded-2xl p-12 text-center">
                <span className="material-symbols-outlined text-5xl text-primary/30 block mb-4">assignment</span>
                <p className="text-on-surface-variant font-medium">У вас пока нет запросов</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {items.map((listing) => (
                <div key={listing.id} className="space-y-3">
                    <ListingCard
                        listing={listing}
                        statusBadge={statusBadges[listing.computedStatus]}
                    />

                    {listing.responses.length > 0 && (
                        <div className="ml-4 pl-4 border-l-2 border-outline-variant/20 space-y-2">
                            <div className="text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-2 flex items-center gap-1.5">
                                <span className="material-symbols-outlined text-[14px]">people</span>
                                Отклики ({listing.responses.length})
                            </div>
                            {listing.responses.map((response: any) => (
                                <ResponseCard
                                    key={response.id}
                                    response={response}
                                    onAccept={
                                        response.status === 'pending' && !listing.deal
                                            ? () => handleAssign(response.id)
                                            : undefined
                                    }
                                />
                            ))}
                        </div>
                    )}

                    {listing.deal && listing.computedStatus === 'completed' && (
                        <CompletedDealBlock deal={listing.deal} />
                    )}

                    {listing.deal && listing.computedStatus === 'in_progress' && (
                        <div className="ml-4 flex items-center gap-2 px-4 py-3 rounded-xl text-sm font-bold bg-primary/10 text-primary">
                            <span className="material-symbols-outlined text-[18px]">autorenew</span>
                            Сделка: В работе
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}

function CompletedDealBlock({ deal }: { deal: any }) {
    const [report, setReport] = useState<any>(null);
    const [expanded, setExpanded] = useState(false);
    const [loading, setLoading] = useState(false);

    const loadReport = async () => {
        if (report) {
            setExpanded(!expanded);
            return;
        }
        setLoading(true);
        try {
            const res = await getDealReport(deal.id);
            setReport(res.data);
            setExpanded(true);
        } catch {
            setReport(null);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="ml-4 space-y-3">
            <div className="flex items-center gap-2 px-4 py-3 rounded-xl text-sm font-bold bg-secondary/10 text-secondary">
                <span className="material-symbols-outlined text-[18px]">check_circle</span>
                <span className="flex-1">Сделка: Завершена</span>
                <button
                    onClick={loadReport}
                    disabled={loading}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-secondary/15 text-secondary hover:bg-secondary/25 transition-colors disabled:opacity-50"
                >
                    {loading ? (
                        <span className="material-symbols-outlined animate-spin text-[14px]">progress_activity</span>
                    ) : (
                        <span className="material-symbols-outlined text-[14px]">{expanded ? 'visibility_off' : 'visibility'}</span>
                    )}
                    {expanded ? 'Скрыть отчёт' : 'Показать отчёт'}
                </button>
            </div>

            {expanded && report && (
                <div className="bg-surface-container-lowest border border-outline-variant/15 rounded-2xl p-6">
                    <div className="flex items-center gap-2 mb-4">
                        <span className="material-symbols-outlined text-primary/70 text-[20px]">description</span>
                        <h3 className="text-sm font-bold text-on-surface font-headline uppercase tracking-wider">Отчёт исполнителя</h3>
                    </div>
                    <DealReportView report={report.content || report} />
                </div>
            )}

            {expanded && !report && !loading && (
                <div className="bg-surface-container-low border border-outline-variant/10 rounded-2xl p-6 text-center text-sm text-on-surface-variant">
                    Отчёт не найден
                </div>
            )}
        </div>
    );
}
