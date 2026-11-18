import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  CloudSun,
  MapPin,
  RefreshCw,
  Thermometer,
  Droplets,
  Wind,
  Compass,
  Sun,
  CloudRain,
  AlertTriangle,
  Bookmark,
  Calendar,
  Sparkles,
  ShieldAlert,
  Clock
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { api } from '../../services/api';

export const WeatherAssistantPage: React.FC = () => {
  const { t } = useTranslation();
  const { profile } = useAuth();
  const { language } = useLanguage();

  const [taluk, setTaluk] = useState(profile?.taluk || 'Mangaluru');
  const [selectedCropFilter, setSelectedCropFilter] = useState('All');
  const [weatherData, setWeatherData] = useState<any>(null);
  const [advisories, setAdvisories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [savedNotice, setSavedNotice] = useState<string | null>(null);

  const taluks = [
    'Mangaluru', 'Bantwal', 'Belthangady', 'Puttur',
    'Sullia', 'Moodbidri', 'Kadaba', 'Mulki', 'Ullal'
  ];

  const crops = ['All', 'Coconut', 'Rice', 'Arecanut', 'Cocoa'];

  const fetchWeatherAndAdvisories = async (selectedTaluk: string) => {
    setLoading(true);
    try {
      const forecast = await api.getWeatherForecast(selectedTaluk);
      setWeatherData(forecast);

      const adv = await api.getWeatherAdvisory({
        taluk: selectedTaluk,
        crop: selectedCropFilter,
      });
      setAdvisories(adv?.advisories || []);
    } catch (err) {
      console.error("Failed to fetch weather", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWeatherAndAdvisories(taluk);
  }, [taluk, selectedCropFilter]);

  const handleBookmarkAdvisory = async (adv: any) => {
    try {
      await api.saveItem({
        itemType: 'Weather Assistant',
        itemId: adv.id || `adv_${Date.now()}`,
        title: adv.title_en,
        title_kn: adv.title_kn,
        crop: adv.crop,
        location: taluk,
        content: adv,
      });
      setSavedNotice("Advisory card bookmarked successfully!");
      setTimeout(() => setSavedNotice(null), 3000);
    } catch (e) {
      console.error("Failed to bookmark", e);
    }
  };

  const isKn = language === 'kn';
  const current = weatherData?.current;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Page Title & Taluk Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-forest mb-1">
            <CloudSun className="w-6 h-6" />
            <span className="text-xs font-bold uppercase tracking-wider">Dakshina Kannada Weather & Advisory</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900">
            {t('weather.title')}
          </h1>
          <p className="text-xs sm:text-sm text-gray-600 mt-1">
            {t('weather.subtitle')}
          </p>
        </div>

        {/* Taluk Control Pill */}
        <div className="flex items-center space-x-2 shrink-0">
          <div className="relative">
            <select
              value={taluk}
              onChange={(e) => setTaluk(e.target.value)}
              className="pl-8 pr-4 py-2 rounded-xl border border-gray-300 text-xs sm:text-sm bg-white font-semibold text-gray-800 shadow-sm focus:outline-none focus:ring-2 focus:ring-forest"
            >
              {taluks.map((tlk) => (
                <option key={tlk} value={tlk}>
                  {t(`taluks.${tlk}`)}
                </option>
              ))}
            </select>
            <MapPin className="w-4 h-4 text-forest absolute left-2.5 top-2.5 pointer-events-none" />
          </div>

          <button
            onClick={() => fetchWeatherAndAdvisories(taluk)}
            disabled={loading}
            className="p-2 rounded-xl bg-forest hover:bg-forest-light text-white transition-colors shadow-sm disabled:opacity-50"
            title={t('weather.getRecommendations')}
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {savedNotice && (
        <div className="p-3 bg-green-50 border border-green-200 text-green-700 text-xs rounded-xl font-medium">
          {savedNotice}
        </div>
      )}

      {/* 1. Main Weather Metrics Hero */}
      {current && (
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-cream-dark shadow-sm space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-gray-100">
            <div className="flex items-center space-x-5">
              <div className="w-16 h-16 rounded-2xl bg-amber-50 text-amber-500 flex items-center justify-center shrink-0">
                <CloudSun className="w-10 h-10" />
              </div>
              <div>
                <div className="flex items-baseline space-x-3">
                  <span className="text-4xl sm:text-5xl font-black text-gray-900">
                    {current.temperature}°C
                  </span>
                  <span className="text-sm font-semibold text-gray-500">
                    {t('dashboard.feelsLike')} {current.feels_like}°C
                  </span>
                </div>
                <h3 className="text-base font-bold text-forest mt-1">
                  {isKn ? current.condition_kn : current.condition_en}
                </h3>
              </div>
            </div>

            <div className="text-xs text-gray-400 md:text-right">
              <span>{weatherData?.source || 'Verified IMD / Open-Meteo Feed'}</span>
            </div>
          </div>

          {/* Grid of Meteorological Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-4">
            <div className="p-3.5 rounded-2xl bg-cream border border-cream-dark">
              <span className="text-[11px] font-semibold text-gray-500 block mb-1">
                {t('dashboard.humidity')}
              </span>
              <div className="flex items-center space-x-1.5 font-bold text-base text-gray-900">
                <Droplets className="w-4 h-4 text-blue-500" />
                <span>{current.humidity}%</span>
              </div>
            </div>

            <div className="p-3.5 rounded-2xl bg-cream border border-cream-dark">
              <span className="text-[11px] font-semibold text-gray-500 block mb-1">
                {t('dashboard.rainfall')}
              </span>
              <div className="flex items-center space-x-1.5 font-bold text-base text-gray-900">
                <CloudRain className="w-4 h-4 text-blue-600" />
                <span>{current.rainfall} mm</span>
              </div>
            </div>

            <div className="p-3.5 rounded-2xl bg-cream border border-cream-dark">
              <span className="text-[11px] font-semibold text-gray-500 block mb-1">
                {t('dashboard.wind')}
              </span>
              <div className="flex items-center space-x-1.5 font-bold text-base text-gray-900">
                <Wind className="w-4 h-4 text-teal-600" />
                <span>{current.wind_speed} km/h</span>
              </div>
            </div>

            <div className="p-3.5 rounded-2xl bg-cream border border-cream-dark">
              <span className="text-[11px] font-semibold text-gray-500 block mb-1">
                {t('weather.cloudCover')}
              </span>
              <div className="flex items-center space-x-1.5 font-bold text-base text-gray-900">
                <CloudSun className="w-4 h-4 text-amber-500" />
                <span>{current.cloud_cover}%</span>
              </div>
            </div>

            <div className="p-3.5 rounded-2xl bg-cream border border-cream-dark">
              <span className="text-[11px] font-semibold text-gray-500 block mb-1">
                {t('weather.pressure')}
              </span>
              <div className="flex items-center space-x-1.5 font-bold text-base text-gray-900">
                <Compass className="w-4 h-4 text-purple-600" />
                <span>{current.pressure} hPa</span>
              </div>
            </div>

            <div className="p-3.5 rounded-2xl bg-cream border border-cream-dark">
              <span className="text-[11px] font-semibold text-gray-500 block mb-1">
                {t('weather.uvIndex')}
              </span>
              <div className="flex items-center space-x-1.5 font-bold text-base text-gray-900">
                <Sun className="w-4 h-4 text-orange-500" />
                <span>6.2 (Mod)</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 2. Severe Weather Alerts Section */}
      {weatherData?.alerts && weatherData.alerts.length > 0 && (
        <div className="bg-red-50 border-2 border-red-200 rounded-3xl p-6 sm:p-7 space-y-4">
          <div className="flex items-center space-x-2 text-red-800">
            <ShieldAlert className="w-6 h-6 text-red-600" />
            <h3 className="font-extrabold text-lg text-red-900">
              {t('weather.alertsTitle')} ({weatherData.alerts.length})
            </h3>
          </div>

          <div className="space-y-4">
            {weatherData.alerts.map((alert: any) => (
              <div
                key={alert.id}
                className="bg-white rounded-2xl p-5 border border-red-100 shadow-sm space-y-3"
              >
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-0.5 rounded-full bg-red-600 text-white text-xs font-black uppercase tracking-wider">
                    {alert.severity}
                  </span>
                  <span className="text-xs text-gray-400">
                    {t('weather.alertSource')}: {alert.source}
                  </span>
                </div>

                <h4 className="font-bold text-base text-gray-900">
                  {isKn && alert.title_kn ? alert.title_kn : alert.title_en}
                </h4>

                <div className="space-y-1.5 text-xs text-gray-700 bg-red-50/50 p-3.5 rounded-xl border border-red-100">
                  <strong className="block text-red-900 mb-1">{t('weather.precautions')}:</strong>
                  {(isKn && alert.precautions_kn ? alert.precautions_kn : alert.precautions_en).map((p: string, i: number) => (
                    <div key={i} className="flex items-start space-x-2">
                      <span className="text-red-600 font-bold">•</span>
                      <span>{p}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 3. Hourly Forecast Timeline (Scrollable) */}
      {weatherData?.hourly_forecast && weatherData.hourly_forecast.length > 0 && (
        <div className="bg-white rounded-3xl p-6 sm:p-7 border border-cream-dark shadow-sm">
          <div className="flex items-center space-x-2 mb-4">
            <Clock className="w-5 h-5 text-forest" />
            <h3 className="font-bold text-gray-900 text-base">
              {t('weather.hourlyForecast')}
            </h3>
          </div>

          <div className="flex space-x-3 overflow-x-auto pb-2 scrollbar-thin">
            {weatherData.hourly_forecast.map((hf: any, idx: number) => {
              const hourLabel = new Date(hf.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
              return (
                <div
                  key={idx}
                  className="min-w-[100px] p-3 rounded-2xl bg-cream border border-cream-dark text-center shrink-0 space-y-1.5"
                >
                  <span className="text-xs font-semibold text-gray-500 block">{hourLabel}</span>
                  <CloudSun className="w-6 h-6 text-amber-500 mx-auto" />
                  <span className="text-sm font-black text-gray-900 block">{hf.temperature}°</span>
                  <span className="text-[10px] text-blue-600 block">{hf.precipitation_probability}% rain</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 4. 4-Day Daily Forecast Outlook */}
      {weatherData?.daily_forecast && (
        <div className="bg-white rounded-3xl p-6 sm:p-7 border border-cream-dark shadow-sm">
          <div className="flex items-center space-x-2 mb-4">
            <Calendar className="w-5 h-5 text-forest" />
            <h3 className="font-bold text-gray-900 text-base">
              {t('weather.dailyForecast')}
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {weatherData.daily_forecast.map((df: any, idx: number) => {
              const dayDate = new Date(df.date).toLocaleDateString(isKn ? 'kn-IN' : 'en-IN', {
                weekday: 'short',
                month: 'short',
                day: 'numeric'
              });
              return (
                <div
                  key={idx}
                  className="p-4 rounded-2xl border border-gray-100 hover:border-forest/20 hover:bg-cream/40 transition-colors space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs text-gray-900">{dayDate}</span>
                    <CloudSun className="w-5 h-5 text-amber-500" />
                  </div>
                  <div className="flex items-baseline space-x-2">
                    <span className="text-xl font-black text-gray-900">{df.temp_max}°</span>
                    <span className="text-xs text-gray-400">/ {df.temp_min}°C</span>
                  </div>
                  <p className="text-[11px] text-forest font-medium">
                    {isKn ? df.condition_kn : df.condition_en}
                  </p>
                  <div className="flex items-center justify-between text-[11px] text-gray-500 pt-2 border-t border-gray-100">
                    <span>Rain: {df.rainfall_sum} mm</span>
                    <span className="text-blue-600 font-semibold">{df.rain_probability}%</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 5. Weather-Based Farming Routines Section */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-cream-dark shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-forest">
              <Sparkles className="w-5 h-5" />
              <h3 className="font-extrabold text-xl text-gray-900">
                {t('weather.routinesTitle')}
              </h3>
            </div>
            <p className="text-xs sm:text-sm text-gray-500 mt-0.5">
              {t('weather.routinesSub')}
            </p>
          </div>

          {/* Filter Pills */}
          <div className="flex items-center space-x-1.5 overflow-x-auto pb-1">
            {crops.map((c) => (
              <button
                key={c}
                onClick={() => setSelectedCropFilter(c)}
                className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                  selectedCropFilter === c
                    ? 'bg-forest text-white shadow'
                    : 'bg-cream text-gray-600 hover:bg-cream-dark'
                }`}
              >
                {c === 'All' ? t('common.all') : t(`crops.${c}`)}
              </button>
            ))}
          </div>
        </div>

        {/* Advisory Cards List */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {advisories.map((adv) => {
            const importanceStyle =
              adv.importance === 'Critical'
                ? 'bg-red-50 text-red-700 border-red-200'
                : adv.importance === 'High'
                ? 'bg-orange-50 text-orange-700 border-orange-200'
                : 'bg-blue-50 text-blue-700 border-blue-200';

            return (
              <div
                key={adv.id}
                className="bg-cream rounded-2xl p-5 border border-cream-dark flex flex-col justify-between space-y-3"
              >
                <div>
                  <div className="flex items-center justify-between gap-2">
                    <span className={`text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full border ${importanceStyle}`}>
                      {adv.importance} • {isKn && adv.category_kn ? adv.category_kn : adv.category}
                    </span>
                    <button
                      onClick={() => handleBookmarkAdvisory(adv)}
                      className="text-gray-400 hover:text-forest p-1 rounded"
                      title="Bookmark routine"
                    >
                      <Bookmark className="w-4 h-4" />
                    </button>
                  </div>

                  <h4 className="font-extrabold text-base text-gray-900 mt-2">
                    {isKn && adv.title_kn ? adv.title_kn : adv.title_en}
                  </h4>
                  <p className="text-xs sm:text-sm text-gray-700 leading-relaxed mt-1">
                    {isKn && adv.task_kn ? adv.task_kn : adv.task_en}
                  </p>
                </div>

                <div className="pt-3 border-t border-gray-200/60 text-xs text-forest">
                  <strong>Agronomic Reason: </strong>
                  <span>{isKn && adv.reason_kn ? adv.reason_kn : adv.reason_en}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
};
