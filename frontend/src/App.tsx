import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { LanguageProvider } from './contexts/LanguageContext';
import { NotificationProvider } from './contexts/NotificationContext';
import { CropProvider } from './contexts/CropContext';
import { FarmProvider } from './contexts/FarmContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { NotificationModal } from './components/NotificationModal';

// Pages
import { LoginPage } from './pages/Login/LoginPage';
import { DashboardPage } from './pages/Dashboard/DashboardPage';
import { MyFarmPage } from './pages/MyFarm/MyFarmPage';
import { CropRecommendationPage } from './pages/CropRecommendation/CropRecommendationPage';
import { WeatherAssistantPage } from './pages/WeatherAssistant/WeatherAssistantPage';
import { StorageAssistantPage } from './pages/StorageAssistant/StorageAssistantPage';
import { SavedPage } from './pages/Saved/SavedPage';
import { ProfilePage } from './pages/Profile/ProfilePage';

const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-cream font-sans text-gray-800">
      <Navbar />
      <main className="flex-1">
        {children}
      </main>
      <Footer />
      <NotificationModal />
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <CropProvider>
        <FarmProvider>
          <LanguageProvider>
            <NotificationProvider>
            <Router>
              <Routes>
                {/* Public Authentication Route */}
                <Route path="/login" element={<LoginPage />} />

                {/* Protected Application Routes */}
                <Route
                  path="/"
                  element={
                    <ProtectedRoute>
                      <AppLayout>
                        <DashboardPage />
                      </AppLayout>
                    </ProtectedRoute>
                  }
                />

                <Route
                  path="/my-farm"
                  element={
                    <ProtectedRoute>
                      <AppLayout>
                        <MyFarmPage />
                      </AppLayout>
                    </ProtectedRoute>
                  }
                />

              <Route
                path="/crop-recommendation"
                element={
                  <ProtectedRoute>
                    <AppLayout>
                      <CropRecommendationPage />
                    </AppLayout>
                  </ProtectedRoute>
                }
              />

              <Route
                path="/weather-assistant"
                element={
                  <ProtectedRoute>
                    <AppLayout>
                      <WeatherAssistantPage />
                    </AppLayout>
                  </ProtectedRoute>
                }
              />

              <Route
                path="/storage-assistant"
                element={
                  <ProtectedRoute>
                    <AppLayout>
                      <StorageAssistantPage />
                    </AppLayout>
                  </ProtectedRoute>
                }
              />

              <Route
                path="/saved"
                element={
                  <ProtectedRoute>
                    <AppLayout>
                      <SavedPage />
                    </AppLayout>
                  </ProtectedRoute>
                }
              />

              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <AppLayout>
                      <ProfilePage />
                    </AppLayout>
                  </ProtectedRoute>
                }
              />

              {/* Catch-all redirect */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Router>
        </NotificationProvider>
      </LanguageProvider>
      </FarmProvider>
    </CropProvider>
  </AuthProvider>
  );
};

export default App;
