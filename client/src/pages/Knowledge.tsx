import {
  Link,
  Outlet,
  useLocation,
} from 'react-router-dom';

export function Knowledge() {
  const location = useLocation();

  const tabs = [
    {
      label: 'Все запросы',
      path: '/knowledge',
    },
    {
      label: 'Мои запросы',
      path: '/knowledge/my',
    },
    {
      label: 'Отклики',
      path: '/knowledge/responses',
    },
  ];

  return (
    <div className="space-y-8">
      <div className="bg-white rounded-3xl p-8">
        <h1 className="text-4xl font-bold text-indigo-900">
          Биржа знаний
        </h1>

        <div className="flex gap-4 mt-6">
          {tabs.map((tab) => {
            const active =
              location.pathname ===
              tab.path;

            return (
              <Link
                key={tab.path}
                to={tab.path}
                className={`px-5 py-3 rounded-2xl transition ${
                  active
                    ? 'bg-indigo-900 text-white'
                    : 'bg-gray-100'
                }`}
              >
                {tab.label}
              </Link>
            );
          })}
        </div>
      </div>

      <Outlet />
    </div>
  );
}