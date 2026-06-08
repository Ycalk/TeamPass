import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { createListing, createResponse, getListings, getTokens } from '../../api/market';
import { ListingCard } from './components/ListingCard';
import { CreateListingModal } from './components/CreateListingModal';

export function MarketAll() {
    const [listings, setListings] = useState<any[]>([]);
    const [tokens, setTokens] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [showCreate, setShowCreate] = useState(false);
    const [creating, setCreating] = useState(false);

    const load = async () => {
        setLoading(true);
        try {
            const [listingsRes, tokensRes] = await Promise.all([
                getListings(),
                getTokens(),
            ]);
            setListings(listingsRes.data);
            setTokens(tokensRes.data);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { load(); }, []);

    const handleCreate = async (title: string, description: string) => {
        setCreating(true);
        try {
            await createListing(title, description);
            toast.success('Запрос создан');
            setShowCreate(false);
            await load();
        } catch {
            toast.error('Ошибка создания запроса');
        } finally {
            setCreating(false);
        }
    };

    const handleRespond = async (listingId: string) => {
        try {
            await createResponse(listingId);
            toast.success('Отклик отправлен');
        } catch {
            toast.error('Ошибка отправки отклика');
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[40vh]">
                <span className="material-symbols-outlined animate-spin text-4xl text-primary">progress_activity</span>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-surface-container-lowest border border-outline-variant/15 rounded-2xl p-5 flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-secondary/10 flex items-center justify-center text-secondary">
                        <span className="material-symbols-outlined text-[24px]">toll</span>
                    </div>
                    <div>
                        <div className="text-2xl font-black text-on-surface font-headline">{tokens?.free_tokens ?? '—'}</div>
                        <div className="text-xs font-bold text-on-surface-variant uppercase tracking-wider">Свободно</div>
                    </div>
                </div>

                <div className="bg-surface-container-lowest border border-outline-variant/15 rounded-2xl p-5 flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-tertiary-container/10 flex items-center justify-center text-on-tertiary-container">
                        <span className="material-symbols-outlined text-[24px]">lock</span>
                    </div>
                    <div>
                        <div className="text-2xl font-black text-on-surface font-headline">{tokens?.reserved_tokens ?? '—'}</div>
                        <div className="text-xs font-bold text-on-surface-variant uppercase tracking-wider">Зарезервировано</div>
                    </div>
                </div>

                <button
                    onClick={() => setShowCreate(true)}
                    className="bg-gradient-to-r from-primary to-primary-container text-on-primary rounded-2xl p-5 flex items-center justify-center gap-3 shadow-lg shadow-primary/20 hover:scale-[0.98] active:scale-95 transition-all font-bold"
                >
                    <span className="material-symbols-outlined text-[24px]">add_circle</span>
                    Создать запрос
                </button>
            </div>

            {listings.length === 0 ? (
                <div className="bg-surface-container-lowest border border-outline-variant/15 rounded-2xl p-12 text-center">
                    <span className="material-symbols-outlined text-5xl text-primary/30 block mb-4">search_off</span>
                    <p className="text-on-surface-variant font-medium">Пока нет доступных запросов</p>
                </div>
            ) : (
                <div className="space-y-4">
                    {listings.map((listing) => (
                        <ListingCard
                            key={listing.id}
                            listing={listing}
                            onRespond={() => handleRespond(listing.id)}
                        />
                    ))}
                </div>
            )}

            <CreateListingModal
                open={showCreate}
                onClose={() => setShowCreate(false)}
                onSubmit={handleCreate}
                loading={creating}
            />
        </div>
    );
}
