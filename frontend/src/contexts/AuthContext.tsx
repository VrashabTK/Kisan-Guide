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
  selected_crop?: string;
  selectedCrop?: string;
  primaryCrops: string[];
  farmingExperienceYears?: number;
  profilePicture?: string | null;
  createdAt?: number;
  updatedAt?: number;
}

interface AuthContextType {
  currentUser: any;
  profile: FarmerProfile | null;
  loading: boolean;
  isFirebaseReady: boolean;
  loginWithIdentifier: (identifier: string, pass: string) => Promise<any>;
  signupWithIdentifier: (
    identifier: string,
    pass: string,
    confirmPass?: string,
    name?: string,
    taluk?: string
  ) => Promise<any>;
  requestPasswordReset: (identifier: string) => Promise<any>;
  confirmPasswordReset: (token: string, newPass: string, confirmNewPass?: string) => Promise<any>;
  loginWithGoogle: () => Promise<void>;
  loginWithEmail: (e: string, p: string) => Promise<void>;
  signupWithEmail: (e: string, p: string, name: string, taluk: string, phone?: string) => Promise<void>;
  sendPhoneOtp: (phoneNumber: string, recaptchaContainerId: string) => Promise<ConfirmationResult | null>;
  verifyPhoneOtp: (confirmationResult: ConfirmationResult, otp: string, name?: string, taluk?: string) => Promise<void>;
  resetPassword: (emailOrPhone: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
  quickDemoLogin: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [profile, setProfile] = useState<FarmerProfile | null>(null);
  const [loading, setLoading] = useState(true);

  // Setup token provider for API calls
  useEffect(() => {
    setAuthTokenGetter(async () => {
      // 1. Check persistent backend JWT
      const authToken = localStorage.getItem('kissan_auth_token');
      if (authToken) {
        return authToken;
      }
      // 2. Firebase user token
      if (currentUser && typeof currentUser.getIdToken === 'function') {
        try {
          return await currentUser.getIdToken();
        } catch (e) {
          console.warn("Could not get Firebase token", e);
        }
      }
      // 3. Demo mode token
      const demoUid = localStorage.getItem('kissan_demo_uid');
      if (demoUid) {
        return `dev-token:${demoUid}`;
      }
      return null;
    });
  }, [currentUser]);

  // Load profile when user changes
  const fetchProfile = async (uid?: string): Promise<FarmerProfile | null> => {
    try {
      const p = await api.getMyProfile();
      setProfile(p);
      if (p?.uid) {
        localStorage.setItem(`kissan_profile_${p.uid}`, JSON.stringify(p));
      }
      return p;
    } catch (e) {
      console.warn("Could not fetch remote profile, checking cache", e);
      const targetUid = uid || profile?.uid || localStorage.getItem('kissan_demo_uid');
      if (targetUid) {
        const cached = localStorage.getItem(`kissan_profile_${targetUid}`);
        if (cached) {
          const parsed = JSON.parse(cached);
          setProfile(parsed);
          return parsed;
        }
      }
      return null;
    }
  };

  // Initial Auth State Detection
  useEffect(() => {
    const initAuth = async () => {
      // 1. Check if backend JWT session exists
      const savedToken = localStorage.getItem('kissan_auth_token');
      const savedUserStr = localStorage.getItem('kissan_auth_user');
      if (savedToken && savedUserStr) {
        try {
          const userObj = JSON.parse(savedUserStr);
          setCurrentUser(userObj);
          await fetchProfile(userObj.uid || userObj.id);
          setLoading(false);
          return;
        } catch (e) {
          console.error("Failed to parse saved user", e);
        }
      }

      // 2. Check Firebase if configured
      if (isFirebaseConfigured && auth) {
        const unsubscribe = auth.onAuthStateChanged(async (user) => {
          setCurrentUser(user);
          if (user) {
            await fetchProfile(user.uid);
          } else {
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
        // 3. Check demo user fallback
        const demoUid = localStorage.getItem('kissan_demo_uid');
        if (demoUid) {
          await fetchProfile(demoUid);
        }
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  // Backend Authentication: Login with Email or Mobile + Password
  const loginWithIdentifier = async (identifier: string, pass: string) => {
    const res = await api.authLogin({ identifier, password: pass });
    if (res?.access_token && res?.user) {
      localStorage.setItem('kissan_auth_token', res.access_token);
      localStorage.setItem('kissan_auth_user', JSON.stringify(res.user));
      localStorage.removeItem('kissan_demo_uid');
      setCurrentUser(res.user);
      setProfile(res.user);
      return res;
    }
    throw new Error("Invalid response from server");
  };

  // Backend Authentication: Sign Up with Email or Mobile + Password
  const signupWithIdentifier = async (
    identifier: string,
    pass: string,
    confirmPass?: string,
    fullName?: string,
    taluk?: string
  ) => {
    const res = await api.authSignup({
      identifier,
      password: pass,
      confirm_password: confirmPass,
      full_name: fullName,
      taluk: taluk || "Mangaluru",
    });
    if (res?.access_token && res?.user) {
      localStorage.setItem('kissan_auth_token', res.access_token);
      localStorage.setItem('kissan_auth_user', JSON.stringify(res.user));
      localStorage.removeItem('kissan_demo_uid');
      setCurrentUser(res.user);
      setProfile(res.user);
      return res;
    }
    throw new Error("Registration failed");
  };

  // Password Reset Flow
  const requestPasswordReset = async (identifier: string) => {
    return await api.authForgotPassword(identifier);
  };

  const confirmPasswordReset = async (token: string, newPass: string, confirmNewPass?: string) => {
    return await api.authResetPassword({
      token,
      new_password: newPass,
      confirm_new_password: confirmNewPass,
    });
  };

  // Compatibility Bridges for Firebase OAuth & OTP
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
    try {
      // First try standard backend login
      await loginWithIdentifier(email, pass);
    } catch (e: any) {
      // If backend reports invalid credentials, throw it directly
      if (e.message && e.message.includes("Invalid credentials")) {
        throw e;
      }
      // Fallback to Firebase if configured
      if (isFirebaseConfigured && auth) {
        const res = await signInWithEmailAndPassword(auth, email, pass);
        await fetchProfile(res.user.uid);
      } else {
        throw e;
      }
    }
  };

  const signupWithEmail = async (
    email: string,
    pass: string,
    fullName: string,
    taluk: string,
    phone?: string
  ) => {
    await signupWithIdentifier(email, pass, pass, fullName, taluk);
  };

  const sendPhoneOtp = async (phone: string, containerId: string) => {
    if (!isFirebaseConfigured || !auth) {
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

  const resetPassword = async (emailOrPhone: string) => {
    try {
      await requestPasswordReset(emailOrPhone);
    } catch (e) {
      if (isFirebaseConfigured && auth && emailOrPhone.includes("@")) {
        await sendPasswordResetEmail(auth, emailOrPhone);
      } else {
        throw e;
      }
    }
  };

  const logout = async () => {
    try {
      await api.authLogout();
    } catch (_) {}
    if (auth) {
      try {
        await firebaseSignOut(auth);
      } catch (_) {}
    }
    localStorage.removeItem('kissan_auth_token');
    localStorage.removeItem('kissan_auth_user');
    localStorage.removeItem('kissan_demo_uid');
    setCurrentUser(null);
    setProfile(null);
  };

  const quickDemoLogin = () => {
    const demoUid = "farmer_dk_demo";
    localStorage.setItem('kissan_demo_uid', demoUid);
    localStorage.removeItem('kissan_auth_token');
    const demoProf: FarmerProfile = {
      uid: demoUid,
      fullName: "Anand Poojary",
      email: "anand.farmer@kissan.in",
      phoneNumber: "+919845012345",
      taluk: "Bantwal",
      district: "Dakshina Kannada",
      state: "Karnataka",
      preferredLanguage: "kn",
      selected_crop: "Arecanut",
      selectedCrop: "Arecanut",
      primaryCrops: ["Arecanut", "Cocoa", "Coconut"],
      farmingExperienceYears: 12,
    };
    setCurrentUser(demoProf);
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
        loginWithIdentifier,
        signupWithIdentifier,
        requestPasswordReset,
        confirmPasswordReset,
        loginWithGoogle,
        loginWithEmail,
        signupWithEmail,
        sendPhoneOtp,
        verifyPhoneOtp,
        resetPassword,
        logout,
        refreshProfile: async () => {
          await fetchProfile();
        },
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
