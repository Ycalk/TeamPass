import { useEffect, useRef, useState, Fragment } from 'react';
import { toast } from 'sonner';
import { Dialog, DialogBackdrop, DialogPanel, Transition, TransitionChild } from '@headlessui/react';
import {
    completeDeal,
    createDealReport,
    getDealReport,
    getMyResponses,
    getResponseDeal,
    updateDealReport,
} from '../../api/market';
import { DealReportEditor } from './components/DealReportEditor';
import { DealReportView } from './components/DealReportView';
import { ConfirmModal } from '../../components/ConfirmModal';

type ResponseItem = {
    id: string;
    status: string;
    team: { name: string };
    listing?: { title: string };
    deal?: any;
};

export function MarketResponses() {
    const [items, setItems] = useState<ResponseItem[]>([]);
    const [loading, setLoading] = useState(true);

    const load = async () => {
        setLoading(true);
        try {
            const res = await getMyResponses();
            const mapped = await Promise.all(
                res.data
                    .filter((r: any) => r.status !== 'rejected')
                    .map(async (response: any) => {
                        if (response.status !== 'accepted') return response;

                        try {
                            const deal = await getResponseDeal(response.id);
                            return { ...response, deal: deal.data };
                        } catch {
                            return response;
                        }
                    })
            );
            setItems(mapped);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { load(); }, []);

    const pending = items.filter((i) => i.status === 'pending');
    const inProgress = items.filter((i) => i.status === 'accepted' && i.deal?.status === 'in_progress');
    const completed = items.filter((i) => i.status === 'accepted' && i.deal?.status === 'completed');

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
                <span className="material-symbols-outlined text-5xl text-primary/30 block mb-4">reply_all</span>
                <p className="text-on-surface-variant font-medium">У вас пока нет откликов</p>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {inProgress.length > 0 && (
                <Section title="Необходимо заполнить отчёт" icon="edit_note" count={inProgress.length}>
                    {inProgress.map((item) => (
                        <DealBlock key={item.id} item={item} onDone={load} />
                    ))}
                </Section>
            )}

            {pending.length > 0 && (
                <Section title="Ожидает подтверждения" icon="hourglass_empty" count={pending.length}>
                    {pending.map((item) => (
                        <PendingCard key={item.id} item={item} />
                    ))}
                </Section>
            )}

            {completed.length > 0 && (
                <Section title="Завершено" icon="check_circle" count={completed.length}>
                    {completed.map((item) => (
                        <CompletedCard key={item.id} item={item} />
                    ))}
                </Section>
            )}
        </div>
    );
}

function Section({ title, icon, count, children }: { title: string; icon: string; count: number; children: React.ReactNode }) {
    return (
        <div>
            <h2 className="text-lg font-bold text-on-surface font-headline flex items-center gap-2 mb-4">
                <span className="material-symbols-outlined text-primary/70 text-[22px]">{icon}</span>
                {title}
                <span className="text-sm font-medium text-on-surface-variant bg-surface-container px-2 py-0.5 rounded-lg ml-1">{count}</span>
            </h2>
            <div className="space-y-4">{children}</div>
        </div>
    );
}

function PendingCard({ item }: { item: ResponseItem }) {
    return (
        <div className="bg-surface-container-lowest border border-outline-variant/15 rounded-2xl p-6 flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-tertiary-container/10 flex items-center justify-center text-on-tertiary-container shrink-0">
                <span className="material-symbols-outlined text-[24px]">hourglass_empty</span>
            </div>
            <div className="flex-1 min-w-0">
                <div className="font-bold text-on-surface">{item.listing?.title || 'Запрос'}</div>
                <div className="text-sm text-on-surface-variant flex items-center gap-1 mt-0.5">
                    <span className="material-symbols-outlined text-[14px]">group</span>
                    {item.team?.name}
                </div>
            </div>
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-tertiary-container/10 text-on-tertiary-container shrink-0">
                <span className="material-symbols-outlined text-[14px]">schedule</span>
                Ожидает
            </span>
        </div>
    );
}

function CompletedCard({ item }: { item: ResponseItem }) {
    const [report, setReport] = useState<any>(null);
    const [expanded, setExpanded] = useState(false);
    const [loadingReport, setLoadingReport] = useState(false);

    const toggleReport = async () => {
        if (report) {
            setExpanded(!expanded);
            return;
        }
        if (!item.deal?.id) return;
        setLoadingReport(true);
        try {
            const r = await getDealReport(item.deal.id);
            setReport(r.data);
            setExpanded(true);
        } catch {
            setReport(null);
        } finally {
            setLoadingReport(false);
        }
    };

    return (
        <div className="bg-surface-container-lowest border border-outline-variant/15 rounded-2xl p-6">
            <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-secondary/10 flex items-center justify-center text-secondary shrink-0">
                    <span className="material-symbols-outlined text-[20px]">check_circle</span>
                </div>
                <div className="flex-1 min-w-0">
                    <div className="font-bold text-on-surface">{item.listing?.title || 'Запрос'}</div>
                    <div className="text-sm text-on-surface-variant">{item.team?.name}</div>
                </div>
                <button
                    onClick={toggleReport}
                    disabled={loadingReport}
                    className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold bg-surface-container text-on-surface-variant hover:bg-surface-container-high hover:text-primary transition-colors disabled:opacity-50"
                >
                    {loadingReport ? (
                        <span className="material-symbols-outlined animate-spin text-[16px]">progress_activity</span>
                    ) : (
                        <span className="material-symbols-outlined text-[16px]">{expanded ? 'visibility_off' : 'visibility'}</span>
                    )}
                    {expanded ? 'Скрыть отчёт' : 'Показать отчёт'}
                </button>
            </div>

            <div
                className={`grid transition-all duration-500 ease-in-out ${
                    expanded ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'
                }`}
            >
                <div className="overflow-hidden min-h-0">
                    {expanded && report && (
                        <div className="mt-4 pt-4 border-t border-outline-variant/15">
                            <DealReportView report={report.content || report} />
                        </div>
                    )}

                    {expanded && !report && !loadingReport && (
                        <div className="mt-4 pt-4 border-t border-outline-variant/15 text-sm text-on-surface-variant text-center py-4">
                            Отчёт не найден
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

function DealBlock({ item, onDone }: { item: ResponseItem; onDone: () => void }) {
    const [reportData, setReportData] = useState<any>(null);
    const [showCompleteModal, setShowCompleteModal] = useState(false);
    const [showPreview, setShowPreview] = useState(false);
    const [completing, setCompleting] = useState(false);
    const [loaded, setLoaded] = useState(false);
    const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved'>('idle');
    const [editorExpanded, setEditorExpanded] = useState(false);
    const [canRender, setCanRender] = useState(false);
    const [loadingReport, setLoadingReport] = useState(false);
    const reportExists = useRef(false);

    useEffect(() => {
        setCanRender(true);
    }, []);

    useEffect(() => {
        if (!editorExpanded || !item.deal?.id || loaded) return;
        setLoadingReport(true);
        getDealReport(item.deal.id)
            .then((r) => {
                setReportData(r.data);
                reportExists.current = true;
                setLoaded(true);
            })
            .catch(async (err: any) => {
                if (err?.response?.status === 404) {
                    try {
                        const emptyContent = { time: Date.now(), blocks: [], version: '2.30.0' };
                        const res = await createDealReport(item.deal.id, emptyContent);
                        setReportData(res.data?.content || emptyContent);
                        reportExists.current = true;
                    } catch {
                        setReportData({ time: Date.now(), blocks: [], version: '2.30.0' });
                    }
                }
                setLoaded(true);
            })
            .finally(() => setLoadingReport(false));
    }, [editorExpanded, item.deal?.id, loaded]);

    const handleSave = async (content: any) => {
        setSaveStatus('saving');
        try {
            if (reportExists.current) {
                await updateDealReport(item.deal.id, content);
            } else {
                await createDealReport(item.deal.id, content);
                reportExists.current = true;
            }
            setSaveStatus('saved');
        } catch {
            setSaveStatus('idle');
            throw new Error('Save failed');
        }
    };

    const handleComplete = async () => {
        setCompleting(true);
        try {
            await completeDeal(item.deal.id);
            toast.success('Отчёт отправлен');
            setShowCompleteModal(false);
            onDone();
        } catch {
            toast.error('Ошибка отправки отчёта');
        } finally {
            setCompleting(false);
        }
    };

    return (
        <div className="bg-surface-container-lowest border border-outline-variant/15 rounded-2xl p-6">
            <div className="flex items-center gap-2 mb-5">
                <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary shrink-0">
                    <span className="material-symbols-outlined text-[20px]">edit_note</span>
                </div>
                <div className="flex-1 min-w-0">
                    <div className="font-bold text-on-surface">{item.listing?.title || 'Запрос'}</div>
                    <div className="text-sm text-on-surface-variant flex items-center gap-1">
                        <span className="material-symbols-outlined text-[14px]">group</span>
                        {item.team?.name}
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setEditorExpanded(!editorExpanded)}
                        className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold bg-surface-container text-on-surface-variant hover:bg-surface-container-high hover:text-primary transition-colors"
                    >
                        <span className="material-symbols-outlined text-[16px]">
                            {editorExpanded ? 'unfold_less' : 'unfold_more'}
                        </span>
                        {editorExpanded ? 'Свернуть' : 'Редактор'}
                    </button>
                    <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-primary/10 text-primary shrink-0">
                        <span className="material-symbols-outlined text-[14px]">autorenew</span>
                        В работе
                    </span>
                </div>
            </div>

            {canRender && (
                <div
                    className={`grid transition-all duration-500 ease-in-out ${
                        editorExpanded
                            ? 'grid-rows-[1fr] opacity-100'
                            : 'grid-rows-[0fr] opacity-0'
                    }`}
                >
                    <div className="overflow-hidden min-h-0">
                        {loadingReport && (
                            <div className="flex items-center justify-center py-10">
                                <span className="material-symbols-outlined animate-spin text-3xl text-primary">progress_activity</span>
                            </div>
                        )}

                        {loaded && (
                            <div className="flex flex-col gap-5">
                                <DealReportEditor
                                    data={reportData?.content || reportData}
                                    onChange={setReportData}
                                    onSave={handleSave}
                                    saveStatus={saveStatus}
                                />

                                <div className="flex justify-end gap-3">
                                    <button
                                        onClick={() => setShowPreview(true)}
                                        className="px-5 py-2.5 rounded-xl font-bold text-sm text-on-surface-variant bg-surface-container hover:bg-surface-container-high hover:text-primary transition-all flex items-center gap-2"
                                    >
                                        <span className="material-symbols-outlined text-[18px]">visibility</span>
                                        Предпросмотр
                                    </button>
                                    <button
                                        onClick={() => setShowCompleteModal(true)}
                                        className="bg-primary text-on-primary px-6 py-2.5 rounded-xl font-bold text-sm shadow-md shadow-primary/20 hover:bg-primary/90 active:scale-[0.98] transition-all flex items-center gap-2"
                                    >
                                        <span className="material-symbols-outlined text-[18px]">send</span>
                                        Отправить отчёт
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            <ConfirmModal
                open={showCompleteModal}
                onClose={() => setShowCompleteModal(false)}
                onConfirm={handleComplete}
                title="Отправить отчёт?"
                description="После отправки отчёт нельзя будет изменить. Убедитесь, что все данные заполнены корректно."
                confirmText="Отправить"
                cancelText="Отмена"
                variant="primary"
                icon="send"
                loading={completing}
            />

            <PreviewModal
                open={showPreview}
                onClose={() => setShowPreview(false)}
                report={reportData?.content || reportData}
            />
        </div>
    );
}

function PreviewModal({ open, onClose, report }: { open: boolean; onClose: () => void; report: any }) {
    return (
        <Transition show={open} as={Fragment}>
            <Dialog onClose={onClose} className="relative z-[100]">
                <TransitionChild
                    as={Fragment}
                    enter="ease-out duration-200"
                    enterFrom="opacity-0"
                    enterTo="opacity-100"
                    leave="ease-in duration-150"
                    leaveFrom="opacity-100"
                    leaveTo="opacity-0"
                >
                    <DialogBackdrop className="fixed inset-0 bg-black/30 backdrop-blur-sm" />
                </TransitionChild>

                <div className="fixed inset-0 flex items-start justify-center p-4 pt-[8vh]">
                    <TransitionChild
                        as={Fragment}
                        enter="ease-out duration-200"
                        enterFrom="opacity-0 scale-95 translate-y-4"
                        enterTo="opacity-100 scale-100 translate-y-0"
                        leave="ease-in duration-150"
                        leaveFrom="opacity-100 scale-100 translate-y-0"
                        leaveTo="opacity-0 scale-95 translate-y-4"
                    >
                        <DialogPanel className="w-full max-w-2xl bg-surface-container-lowest rounded-3xl shadow-2xl shadow-primary/10 border border-outline-variant/15 mb-10 max-h-[85vh] flex flex-col">
                            <div className="flex items-center justify-between px-8 py-5 border-b border-outline-variant/15 shrink-0">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
                                        <span className="material-symbols-outlined text-[20px]">preview</span>
                                    </div>
                                    <h3 className="text-lg font-bold text-on-surface font-headline">Предпросмотр отчёта</h3>
                                </div>
                                <button
                                    onClick={onClose}
                                    className="w-9 h-9 flex items-center justify-center rounded-xl text-on-surface-variant hover:bg-surface-container hover:text-primary transition-colors"
                                >
                                    <span className="material-symbols-outlined text-[20px]">close</span>
                                </button>
                            </div>

                            <div className="px-8 py-6 overflow-y-auto flex-1 min-h-0">
                                {report?.blocks?.length > 0 ? (
                                    <DealReportView report={report} />
                                ) : (
                                    <div className="text-center py-8 text-on-surface-variant text-sm">
                                        Отчёт пуст — добавьте содержимое в редакторе
                                    </div>
                                )}
                            </div>
                        </DialogPanel>
                    </TransitionChild>
                </div>
            </Dialog>
        </Transition>
    );
}
