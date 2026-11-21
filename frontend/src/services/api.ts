import axios from 'axios';
import { 
  User, CandidateProfile, Job, Recommendation, 
  SavedJob, UserPreferences, ChatMessage 
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('careerpilot_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const api = {
  // Auth
  auth: {
    login: async (email: string, password: string) => {
      const res = await apiClient.post<{ access_token: string }>('/auth/login', { email, password });
      return res.data;
    },
    register: async (email: string, password: string, full_name: string) => {
      const res = await apiClient.post<User>('/auth/register', { email, password, full_name });
      return res.data;
    },
    getMe: async () => {
      const res = await apiClient.get<User>('/auth/me');
      return res.data;
    },
  },

  // Profiles
  profile: {
    get: async () => {
      const res = await apiClient.get<CandidateProfile>('/profiles/me');
      return res.data;
    },
    update: async (data: Partial<CandidateProfile>) => {
      const res = await apiClient.put<CandidateProfile>('/profiles/me', data);
      return res.data;
    },
  },

  // Resumes
  resume: {
    upload: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      const res = await apiClient.post('/resumes/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return res.data;
    },
    list: async () => {
      const res = await apiClient.get('/resumes/');
      return res.data;
    },
  },

  // Jobs
  jobs: {
    list: async (params?: { page?: number; limit?: number; remote_policy?: string; experience_level?: string; location?: string }) => {
      const res = await apiClient.get<Job[]>('/jobs/', { params });
      return res.data;
    },
    get: async (id: string) => {
      const res = await apiClient.get<Job>(`/jobs/${id}`);
      return res.data;
    },
  },

  // Semantic Search
  search: {
    semantic: async (query: { query?: string; location?: string; remote_policy?: string; min_salary?: number; limit?: number }) => {
      const res = await apiClient.post<Job[]>('/search/', query);
      return res.data;
    },
  },

  // Recommendations
  recommendations: {
    list: async (limit: number = 10) => {
      const res = await apiClient.get<Recommendation[]>('/recommendations/', { params: { limit } });
      return res.data;
    },
  },

  // Saved Jobs
  savedJobs: {
    list: async () => {
      const res = await apiClient.get<SavedJob[]>('/saved-jobs/');
      return res.data;
    },
    save: async (job_id: string, notes?: string) => {
      const res = await apiClient.post<SavedJob>('/saved-jobs/', { job_id, notes, status: 'SAVED' });
      return res.data;
    },
    update: async (id: string, status: string, notes?: string) => {
      const res = await apiClient.put<SavedJob>(`/saved-jobs/${id}`, { status, notes });
      return res.data;
    },
    delete: async (id: string) => {
      await apiClient.delete(`/saved-jobs/${id}`);
    },
  },

  // Preferences
  preferences: {
    get: async () => {
      const res = await apiClient.get<UserPreferences>('/preferences/');
      return res.data;
    },
    update: async (data: Partial<UserPreferences>) => {
      const res = await apiClient.put<UserPreferences>('/preferences/', data);
      return res.data;
    },
  },

  // Chat
  chat: {
    send: async (message: string, conversation_id?: string) => {
      const res = await apiClient.post<{ conversation_id: string; reply: string; tool_calls_executed: any[] }>('/chat/', {
        message,
        conversation_id,
      });
      return res.data;
    },
  },
};
