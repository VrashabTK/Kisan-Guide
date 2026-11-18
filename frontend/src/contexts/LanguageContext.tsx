import React, { createContext, useContext, useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from './AuthContext';
import { api } from '../services/api';

interface LanguageContextType {
  language: 'en' | 'kn';
  setLanguage: (lang: 'en' | 'kn') => void;
  toggleLanguage: () => void;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { i18n } = useTranslation();
  const { profile } = useAuth();
  const [language, setLangState] = useState<'en' | 'kn'>(
    (localStorage.getItem('kissan_guide_lang') as 'en' | 'kn') || 'en'
  );

  const setLanguage = (lang: 'en' | 'kn') => {
    setLangState(lang);
    i18n.changeLanguage(lang);
    localStorage.setItem('kissan_guide_lang', lang);
    if (profile?.uid) {
      api.updateMyProfile({ preferredLanguage: lang }).catch(() => {});
    }
  };

  const toggleLanguage = () => {
    const next = language === 'en' ? 'kn' : 'en';
    setLanguage(next);
  };

  useEffect(() => {
    if (profile?.preferredLanguage && (profile.preferredLanguage === 'en' || profile.preferredLanguage === 'kn')) {
      if (profile.preferredLanguage !== language) {
        setLanguage(profile.preferredLanguage as 'en' | 'kn');
      }
    }
  }, [profile?.preferredLanguage]);

  return (
    <LanguageContext.Provider value={{ language, setLanguage, toggleLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
