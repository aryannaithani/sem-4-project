// api.js — All API calls for the AI Career Mentor frontend

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';


async function request(path, options = {}) {
    const res = await fetch(`${BASE}${path}`, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || res.statusText);
    }
    return res.json();
}

// ── Profile ──────────────────────────────────────────────────
export const getProfile = () => request('/profile');

export const updateProfile = (data) =>
    request('/profile/update', { method: 'POST', body: JSON.stringify(data) });

// ── Tasks ────────────────────────────────────────────────────
export const getTasks = () => request('/tasks');

export const generateTasks = () =>
    request('/generate', { method: 'POST' });

export const completeTask = (id) =>
    request(`/complete/${id}`, { method: 'POST' });

// ── Roadmap ──────────────────────────────────────────────────
export const getRoadmap = () => request('/roadmap');

export const getFullRoadmap = () => request('/roadmap/full');

// ── Trends ───────────────────────────────────────────────────
export const getTrends = () => request('/trends');

// ── Analytics ────────────────────────────────────────────────
export const getAnalytics = () => request('/analytics');

// ── Learning Profile (Digital Twin) ──────────────────────────
export const getLearningProfile = () => request('/learning-profile');

// ── Mentor Chat ───────────────────────────────────────────────
export const sendMentorMessage = (message, history = []) =>
    request('/mentor/chat', {
        method: 'POST',
        body: JSON.stringify({ message, history }),
    });

export const getMentorHistory = () => request('/mentor/history');

export const clearMentorHistory = () =>
    request('/mentor/clear', { method: 'POST' });
