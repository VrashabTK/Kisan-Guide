import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { Farm, FarmActivity, SupportedCrop } from '../types/farm';
import { api } from '../services/api';
import { useAuth } from './AuthContext';

interface FarmContextType {
  farms: Farm[];
  selectedFarm: Farm | null;
  selectedFarmId: string | null;
  setSelectedFarmId: (id: string) => void;
  isLoading: boolean;
  refreshFarms: () => Promise<void>;
  todayActivities: FarmActivity[];
  refreshTodayActivities: () => Promise<void>;
  markDone: (activityId: string) => Promise<void>;
  markSkipped: (activityId: string, reason?: string) => Promise<void>;
  addFarmModalOpen: boolean;
  setAddFarmModalOpen: (open: boolean) => void;
  preselectedCropForNewFarm: SupportedCrop | null;
  openAddFarmModalWithCrop: (crop?: SupportedCrop) => void;
}

const FarmContext = createContext<FarmContextType | undefined>(undefined);

export const FarmProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { currentUser, profile } = useAuth();
  const [farms, setFarms] = useState<Farm[]>([]);
  const [selectedFarmId, setSelectedFarmIdState] = useState<string | null>(() => {
    return localStorage.getItem('kissan_selected_farm_id');
  });
  const [isLoading, setIsLoading] = useState(false);
  const [todayActivities, setTodayActivities] = useState<FarmActivity[]>([]);
  const [addFarmModalOpen, setAddFarmModalOpen] = useState(false);
  const [preselectedCropForNewFarm, setPreselectedCropForNewFarm] = useState<SupportedCrop | null>(null);

  const selectedFarm = farms.find((f) => f.id === selectedFarmId) || farms[0] || null;

  const setSelectedFarmId = (id: string) => {
    setSelectedFarmIdState(id);
    localStorage.setItem('kissan_selected_farm_id', id);
  };

  const refreshFarms = useCallback(async () => {
    if (!currentUser && !profile) {
      setFarms([]);
      setSelectedFarmIdState(null);
      return;
    }
    try {
      setIsLoading(true);
      const data = await api.getFarms();
      if (Array.isArray(data)) {
        setFarms(data);
        if (data.length > 0) {
          if (!selectedFarmId || !data.some((f: Farm) => f.id === selectedFarmId)) {
            setSelectedFarmId(data[0].id);
          }
        } else {
          setSelectedFarmIdState(null);
        }
      }
    } catch (err) {
      console.error('Failed to load farms:', err);
    } finally {
      setIsLoading(false);
    }
  }, [currentUser, profile, selectedFarmId]);

  const refreshTodayActivities = useCallback(async () => {
    if (!selectedFarm) {
      setTodayActivities([]);
      return;
    }
    try {
      const data = await api.getTodayActivities(selectedFarm.id);
      if (Array.isArray(data)) {
        setTodayActivities(data);
      }
    } catch (err) {
      console.error('Failed to load activities:', err);
    }
  }, [selectedFarm]);

  useEffect(() => {
    if (currentUser || profile) {
      refreshFarms();
    } else {
      setFarms([]);
      setTodayActivities([]);
      setSelectedFarmIdState(null);
    }
  }, [currentUser, profile]);

  useEffect(() => {
    if (selectedFarm) {
      refreshTodayActivities();
    } else {
      setTodayActivities([]);
    }
  }, [selectedFarm?.id, refreshTodayActivities]);

  const markDone = async (activityId: string) => {
    if (!selectedFarm) return;
    try {
      const updated = await api.completeActivity(selectedFarm.id, activityId);
      setTodayActivities((prev) =>
        prev.map((act) => (act.id === activityId ? { ...act, ...updated, status: 'completed' } : act))
      );
      // Also update counts in farm list locally
      setFarms((prev) =>
        prev.map((f) =>
          f.id === selectedFarm.id
            ? {
                ...f,
                today_completed_count: (f.today_completed_count || 0) + 1,
                today_pending_count: Math.max(0, (f.today_pending_count || 1) - 1),
              }
            : f
        )
      );
    } catch (err) {
      console.error('Failed to mark task completed:', err);
      throw err;
    }
  };

  const markSkipped = async (activityId: string, reason?: string) => {
    if (!selectedFarm) return;
    try {
      const updated = await api.skipActivity(selectedFarm.id, activityId, reason);
      setTodayActivities((prev) =>
        prev.map((act) => (act.id === activityId ? { ...act, ...updated, status: 'skipped', skip_reason: reason } : act))
      );
      setFarms((prev) =>
        prev.map((f) =>
          f.id === selectedFarm.id
            ? {
                ...f,
                today_skipped_count: (f.today_skipped_count || 0) + 1,
                today_pending_count: Math.max(0, (f.today_pending_count || 1) - 1),
              }
            : f
        )
      );
    } catch (err) {
      console.error('Failed to skip task:', err);
      throw err;
    }
  };

  const openAddFarmModalWithCrop = (crop?: SupportedCrop) => {
    if (crop) {
      setPreselectedCropForNewFarm(crop);
    } else {
      setPreselectedCropForNewFarm(null);
    }
    setAddFarmModalOpen(true);
  };

  return (
    <FarmContext.Provider
      value={{
        farms,
        selectedFarm,
        selectedFarmId,
        setSelectedFarmId,
        isLoading,
        refreshFarms,
        todayActivities,
        refreshTodayActivities,
        markDone,
        markSkipped,
        addFarmModalOpen,
        setAddFarmModalOpen,
        preselectedCropForNewFarm,
        openAddFarmModalWithCrop,
      }}
    >
      {children}
    </FarmContext.Provider>
  );
};

export const useFarm = () => {
  const context = useContext(FarmContext);
  if (!context) {
    throw new Error('useFarm must be used within a FarmProvider');
  }
  return context;
};
