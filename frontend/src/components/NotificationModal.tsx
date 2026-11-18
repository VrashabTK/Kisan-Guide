import React from 'react';
import { useTranslation } from 'react-i18next';
import { X, Bell, AlertTriangle, Info, CheckCircle2 } from 'lucide-react';
import { useNotifications } from '../contexts/NotificationContext';
import { useLanguage } from '../contexts/LanguageContext';

export const NotificationModal: React.FC = () => {
  const { t } = useTranslation();
  const { language } = useLanguage();
  const { notifications, isOpen, closeDrawer, markAsRead } = useNotifications();

  if (!isOpen) return null;

  const getSeverityStyle = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return 'bg-red-50 text-red-800 border-red-200';
      case 'severe':
        return 'bg-orange-50 text-orange-800 border-orange-200';
      case 'moderate':
        return 'bg-amber-50 text-amber-800 border-amber-200';
      default:
        return 'bg-blue-50 text-blue-800 border-blue-200';
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/40 backdrop-blur-sm flex justify-end">
      <div className="w-full max-w-md bg-white h-full shadow-2xl flex flex-col transform transition-transform animate-in slide-in-from-right">
        
        {/* Header */}
        <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between bg-cream">
          <div className="flex items-center space-x-2">
            <Bell className="w-5 h-5 text-forest" />
            <h3 className="font-bold text-gray-900 text-lg">
              {t('nav.notifications')}
            </h3>
          </div>
          <button
            onClick={closeDrawer}
            className="p-1 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-200/50"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {notifications.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <CheckCircle2 className="w-12 h-12 mx-auto mb-3 opacity-40 text-forest" />
              <p className="text-sm font-medium">No alerts at this moment</p>
              <p className="text-xs text-gray-400 mt-1">
                You will be notified when weather warnings or farming routines are issued.
              </p>
            </div>
          ) : (
            notifications.map((notif) => {
              const isKn = language === 'kn';
              const title = isKn && notif.title_kn ? notif.title_kn : notif.title_en;
              const msg = isKn && notif.message_kn ? notif.message_kn : notif.message_en;
              const sevClass = getSeverityStyle(notif.severity);

              return (
                <div
                  key={notif.notificationId}
                  className={`p-4 rounded-xl border transition-all ${
                    notif.isRead ? 'bg-white border-gray-100 opacity-80' : `${sevClass} shadow-sm`
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center space-x-2">
                      <AlertTriangle className="w-4 h-4 shrink-0" />
                      <span className="text-xs font-bold uppercase tracking-wider">
                        {notif.category || 'Weather'}
                      </span>
                    </div>
                    {!notif.isRead && (
                      <button
                        onClick={() => markAsRead(notif.notificationId)}
                        className="text-[11px] underline font-medium hover:text-black shrink-0"
                      >
                        Mark read
                      </button>
                    )}
                  </div>

                  <h4 className="font-semibold text-sm mt-1.5 text-gray-900 leading-snug">
                    {title}
                  </h4>
                  <p className="text-xs text-gray-600 mt-1 leading-relaxed">
                    {msg}
                  </p>
                  <span className="text-[10px] text-gray-400 mt-2 block">
                    {new Date(notif.createdAt * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              );
            })
          )}
        </div>

      </div>
    </div>
  );
};
