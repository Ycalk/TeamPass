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
    <main className="pt-28 pb-16 px-10 max-w-7xl mx-auto">

            {/* HEADER */}
            <section className="mb-10">
                <div className="flex flex-col md:flex-row items-center gap-8 bg-surface-container-low p-8 rounded-3xl">

                    {/* Заглушка аватарки */}
                    <div className="w-32 h-32 rounded-2xl bg-gray-200 flex items-center justify-center text-4xl">
                        👤
                    </div>

                    <div className="flex-1 text-center md:text-left">
                        <h2 className="text-4xl font-extrabold text-indigo-900 font-headline">
                            {profile.user.student.last_name}{" "}
                            {profile.user.student.first_name}{" "}
                            {profile.user.student.patronymic}
                        </h2>

                        <div className="mt-3 flex justify-center md:justify-start">
                            <div className="flex items-center gap-2 text-indigo-400 font-semibold bg-white/50 px-3 py-1 rounded-full">
                                <span className="text-xs uppercase">
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
                <div className="bg-surface-container-low p-8 rounded-3xl">
                    <h3 className="text-xl font-extrabold text-indigo-900 mb-6 uppercase">
                        Чем я могу помочь
                    </h3>

                    <textarea
                        className="w-full bg-white/60 rounded-2xl p-4 text-sm min-h-[120px]"
                        value={profile.strengths_text || ''}
                        onChange={(e) =>
                            handleChange('strengths_text', e.target.value)
                        }
                        placeholder="Опишите свои навыки..."
                    />
                </div>

                {/* Нужна помощь */}
                <div className="bg-surface-container-low p-8 rounded-3xl">
                    <h3 className="text-xl font-extrabold text-indigo-900 mb-6 uppercase">
                        В чем мне нужна помощь
                    </h3>

                    <textarea
                        className="w-full bg-white/60 rounded-2xl p-4 text-sm min-h-[120px]"
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
                <h3 className="text-xl font-extrabold text-indigo-900 mb-8 uppercase">
                    Контактная информация
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                    {/* TG */}
                    <div>
                        <label className="text-xs text-indigo-400 mb-2 block">
                            TG
                        </label>
                        <input
                            className="w-full bg-white px-4 py-3 rounded-xl"
                            value={profile.telegram_username || ''}
                            onChange={(e) =>
                                handleChange('telegram_username', e.target.value)
                            }
                        />
                    </div>

                    {/* VK */}
                    <div>
                        <label className="text-xs text-indigo-400 mb-2 block">
                            VK
                        </label>
                        <input
                            className="w-full bg-white px-4 py-3 rounded-xl"
                            value={profile.vk_profile_link || ''}
                            onChange={(e) =>
                                handleChange('vk_profile_link', e.target.value)
                            }
                        />
                    </div>

                    {/* PHONE */}
                    <div>
                        <label className="text-xs text-indigo-400 mb-2 block">
                            Телефон
                        </label>
                        <input
                            className="w-full bg-white px-4 py-3 rounded-xl"
                            value={profile.phone_number || ''}
                            onChange={(e) =>
                                handleChange('phone_number', e.target.value)
                            }
                        />
                    </div>

                </div>
            </section>

            {/* SAVE BUTTON */}
            <div className="flex justify-end">
                <button
                    onClick={handleSave}
                    className="px-10 py-4 rounded-2xl font-bold bg-secondary text-white"
                >
                    Сохранить изменения
                </button>
            </div>

        </main>
  );
}