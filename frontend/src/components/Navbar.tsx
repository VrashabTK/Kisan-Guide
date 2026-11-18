import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Sprout,
  CloudSun,
  Warehouse,
  Bookmark,
  User,
  Bell,
  Menu,
  X,
  Languages,
  LogOut
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { useNotifications } from '../contexts/NotificationContext';

export const Navbar: React.FC = () => {
  const { t } = useTranslation();
  const { profile, logout } = useAuth();
  const { language, toggleLanguage } = useLanguage();
  const { unreadCount, openDrawer } = useNotifications();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  const navLinks = [
    { to: '/', label: t('nav.dashboard'), icon: Sprout },
    { to: '/crop-recommendation', label: t('nav.cropRecommendation'), icon: Sprout },
    { to: '/weather-assistant', label: t('nav.weatherAssistant'), icon: CloudSun },
    { to: '/storage-assistant', label: t('nav.storageAssistant'), icon: Warehouse },
    { to: '/saved', label: t('nav.saved'), icon: Bookmark },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur shadow-sm border-b border-cream-dark">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Brand */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 rounded-xl bg-forest flex items-center justify-center text-white shadow-md shadow-forest/20 group-hover:bg-leaf transition-colors">
              <Sprout className="w-6 h-6 text-cream" />
            </div>
            <div>
              <span className="font-bold text-xl tracking-tight text-forest block leading-none">
                {t('brand.name')}
              </span>
              <span className="text-xs text-earth font-medium hidden sm:block">
                Dakshina Kannada
              </span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1 lg:space-x-2">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const active = isActive(link.to);
              return (
                <Link
                  key={link.to}
                  to={link.to}
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    active
                      ? 'bg-forest/10 text-forest font-semibold'
                      : 'text-gray-600 hover:text-forest hover:bg-forest/5'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${active ? 'text-forest' : 'text-gray-400'}`} />
                  <span>{link.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Right Action Icons */}
          <div className="flex items-center space-x-2 sm:space-x-3">
            
            {/* Language Switcher Pill */}
            <button
              onClick={toggleLanguage}
              className="flex items-center space-x-1 px-2.5 py-1.5 text-xs font-semibold rounded-full border border-forest/20 text-forest hover:bg-forest/10 transition-colors"
              title="Switch language / ಭಾಷೆ ಬದಲಾಯಿಸಿ"
            >
              <Languages className="w-3.5 h-3.5" />
              <span>{language === 'en' ? 'ಕನ್ನಡ' : 'English'}</span>
            </button>

            {/* Notifications Bell */}
            <button
              onClick={openDrawer}
              className="relative p-2 rounded-full text-gray-600 hover:text-forest hover:bg-forest/5 transition-colors"
              aria-label={t('nav.notifications')}
            >
              <Bell className="w-5 h-5" />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 w-4 h-4 bg-red-600 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </button>

            {/* Profile Avatar & Link */}
            <Link
              to="/profile"
              className={`flex items-center space-x-2 p-1.5 rounded-lg transition-colors ${
                isActive('/profile') ? 'bg-forest/10 text-forest' : 'hover:bg-gray-100 text-gray-700'
              }`}
            >
              <div className="w-8 h-8 rounded-full bg-forest/10 text-forest border border-forest/30 flex items-center justify-center font-bold text-sm">
                {profile?.fullName ? profile.fullName.charAt(0).toUpperCase() : <User className="w-4 h-4" />}
              </div>
              <span className="hidden xl:inline text-sm font-medium">
                {profile?.fullName || t('nav.profile')}
              </span>
            </Link>

            {/* Mobile Menu Toggle */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-gray-600 hover:text-forest"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>

        </div>
      </div>

      {/* Mobile Navigation Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-cream-dark bg-white px-4 pt-2 pb-4 space-y-1">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const active = isActive(link.to);
            return (
              <Link
                key={link.to}
                to={link.to}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center space-x-3 px-3 py-2.5 rounded-lg text-base font-medium ${
                  active
                    ? 'bg-forest/10 text-forest font-semibold'
                    : 'text-gray-700 hover:bg-forest/5'
                }`}
              >
                <Icon className={`w-5 h-5 ${active ? 'text-forest' : 'text-gray-400'}`} />
                <span>{link.label}</span>
              </Link>
            );
          })}
          <div className="pt-2 border-t border-gray-100 flex items-center justify-between">
            <Link
              to="/profile"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center space-x-2 text-sm text-gray-700 font-medium py-2"
            >
              <User className="w-4 h-4 text-forest" />
              <span>{profile?.fullName || t('nav.profile')}</span>
            </Link>
            <button
              onClick={() => {
                setMobileMenuOpen(false);
                logout();
              }}
              className="flex items-center space-x-1 text-sm text-red-600 hover:text-red-700 font-medium py-2"
            >
              <LogOut className="w-4 h-4" />
              <span>{t('nav.logout')}</span>
            </button>
          </div>
        </div>
      )}
    </header>
  );
};
