import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000'; // Target FastAPI backend

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getProfile = async () => {
    const response = await api.get('/profile');
    return response.data;
};

export const getTasks = async () => {
    const response = await api.get('/tasks');
    return response.data.tasks;
};

export const generateTasks = async () => {
    const response = await api.post('/generate');
    return response.data;
};

export const completeTask = async (taskId) => {
    const response = await api.post(`/complete/${taskId}`);
    return response.data;
};

export const getRoadmap = async () => {
    const response = await api.get('/roadmap');
    return response.data;
};

export default api;
