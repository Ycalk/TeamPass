import { useEffect, useState } from "react";
import { profileApi } from '../api/profile';
import type { Profile } from '../api/profile';


export function Profile() {
  const [profile, setProfile] = useState<Profile | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            try {
                const data = await profileApi.getMyProfile();
                setProfile(data);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };

        load();
    }, []);

    const handleChange = (field: keyof Profile, value: any) => {
        setProfile(prev => prev ? { ...prev, [field]: value } : prev);
    };

    const handleSave = async () => {
        if (!profile) return;

        const payload = {
            telegram_username: profile.telegram_username,
            vk_profile_link: profile.vk_profile_link,
            phone_number: profile.phone_number,
            strengths_text: profile.strengths_text,
            weaknesses_text: profile.weaknesses_text
        };

        await profileApi.updateProfile(payload);
    };

    if (loading || !profile) {
        return <div className="p-10">Загрузка...</div>;
    }

  return (
    <main className="pb-16 max-w-7xl mx-auto">

            {/* HEADER */}
            <section className="mb-10">
                <div className="flex flex-col md:flex-row items-center gap-8 bg-surface-container-low p-8 rounded-3xl">

                    {/* Заглушка аватарки */}
                    <div className="w-32 h-32 rounded-2xl bg-gray-200 flex items-center justify-center text-4xl">
                        👤
                    </div>

                    <div className="flex-1 text-center md:text-left">
                        <h2 className="text-4xl font-extrabold text-indigo-900 tracking-tight font-headline">
                            {profile.user.student.last_name}{" "}
                            {profile.user.student.first_name}{" "}
                            {profile.user.student.patronymic}
                        </h2>

                        <div className="flex flex-col md:flex-row md:items-center gap-4 mt-3">
                            <div className="flex items-center gap-2 text-indigo-400 font-semibold bg-white/50 px-3 py-1 rounded-full w-fit mx-auto md:mx-0">
                                <span className="material-symbols-outlined text-sm" data-icon="badge">badge</span>
                                <span className="text-xs uppercase tracking-wider font-label">
                                    Студенческий №: {profile.user.student.student_id}
                                </span>
                            </div>
                        </div>
                    </div>

                </div>
            </section>

            {/* SKILLS */}
            <section className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">

                {/* Чем могу помочь */}
                <div className="bg-surface-container-low p-8 rounded-3xl border border-transparent transition-all hover:border-teal-500/20">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="p-3 bg-secondary-container/30 text-secondary rounded-xl">
                      <span className="pt-1.5 material-symbols-outlined" data-icon="bolt">bolt</span>
                    </div>
                    <h3 className="text-xl font-extrabold text-indigo-900 font-headline uppercase tracking-tight">
                      Чем я могу помочь
                    </h3>
                  </div>
                  
                  <textarea
                    className="w-full bg-white/60 border-none rounded-2xl p-4 text-sm text-on-surface-variant font-label focus:ring-2 focus:ring-teal-500 transition-shadow min-h-[120px] resize-none"
                    value={profile.strengths_text || ''}
                    onChange={(e) =>
                        handleChange('strengths_text', e.target.value)
                    }
                    placeholder="Опишите свои навыки..."
                  />
                </div>

                {/* Нужна помощь */}
                <div className="bg-surface-container-low p-8 rounded-3xl border border-transparent transition-all hover:border-amber-500/20">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="p-3 bg-tertiary-fixed text-tertiary-container rounded-xl">
                      <span className="pt-1.5 material-symbols-outlined" data-icon="handshake">handshake</span>
                    </div>
                  <h3 className="text-xl font-extrabold text-indigo-900 font-headline uppercase tracking-tight">
                    В чем мне нужна помощь
                  </h3>
                </div>

                  <textarea
                    className="w-full bg-white/60 border-none rounded-2xl p-4 text-sm text-on-surface-variant font-label focus:ring-2 focus:ring-amber-500 transition-shadow min-h-[120px] resize-none"
                    value={profile.weaknesses_text || ''}
                    onChange={(e) =>
                      handleChange('weaknesses_text', e.target.value)
                    }
                    placeholder="Что вам трудно дается?"
                  />
                </div>

            </section>

            {/* CONTACTS */}
            <section className="bg-surface-container-low p-8 rounded-3xl mb-10">
                <h3 className="text-xl font-extrabold text-indigo-900 font-headline mb-8 uppercase tracking-tight">
                    Контактная информация
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                    {/* TG */}
                    <div>
                        <label className="block text-xs font-bold text-indigo-400 uppercase tracking-widest mb-2 ml-1">
                            TG
                        </label>
                        <div className="flex items-center gap-3 bg-white px-5 py-4 rounded-2xl shadow-sm group-focus-within:ring-2 ring-indigo-500 transition-all">
                          <span className="material-symbols-outlined text-indigo-400" data-icon="alternate_email">alternate_email</span>
                          <input
                              className="bg-transparent border-none focus:ring-0 p-0 text-indigo-900 font-bold flex-1"
                              value={profile.telegram_username || ''}
                              onChange={(e) =>
                                  handleChange('telegram_username', e.target.value)
                              }
                          />
                        </div>
                    </div>

                    {/* VK */}
                    <div>
                        <label className="block text-xs font-bold text-indigo-400 uppercase tracking-widest mb-2 ml-1">
                            VK
                        </label>
                        <div className="flex items-center gap-3 bg-white px-5 py-4 rounded-2xl shadow-sm group-focus-within:ring-2 ring-indigo-500 transition-all">
                          <span className="material-symbols-outlined text-indigo-400" data-icon="public">public</span>
                          <input
                            className="bg-transparent border-none focus:ring-0 p-0 text-indigo-900 font-bold flex-1"
                            value={profile.vk_profile_link || ''}
                            onChange={(e) =>
                              handleChange('vk_profile_link', e.target.value)
                            }
                          />
                        </div>
                    </div>

                    {/* PHONE */}
                    <div>
                        <label className="block text-xs font-bold text-indigo-400 uppercase tracking-widest mb-2 ml-1">
                            телефон
                        </label>
                        <div className="flex items-center gap-3 bg-white px-5 py-4 rounded-2xl shadow-sm group-focus-within:ring-2 ring-indigo-500 transition-all">
                          <span className="material-symbols-outlined text-indigo-400" data-icon="call">call</span>
                          <input
                            className="bg-transparent border-none focus:ring-0 p-0 text-indigo-900 font-bold flex-1"
                            value={profile.phone_number || ''}
                            onChange={(e) =>
                              handleChange('phone_number', e.target.value)
                            }
                          />
                        </div>
                    </div>

                </div>
            </section>

            {/* FOOTER ACTION */}
            <footer className="flex items-center justify-end gap-4 border-t border-indigo-100 pt-10">
              <button
                /* onClick={} */
                className="px-8 py-4 text-indigo-400 font-bold hover:text-indigo-900 transition-colors uppercase tracking-widest text-xs"
              >
                Отменить
              </button>
                <button
                    onClick={handleSave}
                    className="px-10 py-4 rounded-2xl font-black shadow-xl shadow-teal-900/10 active:scale-95 transition-all uppercase tracking-widest text-xs bg-secondary text-white"
                >
                    Сохранить изменения
                </button>
            </footer>

        </main>
  );
}