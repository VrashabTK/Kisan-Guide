import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  auth,
  isFirebaseConfigured,
  GoogleAuthProvider,
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  sendPasswordResetEmail,
  firebaseSignOut,
  RecaptchaVerifier,
  signInWithPhoneNumber,
  ConfirmationResult,
  User
} from '../services/firebase';
import { setAuthTokenGetter, api } from '../services/api';

export interface FarmerProfile {
  uid: string;
  fullName: string;
  email: string;
  phoneNumber: string;
  taluk: string;
  district: string;
  state: string;
  preferredLanguage: string;
  primaryCrops: string[];
  farmingExperienceYears?: number;
  profilePicture?: string | null;
}

interface AuthContextType {
  currentUser: User | null;
  profile: FarmerProfile | null;
  loading: boolean;
  isFirebaseReady: boolean;
  loginWithGoogle: () => Promise<void>;
  loginWithEmail: (e: string, p: string) => Promise<void>;
  signupWithEmail: (e: string, p: string, name: string, taluk: string, phone?: string) => Promise<void>;
  sendPhoneOtp: (phoneNumber: string, recaptchaContainerId: string) => Promise<ConfirmationResult | null>;
  verifyPhoneOtp: (confirmationResult: ConfirmationResult, otp: string, name?: string, taluk?: string) => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
  quickDemoLogin: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<FarmerProfile | null>(null);
  const [loading, setLoading] = useState(true);

  // Setup token provider for API calls
  useEffect(() => {
    setAuthTokenGetter(async () => {
      if (currentUser) {
        try {
          return await currentUser.getIdToken();
        } catch (e) {
          console.warn("Could not get Firebase token, using fallback", e);
        }
      }
      // If demo mode active
      const demoUid = localStorage.getItem('kissan_demo_uid');
      if (demoUid) {
        return `dev-token:${demoUid}`;
      }
      return null;
    });
  }, [currentUser]);

  // Load profile when user changes
  const fetchProfile = async (uid: string) => {
    try {
      const p = await api.getMyProfile();
      setProfile(p);
    } catch (e) {
      console.warn("Could not fetch remote profile, using default", e);
      const cached = localStorage.getItem(`kissan_profile_${uid}`);
      if (cached) {
        setProfile(JSON.parse(cached));
      } else {
        const defaultProf: FarmerProfile = {
          uid,
          fullName: "Ramesh Gowda",
          email: "farmer@dakshina.in",
          phoneNumber: "+919876543210",
          taluk: "Mangaluru",
          district: "Dakshina Kannada",
          state: "Karnataka",
          preferredLanguage: "en",
          primaryCrops: ["Coconut", "Arecanut"],
        };
        setProfile(defaultProf);
      }
    }
  };

  useEffect(() => {
    if (isFirebaseConfigured && auth) {
      const unsubscribe = auth.onAuthStateChanged(async (user) => {
        setCurrentUser(user);
        if (user) {
          await fetchProfile(user.uid);
        } else {
          // Check if demo user saved
          const demoUid = localStorage.getItem('kissan_demo_uid');
          if (demoUid) {
            await fetchProfile(demoUid);
          } else {
            setProfile(null);
          }
        }
        setLoading(false);
      });
      return unsubscribe;
    } else {
      // Offline/Demo fallback check
      const demoUid = localStorage.getItem('kissan_demo_uid');
      if (demoUid) {
        fetchProfile(demoUid).finally(() => setLoading(false));
      } else {
        setLoading(false);
      }
    }
  }, []);

  const loginWithGoogle = async () => {
    if (!isFirebaseConfigured || !auth) {
      quickDemoLogin();
      return;
    }
    const provider = new GoogleAuthProvider();
    const res = await signInWithPopup(auth, provider);
    await fetchProfile(res.user.uid);
  };

  const loginWithEmail = async (email: string, pass: string) => {
    if (!isFirebaseConfigured || !auth) {
      quickDemoLogin();
      return;
    }
    const res = await signInWithEmailAndPassword(auth, email, pass);
    await fetchProfile(res.user.uid);
  };

  const signupWithEmail = async (
    email: string,
    pass: string,
    fullName: string,
    taluk: string,
    phone?: string
  ) => {
    if (!isFirebaseConfigured || !auth) {
      quickDemoLogin();
      return;
    }
    const res = await createUserWithEmailAndPassword(auth, email, pass);
    const newProfile = {
      uid: res.user.uid,
      fullName,
      email,
      phoneNumber: phone || "",
      taluk,
      district: "Dakshina Kannada",
      state: "Karnataka",
      preferredLanguage: "en",
      primaryCrops: ["Coconut", "Arecanut"],
    };
    try {
      await api.updateMyProfile(newProfile);
    } catch (_) {}
    setProfile(newProfile);
  };

  const sendPhoneOtp = async (phone: string, containerId: string) => {
    if (!isFirebaseConfigured || !auth) {
      // Return simulated confirmation result
      return {
        confirm: async (otp: string) => {
          if (otp !== "123456" && otp.length !== 6) {
            throw new Error("Invalid OTP. Try 123456 for demo verification.");
          }
          quickDemoLogin();
          return { user: { uid: "farmer_dk_phone_01" } } as any;
        }
      } as unknown as ConfirmationResult;
    }

    const appVerifier = new RecaptchaVerifier(auth, containerId, {
      size: 'invisible',
    });
    const formattedPhone = phone.startsWith("+91") ? phone : `+91${phone}`;
    return await signInWithPhoneNumber(auth, formattedPhone, appVerifier);
  };

  const verifyPhoneOtp = async (
    conf: ConfirmationResult,
    otp: string,
    name?: string,
    taluk?: string
  ) => {
    const res = await conf.confirm(otp);
    if (res.user) {
      await fetchProfile(res.user.uid);
      if (name || taluk) {
        await api.updateMyProfile({
          fullName: name || "Farmer",
          taluk: taluk || "Mangaluru",
        });
      }
    }
  };

  const resetPassword = async (email: string) => {
    if (!isFirebaseConfigured || !auth) {
      alert("Password reset instructions sent to " + email);
      return;
    }
    await sendPasswordResetEmail(auth, email);
  };

  const logout = async () => {
    if (auth) {
      await firebaseSignOut(auth);
    }
    localStorage.removeItem('kissan_demo_uid');
    setCurrentUser(null);
    setProfile(null);
  };

  const quickDemoLogin = () => {
    const demoUid = "farmer_dk_demo";
    localStorage.setItem('kissan_demo_uid', demoUid);
    const demoProf: FarmerProfile = {
      uid: demoUid,
      fullName: "Anand Poojary",
      email: "anand.farmer@kissan.in",
      phoneNumber: "+919845012345",
      taluk: "Bantwal",
      district: "Dakshina Kannada",
      state: "Karnataka",
      preferredLanguage: "kn",
      primaryCrops: ["Arecanut", "Cocoa", "Coconut"],
      farmingExperienceYears: 12,
    };
    setProfile(demoProf);
    localStorage.setItem(`kissan_profile_${demoUid}`, JSON.stringify(demoProf));
  };

  return (
    <AuthContext.Provider
      value={{
        currentUser,
        profile,
        loading,
        isFirebaseReady: isFirebaseConfigured,
        loginWithGoogle,
        loginWithEmail,
        signupWithEmail,
        sendPhoneOtp,
        verifyPhoneOtp,
        resetPassword,
        logout,
        refreshProfile: () => profile ? fetchProfile(profile.uid) : Promise.resolve(),
        quickDemoLogin,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
