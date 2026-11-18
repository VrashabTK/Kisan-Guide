import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';
import { useAuth } from './AuthContext';

export interface AppNotification {
  notificationId: string;
  userId: string;
  title_en: string;
  title_kn: string;
  message_en: string;
  message_kn: string;
  category: string;
  severity: string;
  isRead: boolean;
  createdAt: number;
}

interface NotificationContextType {
  notifications: AppNotification[];
  unreadCount: number;
  isOpen: boolean;
  openDrawer: () => void;
  closeDrawer: () => void;
  markAsRead: (id: string) => Promise<void>;
  refreshNotifications: () => Promise<void>;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { profile } = useAuth();
  const [notifications, setNotifications] = useState<AppNotification[]>([]);
  const [isOpen, setIsOpen] = useState(false);

  const fetchNotifs = async () => {
    if (!profile?.uid) return;
    try {
      const data = await api.getNotifications();
      setNotifications(data || []);
    } catch (e) {
      console.warn("Could not load notifications", e);
    }
  };

  useEffect(() => {
    if (profile?.uid) {
      fetchNotifs();
      const interval = setInterval(fetchNotifs, 60000); // 1 minute poll
      return () => clearInterval(interval);
    }
  }, [profile?.uid]);

  const markAsRead = async (id: string) => {
    try {
      await api.markNotificationRead(id);
      setNotifications(prev =>
        prev.map(n => n.notificationId === id ? { ...n, isRead: true } : n)
      );
    } catch (e) {
      console.error("Failed to mark notification read", e);
    }
  };

  const unreadCount = notifications.filter(n => !n.isRead).length;

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        unreadCount,
        isOpen,
        openDrawer: () => setIsOpen(true),
        closeDrawer: () => setIsOpen(false),
        markAsRead,
        refreshNotifications: fetchNotifs,
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};
