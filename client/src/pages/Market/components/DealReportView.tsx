type Props = {
    report: any;
};

export function DealReportView({ report }: Props) {
    if (!report?.blocks) return null;

    return (
        <div className="space-y-3 text-sm text-on-surface break-words overflow-hidden">
            {report.blocks.map((block: any, index: number) => {
                switch (block.type) {
                    case 'header': {
                        const level = block.data.level || 2;
                        const text = block.data.text;
                        const cls = "font-bold font-headline text-on-surface mt-4 first:mt-0";
                        if (level === 3) return <h3 key={index} className={cls}>{text}</h3>;
                        if (level === 4) return <h4 key={index} className={cls}>{text}</h4>;
                        return <h2 key={index} className={cls}>{text}</h2>;
                    }
                    case 'paragraph':
                        return (
                            <p key={index} className="leading-relaxed" dangerouslySetInnerHTML={{ __html: block.data.text }} />
                        );
                    case 'quote':
                        return (
                            <blockquote key={index} className="border-l-4 border-primary/30 pl-4 py-1 italic text-on-surface-variant bg-primary/5 rounded-r-lg">
                                {block.data.text}
                                {block.data.caption && (
                                    <cite className="block text-xs mt-1 not-italic text-on-surface-variant/70">— {block.data.caption}</cite>
                                )}
                            </blockquote>
                        );
                    case 'code':
                        return (
                            <pre key={index} className="bg-surface-container-lowest border border-outline-variant/15 p-4 rounded-xl overflow-x-auto text-xs font-mono max-w-full">
                                <code>{block.data.code}</code>
                            </pre>
                        );
                    case 'delimiter':
                        return (
                            <div key={index} className="flex items-center justify-center py-2">
                                <div className="flex gap-1.5">
                                    <div className="w-1.5 h-1.5 rounded-full bg-outline-variant/50" />
                                    <div className="w-1.5 h-1.5 rounded-full bg-outline-variant/50" />
                                    <div className="w-1.5 h-1.5 rounded-full bg-outline-variant/50" />
                                </div>
                            </div>
                        );
                    case 'list': {
                        const isOrdered = block.data.style === 'ordered';
                        const ListTag = isOrdered ? 'ol' : 'ul';
                        return (
                            <ListTag key={index} className={`${isOrdered ? 'list-decimal' : 'list-disc'} pl-6 space-y-1`}>
                                {block.data.items.map((item: any, i: number) => (
                                    <li key={i} dangerouslySetInnerHTML={{ __html: item.content || item }} />
                                ))}
                            </ListTag>
                        );
                    }
                    default:
                        return null;
                }
            })}
        </div>
    );
}
