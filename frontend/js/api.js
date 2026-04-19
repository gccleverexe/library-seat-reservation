// api.js - Axios wrapper for the library seat reservation system
const BASE_URL = 'http://localhost:8000';

const api = axios.create({
    baseURL: BASE_URL,
    timeout: 10000,
    headers: { 'Content-Type': 'application/json' }
});

// Request interceptor: inject JWT token
api.interceptors.request.use(config => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Response interceptor: handle 401 redirect and parse unified response
api.interceptors.response.use(
    response => {
        const data = response.data;
        if (data.code && data.code !== 200 && data.code !== 201) {
            return Promise.reject(new Error(data.message || '请求失败'));
        }
        return data;
    },
    error => {
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_info');
            window.location.href = '/pages/login.html';
        }
        const msg = error.response?.data?.detail || error.message || '网络错误';
        return Promise.reject(new Error(msg));
    }
);

// Auth API
const authAPI = {
    register: (data) => api.post('/api/auth/register', data),
    login: (data) => api.post('/api/auth/login', data),
    me: () => api.get('/api/auth/me'),
};

// Seats API
const seatsAPI = {
    list: (params) => api.get('/api/seats', { params }),
    get: (id) => api.get(`/api/seats/${id}`),
};

// Reservations API
const reservationsAPI = {
    create: (data) => api.post('/api/reservations', data),
    cancel: (id) => api.delete(`/api/reservations/${id}`),
    history: (params) => api.get('/api/reservations/history', { params }),
};

// Checkin API
const checkinAPI = {
    checkin: (data) => api.post('/api/checkin', data),
    checkout: (data) => api.post('/api/checkout', data),
};

// Admin API
const adminAPI = {
    // Seats
    createSeat: (data) => api.post('/api/admin/seats', data),
    updateSeat: (id, data) => api.put(`/api/admin/seats/${id}`, data),
    deleteSeat: (id) => api.delete(`/api/admin/seats/${id}`),
    setSeatStatus: (id, data) => api.patch(`/api/admin/seats/${id}/status`, data),
    // Reservations
    listReservations: (params) => api.get('/api/admin/reservations', { params }),
    cancelReservation: (id) => api.delete(`/api/admin/reservations/${id}`),
    // Violations
    getViolations: (studentId) => api.get('/api/admin/violations', { params: { student_id: studentId } }),
    liftRestriction: (studentId) => api.delete(`/api/admin/violations/${studentId}/restriction`),
    // Dashboard
    getSummary: (params) => api.get('/api/admin/dashboard/summary', { params }),
    getHotSeats: () => api.get('/api/admin/dashboard/hot-seats'),
    getHourly: () => api.get('/api/admin/dashboard/hourly'),
    getViolationStats: (params) => api.get('/api/admin/dashboard/violations', { params }),
};
