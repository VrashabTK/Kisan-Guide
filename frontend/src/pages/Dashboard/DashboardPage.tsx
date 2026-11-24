import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Sprout,
  CloudSun,
  Warehouse,
  ArrowRight,
  Droplets,
  Wind,
  Thermometer,
  Calendar,
  AlertTriangle,
  Bookmark,
  CheckCircle2,
  MapPin,
  ChevronRight,
  Sparkles
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { useCrop } from '../../contexts/CropContext';
import { api } from '../../services/api';

export const DashboardPage: React.FC = () => {
  const { t } = useTranslation();
  const { profile } = useAuth();
  const { language } = useLanguage();
  const { selectedCrop } = useCrop();

  const [weather, setWeather] = useState<any>(null);
  const [advisory, setAdvisory] = useState<any>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [savedItems, setSavedItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const selectedTaluk = profile?.taluk || 'Mangaluru';

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        // Fetch weather
        const wData = await api.getCurrentWeather(selectedTaluk);
        setWeather(wData);

        // Fetch advisories
        const advData = await api.getWeatherAdvisory({ taluk: selectedTaluk, crop: 'All' });
        setAdvisory(advData?.advisories?.[0] || null);

        // Fetch alerts
        const alData = await api.getWeatherAlerts(selectedTaluk);
        setAlerts(alData?.alerts || []);

        // Fetch saved bookmarks
        const sData = await api.getSavedItems();
        setSavedItems((sData || []).slice(0, 3));
      } catch (err) {
        console.warn("Error loading dashboard data", err);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, [selectedTaluk]);

  const todayDateFormatted = new Date().toLocaleDateString(
    language === 'kn' ? 'kn-IN' : 'en-IN',
    { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }
  );

  return (
    <div className="space-y-8 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      
      {/* 1. Welcome Header Banner */}
      <div className="relative overflow-hidden bg-gradient-to-r from-forest via-forest-light to-leaf rounded-3xl p-6 sm:p-8 text-white shadow-xl shadow-forest/15">
        <div className="absolute top-0 right-0 w-80 h-80 bg-white/5 rounded-full blur-3xl pointer-events-none" />
        
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2 text-leaf-light text-xs sm:text-sm font-semibold tracking-wide">
              <span className="flex items-center space-x-1">
                <Calendar className="w-4 h-4" />
                <span>{todayDateFormatted}</span>
              </span>
              <span>•</span>
              <span className="flex items-center space-x-1">
                <MapPin className="w-3.5 h-3.5" />
                <span>{t(`taluks.${selectedTaluk}`)}</span>
              </span>
              <span>•</span>
              <span className="flex items-center space-x-1 bg-white/15 px-2.5 py-0.5 rounded-full text-cream border border-white/20">
                <Sprout className="w-3.5 h-3.5 text-leaf-light" />
                <span>{language === 'kn' ? t(`crops.${selectedCrop}`) : selectedCrop}</span>
              </span>
            </div>

            <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight">
              {t('dashboard.greeting')}, {profile?.fullName || 'Farmer'}!
            </h1>
            <p className="text-cream/90 text-xs sm:text-sm max-w-xl">
              {t('dashboard.welcomeSub')}
            </p>
          </div>

          {/* Quick Weather Snapshot Card inside Banner */}
          {weather && weather.current && (
            <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-4 sm:p-5 flex items-center space-x-5 text-white shrink-0">
              <div className="p-3 bg-white/10 rounded-2xl">
                <CloudSun className="w-8 h-8 text-amber-300" />
              </div>
              <div>
                <div className="flex items-baseline space-x-2">
                  <span className="text-3xl font-black">
                    {weather.current.temperature}°C
                  </span>
                  <span className="text-xs text-cream/80">
                    {language === 'kn' ? weather.current.condition_kn : weather.current.condition_en}
                  </span>
                </div>
                <div className="flex items-center space-x-3 text-xs text-cream/80 mt-1">
                  <span className="flex items-center space-x-1">
                    <Droplets className="w-3.5 h-3.5 text-blue-300" />
                    <span>{weather.current.humidity}%</span>
                  </span>
                  <span>•</span>
                  <span className="flex items-center space-x-1">
                    <Wind className="w-3.5 h-3.5 text-cream" />
                    <span>{weather.current.wind_speed} km/h</span>
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 2. Severe Weather Alert Banner (If Any) */}
      {alerts && alerts.length > 0 && (
        <div className="p-4 sm:p-5 rounded-2xl bg-amber-50 border border-amber-200 text-amber-900 flex items-start space-x-3 shadow-sm animate-pulse">
          <AlertTriangle className="w-6 h-6 text-amber-600 shrink-0 mt-0.5" />
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-sm sm:text-base">
                {language === 'kn' && alerts[0].title_kn ? alerts[0].title_kn : alerts[0].title_en}
              </h3>
              <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-amber-200/80 text-amber-900">
                {alerts[0].severity}
              </span>
            </div>
            <p className="text-xs text-amber-800 mt-1">
              {language === 'kn' && alerts[0].precautions_kn
                ? alerts[0].precautions_kn[0]
                : alerts[0].precautions_en?.[0]}
            </p>
          </div>
          <Link
            to="/weather-assistant"
            className="text-xs font-bold text-amber-800 hover:text-amber-900 underline shrink-0 self-center"
          >
            {t('common.viewDetails')}
          </Link>
        </div>
      )}

      {/* 3. The Three Primary Feature Cards (Prominent CTA) */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg sm:text-xl font-bold text-gray-900">
            Dakshina Kannada Core Services
          </h2>
          <span className="text-xs text-earth font-semibold">
            Coconut • Rice • Arecanut • Cocoa
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Card 1: Crop Recommendation */}
          <Link
            to="/crop-recommendation"
            className="group relative bg-white rounded-3xl p-6 sm:p-7 border border-cream-dark shadow-sm hover:shadow-xl hover:shadow-forest/10 hover:border-forest/30 transition-all flex flex-col justify-between"
          >
            <div>
              <div className="w-14 h-14 rounded-2xl bg-forest/10 text-forest flex items-center justify-center mb-5 group-hover:bg-forest group-hover:text-white transition-colors">
                <Sprout className="w-7 h-7" />
              </div>
              <h3 className="font-extrabold text-xl text-gray-900 mb-2 group-hover:text-forest transition-colors">
                {t('dashboard.featureCropTitle')}
              </h3>
              <p className="text-xs sm:text-sm text-gray-600 leading-relaxed mb-6">
                {t('dashboard.featureCropDesc')}
              </p>
            </div>
            
            <div className="flex items-center text-xs font-bold text-forest group-hover:text-leaf-dark space-x-1.5 pt-4 border-t border-gray-100">
              <span>{t('dashboard.featureCropCta')}</span>
              <ArrowRight className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>

          {/* Card 2: Weather Assistant */}
          <Link
            to="/weather-assistant"
            className="group relative bg-white rounded-3xl p-6 sm:p-7 border border-cream-dark shadow-sm hover:shadow-xl hover:shadow-forest/10 hover:border-forest/30 transition-all flex flex-col justify-between"
          >
            <div>
              <div className="w-14 h-14 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mb-5 group-hover:bg-amber-500 group-hover:text-white transition-colors">
                <CloudSun className="w-7 h-7" />
              </div>
              <h3 className="font-extrabold text-xl text-gray-900 mb-2 group-hover:text-forest transition-colors">
                {t('dashboard.featureWeatherTitle')}
              </h3>
              <p className="text-xs sm:text-sm text-gray-600 leading-relaxed mb-6">
                {t('dashboard.featureWeatherDesc')}
              </p>
            </div>
            
            <div className="flex items-center text-xs font-bold text-forest group-hover:text-leaf-dark space-x-1.5 pt-4 border-t border-gray-100">
              <span>{t('dashboard.featureWeatherCta')}</span>
              <ArrowRight className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>

          {/* Card 3: Storage Assistant */}
          <Link
            to="/storage-assistant"
            className="group relative bg-white rounded-3xl p-6 sm:p-7 border border-cream-dark shadow-sm hover:shadow-xl hover:shadow-forest/10 hover:border-forest/30 transition-all flex flex-col justify-between"
          >
            <div>
              <div className="w-14 h-14 rounded-2xl bg-earth/10 text-earth flex items-center justify-center mb-5 group-hover:bg-earth group-hover:text-white transition-colors">
                <Warehouse className="w-7 h-7" />
              </div>
              <h3 className="font-extrabold text-xl text-gray-900 mb-2 group-hover:text-forest transition-colors">
                {t('dashboard.featureStorageTitle')}
              </h3>
              <p className="text-xs sm:text-sm text-gray-600 leading-relaxed mb-6">
                {t('dashboard.featureStorageDesc')}
              </p>
            </div>
            
            <div className="flex items-center text-xs font-bold text-forest group-hover:text-leaf-dark space-x-1.5 pt-4 border-t border-gray-100">
              <span>{t('dashboard.featureStorageCta')}</span>
              <ArrowRight className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>

        </div>
      </div>

      {/* 4. Dual Section: Today's Advisory & Bookmarks */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Today's Advisory (2 cols) */}
        <div className="lg:col-span-2 bg-white rounded-3xl p-6 sm:p-7 border border-cream-dark shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-forest" />
              <h3 className="font-bold text-gray-900 text-lg">
                {t('dashboard.todayAdvisory')}
              </h3>
            </div>
            <Link
              to="/weather-assistant"
              className="text-xs text-forest hover:underline font-semibold"
            >
              All Routines
            </Link>
          </div>

          {advisory ? (
            <div className="p-5 rounded-2xl bg-cream border border-cream-dark space-y-3">
              <div className="flex items-center justify-between">
                <span className="px-2.5 py-1 rounded-full bg-forest/10 text-forest text-xs font-bold">
                  {language === 'kn' && advisory.category_kn ? advisory.category_kn : advisory.category}
                </span>
                <span className="text-xs text-gray-500 font-medium">
                  Crop: {language === 'kn' && advisory.crop_kn ? advisory.crop_kn : advisory.crop}
                </span>
              </div>
              <h4 className="font-extrabold text-base text-gray-900">
                {language === 'kn' && advisory.title_kn ? advisory.title_kn : advisory.title_en}
              </h4>
              <p className="text-xs sm:text-sm text-gray-700 leading-relaxed">
                {language === 'kn' && advisory.task_kn ? advisory.task_kn : advisory.task_en}
              </p>
              <div className="text-xs text-forest bg-white p-3 rounded-xl border border-forest/10">
                <strong>Why: </strong>
                {language === 'kn' && advisory.reason_kn ? advisory.reason_kn : advisory.reason_en}
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-400 text-xs">
              Loading current farming routines for {t(`taluks.${selectedTaluk}`)}...
            </div>
          )}
        </div>

        {/* Quick Saved Items (1 col) */}
        <div className="bg-white rounded-3xl p-6 sm:p-7 border border-cream-dark shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Bookmark className="w-5 h-5 text-earth" />
                <h3 className="font-bold text-gray-900 text-lg">
                  {t('dashboard.recentBookmarks')}
                </h3>
              </div>
              <Link to="/saved" className="text-xs text-forest hover:underline font-semibold">
                {t('common.all')}
              </Link>
            </div>

            {savedItems.length === 0 ? (
              <div className="text-center py-8 text-gray-400 text-xs">
                {t('dashboard.noBookmarks')}
              </div>
            ) : (
              <div className="space-y-3">
                {savedItems.map((item) => (
                  <Link
                    key={item.savedItemId}
                    to="/saved"
                    className="block p-3 rounded-xl border border-gray-100 hover:border-forest/20 hover:bg-cream transition-colors"
                  >
                    <span className="text-[10px] font-bold text-forest uppercase tracking-wider block">
                      {item.itemType}
                    </span>
                    <h5 className="font-semibold text-xs text-gray-900 truncate mt-0.5">
                      {language === 'kn' && item.title_kn ? item.title_kn : item.title}
                    </h5>
                  </Link>
                ))}
              </div>
            )}
          </div>

          <Link
            to="/saved"
            className="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between text-xs font-bold text-forest"
          >
            <span>Open Bookmarked Items</span>
            <ChevronRight className="w-4 h-4" />
          </Link>
        </div>

      </div>

    </div>
  );
};
