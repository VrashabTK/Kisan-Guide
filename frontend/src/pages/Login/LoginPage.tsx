import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Sprout,
  Mail,
  Lock,
  ArrowRight,
  Languages,
  CheckCircle2,
  AlertCircle,
  KeyRound,
  ShieldCheck,
  UserCheck
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';

export const LoginPage: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const {
    loginWithIdentifier,
    signupWithIdentifier,
    requestPasswordReset,
    confirmPasswordReset,
    loginWithGoogle,
    quickDemoLogin,
  } = useAuth();
  const { language, toggleLanguage } = useLanguage();

  // Mode: 'login' | 'signup'
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('login');

  // Shared form inputs
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successNotice, setSuccessNotice] = useState<string | null>(null);

  // Forgot password modal state
  const [showForgotModal, setShowForgotModal] = useState(false);
  const [forgotIdentifier, setForgotIdentifier] = useState('');
  const [resetToken, setResetToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');
  const [forgotStep, setForgotStep] = useState<1 | 2>(1);
  const [forgotLoading, setForgotLoading] = useState(false);
  const [forgotError, setForgotError] = useState<string | null>(null);
  const [forgotSuccess, setForgotSuccess] = useState<string | null>(null);

  // Validation Helper
  const validateIdentifier = (value: string): boolean => {
    const raw = (value || '').trim();
    if (!raw) return false;
    if (raw.includes('@')) {
      const emailRegex = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
      return emailRegex.test(raw);
    } else {
      const digits = raw.replace(/\D/g, '');
      const clean = (digits.startsWith('91') && digits.length === 12) ? digits.slice(2) : digits;
      return clean.length === 10 && ['6', '7', '8', '9'].includes(clean[0]);
    }
  };

  // Submit Handler: Sign Up
  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessNotice(null);

    const cleanId = identifier.trim();
    if (!cleanId || !password || !confirmPassword) {
      setError(t('auth.emptyFields'));
      return;
    }

    if (!validateIdentifier(cleanId)) {
      setError(t('auth.errors.invalidPhone') + ' ' + t('common.or', 'or') + ' ' + t('auth.errors.invalidEmail'));
      return;
    }

    if (password.length < 6) {
      setError(t('auth.errors.passwordShort'));
      return;
    }

    if (password !== confirmPassword) {
      setError(t('auth.errors.passwordMismatch'));
      return;
    }

    setLoading(true);
    try {
      await signupWithIdentifier(cleanId, password, confirmPassword);
      navigate('/');
    } catch (err: any) {
      const msg = err.message || '';
      if (msg.includes('already exists') || err.status === 409) {
        setError(t('auth.accountExists'));
      } else {
        setError(msg || t('auth.accountExists'));
      }
    } finally {
      setLoading(false);
    }
  };

  // Submit Handler: Login
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessNotice(null);

    const cleanId = identifier.trim();
    if (!cleanId || !password) {
      setError(t('auth.emptyFields'));
      return;
    }

    setLoading(true);
    try {
      await loginWithIdentifier(cleanId, password);
      navigate('/');
    } catch (err: any) {
      const msg = err.message || '';
      if (msg.includes('too many failed') || err.status === 429) {
        setError(msg);
      } else {
        // Enforce generic message that does not reveal account existence
        setError(t('auth.invalidCredentials'));
      }
    } finally {
      setLoading(false);
    }
  };

  // Forgot Password: Step 1 (Request Reset Token)
  const handleRequestReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setForgotError(null);
    setForgotSuccess(null);

    const cleanId = forgotIdentifier.trim();
    if (!cleanId) {
      setForgotError(t('auth.emptyFields'));
      return;
    }

    setForgotLoading(true);
    try {
      const res = await requestPasswordReset(cleanId);
      if (res?.token) {
        setResetToken(res.token);
        setForgotStep(2);
        setForgotSuccess("Verification token issued! Please create your new password.");
      } else {
        setForgotError("Unable to process reset. Please verify your details.");
      }
    } catch (err: any) {
      setForgotError(err.message || "No account found with this email address or mobile number.");
    } finally {
      setForgotLoading(false);
    }
  };

  // Forgot Password: Step 2 (Confirm New Password)
  const handleConfirmReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setForgotError(null);
    setForgotSuccess(null);

    if (!resetToken || !newPassword || !confirmNewPassword) {
      setForgotError(t('auth.emptyFields'));
      return;
    }

    if (newPassword.length < 6) {
      setForgotError(t('auth.errors.passwordShort'));
      return;
    }

    if (newPassword !== confirmNewPassword) {
      setForgotError(t('auth.errors.passwordMismatch'));
      return;
    }

    setForgotLoading(true);
    try {
      const res = await confirmPasswordReset(resetToken, newPassword, confirmNewPassword);
      if (res?.success) {
        setForgotSuccess(t('auth.resetSuccess'));
        setTimeout(() => {
          setShowForgotModal(false);
          setForgotStep(1);
          setForgotIdentifier('');
          setResetToken('');
          setNewPassword('');
          setConfirmNewPassword('');
          setAuthMode('login');
          setSuccessNotice(t('auth.resetSuccess'));
        }, 1500);
      } else {
        setForgotError("Password reset failed. Invalid or expired token.");
      }
    } catch (err: any) {
      setForgotError(err.message || "Failed to reset password. Please check your token.");
    } finally {
      setForgotLoading(false);
    }
  };

  const handleDemoSignIn = () => {
    quickDemoLogin();
    navigate('/');
  };

  const handleGoogleSignIn = async () => {
    setError(null);
    setLoading(true);
    try {
      await loginWithGoogle();
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Google sign-in canceled or failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row bg-cream font-sans">
      
      {/* Left Column: Visual & Agricultural Branding */}
      <div className="lg:w-1/2 bg-gradient-to-br from-forest-dark via-forest to-leaf text-white p-8 lg:p-12 flex flex-col justify-between relative overflow-hidden">
        <div className="absolute -bottom-16 -right-16 w-96 h-96 rounded-full bg-white/5 pointer-events-none blur-2xl" />
        <div className="absolute top-1/4 -left-20 w-64 h-64 rounded-full bg-leaf/20 pointer-events-none blur-3xl" />

        {/* Top Header */}
        <div className="flex items-center justify-between z-10">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-2xl bg-white/10 backdrop-blur border border-white/20 flex items-center justify-center shadow-inner">
              <Sprout className="w-7 h-7 text-cream" />
            </div>
            <div>
              <h1 className="text-2xl font-black tracking-tight leading-none">
                {t('brand.name')}
              </h1>
              <p className="text-xs text-cream/80 mt-0.5">
                Dakshina Kannada Agricultural Platform
              </p>
            </div>
          </div>

          {/* Language Switch Button */}
          <button
            onClick={toggleLanguage}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-full bg-white/10 hover:bg-white/20 backdrop-blur border border-white/20 text-xs font-semibold text-white transition-colors"
          >
            <Languages className="w-3.5 h-3.5" />
            <span>{language === 'en' ? 'ಕನ್ನಡಕ್ಕೆ ಬದಲಾಯಿಸಿ' : 'Switch to English'}</span>
          </button>
        </div>

        {/* Center Presentation */}
        <div className="my-12 z-10 max-w-lg space-y-6">
          <span className="inline-block px-3 py-1 bg-white/10 text-cream text-xs font-bold rounded-full tracking-wide uppercase">
            Coconut • Rice (Paddy) • Arecanut • Cocoa
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold leading-tight">
            {t('auth.welcomeTitle')}
          </h2>
          <p className="text-cream/90 text-sm sm:text-base leading-relaxed">
            {t('auth.welcomeSubtitle')}
          </p>

          <div className="grid grid-cols-2 gap-3 pt-4 text-xs">
            <div className="flex items-center space-x-2 bg-white/10 backdrop-blur p-2.5 rounded-xl border border-white/10">
              <CheckCircle2 className="w-4 h-4 text-leaf-light shrink-0" />
              <span>Dakshina Kannada Agro-Rules</span>
            </div>
            <div className="flex items-center space-x-2 bg-white/10 backdrop-blur p-2.5 rounded-xl border border-white/10">
              <CheckCircle2 className="w-4 h-4 text-leaf-light shrink-0" />
              <span>Real-Time Weather Advisories</span>
            </div>
            <div className="flex items-center space-x-2 bg-white/10 backdrop-blur p-2.5 rounded-xl border border-white/10">
              <CheckCircle2 className="w-4 h-4 text-leaf-light shrink-0" />
              <span>Post-Harvest Storage Science</span>
            </div>
            <div className="flex items-center space-x-2 bg-white/10 backdrop-blur p-2.5 rounded-xl border border-white/10">
              <CheckCircle2 className="w-4 h-4 text-leaf-light shrink-0" />
              <span>Global Shared Crop Selection</span>
            </div>
          </div>
        </div>

        {/* Footer Note */}
        <div className="z-10 text-xs text-white/60">
          Covering 9 Taluks: Mangaluru, Bantwal, Belthangady, Puttur, Sullia, Moodbidri, Kadaba, Mulki, Ullal.
        </div>
      </div>

      {/* Right Column: Authentication Card */}
      <div className="lg:w-1/2 flex items-center justify-center p-6 sm:p-10 lg:p-12">
        <div className="w-full max-w-md bg-white rounded-3xl shadow-xl shadow-forest/5 border border-cream-dark p-6 sm:p-8">
          
          {/* Top Tabs: Login vs Sign Up */}
          <div className="flex bg-cream p-1.5 rounded-2xl mb-6 border border-cream-dark">
            <button
              type="button"
              onClick={() => {
                setAuthMode('login');
                setError(null);
                setSuccessNotice(null);
              }}
              className={`flex-1 py-2.5 rounded-xl text-sm font-extrabold transition-all ${
                authMode === 'login'
                  ? 'bg-forest text-white shadow-md'
                  : 'text-gray-600 hover:text-forest'
              }`}
            >
              {t('auth.loginBtn')}
            </button>
            <button
              type="button"
              onClick={() => {
                setAuthMode('signup');
                setError(null);
                setSuccessNotice(null);
              }}
              className={`flex-1 py-2.5 rounded-xl text-sm font-extrabold transition-all ${
                authMode === 'signup'
                  ? 'bg-forest text-white shadow-md'
                  : 'text-gray-600 hover:text-forest'
              }`}
            >
              {t('auth.signUpBtn')}
            </button>
          </div>

          {/* Status Banners */}
          {error && (
            <div className="mb-5 p-3.5 rounded-2xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-red-500" />
              <span>{error}</span>
            </div>
          )}

          {successNotice && (
            <div className="mb-5 p-3.5 rounded-2xl bg-green-50 border border-green-200 text-green-700 text-xs flex items-start space-x-2">
              <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5 text-green-600" />
              <span>{successNotice}</span>
            </div>
          )}

          {/* Form: LOGIN */}
          {authMode === 'login' && (
            <form onSubmit={handleLogin} className="space-y-4">
              
              {/* Field 1: Email OR Mobile */}
              <div>
                <label className="block text-xs font-bold text-gray-700 mb-1">
                  {t('auth.identifierLabel')}
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                    <Mail className="w-4 h-4" />
                  </div>
                  <input
                    type="text"
                    required
                    value={identifier}
                    onChange={(e) => setIdentifier(e.target.value)}
                    placeholder={t('auth.identifierPlaceholder')}
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-forest/30 focus:border-forest transition-colors font-medium"
                  />
                </div>
              </div>

              {/* Field 2: Password */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="text-xs font-bold text-gray-700">
                    {t('auth.password')}
                  </label>
                  <button
                    type="button"
                    onClick={() => {
                      setShowForgotModal(true);
                      setForgotIdentifier(identifier);
                      setForgotError(null);
                      setForgotSuccess(null);
                      setForgotStep(1);
                    }}
                    className="text-xs font-semibold text-forest hover:text-forest-dark"
                  >
                    {t('auth.forgotPassword')}
                  </button>
                </div>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-forest/30 focus:border-forest transition-colors font-medium"
                  />
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-xl bg-forest hover:bg-forest-light text-white font-bold text-sm transition-all shadow-md shadow-forest/20 flex items-center justify-center space-x-2 disabled:opacity-60 mt-2"
              >
                <span>{loading ? t('common.submitting') : t('auth.loginBtn')}</span>
                <ArrowRight className="w-4 h-4" />
              </button>

              {/* Switch to Sign Up Link */}
              <div className="text-center pt-2">
                <p className="text-xs text-gray-500">
                  {t('auth.noAccount')}{' '}
                  <button
                    type="button"
                    onClick={() => {
                      setAuthMode('signup');
                      setError(null);
                    }}
                    className="font-bold text-forest hover:underline"
                  >
                    {t('auth.signUpBtn')}
                  </button>
                </p>
              </div>

            </form>
          )}

          {/* Form: SIGN UP */}
          {authMode === 'signup' && (
            <form onSubmit={handleSignUp} className="space-y-4">
              
              {/* Field 1: Email OR Mobile */}
              <div>
                <label className="block text-xs font-bold text-gray-700 mb-1">
                  {t('auth.identifierLabel')} *
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                    <Mail className="w-4 h-4" />
                  </div>
                  <input
                    type="text"
                    required
                    value={identifier}
                    onChange={(e) => setIdentifier(e.target.value)}
                    placeholder={t('auth.identifierPlaceholder')}
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-forest/30 focus:border-forest transition-colors font-medium"
                  />
                </div>
                <p className="text-[11px] text-gray-400 mt-1">
                  Enter your email address or 10-digit Indian mobile number.
                </p>
              </div>

              {/* Field 2: Create Password */}
              <div>
                <label className="block text-xs font-bold text-gray-700 mb-1">
                  {t('auth.createPassword')} *
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    type="password"
                    required
                    minLength={6}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="At least 6 characters"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-forest/30 focus:border-forest transition-colors font-medium"
                  />
                </div>
              </div>

              {/* Field 3: Confirm Password */}
              <div>
                <label className="block text-xs font-bold text-gray-700 mb-1">
                  {t('auth.confirmPassword')} *
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    type="password"
                    required
                    minLength={6}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Repeat password"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-forest/30 focus:border-forest transition-colors font-medium"
                  />
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-xl bg-forest hover:bg-forest-light text-white font-bold text-sm transition-all shadow-md shadow-forest/20 flex items-center justify-center space-x-2 disabled:opacity-60 mt-2"
              >
                <span>{loading ? t('common.submitting') : t('auth.signUpBtn')}</span>
                <ArrowRight className="w-4 h-4" />
              </button>

              {/* Switch to Login Link */}
              <div className="text-center pt-2">
                <p className="text-xs text-gray-500">
                  {t('auth.haveAccount')}{' '}
                  <button
                    type="button"
                    onClick={() => {
                      setAuthMode('login');
                      setError(null);
                    }}
                    className="font-bold text-forest hover:underline"
                  >
                    {t('auth.loginBtn')}
                  </button>
                </p>
              </div>

            </form>
          )}

          {/* Social and Demo Authentication Options */}
          <div className="mt-6 pt-5 border-t border-gray-100 space-y-3">
            
            {/* Google OAuth Button */}
            <button
              type="button"
              onClick={handleGoogleSignIn}
              disabled={loading}
              className="w-full py-2.5 rounded-xl border border-gray-300 hover:border-gray-400 text-gray-700 text-xs font-bold transition-all flex items-center justify-center space-x-2 bg-white shadow-sm"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                />
              </svg>
              <span>{t('auth.googleLogin')}</span>
            </button>

            {/* Quick Demo Login Button */}
            <button
              type="button"
              onClick={handleDemoSignIn}
              className="w-full py-2.5 rounded-xl bg-leaf/10 hover:bg-leaf/20 text-forest text-xs font-bold transition-all flex items-center justify-center space-x-2 border border-leaf/30"
            >
              <UserCheck className="w-4 h-4 text-forest" />
              <span>{t('auth.demoLogin')}</span>
            </button>

          </div>

        </div>
      </div>

      {/* Forgot Password Modal */}
      {showForgotModal && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-sm w-full p-6 space-y-4 shadow-2xl border border-cream-dark">
            
            <div className="flex items-center space-x-2.5">
              <div className="p-2.5 rounded-2xl bg-forest/10 text-forest">
                <KeyRound className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-extrabold text-base text-gray-900">
                  {t('auth.resetPassword')}
                </h3>
                <p className="text-xs text-gray-500">
                  {forgotStep === 1
                    ? 'Enter registered email or mobile'
                    : 'Set new account password'}
                </p>
              </div>
            </div>

            {forgotError && (
              <div className="p-3 rounded-xl bg-red-50 text-red-700 text-xs flex items-center space-x-1.5">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{forgotError}</span>
              </div>
            )}

            {forgotSuccess && (
              <div className="p-3 rounded-xl bg-green-50 text-green-700 text-xs flex items-center space-x-1.5">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>{forgotSuccess}</span>
              </div>
            )}

            {forgotStep === 1 ? (
              <form onSubmit={handleRequestReset} className="space-y-3">
                <div>
                  <label className="block text-xs font-bold text-gray-700 mb-1">
                    {t('auth.identifierLabel')}
                  </label>
                  <input
                    type="text"
                    required
                    value={forgotIdentifier}
                    onChange={(e) => setForgotIdentifier(e.target.value)}
                    placeholder="e.g. farmer@dakshina.in or 9845012345"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-forest/30"
                  />
                </div>
                <div className="flex items-center justify-end space-x-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowForgotModal(false)}
                    className="px-4 py-2 rounded-xl text-xs font-bold text-gray-600 hover:bg-gray-100"
                  >
                    {t('common.cancel')}
                  </button>
                  <button
                    type="submit"
                    disabled={forgotLoading}
                    className="px-4 py-2 rounded-xl text-xs font-bold bg-forest text-white hover:bg-forest-light disabled:opacity-50"
                  >
                    {forgotLoading ? t('common.submitting') : 'Verify Account'}
                  </button>
                </div>
              </form>
            ) : (
              <form onSubmit={handleConfirmReset} className="space-y-3">
                <div>
                  <label className="block text-xs font-bold text-gray-700 mb-1">
                    {t('auth.resetTokenLabel')}
                  </label>
                  <input
                    type="text"
                    required
                    value={resetToken}
                    onChange={(e) => setResetToken(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl border border-gray-300 text-xs font-mono bg-gray-50"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-700 mb-1">
                    {t('auth.newPasswordLabel')}
                  </label>
                  <input
                    type="password"
                    required
                    minLength={6}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Min 6 characters"
                    className="w-full px-3.5 py-2 rounded-xl border border-gray-300 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-700 mb-1">
                    {t('auth.confirmPassword')}
                  </label>
                  <input
                    type="password"
                    required
                    minLength={6}
                    value={confirmNewPassword}
                    onChange={(e) => setConfirmNewPassword(e.target.value)}
                    placeholder="Repeat new password"
                    className="w-full px-3.5 py-2 rounded-xl border border-gray-300 text-sm"
                  />
                </div>
                <div className="flex items-center justify-end space-x-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowForgotModal(false)}
                    className="px-4 py-2 rounded-xl text-xs font-bold text-gray-600 hover:bg-gray-100"
                  >
                    {t('common.cancel')}
                  </button>
                  <button
                    type="submit"
                    disabled={forgotLoading}
                    className="px-4 py-2 rounded-xl text-xs font-bold bg-forest text-white hover:bg-forest-light disabled:opacity-50"
                  >
                    {forgotLoading ? t('common.submitting') : 'Save New Password'}
                  </button>
                </div>
              </form>
            )}

          </div>
        </div>
      )}

    </div>
  );
};
