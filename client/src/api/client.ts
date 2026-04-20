import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { toast } from 'sonner';
import { RefreshResponse, ApiErrorResponse } from './types';

let accessToken: string | null = null;

export const setAccessToken = (token: string | null) => {
    accessToken = token;
};

export const getAccessToken = () => accessToken;

export const apiClient = axios.create({
    baseURL: '/api/v1',
    withCredentials: true,
});


export const refreshAccessToken = async () => {
    const { data } = await axios.post<RefreshResponse>(
        '/api/v1/auth/refresh',
        {},
        { withCredentials: true }
    );
    setAccessToken(data.access_token);
    return data.access_token;
};

apiClient.interceptors.request.use((config) => {
    if (accessToken && config.headers) {
        config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
});

let isRefreshing = false;
let failedQueue: Array<{
    resolve: (token: string) => void;
    reject: (error: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
    failedQueue.forEach((prom) => {
        if (error) {
            prom.reject(error);
        } else if (token) {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

apiClient.interceptors.response.use(
    (response) => response,
    async (error: AxiosError<ApiErrorResponse>) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

        if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
            const isAuthRoute = originalRequest.url?.includes('/auth/refresh') || originalRequest.url?.includes('/auth/login');

            if (!isAuthRoute) {
                if (isRefreshing) {
                    return new Promise(function (resolve, reject) {
                        failedQueue.push({ resolve, reject });
                    })
                        .then((token) => {
                            originalRequest.headers.Authorization = `Bearer ${token}`;
                            return apiClient(originalRequest);
                        })
                        .catch((err) => Promise.reject(err));
                }

                originalRequest._retry = true;
                isRefreshing = true;

                try {
                    // Используем нашу новую функцию
                    const newToken = await refreshAccessToken();

                    processQueue(null, newToken);

                    originalRequest.headers.Authorization = `Bearer ${newToken}`;
                    return apiClient(originalRequest);
                } catch (refreshError) {
                    processQueue(refreshError, null);
                    setAccessToken(null);
                    return Promise.reject(refreshError);
                } finally {
                    isRefreshing = false;
                }
            }
        }

        const customConfig = originalRequest as any;
        if (!customConfig?.skipGlobalErrorNotification && error.response) {
            const status = error.response.status;
            if ([400, 401, 403, 404, 409, 500].includes(status)) {
                const errName = error.response.data?.error || 'Ошибка';
                const errMessage = error.response.data?.message || 'Произошла непредвиденная ошибка';
                toast.error(`${errName}: ${errMessage}`);
            }
        }

        return Promise.reject(error);
    }
);