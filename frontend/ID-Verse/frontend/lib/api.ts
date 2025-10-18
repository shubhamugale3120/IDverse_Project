import axios from 'axios';

// API Configuration
const API_BASE_URL = 'http://localhost:5000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('jwt_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('jwt_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API Service Functions
export const authAPI = {
  // User Registration
  register: async (userData: { username: string; email: string; password: string }) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  // User Login
  login: async (credentials: { email: string; password: string }) => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },

  // OTP Request
  requestOTP: async (email: string) => {
    const response = await api.post('/auth/otp/request', { email });
    return response.data;
  },

  // OTP Verification
  verifyOTP: async (otpData: { email: string; otp: string; otp_token: string }) => {
    const response = await api.post('/auth/otp/verify', otpData);
    return response.data;
  },
};

export const schemesAPI = {
  // Get Available Schemes
  getSchemes: async () => {
    const response = await api.get('/schemes/');
    return response.data;
  },
};

export const vcAPI = {
  // Request VC Issue
  requestIssue: async (vcData: { scheme_id: number; citizen_data: any }) => {
    const response = await api.post('/vc/request-issue', vcData);
    return response.data;
  },

  // Issue VC
  issue: async (vcData: { request_id: string; citizen_data: any }) => {
    const response = await api.post('/vc/issue', vcData);
    return response.data;
  },

  // Present VC
  present: async (vcData: { vc: any }) => {
    const response = await api.post('/vc/present', vcData);
    return response.data;
  },

  // Get VC Status
  getStatus: async (vcId: string) => {
    const response = await api.get(`/vc/status/${vcId}`);
    return response.data;
  },
};

export const benefitsAPI = {
  // Apply for Benefits
  apply: async (applicationData: { scheme_id: number; citizen_data: any }) => {
    const response = await api.post('/benefits/apply', applicationData);
    return response.data;
  },

  // Approve Benefits
  approve: async (approvalData: { application_id: string; approved: boolean }) => {
    const response = await api.post('/benefits/approve', approvalData);
    return response.data;
  },

  // Get Wallet Balance
  getWallet: async () => {
    const response = await api.get('/benefits/wallet');
    return response.data;
  },

  // Get Applications
  getApplications: async () => {
    const response = await api.get('/benefits/applications');
    return response.data;
  },
};

// Health Check
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

// Transactions API
export const transactionsAPI = {
  getTransactions: async () => {
    const response = await api.get('/transactions/');
    return response.data;
  },
  getSummary: async () => {
    const response = await api.get('/transactions/summary');
    return response.data;
  },
};

// QR Code API
export const qrAPI = {
  generate: async () => {
    const response = await api.post('/qr/generate');
    return response.data;
  },
  getSmartCard: async () => {
    const response = await api.get('/qr/smartcard');
    return response.data;
  },
};

export default api;
