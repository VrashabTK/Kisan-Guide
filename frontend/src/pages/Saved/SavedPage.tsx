import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Bookmark,
  Sprout,
  CloudSun,
  Warehouse,
  Trash2,
  Calendar,
  MapPin,
  ExternalLink,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { useLanguage } from '../../contexts/LanguageContext';
import { api } from '../../services/api';

export const SavedPage: React.FC = () => {
  const { t } = useTranslation();
  const { language } = useLanguage();

  const [filter, setFilter] = useState<string>('All');
  const [savedItems, setSavedItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [notice, setNotice] = useState<string | null>(null);

  const fetchBookmarks = async () => {
    setLoading(true);
    try {
      const categoryParam = filter === 'All' ? undefined : filter;
      const data = await api.getSavedItems(categoryParam);
      setSavedItems(data || []);
    } catch (err) {
      console.error("Failed to load saved items", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBookmarks();
  }, [filter]);

  const handleRemove = async (savedId: string) => {
    try {
      await api.deleteSavedItem(savedId);
      setSavedItems(prev => prev.filter(item => item.savedItemId !== savedId));
      setNotice("Bookmark removed successfully.");
      setTimeout(() => setNotice(null), 3000);
    } catch (err) {
      console.error("Failed to remove bookmark", err);
    }
  };

  const isKn = language === 'kn';

  const filterButtons = [
    { key: 'All', label: t('savedPage.filterAll') },
    { key: 'Crop Recommendation', label: t('savedPage.filterCrop') },
    { key: 'Weather Assistant', label: t('savedPage.filterWeather') },
    { key: 'Storage Assistant', label: t('savedPage.filterStorage') },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Page Title */}
      <div>
        <div className="flex items-center space-x-2 text-earth mb-1">
          <Bookmark className="w-6 h-6" />
          <span className="text-xs font-bold uppercase tracking-wider">Saved Guidelines</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900">
          {t('savedPage.title')}
        </h1>
        <p className="text-xs sm:text-sm text-gray-600 mt-1">
          {t('savedPage.subtitle')}
        </p>
      </div>

      {notice && (
        <div className="p-3 bg-green-50 border border-green-200 text-green-700 text-xs rounded-xl font-medium">
          {notice}
        </div>
      )}

      {/* Category Filter Pills */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-1">
        {filterButtons.map((btn) => (
          <button
            key={btn.key}
            onClick={() => setFilter(btn.key)}
            className={`px-4 py-2 rounded-2xl text-xs font-bold transition-all shrink-0 ${
              filter === btn.key
                ? 'bg-forest text-white shadow-sm'
                : 'bg-white text-gray-600 border border-gray-200 hover:bg-cream'
            }`}
          >
            {btn.label}
          </button>
        ))}
      </div>

      {/* Bookmarks List */}
      {loading ? (
        <div className="py-16 text-center text-gray-400 text-xs">
          Loading your bookmarked records...
        </div>
      ) : savedItems.length === 0 ? (
        <div className="bg-white rounded-3xl p-12 border border-dashed border-gray-200 text-center space-y-3">
          <Bookmark className="w-12 h-12 text-gray-300 mx-auto" />
          <h3 className="font-bold text-gray-800 text-base">
            {t('savedPage.emptyTitle')}
          </h3>
          <p className="text-xs text-gray-500 max-w-md mx-auto leading-relaxed">
            {t('savedPage.emptySubtitle')}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {savedItems.map((item) => {
            const title = isKn && item.title_kn ? item.title_kn : item.title;
            const content = item.content || {};

            return (
              <div
                key={item.savedItemId}
                className="bg-white rounded-3xl p-6 border border-cream-dark shadow-sm flex flex-col justify-between space-y-4 hover:shadow-md transition-shadow"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-full bg-forest/10 text-forest">
                      {item.itemType}
                    </span>
                    <button
                      onClick={() => handleRemove(item.savedItemId)}
                      className="text-gray-400 hover:text-red-600 p-1 rounded-lg"
                      title={t('savedPage.remove')}
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <h3 className="font-extrabold text-base text-gray-900 mt-3 leading-snug">
                    {title}
                  </h3>

                  {/* Summary / Snippet */}
                  <div className="mt-2 text-xs text-gray-600 space-y-1">
                    {content.plantation_window_en && (
                      <p className="font-semibold text-forest">
                        {isKn && content.plantation_window_kn ? content.plantation_window_kn : content.plantation_window_en}
                      </p>
                    )}
                    {content.estimated_deadline && (
                      <p className="text-earth font-semibold">
                        Deadline: {content.estimated_deadline} (~{content.remaining_days} days safe)
                      </p>
                    )}
                    {content.task_en && (
                      <p className="line-clamp-2">
                        {isKn && content.task_kn ? content.task_kn : content.task_en}
                      </p>
                    )}
                  </div>
                </div>

                <div className="pt-3 border-t border-gray-100 flex items-center justify-between text-[11px] text-gray-400">
                  <span className="flex items-center space-x-1">
                    <MapPin className="w-3 h-3 text-forest" />
                    <span>{item.location || 'Dakshina Kannada'}</span>
                  </span>
                  <span>
                    {new Date(item.createdAt * 1000).toLocaleDateString()}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}

    </div>
  );
};
