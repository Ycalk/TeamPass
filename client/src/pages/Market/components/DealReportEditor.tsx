import { useEffect, useRef } from 'react';
import EditorJS from '@editorjs/editorjs';
import Header from '@editorjs/header';
import List from '@editorjs/list';
import Quote from '@editorjs/quote';
import Code from '@editorjs/code';
import Delimiter from '@editorjs/delimiter';
import Paragraph from '@editorjs/paragraph';
import InlineCode from '@editorjs/inline-code';
import Underline from '@editorjs/underline';

type SaveStatus = 'idle' | 'saving' | 'saved';

type Props = {
    data?: any;
    onChange: (data: any) => void;
    onSave?: (data: any) => Promise<void>;
    saveStatus?: SaveStatus;
};

const statusConfig: Record<SaveStatus, { icon: string; label: string; color: string }> = {
    idle: { icon: 'cloud_off', label: 'Не сохранено', color: 'text-on-surface-variant/50' },
    saving: { icon: 'cloud_sync', label: 'Сохранение...', color: 'text-primary' },
    saved: { icon: 'cloud_done', label: 'Сохранено', color: 'text-secondary' },
};

export function DealReportEditor({ data, onChange, onSave, saveStatus = 'idle' }: Props) {
    const holderRef = useRef<HTMLDivElement>(null);
    const autosaveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
    const onChangeRef = useRef(onChange);
    const onSaveRef = useRef(onSave);

    onChangeRef.current = onChange;
    onSaveRef.current = onSave;

    useEffect(() => {
        const holder = holderRef.current;
        if (!holder) return;

        const editor = new EditorJS({
            holder,
            data,
            placeholder: 'Начните писать отчёт...',
            async onChange(api: any) {
                const saved = await api.saver.save();
                onChangeRef.current(saved);

                if (onSaveRef.current) {
                    if (autosaveTimer.current) clearTimeout(autosaveTimer.current);
                    autosaveTimer.current = setTimeout(() => {
                        onSaveRef.current?.(saved).catch(() => {});
                    }, 1500);
                }
            },
            tools: {
                header: { class: Header, config: { levels: [2, 3, 4], defaultLevel: 2 } },
                list: { class: List, config: { defaultStyle: 'ordered' } },
                quote: Quote,
                code: Code,
                delimiter: Delimiter,
                paragraph: { class: Paragraph, inlineToolbar: true },
                inlineCode: InlineCode,
                underline: Underline,
            },
        });

        editor.isReady.catch((e: any) => {
            console.error('[DealReportEditor] isReady failed:', e);
        });

        return () => {
            if (autosaveTimer.current) clearTimeout(autosaveTimer.current);
            holder.innerHTML = '';
        };
    }, []);

    const status = statusConfig[saveStatus];

    return (
        <div className="bg-surface-container-lowest border border-outline-variant/15 rounded-2xl overflow-hidden">
            <div
                ref={holderRef}
                className="px-4 py-3 text-on-surface text-sm
                    [&_.ce-block]:py-0.5 [&_.ce-block]:text-on-surface
                    [&_.ce-toolbar__content]:max-w-full [&_.ce-toolbar__content]:!mx-0
                    [&_.ce-block__content]:max-w-full [&_.ce-block__content]:!mx-0
                    [&_.cdx-block]:text-on-surface
                    [&_.codex-editor\_\_redactor]:pb-0"
            />
            <div className={`flex items-center gap-1.5 px-4 py-2 border-t border-outline-variant/10 text-xs font-medium ${status.color}`}>
                <span className={`material-symbols-outlined text-[16px] ${saveStatus === 'saving' ? 'animate-spin' : ''}`}>
                    {status.icon}
                </span>
                {status.label}
            </div>
        </div>
    );
}