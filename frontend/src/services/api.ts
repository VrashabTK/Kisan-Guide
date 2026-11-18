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
  // User Profile
  getMyProfile: () => fetchWithAuth('/users/me'),
  updateMyProfile: (data: any) => fetchWithAuth('/users/me', {
    method: 'PUT',
    body: JSON.stringify(data),
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
};
