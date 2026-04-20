import { apiClient } from './client';
import { User } from './types';

export const usersApi = {
    async getMe(): Promise<User> {

        const response = await apiClient.get<User>('/users/me', {
            skipGlobalErrorNotification: true
        } as any);
        return response.data;
    }
};