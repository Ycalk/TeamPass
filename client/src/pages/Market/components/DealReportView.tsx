type Props = {
  report: any;
};

export function DealReportView({
  report,
}: Props) {
  if (!report?.blocks) {
    return null;
  }

  return (
    <div className="space-y-4">
      {report.blocks.map(
        (block: any, index: number) => {
          switch (block.type) {
            case 'header':
              return (
                <h2
                  key={index}
                  className="text-2xl font-bold"
                >
                  {block.data.text}
                </h2>
              );

            case 'paragraph':
              return (
                <p key={index}>
                  {block.data.text}
                </p>
              );

            case 'quote':
              return (
                <blockquote
                  key={index}
                  className="border-l-4 pl-4 italic"
                >
                  {block.data.text}
                </blockquote>
              );

            case 'code':
              return (
                <pre
                  key={index}
                  className="bg-gray-100 p-4 rounded-xl overflow-auto"
                >
                  <code>
                    {block.data.code}
                  </code>
                </pre>
              );

            case 'delimiter':
              return <hr key={index} />;

            case 'list':
              return (
                <ul
                  key={index}
                  className="list-disc pl-6"
                >
                  {block.data.items.map(
                    (
                      item: any,
                      i: number
                    ) => (
                      <li key={i}>
                        {item.content ||
                          item}
                      </li>
                    )
                  )}
                </ul>
              );

            default:
              return null;
          }
        }
      )}
    </div>
  );
}