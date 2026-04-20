import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { authApi } from "../api/auth";
import { LoginUserCommand } from "../api/types";

export function Login() {
    const navigate = useNavigate();
    const [showPassword, setShowPassword] = useState(false);

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm<LoginUserCommand>();

    const onSubmit = async (data: LoginUserCommand) => {
        try {
            await authApi.login(data);
            toast.success("Вход выполнен успешно!");
            navigate("/dashboard");
        } catch (error) {
            // Ошибки перехватываются интерцептором
        }
    };

    return (
        <div className="bg-background font-body text-on-surface min-h-screen flex flex-col">
            {/* TopAppBar - теперь точно такой же как в Register */}
            <header className="bg-white/70 backdrop-blur-xl sticky top-0 z-50 shadow-[0_1px_15px_-3px_rgba(26,35,126,0.08)]">
                <div className="flex justify-between items-center w-full px-8 py-4 max-w-screen-2xl mx-auto">
                    <div className="text-2xl font-black text-indigo-900 tracking-tighter font-headline">
                        TeamPass
                    </div>
                </div>
            </header>

            <main className="flex-1 flex items-center justify-center py-16 px-4 relative overflow-hidden">
                {/* Abstract Background Decorative Elements */}
                <div className="absolute top-[-10%] left-[-5%] w-[400px] h-[400px] bg-primary/5 rounded-full blur-[100px]"></div>
                <div className="absolute bottom-[-10%] right-[-5%] w-[500px] h-[500px] bg-secondary-fixed/10 rounded-full blur-[120px]"></div>

                {/* Login Card - убрана полоса, скругления 2rem, отступы как в Register */}
                <div className="w-full max-w-xl bg-surface-container-lowest overflow-hidden rounded-[2rem] shadow-2xl shadow-primary/10 relative z-10 border border-outline-variant/15 p-8 md:p-12">

                    <div className="mb-10 text-center">
                        <h2 className="font-headline text-3xl font-bold text-primary mb-2">
                            Вход в систему
                        </h2>
                        <p className="text-on-surface-variant font-medium">
                            Добро пожаловать в TeamPass!
                        </p>
                    </div>

                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                        {/* Email Field */}
                        <div className="space-y-1.5">
                            <label
                                className="text-sm font-semibold text-on-surface-variant px-1"
                                htmlFor="email"
                            >
                                Email
                            </label>
                            <div className="relative group">
                                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-outline text-xl group-focus-within:text-secondary transition-colors">
                                    mail
                                </span>
                                <input
                                    {...register("email", {
                                        required: "Обязательное поле",
                                        pattern: {
                                            value: /^\S+@\S+$/i,
                                            message: "Некорректный формат email",
                                        },
                                    })}
                                    className="w-full pl-12 pr-4 py-3 bg-surface-container-low border-none rounded-xl focus:ring-2 focus:ring-primary/30 focus:bg-surface-container-lowest transition-all duration-200"
                                    id="email"
                                    placeholder="student@academy.edu"
                                    type="email"
                                />
                            </div>
                            {errors.email && (
                                <span className="text-xs text-error px-1">{errors.email.message}</span>
                            )}
                        </div>

                        {/* Password Field */}
                        <div className="space-y-1.5">
                            <div className="flex justify-between items-center px-1">
                                <label
                                    className="text-sm font-semibold text-on-surface-variant"
                                    htmlFor="password"
                                >
                                    Пароль
                                </label>
                                <a
                                    className="text-xs font-semibold text-primary hover:text-secondary-fixed-dim transition-colors"
                                    href="#"
                                >
                                    Забыли пароль?
                                </a>
                            </div>
                            <div className="relative group">
                                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-outline text-xl group-focus-within:text-secondary transition-colors">
                                    lock
                                </span>
                                <input
                                    {...register("plain_password", { required: "Введите пароль" })}
                                    className="w-full pl-12 pr-12 py-3 bg-surface-container-low border-none rounded-xl focus:ring-2 focus:ring-primary/30 focus:bg-surface-container-lowest transition-all duration-200"
                                    id="password"
                                    placeholder="••••••••"
                                    type={showPassword ? "text" : "password"}
                                />
                                <button
                                    className="absolute right-4 top-1/2 -translate-y-1/2 text-outline hover:text-on-surface-variant transition-colors"
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                >
                                    <span className="material-symbols-outlined text-lg">
                                        {showPassword ? "visibility_off" : "visibility"}
                                    </span>
                                </button>
                            </div>
                            {errors.plain_password && (
                                <span className="text-xs text-error px-1">
                                    {errors.plain_password.message}
                                </span>
                            )}
                        </div>

                        {/* CTA Button - стили точно как в Register */}
                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="w-full mt-6 py-4 bg-gradient-to-r from-primary to-primary-container text-on-primary font-headline font-bold text-lg rounded-xl shadow-lg shadow-primary/20 hover:scale-[0.98] active:scale-95 disabled:opacity-70 disabled:hover:scale-100 transition-all duration-200"
                        >
                            {isSubmitting ? "Вход..." : "Войти"}
                        </button>
                    </form>

                    {/* Подвал со ссылкой - стили точно как в Register */}
                    <div className="mt-8 pt-8 border-t border-surface-container text-center">
                        <p className="text-on-surface-variant text-sm font-medium">
                            Нет аккаунта?
                            <Link
                                to="/register"
                                className="text-primary font-bold hover:text-secondary-fixed-dim transition-colors ml-1"
                            >
                                Зарегистрироваться
                            </Link>
                        </p>
                    </div>
                </div>
            </main>
        </div>
    );
}