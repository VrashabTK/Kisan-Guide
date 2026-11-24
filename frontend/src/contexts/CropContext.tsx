import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { api } from '../services/api';

export type SupportedCrop = 'Coconut' | 'Rice' | 'Arecanut' | 'Cocoa';

export const SUPPORTED_CROPS: SupportedCrop[] = ['Coconut', 'Rice', 'Arecanut', 'Cocoa'];

interface CropContextType {
  selectedCrop: SupportedCrop;
  setSelectedCrop: (crop: string, persistToBackend?: boolean) => Promise<void>;
  loading: boolean;
  supportedCrops: SupportedCrop[];
}

const CropContext = createContext<CropContextType | undefined>(undefined);

export const CropProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { profile, currentUser, refreshProfile } = useAuth();
  const [selectedCrop, setSelectedCropState] = useState<SupportedCrop>('Arecanut');
  const [loading, setLoading] = useState<boolean>(true);

  // Synchronize from authenticated profile or user-scoped cache on login/profile change
  useEffect(() => {
    const activeUid = profile?.uid || currentUser?.uid || currentUser?.id;
    if (activeUid) {
      // 1. Check profile from backend
      const profileCrop = (profile?.selected_crop || profile?.selectedCrop) as SupportedCrop | undefined;
      if (profileCrop && SUPPORTED_CROPS.includes(profileCrop)) {
        setSelectedCropState(profileCrop);
        localStorage.setItem(`kissan_selected_crop_${activeUid}`, profileCrop);
        setLoading(false);
        return;
      }

      // 2. Check user-scoped local storage cache
      const cached = localStorage.getItem(`kissan_selected_crop_${activeUid}`) as SupportedCrop | null;
      if (cached && SUPPORTED_CROPS.includes(cached)) {
        setSelectedCropState(cached);
        setLoading(false);
        return;
      }
    } else {
      // If logged out, reset to default state
      setSelectedCropState('Arecanut');
    }
    setLoading(false);
  }, [profile?.uid, profile?.selected_crop, profile?.selectedCrop, currentUser?.uid]);

  const setSelectedCrop = async (crop: string, persistToBackend: boolean = true) => {
    if (!SUPPORTED_CROPS.includes(crop as SupportedCrop)) {
      console.warn(`Attempted to select unsupported crop '${crop}'. Supported:`, SUPPORTED_CROPS);
      return;
    }

    const validCrop = crop as SupportedCrop;
    setSelectedCropState(validCrop);

    const activeUid = profile?.uid || currentUser?.uid || currentUser?.id;
    if (activeUid) {
      localStorage.setItem(`kissan_selected_crop_${activeUid}`, validCrop);

      if (persistToBackend) {
        try {
          await api.updateCropPreference(validCrop);
          if (refreshProfile) {
            refreshProfile().catch(() => {});
          }
        } catch (err) {
          console.warn("Failed to persist crop preference to backend:", err);
        }
      }
    } else {
      localStorage.setItem('kissan_selected_crop_guest', validCrop);
    }
  };

  return (
    <CropContext.Provider
      value={{
        selectedCrop,
        setSelectedCrop,
        loading,
        supportedCrops: SUPPORTED_CROPS,
      }}
    >
      {children}
    </CropContext.Provider>
  );
};

export const useCrop = () => {
  const context = useContext(CropContext);
  if (!context) {
    throw new Error('useCrop must be used within a CropProvider');
  }
  return context;
};
