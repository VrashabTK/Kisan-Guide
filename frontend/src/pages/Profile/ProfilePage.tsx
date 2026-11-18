import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  User,
  MapPin,
  Phone,
  Mail,
  Languages,
  Bell,
  LogOut,
  Trash2,
  CheckCircle2,
  Shield,
  Sprout,
  Save
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { api } from '../../services/api';

export const ProfilePage: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { profile, logout, refreshProfile } = useAuth();
  const { language, setLanguage } = useLanguage();

  const [fullName, setFullName] = useState(profile?.fullName || '');
  const [phoneNumber, setPhoneNumber] = useState(profile?.phoneNumber || '');
  const [email, setEmail] = useState(profile?.email || '');
  const [taluk, setTaluk] = useState(profile?.taluk || 'Mangaluru');
  const [experience, setExperience] = useState(String(profile?.farmingExperienceYears || 5));
  const [selectedCrops, setSelectedCrops] = useState<string[]>(
    profile?.primaryCrops || ['Coconut', 'Arecanut']
  );

  // Notification Preferences
  const [prefs, setPrefs] = useState({
    thunderstormEnabled: true,
    rainfallEnabled: true,
    heatEnabled: true,
    windEnabled: true,
    generalAdvisoryEnabled: true,
    pushEnabled: false,
  });

  const [loading, setLoading] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const taluks = [
    'Mangaluru', 'Bantwal', 'Belthangady', 'Puttur',
    'Sullia', 'Moodbidri', 'Kadaba', 'Mulki', 'Ullal'
  ];

  const allCrops = ['Coconut', 'Rice', 'Arecanut', 'Cocoa'];

  useEffect(() => {
    if (profile) {
      setFullName(profile.fullName || '');
      setPhoneNumber(profile.phoneNumber || '');
      setEmail(profile.email || '');
      setTaluk(profile.taluk || 'Mangaluru');
      setExperience(String(profile.farmingExperienceYears || 5));
      setSelectedCrops(profile.primaryCrops || ['Coconut', 'Arecanut']);
    }
    // Load preferences
    api.getNotificationPreferences().then(p => {
      if (p) setPrefs(p);
    }).catch(() => {});
  }, [profile]);

  const toggleCrop = (c: string) => {
    if (selectedCrops.includes(c)) {
      if (selectedCrops.length > 1) {
        setSelectedCrops(selectedCrops.filter(item => item !== c));
      }
    } else {
      setSelectedCrops([...selectedCrops, c]);
    }
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setSavedSuccess(false);

    try {
      await api.updateMyProfile({
        fullName,
        phoneNumber,
        taluk,
        farmingExperienceYears: parseInt(experience, 10) || 5,
        primaryCrops: selectedCrops,
        preferredLanguage: language,
      });

      await api.updateNotificationPreferences(prefs);

      await refreshProfile();
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      console.error("Failed to update profile", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (window.confirm("Are you certain you wish to delete your farmer profile? This action is permanent.")) {
      try {
        await api.deleteMyAccount();
        await logout();
        navigate('/login');
      } catch (err) {
        console.error("Delete account failed", err);
      }
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Page Title */}
      <div>
        <div className="flex items-center space-x-2 text-forest mb-1">
          <User className="w-6 h-6" />
          <span className="text-xs font-bold uppercase tracking-wider">Farmer Account</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900">
          {t('profile.title')}
        </h1>
        <p className="text-xs sm:text-sm text-gray-600 mt-1">
          {t('profile.subtitle')}
        </p>
      </div>

      {savedSuccess && (
        <div className="p-4 rounded-2xl bg-green-50 border border-green-200 text-green-700 text-sm flex items-center space-x-2">
          <CheckCircle2 className="w-5 h-5 shrink-0" />
          <span>{t('profile.savedSuccess')}</span>
        </div>
      )}

      <form onSubmit={handleSaveProfile} className="space-y-6">
        
        {/* Personal Details Card */}
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-cream-dark shadow-sm space-y-5">
          <h2 className="text-lg font-bold text-gray-900 pb-2 border-b border-gray-100 flex items-center space-x-2">
            <User className="w-5 h-5 text-forest" />
            <span>{t('profile.personalInfo')}</span>
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                {t('profile.fullName')} *
              </label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-forest"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                {t('profile.phone')}
              </label>
              <input
                type="tel"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-forest"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                {t('profile.email')}
              </label>
              <input
                type="email"
                value={email}
                disabled
                className="w-full px-4 py-2.5 rounded-xl border border-gray-200 bg-gray-50 text-gray-500 text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                {t('profile.taluk')}
              </label>
              <select
                value={taluk}
                onChange={(e) => setTaluk(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl border border-gray-300 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-forest"
              >
                {taluks.map((tlk) => (
                  <option key={tlk} value={tlk}>
                    {t(`taluks.${tlk}`)}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                {t('profile.language')}
              </label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value as 'en' | 'kn')}
                className="w-full px-4 py-2.5 rounded-xl border border-gray-300 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-forest"
              >
                <option value="en">English (ಆಂಗ್ಲ)</option>
                <option value="kn">ಕನ್ನಡ (Kannada)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                {t('profile.experience')}
              </label>
              <input
                type="number"
                min="0"
                max="80"
                value={experience}
                onChange={(e) => setExperience(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-forest"
              />
            </div>
          </div>

          {/* Primary Crops Cultivated */}
          <div className="pt-2">
            <label className="block text-xs font-semibold text-gray-700 mb-2">
              {t('profile.primaryCrops')}
            </label>
            <div className="flex flex-wrap gap-2">
              {allCrops.map((c) => {
                const selected = selectedCrops.includes(c);
                return (
                  <button
                    type="button"
                    key={c}
                    onClick={() => toggleCrop(c)}
                    className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center space-x-1.5 ${
                      selected
                        ? 'bg-forest text-white shadow-sm'
                        : 'bg-cream text-gray-600 hover:bg-cream-dark'
                    }`}
                  >
                    <Sprout className="w-3.5 h-3.5" />
                    <span>{t(`crops.${c}`)}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Notification Preferences Card */}
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-cream-dark shadow-sm space-y-4">
          <h2 className="text-lg font-bold text-gray-900 pb-2 border-b border-gray-100 flex items-center space-x-2">
            <Bell className="w-5 h-5 text-forest" />
            <span>{t('profile.notificationsTitle')}</span>
          </h2>
          <p className="text-xs text-gray-500">
            {t('profile.notificationsDesc')}
          </p>

          <div className="space-y-3 pt-2 text-sm text-gray-700">
            <label className="flex items-center justify-between p-3 rounded-xl bg-cream cursor-pointer">
              <span>{t('profile.prefThunderstorm')}</span>
              <input
                type="checkbox"
                checked={prefs.thunderstormEnabled}
                onChange={(e) => setPrefs({ ...prefs, thunderstormEnabled: e.target.checked })}
                className="w-4 h-4 text-forest rounded focus:ring-forest"
              />
            </label>

            <label className="flex items-center justify-between p-3 rounded-xl bg-cream cursor-pointer">
              <span>{t('profile.prefRainfall')}</span>
              <input
                type="checkbox"
                checked={prefs.rainfallEnabled}
                onChange={(e) => setPrefs({ ...prefs, rainfallEnabled: e.target.checked })}
                className="w-4 h-4 text-forest rounded focus:ring-forest"
              />
            </label>

            <label className="flex items-center justify-between p-3 rounded-xl bg-cream cursor-pointer">
              <span>{t('profile.prefHeat')}</span>
              <input
                type="checkbox"
                checked={prefs.heatEnabled}
                onChange={(e) => setPrefs({ ...prefs, heatEnabled: e.target.checked })}
                className="w-4 h-4 text-forest rounded focus:ring-forest"
              />
            </label>

            <label className="flex items-center justify-between p-3 rounded-xl bg-cream cursor-pointer">
              <span>{t('profile.prefWind')}</span>
              <input
                type="checkbox"
                checked={prefs.windEnabled}
                onChange={(e) => setPrefs({ ...prefs, windEnabled: e.target.checked })}
                className="w-4 h-4 text-forest rounded focus:ring-forest"
              />
            </label>

            <label className="flex items-center justify-between p-3 rounded-xl bg-cream cursor-pointer">
              <span>{t('profile.prefAdvisory')}</span>
              <input
                type="checkbox"
                checked={prefs.generalAdvisoryEnabled}
                onChange={(e) => setPrefs({ ...prefs, generalAdvisoryEnabled: e.target.checked })}
                className="w-4 h-4 text-forest rounded focus:ring-forest"
              />
            </label>
          </div>
        </div>

        {/* Submit Actions */}
        <div className="flex items-center justify-end space-x-3 pt-2">
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2.5 rounded-xl bg-forest hover:bg-forest-light text-white text-sm font-bold shadow-md shadow-forest/20 flex items-center space-x-2 disabled:opacity-60"
          >
            <Save className="w-4 h-4" />
            <span>{loading ? t('common.loading') : t('profile.saveChanges')}</span>
          </button>
        </div>
      </form>

      {/* Account Operations (Logout & Delete) */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-cream-dark shadow-sm space-y-4">
        <h3 className="font-bold text-gray-900 text-base pb-2 border-b border-gray-100">
          {t('profile.accountActions')}
        </h3>

        <div className="flex flex-col sm:flex-row gap-3">
          <button
            type="button"
            onClick={() => { logout(); navigate('/login'); }}
            className="px-4 py-2.5 rounded-xl border border-gray-300 text-gray-700 hover:bg-gray-50 text-xs font-semibold flex items-center justify-center space-x-2"
          >
            <LogOut className="w-4 h-4" />
            <span>{t('profile.logout')}</span>
          </button>

          <button
            type="button"
            onClick={handleDeleteAccount}
            className="px-4 py-2.5 rounded-xl border border-red-200 text-red-600 hover:bg-red-50 text-xs font-semibold flex items-center justify-center space-x-2"
          >
            <Trash2 className="w-4 h-4" />
            <span>{t('profile.deleteAccount')}</span>
          </button>
        </div>
      </div>

    </div>
  );
};
