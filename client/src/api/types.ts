export interface Student {
    student_id: string;
    first_name: string;
    last_name: string;
    patronymic?: string;
}

export interface User {
    id: string;
    email: string;
    student: Student;
}

export interface AuthResponse {
    access_token: string;
    user: User;
}

export interface RefreshResponse {
    access_token: string;
}

export interface MessageResponse {
    message: string;
}

export interface ApiErrorResponse {
    error: string;
    message: string;
}

export interface RegisterUserCommand {
    email: string;
    plain_password: string;
    student_id: string;
    first_name: string;
    last_name: string;
    patronymic: string | null;
}

export interface LoginUserCommand {
    email: string;
    plain_password: string;
}