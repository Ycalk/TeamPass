import { apiClient } from './client';

export interface Profile {
    telegram_username: string;
    vk_profile_link: string;
    phone_number: string;
    strengths_text: string;
    weaknesses_text: string;
    user: {
        student: {
            student_id: string;
            first_name: string;
            last_name: string;
            patronymic: string;
        };
    };
}

export const profileApi = {
    async getMyProfile(): Promise<Profile> {
        const res = await apiClient.get('/users/me/profile');
        return res.data;
    },

    async updateProfile(data: Partial<Profile>): Promise<Profile> {
        const res = await apiClient.patch('/users/me/profile', data);
        return res.data;
    }
};