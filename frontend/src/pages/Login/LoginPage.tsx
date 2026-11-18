import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Sprout,
  Phone,
  Mail,
  Lock,
  User,
  MapPin,
  ArrowRight,
  ShieldCheck,
  Languages,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { ConfirmationResult } from '../../services/firebase';

export const LoginPage: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const {
    loginWithGoogle,
    loginWithEmail,
    signupWithEmail,
    sendPhoneOtp,
    verifyPhoneOtp,
    resetPassword,
    quickDemoLogin,
  } = useAuth();
  const { language, toggleLanguage } = useLanguage();

  const [authMethod, setAuthMethod] = useState<'phone' | 'email' | 'signup'>('phone');
  
  // Phone OTP state
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [confirmationResult, setConfirmationResult] = useState<ConfirmationResult | null>(null);
  const [otpSent, setOtpSent] = useState(false);
  const [cooldown, setCooldown] = useState(0);

  // Email state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [taluk, setTaluk] = useState('Mangaluru');
  const [agreeTerms, setAgreeTerms] = useState(false);

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [showForgotModal, setShowForgotModal] = useState(false);
  const [forgotEmail, setForgotEmail] = useState('');

  const taluks = [
    'Mangaluru', 'Bantwal', 'Belthangady', 'Puttur',
    'Sullia', 'Moodbidri', 'Kadaba', 'Mulki', 'Ullal'
  ];

  // Phone Login Submit
  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!phone || phone.replace(/\D/g, '').length < 10) {
      setError(t('auth.errors.invalidPhone'));
      return;
    }
    setLoading(true);
    try {
      const res = await sendPhoneOtp(phone, 'recaptcha-container');
      if (res) {
        setConfirmationResult(res);
        setOtpSent(true);
        setCooldown(60);
        const timer = setInterval(() => {
          setCooldown((prev) => {
            if (prev <= 1) {
              clearInterval(timer);
              return 0;
            }
            return prev - 1;
          });
        }, 1000);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to send OTP.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!confirmationResult || !otp) return;
    setLoading(true);
    setError(null);
    try {
      await verifyPhoneOtp(confirmationResult, otp, fullName, taluk);
      navigate('/');
    } catch (err: any) {
      setError(t('auth.errors.otpInvalid'));
    } finally {
      setLoading(false);
    }
  };

  // Email Login
  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!email) return setError(t('auth.errors.invalidEmail'));
    if (!password) return setError(t('auth.errors.passwordShort'));
    setLoading(true);
    try {
      await loginWithEmail(email, password);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Failed to sign in.');
    } finally {
      setLoading(false);
    }
  };

  // Email Signup
  const handleEmailSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!fullName) return setError(t('auth.errors.nameRequired'));
    if (!email) return setError(t('auth.errors.invalidEmail'));
    if (password.length < 6) return setError(t('auth.errors.passwordShort'));
    if (password !== confirmPassword) return setError(t('auth.errors.passwordMismatch'));
    if (!agreeTerms) return setError(t('auth.errors.termsRequired'));

    setLoading(true);
    try {
      await signupWithEmail(email, password, fullName, taluk, phone);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Failed to create account.');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setError(null);
    setLoading(true);
    try {
      await loginWithGoogle();
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Google sign in canceled or failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!forgotEmail) return;
    try {
      await resetPassword(forgotEmail);
      setMessage(`Password reset email dispatched to ${forgotEmail}`);
      setShowForgotModal(false);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDemoSignIn = () => {
    quickDemoLogin();
    navigate('/');
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row bg-cream font-sans">
      
      {/* Invisible container for Firebase phone verification */}
      <div id="recaptcha-container"></div>

      {/* Left Column: Visual & Agricultural Branding */}
      <div className="lg:w-1/2 bg-gradient-to-br from-forest-dark via-forest to-leaf text-white p-8 lg:p-12 flex flex-col justify-between relative overflow-hidden">
        {/* Subtle background plant art */}
        <div className="absolute -bottom-16 -right-16 w-96 h-96 rounded-full bg-white/5 pointer-events-none blur-2xl" />
        <div className="absolute top-1/4 -left-20 w-64 h-64 rounded-full bg-leaf/20 pointer-events-none blur-3xl" />

        {/* Top Header */}
        <div className="flex items-center justify-between z-10">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-2xl bg-white/10 backdrop-blur border border-white/20 flex items-center justify-center">
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
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-white/10 hover:bg-white/20 backdrop-blur border border-white/20 text-xs font-semibold text-white transition-colors"
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
              <span>Real-Time Weather Advisories</span>
            </div>
            <div className="flex items-center space-x-2 bg-white/10 backdrop-blur p-2.5 rounded-xl border border-white/10">
              <CheckCircle2 className="w-4 h-4 text-leaf-light shrink-0" />
              <span>Dakshina Kannada Agro-Rules</span>
            </div>
            <div className="flex items-center space-x-2 bg-white/10 backdrop-blur p-2.5 rounded-xl border border-white/10">
              <CheckCircle2 className="w-4 h-4 text-leaf-light shrink-0" />
              <span>Safe Storage Duration AI</span>
            </div>
            <div className="flex items-center space-x-2 bg-white/10 backdrop-blur p-2.5 rounded-xl border border-white/10">
              <CheckCircle2 className="w-4 h-4 text-leaf-light shrink-0" />
              <span>Bilingual English & Kannada</span>
            </div>
          </div>
        </div>

        {/* Footer Note */}
        <div className="z-10 text-xs text-white/60">
          Covering 9 Taluks: Mangaluru, Bantwal, Belthangady, Puttur, Sullia, Moodbidri, Kadaba, Mulki, Ullal.
        </div>
      </div>

      {/* Right Column: Authentication Card Forms */}
      <div className="lg:w-1/2 flex items-center justify-center p-6 sm:p-10 lg:p-12">
        <div className="w-full max-w-md bg-white rounded-3xl shadow-xl shadow-forest/5 border border-cream-dark p-6 sm:p-8">
          
          {/* Method Selector Tabs */}
          <div className="flex bg-cream p-1 rounded-2xl mb-6">
            <button
              onClick={() => { setAuthMethod('phone'); setError(null); }}
              className={`flex-1 py-2 text-xs sm:text-sm font-semibold rounded-xl transition-all ${
                authMethod === 'phone'
                  ? 'bg-white text-forest shadow-sm'
                  : 'text-gray-500 hover:text-forest'
              }`}
            >
              {t('auth.mobileLogin')}
            </button>
            <button
              onClick={() => { setAuthMethod('email'); setError(null); }}
              className={`flex-1 py-2 text-xs sm:text-sm font-semibold rounded-xl transition-all ${
                authMethod === 'email'
                  ? 'bg-white text-forest shadow-sm'
                  : 'text-gray-500 hover:text-forest'
              }`}
            >
              {t('auth.emailLogin')}
            </button>
            <button
              onClick={() => { setAuthMethod('signup'); setError(null); }}
              className={`flex-1 py-2 text-xs sm:text-sm font-semibold rounded-xl transition-all ${
                authMethod === 'signup'
                  ? 'bg-white text-forest shadow-sm'
                  : 'text-gray-500 hover:text-forest'
              }`}
            >
              {t('auth.signup')}
            </button>
          </div>

          {/* Feedback messages */}
          {error && (
            <div className="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}
          {message && (
            <div className="mb-4 p-3 rounded-xl bg-green-50 border border-green-200 text-green-700 text-xs flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{message}</span>
            </div>
          )}

          {/* 1. Mobile Phone Login Form */}
          {authMethod === 'phone' && (
            <div>
              {!otpSent ? (
                <form onSubmit={handleSendOtp} className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">
                      {t('auth.phoneNumber')}
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                        <Phone className="w-4 h-4" />
                        <span className="ml-1 text-xs font-bold text-gray-500">+91</span>
                      </div>
                      <input
                        type="tel"
                        maxLength={10}
                        value={phone}
                        onChange={(e) => setPhone(e.target.value.replace(/\D/g, ''))}
                        placeholder={t('auth.phoneNumberPlaceholder')}
                        className="w-full pl-16 pr-4 py-2.5 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-forest/30 focus:border-forest"
                        required
                      />
                    </div>
                  </div>

                  <p className="text-[11px] text-gray-400">
                    {t('auth.recaptchaNotice')}
                  </p>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-2.5 rounded-xl bg-forest hover:bg-forest-light text-white text-sm font-semibold transition-colors flex items-center justify-center space-x-2 shadow-md shadow-forest/20 disabled:opacity-60"
                  >
                    <span>{loading ? t('common.loading') : t('auth.sendOtp')}</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </form>
              ) : (
                <form onSubmit={handleVerifyOtp} className="space-y-4">
                  <div>
                    <div className="flex justify-between items-center mb-1">
                      <label className="block text-xs font-semibold text-gray-700">
                        {t('auth.enterOtp')}
                      </label>
                      <button
                        type="button"
                        onClick={() => setOtpSent(false)}
                        className="text-[11px] text-forest underline font-medium"
                      >
                        Change Number
                      </button>
                    </div>
                    <input
                      type="text"
                      maxLength={6}
                      value={otp}
                      onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                      placeholder="6-digit code"
                      className="w-full px-4 py-2.5 rounded-xl border border-gray-300 text-center tracking-widest text-lg font-bold focus:outline-none focus:ring-2 focus:ring-forest/30 focus:border-forest"
                      required
                      autoFocus
                    />
                  </div>

                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>
                      {cooldown > 0 ? (
                        t('auth.cooldown', { seconds: cooldown })
                      ) : (
                        <button
                          type="button"
                          onClick={handleSendOtp}
                          className="text-forest underline font-semibold"
                        >
                          {t('auth.resendOtp')}
                        </button>
                      )}
                    </span>
                  </div>

                  <button
                    type="submit"
                    disabled={loading || otp.length < 6}
                    className="w-full py-2.5 rounded-xl bg-forest hover:bg-forest-light text-white text-sm font-semibold transition-colors flex items-center justify-center space-x-2 shadow-md shadow-forest/20 disabled:opacity-60"
                  >
                    <span>{loading ? t('common.loading') : t('auth.verifyOtp')}</span>
                    <ShieldCheck className="w-4 h-4" />
                  </button>
                </form>
              )}
            </div>
          )}

          {/* 2. Email Login Form */}
          {authMethod === 'email' && (
            <form onSubmit={handleEmailLogin} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  {t('auth.email')}
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                    <Mail className="w-4 h-4" />
                  </div>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="farmer@dakshina.in"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-forest/30 focus:border-forest"
                    required
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="block text-xs font-semibold text-gray-700">
                    {t('auth.password')}
                  </label>
                  <button
                    type="button"
                    onClick={() => setShowForgotModal(true)}
                    className="text-[11px] text-forest hover:underline font-medium"
                  >
                    {t('auth.forgotPassword')}
                  </button>
                </div>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-forest/30 focus:border-forest"
                    required
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 rounded-xl bg-forest hover:bg-forest-light text-white text-sm font-semibold transition-colors flex items-center justify-center space-x-2 shadow-md shadow-forest/20 disabled:opacity-60"
              >
                <span>{loading ? t('common.loading') : t('auth.login')}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>
          )}

          {/* 3. Signup Form */}
          {authMethod === 'signup' && (
            <form onSubmit={handleEmailSignup} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  {t('auth.fullName')}
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                    <User className="w-4 h-4" />
                  </div>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="e.g. Ramesh Gowda"
                    className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-forest/30 focus:border-forest"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  {t('auth.taluk')}
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                    <MapPin className="w-4 h-4" />
                  </div>
                  <select
                    value={taluk}
                    onChange={(e) => setTaluk(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-300 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-forest/30 focus:border-forest"
                  >
                    {taluks.map((tlk) => (
                      <option key={tlk} value={tlk}>
                        {t(`taluks.${tlk}`)}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  {t('auth.email')}
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                    <Mail className="w-4 h-4" />
                  </div>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="farmer@dakshina.in"
                    className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-forest/30 focus:border-forest"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    {t('auth.password')}
                  </label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full px-3 py-2 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-forest/30 focus:border-forest"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    {t('auth.confirmPassword')}
                  </label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full px-3 py-2 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-forest/30 focus:border-forest"
                    required
                  />
                </div>
              </div>

              <div className="flex items-start space-x-2 pt-1">
                <input
                  type="checkbox"
                  id="terms"
                  checked={agreeTerms}
                  onChange={(e) => setAgreeTerms(e.target.checked)}
                  className="mt-1 rounded text-forest focus:ring-forest"
                  required
                />
                <label htmlFor="terms" className="text-[11px] text-gray-600 leading-tight">
                  {t('auth.agreeTerms')}
                </label>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 rounded-xl bg-forest hover:bg-forest-light text-white text-sm font-semibold transition-colors flex items-center justify-center space-x-2 shadow-md shadow-forest/20 disabled:opacity-60 mt-2"
              >
                <span>{loading ? t('common.loading') : t('auth.signup')}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>
          )}

          {/* Social / Google & Demo Dividers */}
          <div className="relative my-5">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-2 text-gray-400 font-semibold">{t('auth.or')}</span>
            </div>
          </div>

          {/* Google Login Button */}
          <button
            onClick={handleGoogleLogin}
            disabled={loading}
            className="w-full py-2.5 rounded-xl border border-gray-300 bg-white hover:bg-gray-50 text-gray-700 text-xs sm:text-sm font-semibold transition-colors flex items-center justify-center space-x-2 shadow-sm disabled:opacity-60"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.8-2.4 3.66v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.15z"
              />
              <path
                fill="#34A853"
                d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z"
              />
              <path
                fill="#FBBC05"
                d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.99 0 12s.45 3.82 1.25 5.42l4.03-3.15z"
              />
              <path
                fill="#EA4335"
                d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"
              />
            </svg>
            <span>{t('auth.googleLogin')}</span>
          </button>

          {/* Instant Quick Demo Login Button */}
          <div className="mt-4 pt-4 border-t border-cream-dark text-center">
            <button
              onClick={handleDemoSignIn}
              className="w-full py-2 rounded-xl bg-cream hover:bg-cream-dark text-forest text-xs font-bold transition-colors border border-forest/15"
            >
              {t('auth.demoLogin')}
            </button>
            <p className="text-[10px] text-gray-400 mt-1">
              One-click access with simulated Dakshina Kannada farmer credentials.
            </p>
          </div>

        </div>
      </div>

      {/* Forgot Password Modal */}
      {showForgotModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl max-w-sm w-full p-6 shadow-2xl space-y-4">
            <h3 className="font-bold text-gray-900 text-lg">
              {t('auth.resetPassword')}
            </h3>
            <p className="text-xs text-gray-600">
              Enter your registered email address to receive password reset instructions.
            </p>
            <form onSubmit={handleForgotPassword} className="space-y-3">
              <input
                type="email"
                value={forgotEmail}
                onChange={(e) => setForgotEmail(e.target.value)}
                placeholder="farmer@dakshina.in"
                className="w-full px-3 py-2 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-forest"
                required
              />
              <div className="flex space-x-2">
                <button
                  type="button"
                  onClick={() => setShowForgotModal(false)}
                  className="flex-1 py-2 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-semibold"
                >
                  {t('common.cancel')}
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2 rounded-xl bg-forest hover:bg-forest-light text-white text-xs font-semibold"
                >
                  {t('auth.sendResetLink')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};
