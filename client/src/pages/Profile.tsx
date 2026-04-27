import { useEffect, useState } from "react";
import { profileApi } from '../api/profile';
import type { Profile } from '../api/profile';
import { toast } from "sonner";

export function Profile() {
    const [profile, setProfile] = useState<Profile | null>(null);
    const [originalProfile, setOriginalProfile] = useState<Profile | null>(null);
    const [loading, setLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);

    useEffect(() => {
        const load = async () => {
            try {
                const data = await profileApi.getMyProfile();
                setProfile(data);
                setOriginalProfile(data);
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

    const handleReset = () => {
        setProfile(originalProfile);
    };

    const handleSave = async () => {
        if (!profile) return;
        setIsSaving(true);

        const payload = {
            telegram_username: profile.telegram_username,
            vk_profile_link: profile.vk_profile_link,
            phone_number: profile.phone_number,
            strengths_text: profile.strengths_text,
            weaknesses_text: profile.weaknesses_text
        };

        try {
            await profileApi.updateProfile(payload);
            setOriginalProfile(profile);
            toast.success("Профиль успешно обновлен!");
        } finally {
            setIsSaving(false);
        }
    };

    const isEdited = originalProfile && profile && (
        profile.telegram_username !== originalProfile.telegram_username ||
        profile.vk_profile_link !== originalProfile.vk_profile_link ||
        profile.phone_number !== originalProfile.phone_number ||
        profile.strengths_text !== originalProfile.strengths_text ||
        profile.weaknesses_text !== originalProfile.weaknesses_text
    );

    if (loading || !profile) {
        return (
            <div className="flex items-center justify-center min-h-[50vh] w-full">
                <span className="material-symbols-outlined animate-spin text-4xl text-primary">
                    progress_activity
                </span>
            </div>
        );
    }

    return (
        <div className="w-full space-y-8 font-body">

            {/* HEADER CARD */}
            <section className="bg-surface-container-lowest overflow-hidden rounded-[2rem] shadow-2xl shadow-primary/5 border border-outline-variant/15 p-8 md:p-10">
                <div className="flex flex-col md:flex-row items-center gap-8">
                    <div className="w-32 h-32 rounded-[1.5rem] bg-primary/10 flex items-center justify-center text-5xl shadow-inner border border-primary/20">
                        🧑‍🎓
                    </div>
                    <div className="flex-1 text-center md:text-left">
                        <h2 className="text-3xl md:text-4xl font-black text-primary tracking-tight font-headline mb-4">
                            {profile.user.student.last_name} {profile.user.student.first_name} {profile.user.student.patronymic}
                        </h2>
                        <div className="flex flex-wrap items-center justify-center md:justify-start gap-3">
                            <div className="flex items-center gap-2 text-on-surface-variant bg-surface-container-low px-4 py-2 rounded-xl border border-outline-variant/20">
                                <span className="material-symbols-outlined text-sm text-primary" data-icon="badge">badge</span>
                                <span className="text-xs uppercase tracking-wider font-bold">
                                    Студенческий №: {profile.user.student.student_id}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* SKILLS CARDS */}
            <section className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Чем могу помочь */}
                <div className="bg-surface-container-lowest rounded-[2rem] shadow-xl shadow-primary/5 border border-outline-variant/15 p-8 flex flex-col">
                    <div className="flex items-center gap-4 mb-6">
                        <div className="p-3 bg-secondary-container/30 text-secondary rounded-xl">
                            <span className="material-symbols-outlined block" data-icon="bolt">bolt</span>
                        </div>
                        <h3 className="text-lg font-bold text-primary font-headline uppercase tracking-tight">
                            Чем я могу помочь
                        </h3>
                    </div>
                    <div className="relative group flex-1">
                        <textarea
                            className="w-full h-full min-h-[140px] p-5 bg-surface-container-low border-none rounded-2xl focus:ring-2 focus:ring-teal-500/30 focus:bg-surface-container-lowest transition-all duration-200 text-sm text-on-surface font-medium resize-none"
                            value={profile.strengths_text || ''}
                            onChange={(e) => handleChange('strengths_text', e.target.value)}
                            placeholder="Опишите темы и предметы, в которых вы хорошо разбираетесь..."
                        />
                    </div>
                </div>

                {/* Нужна помощь */}
                <div className="bg-surface-container-lowest rounded-[2rem] shadow-xl shadow-primary/5 border border-outline-variant/15 p-8 flex flex-col">
                    <div className="flex items-center gap-4 mb-6">
                        <div className="p-3 bg-tertiary-fixed text-tertiary-container rounded-xl">
                            <span className="material-symbols-outlined block" data-icon="handshake">handshake</span>
                        </div>
                        <h3 className="text-lg font-bold text-primary font-headline uppercase tracking-tight">
                            В чем мне нужна помощь
                        </h3>
                    </div>
                    <div className="relative group flex-1">
                        <textarea
                            className="w-full h-full min-h-[140px] p-5 bg-surface-container-low border-none rounded-2xl focus:ring-2 focus:ring-amber-500/30 focus:bg-surface-container-lowest transition-all duration-200 text-sm text-on-surface font-medium resize-none"
                            value={profile.weaknesses_text || ''}
                            onChange={(e) => handleChange('weaknesses_text', e.target.value)}
                            placeholder="Укажите, с чем у вас возникают трудности..."
                        />
                    </div>
                </div>
            </section>

            {/* CONTACTS CARD */}
            <section className="bg-surface-container-lowest rounded-[2rem] shadow-xl shadow-primary/5 border border-outline-variant/15 p-8">
                <h3 className="text-lg font-bold text-primary font-headline mb-8 uppercase tracking-tight flex items-center gap-3">
                    <span className="material-symbols-outlined text-primary/70" data-icon="contact_page">contact_page</span>
                    Контактная информация
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* TG */}
                    <div className="space-y-1.5">
                        <label className="text-xs font-bold text-on-surface-variant uppercase tracking-widest px-1">
                            Telegram
                        </label>
                        <div className="relative group">
                            <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-outline text-xl group-focus-within:text-primary transition-colors">
                                alternate_email
                            </span>
                            <input
                                className="w-full pl-12 pr-4 py-3 bg-surface-container-low border-none rounded-xl focus:ring-2 focus:ring-primary/30 focus:bg-surface-container-lowest transition-all duration-200 text-on-surface font-medium"
                                value={profile.telegram_username || ''}
                                onChange={(e) => handleChange('telegram_username', e.target.value)}
                                placeholder="@username"
                            />
                        </div>
                    </div>

                    {/* VK */}
                    <div className="space-y-1.5">
                        <label className="text-xs font-bold text-on-surface-variant uppercase tracking-widest px-1">
                            ВКонтакте
                        </label>
                        <div className="relative group">
                            <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-outline text-xl group-focus-within:text-primary transition-colors">
                                public
                            </span>
                            <input
                                className="w-full pl-12 pr-4 py-3 bg-surface-container-low border-none rounded-xl focus:ring-2 focus:ring-primary/30 focus:bg-surface-container-lowest transition-all duration-200 text-on-surface font-medium"
                                value={profile.vk_profile_link || ''}
                                onChange={(e) => handleChange('vk_profile_link', e.target.value)}
                                placeholder="vk.com/id..."
                            />
                        </div>
                    </div>

                    {/* PHONE */}
                    <div className="space-y-1.5">
                        <label className="text-xs font-bold text-on-surface-variant uppercase tracking-widest px-1">
                            Телефон
                        </label>
                        <div className="relative group">
                            <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-outline text-xl group-focus-within:text-primary transition-colors">
                                call
                            </span>
                            <input
                                className="w-full pl-12 pr-4 py-3 bg-surface-container-low border-none rounded-xl focus:ring-2 focus:ring-primary/30 focus:bg-surface-container-lowest transition-all duration-200 text-on-surface font-medium"
                                value={profile.phone_number || ''}
                                onChange={(e) => handleChange('phone_number', e.target.value)}
                                placeholder="+7..."
                            />
                        </div>
                    </div>
                </div>
            </section>

            {/* FOOTER ACTIONS */}
            <footer className="flex items-center justify-end gap-4 border-t border-surface-container pt-8 mt-8">
                {isEdited && (
                    <button
                        onClick={handleReset}
                        disabled={isSaving}
                        className="px-6 py-3 text-on-surface-variant font-bold hover:text-error hover:bg-error/10 rounded-xl transition-all uppercase tracking-widest text-xs disabled:opacity-50"
                    >
                        Сбросить
                    </button>
                )}
                <button
                    onClick={handleSave}
                    disabled={!isEdited || isSaving}
                    className={`px-8 py-3 rounded-xl font-headline font-bold text-sm transition-all duration-200 uppercase tracking-widest ${isEdited
                        ? "bg-gradient-to-r from-primary to-primary-container text-on-primary shadow-lg shadow-primary/20 hover:scale-[0.98] active:scale-95"
                        : "bg-surface-container-high text-on-surface-variant opacity-50 cursor-not-allowed"
                        }`}
                >
                    {isSaving ? "Сохранение..." : "Сохранить изменения"}
                </button>
            </footer>
        </div>
    );
}