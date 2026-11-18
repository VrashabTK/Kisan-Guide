import React from 'react';
import { useTranslation } from 'react-i18next';
import { Sprout, ShieldAlert, Heart } from 'lucide-react';

export const Footer: React.FC = () => {
  const { t } = useTranslation();

  const taluks = [
    'Mangaluru', 'Bantwal', 'Belthangady', 'Puttur',
    'Sullia', 'Moodbidri', 'Kadaba', 'Mulki', 'Ullal'
  ];

  return (
    <footer className="bg-white border-t border-cream-dark mt-16 text-gray-600 text-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          
          {/* Brand Col */}
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-lg bg-forest flex items-center justify-center text-white">
                <Sprout className="w-5 h-5" />
              </div>
              <span className="font-bold text-lg text-forest">{t('brand.name')}</span>
            </div>
            <p className="text-gray-500 max-w-md text-xs sm:text-sm">
              {t('brand.tagline')}. Focused strictly on verified agronomic practices for Coconut, Rice (Paddy), Arecanut, and Cocoa.
            </p>
            <div className="flex items-center space-x-2 text-xs text-amber-700 bg-amber-50 p-2.5 rounded-lg border border-amber-200">
              <ShieldAlert className="w-4 h-4 shrink-0" />
              <span>
                Advisory guidance is based on tropical agronomic standards. Always inspect local field topography and consult local Raitha Samparka Kendras (RSK).
              </span>
            </div>
          </div>

          {/* Taluks Coverage */}
          <div>
            <h4 className="font-semibold text-gray-900 mb-2.5 text-xs uppercase tracking-wider">
              DK Taluks Covered
            </h4>
            <div className="grid grid-cols-2 gap-1 text-xs text-gray-500">
              {taluks.map((taluk) => (
                <span key={taluk} className="hover:text-forest transition-colors">
                  {t(`taluks.${taluk}`)}
                </span>
              ))}
            </div>
          </div>

          {/* Primary Crops */}
          <div>
            <h4 className="font-semibold text-gray-900 mb-2.5 text-xs uppercase tracking-wider">
              Supported Crops
            </h4>
            <ul className="space-y-1 text-xs text-gray-500">
              <li>{t('crops.Coconut')} (Cocos nucifera)</li>
              <li>{t('crops.Rice')} (Oryza sativa)</li>
              <li>{t('crops.Arecanut')} (Areca catechu)</li>
              <li>{t('crops.Cocoa')} (Theobroma cacao)</li>
            </ul>
          </div>

        </div>

        <div className="border-t border-gray-100 mt-8 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-gray-400">
          <p>© {new Date().getFullYear()} KISSAN GUIDE — Dakshina Kannada, Karnataka, India.</p>
          <p className="flex items-center space-x-1 mt-2 sm:mt-0">
            <span>Built with</span>
            <Heart className="w-3.5 h-3.5 text-red-500 inline fill-red-500" />
            <span>for Indian Farmers</span>
          </p>
        </div>
      </div>
    </footer>
  );
};
