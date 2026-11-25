const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

let authTokenGetter: (() => Promise<string | null>) | null = null;

export const setAuthTokenGetter = (getter: () => Promise<string | null>) => {
  authTokenGetter = getter;
};

async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (authTokenGetter) {
    try {
      const token = await authTokenGetter();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    } catch (e) {
      console.warn("Could not get auth token", e);
    }
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = response.statusText;
    try {
      const errJson = await response.json();
      if (errJson && errJson.detail) {
        errorDetail = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
      }
    } catch (_) {}
    throw new Error(errorDetail || `API request failed with status ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Authentication
  authSignup: (payload: {
    identifier: string;
    password: string;
    confirm_password?: string;
    full_name?: string;
    taluk?: string;
  }) => fetchWithAuth('/auth/signup', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  authLogin: (payload: { identifier: string; password: string }) =>
    fetchWithAuth('/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  authForgotPassword: (identifier: string) =>
    fetchWithAuth('/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ identifier }),
    }),
  authResetPassword: (payload: {
    token: string;
    new_password: string;
    confirm_new_password?: string;
  }) => fetchWithAuth('/auth/reset-password', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  authLogout: () => fetchWithAuth('/auth/logout', { method: 'POST' }),

  // User Profile & Global Crop Preference
  getMyProfile: () => fetchWithAuth('/users/me'),
  updateMyProfile: (data: any) => fetchWithAuth('/users/me', {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  getCropPreference: () => fetchWithAuth('/users/me/crop-preference'),
  updateCropPreference: (crop: string) => fetchWithAuth('/users/me/crop-preference', {
    method: 'PUT',
    body: JSON.stringify({ crop }),
  }),
  deleteMyAccount: () => fetchWithAuth('/users/me', {
    method: 'DELETE',
  }),

  // Crop Recommendation
  recommendCrops: (payload: {
    taluk: string;
    water_availability: string;
    soil_type?: string;
    irrigation_available?: boolean;
    previous_crop?: string;
    plantation_area_acres?: number;
  }) => fetchWithAuth('/crops/recommend', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  getCropRecommendations: () => fetchWithAuth('/crops/recommendations'),

  // Weather Assistant
  getCurrentWeather: (taluk: string = 'Mangaluru') =>
    fetchWithAuth(`/weather/current?taluk=${encodeURIComponent(taluk)}`),
  getWeatherForecast: (taluk: string = 'Mangaluru') =>
    fetchWithAuth(`/weather/forecast?taluk=${encodeURIComponent(taluk)}`),
  getWeatherAdvisory: (payload: { taluk: string; crop?: string }) =>
    fetchWithAuth('/weather/advisory', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getWeatherAlerts: (taluk: string = 'Mangaluru') =>
    fetchWithAuth(`/weather/alerts?taluk=${encodeURIComponent(taluk)}`),

  // Storage Assistant
  recommendStorage: (payload: {
    crop: string;
    harvest_date: string;
    storage_method: string;
    crop_condition: string;
    taluk?: string;
    quantity_kg?: number;
    storage_facility_description?: string;
  }) => fetchWithAuth('/storage/recommend', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  getStorageHistory: () => fetchWithAuth('/storage/history'),
  getStorageRecord: (id: string) => fetchWithAuth(`/storage/${id}`),

  // AI Assistant
  getAIStorageAdvice: (payload: {
    crop: string;
    harvest_date: string;
    storage_method: string;
    crop_condition: string;
    taluk?: string;
    language?: string;
  }) => fetchWithAuth('/ai/storage-assistant', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),

  // Bookmarks / Saved Items
  saveItem: (item: {
    itemType: string;
    itemId: string;
    title: string;
    title_kn?: string;
    crop?: string;
    location?: string;
    content: any;
  }) => fetchWithAuth('/saved', {
    method: 'POST',
    body: JSON.stringify(item),
  }),
  getSavedItems: (category?: string) =>
    fetchWithAuth(`/saved${category ? `?category=${encodeURIComponent(category)}` : ''}`),
  deleteSavedItem: (id: string) =>
    fetchWithAuth(`/saved/${id}`, { method: 'DELETE' }),

  // Notifications
  getNotifications: () => fetchWithAuth('/notifications'),
  markNotificationRead: (id: string) =>
    fetchWithAuth(`/notifications/${id}/read`, { method: 'PUT' }),
  getNotificationPreferences: () => fetchWithAuth('/notifications/preferences'),
  updateNotificationPreferences: (prefs: any) =>
    fetchWithAuth('/notifications/preferences', {
      method: 'PUT',
      body: JSON.stringify(prefs),
    }),

  // Farm Management & Daily Monitoring
  createFarm: (payload: {
    name?: string;
    crop: string;
    taluk: string;
    area: number;
    area_unit?: string;
    cultivation_start_date?: string;
    initial_farming_day?: number;
    current_stage?: string;
    variety?: string;
    cultivation_method?: string;
    soil_type?: string;
    water_availability?: string;
    notes?: string;
  }) => fetchWithAuth('/farms', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  getFarms: () => fetchWithAuth('/farms'),
  getFarm: (id: string) => fetchWithAuth(`/farms/${id}`),
  updateFarm: (id: string, updates: any) => fetchWithAuth(`/farms/${id}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  }),
  deleteFarm: (id: string) => fetchWithAuth(`/farms/${id}`, { method: 'DELETE' }),
  correctFarmProgress: (id: string, payload: {
    new_crop_day?: number;
    new_stage?: string;
    reason?: string;
  }) => fetchWithAuth(`/farms/${id}/progress-correction`, {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  getFarmCorrections: (id: string) => fetchWithAuth(`/farms/${id}/corrections`),
  getTodayActivities: (farmId: string) => fetchWithAuth(`/farms/${farmId}/activities/today`),
  completeActivity: (farmId: string, activityId: string) =>
    fetchWithAuth(`/farms/${farmId}/activities/${activityId}/complete`, { method: 'POST' }),
  skipActivity: (farmId: string, activityId: string, reason?: string) =>
    fetchWithAuth(`/farms/${farmId}/activities/${activityId}/skip`, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    }),
  getActivitiesHistory: (farmId: string, dateQuery?: string) =>
    fetchWithAuth(`/farms/${farmId}/activities/history${dateQuery ? `?date=${encodeURIComponent(dateQuery)}` : ''}`),
  createFarmObservation: (farmId: string, payload: any) =>
    fetchWithAuth(`/farms/${farmId}/observations`, {
      method: 'POST',
      body: JSON.stringify({ ...payload, farm_id: farmId }),
    }),
  getFarmObservations: (farmId: string) => fetchWithAuth(`/farms/${farmId}/observations`),
  createFarmHarvest: (farmId: string, payload: any) =>
    fetchWithAuth(`/farms/${farmId}/harvests`, {
      method: 'POST',
      body: JSON.stringify({ ...payload, farm_id: farmId }),
    }),
  getFarmHarvests: (farmId: string) => fetchWithAuth(`/farms/${farmId}/harvests`),
  getCropStages: (crop: string) => fetchWithAuth(`/farms/stages/${encodeURIComponent(crop)}`),
};
