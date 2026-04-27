import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { authApi } from "../api/auth";
import { RegisterUserCommand } from "../api/types";

// Расширяем тип для формы, чтобы добавить поле подтверждения пароля
interface RegisterFormValues extends RegisterUserCommand {
    password_confirm: string;
}

export function Register() {
    const navigate = useNavigate();
    const {
        register,
        handleSubmit,
        watch,
        formState: { errors, isSubmitting },
    } = useForm<RegisterFormValues>();

    const password = watch("plain_password");

    const onSubmit = async (data: RegisterFormValues) => {
        const payload: RegisterUserCommand = {
            email: data.email,
            plain_password: data.plain_password,
            student_id: data.student_id,
            first_name: data.first_name,
            last_name: data.last_name,
            patronymic: data.patronymic?.trim() ? data.patronymic : null,
        };

        await authApi.register(payload);
        toast.success("Регистрация успешна!");
        navigate("/profile");
    };

    return (
        <div className="bg-background font-body text-on-surface min-h-screen flex flex-col relative">

            {/* Логотип (абсолютное позиционирование) */}
            <div className="absolute top-8 left-8 z-50 flex items-center">
                <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center mr-3 shadow-md shadow-primary/20">
                    <span className="material-symbols-outlined text-on-primary">school</span>
                </div>
                <span className="text-2xl font-black text-primary tracking-tighter font-headline">
                    TeamPass
                </span>
            </div>

            <main className="flex-1 flex items-center justify-center py-16 px-4 relative overflow-hidden">
                {/* Abstract Background Decorative Elements */}
                <div className="absolute top-[-10%] left-[-5%] w-[400px] h-[400px] bg-primary/5 rounded-full blur-[100px]"></div>
                <div className="absolute bottom-[-10%] right-[-5%] w-[500px] h-[500px] bg-secondary-fixed/10 rounded-full blur-[120px]"></div>

                <div className="w-full max-w-xl bg-surface-container-lowest overflow-hidden rounded-[2rem] shadow-2xl shadow-primary/10 relative z-10 border border-outline-variant/15 p-8 md:p-12">
                    <div className="mb-10 text-center">
                        <h2 className="font-headline text-3xl font-bold text-primary mb-2">
                            Регистрация
                        </h2>
                        <p className="text-on-surface-variant font-medium">
                            Создайте учетную запись, чтобы начать обучение.
                        </p>
                    </div>

                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                        {/* Name Row */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div className="space-y-1.5">
                                <label className="text-sm font-semibold text-on-surface-variant px-1">
                                    Имя <span className="text-error">*</span>
                                </label>
                                <input
                                    {...register("first_name", { required: "Введите имя" })}
                                    className="w-full px-4 py-3 bg-surface-container-low border-none rounded-xl focus:ring-2 focus:ring-primary/30 focus:bg-surface-container-lowest transition-all duration-200"
                                    placeholder="Иван"
                                    type="text"
                                    autoComplete="given-name"
                                />
                                {errors.first_name && (
                                    <span className="text-xs text-error px-1">{errors.first_name.message}</span>
                                )}
                            </div>
                            <div className="space-y-1.5">
                                <label className="text-sm font-semibold text-on-surface-variant px-1">
                                    Фамилия <span className="text-error">*</span>
                                </label>
                                <input
                                    {...register("last_name", { required: "Введите фамилию" })}
                                    className="w-full px-4 py-3 bg-surface-container-low border-none rounded-xl focus:ring-2 focus:ring-primary/30 focus:bg-surface-container-lowest transition-all duration-200"
                                    placeholder="Иванов"
                                    type="text"
                                    autoComplete="family-name"
                                />
                                {errors.last_name && (
                                    <span className="text-xs text-error px-1">{errors.last_name.message}</span>
                                )}
                            </div>
                        </div>

                        {/* Middle Name */}
                        <div className="space-y-1.5">
                            <label className="text-sm font-semibold text-on-surface-variant px-1 block">
                                Отчество
                            </label>
                            <input
                                {...register("patronymic")}
                                className="w-full px-4 py-3 bg-surface-container-low border-none rounded-xl focus:ring-2 focus:ring-primary/30 focus:bg-surface-container-lowest transition-all duration-200"
                                placeholder="Иванович"
                                type="text"
                                autoComplete="additional-name"
                            />
                        </div>

                        {/* Student ID */}
                        <div className="space-y-1.5">
                            <label className="text-sm font-semibold text-on-surface-variant px-1">
                                Номер студенческого билета <span className="text-error">*</span>
                            </label>
                            <div className="relative group">
                                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-outline text-xl group-focus-within:text-primary transition-colors">
                                    badge
                                </span>
                                <input
                                    {...register("student_id", {
                                        required: "Введите номер студенческого билета",
                                        pattern: { value: /^\d+$/, message: "Должны быть только цифры" }
                                    })}
                                    className="w-full pl-12 pr-4 py-3 bg-surface-container-low border-none rounded-xl focus:ring-2 focus:ring-primary/30 focus:bg-surface-container-lowest transition-all duration-200"
                                    placeholder="01234567"
                                    type="text"
                                />
                            </div>
                            {errors.student_id && (
                                <span className="text-xs text-error px-1">{errors.student_id.message}</span>
                            )}
                        </div>

                        {/* Email */}
                        <div className="space-y-1.5">
                            <label className="text-sm font-semibold text-on-surface-variant px-1">
                                Email <span className="text-error">*</span>
                            </label>
                            <div className="relative group">
                                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-outline text-xl group-focus-within:text-primary transition-colors">
                                    mail
                                </span>
                                <input
                                    {...register("email", {
                                        required: "Введите email",
                                        pattern: { value: /^\S+@\S+$/i, message: "Некорректный email" }
                                    })}
                                    className="w-full pl-12 pr-4 py-3 bg-surface-container-low border-none rounded-xl focus:ring-2 focus:ring-primary/30 focus:bg-surface-container-lowest transition-all duration-200"
                                    placeholder="student@example.com"
                                    type="email"
                                    autoComplete="email"
                                />
                            </div>
                            {errors.email && (
                                <span className="text-xs text-error px-1">{errors.email.message}</span>
                            )}
                        </div>

                        {/* Passwords */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div className="space-y-1.5">
                                <label className="text-sm font-semibold text-on-surface-variant px-1">
                                    Пароль <span className="text-error">*</span>
                                </label>
                                <input
                                    {...register("plain_password", {
                                        required: "Введите пароль",
                                        minLength: { value: 8, message: "Минимум 8 символов" }
                                    })}
                                    className="w-full px-4 py-3 bg-surface-container-low border-none rounded-xl focus:ring-2 focus:ring-primary/30 focus:bg-surface-container-lowest transition-all duration-200"
                                    placeholder="••••••••"
                                    type="password"
                                    autoComplete="new-password"
                                />
                                {errors.plain_password && (
                                    <span className="text-xs text-error px-1">{errors.plain_password.message}</span>
                                )}
                            </div>
                            <div className="space-y-1.5">
                                <label className="text-sm font-semibold text-on-surface-variant px-1">
                                    Повтор пароля <span className="text-error">*</span>
                                </label>
                                <input
                                    {...register("password_confirm", {
                                        required: "Повторите пароль",
                                        validate: value => value === password || "Пароли не совпадают"
                                    })}
                                    className="w-full px-4 py-3 bg-surface-container-low border-none rounded-xl focus:ring-2 focus:ring-primary/30 focus:bg-surface-container-lowest transition-all duration-200"
                                    placeholder="••••••••"
                                    type="password"
                                    autoComplete="new-password"
                                />
                                {errors.password_confirm && (
                                    <span className="text-xs text-error px-1">{errors.password_confirm.message}</span>
                                )}
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="w-full mt-6 py-4 bg-gradient-to-r from-primary to-primary-container text-on-primary font-headline font-bold text-lg rounded-xl shadow-lg shadow-primary/20 hover:scale-[0.98] active:scale-95 disabled:opacity-70 disabled:hover:scale-100 transition-all duration-200"
                        >
                            {isSubmitting ? "Отправка..." : "Зарегистрироваться"}
                        </button>
                    </form>

                    <div className="mt-8 pt-8 border-t border-surface-container text-center">
                        <p className="text-on-surface-variant text-sm font-medium">
                            Уже есть аккаунт?
                            <Link
                                to="/login"
                                className="text-primary font-bold hover:text-primary/80 transition-colors ml-1"
                            >
                                Войти
                            </Link>
                        </p>
                    </div>
                </div>
            </main>
        </div>
    );
}