import { apiClient, setAccessToken } from './client';
import { AuthResponse, MessageResponse, RegisterUserCommand } from './types';

export const authApi = {
    async login(data: any): Promise<AuthResponse> {
        const response = await apiClient.post<AuthResponse>('/auth/login', data);
        setAccessToken(response.data.access_token);
        return response.data;
    },

    async register(data: RegisterUserCommand): Promise<AuthResponse> {
        const response = await apiClient.post<AuthResponse>('/auth/register', data);
        setAccessToken(response.data.access_token);
        return response.data;
    },

    async logout(): Promise<MessageResponse> {
        const response = await apiClient.post<MessageResponse>('/auth/logout');
        setAccessToken(null);
        return response.data;
    }
};