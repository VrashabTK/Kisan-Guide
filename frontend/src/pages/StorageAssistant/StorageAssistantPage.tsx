import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Warehouse,
  Calendar,
  Package,
  AlertTriangle,
  Bookmark,
  CheckCircle2,
  Clock,
  Sparkles,
  Bot,
  ShieldCheck,
  Thermometer,
  Droplets,
  ArrowRight,
  Info
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { api } from '../../services/api';

export const StorageAssistantPage: React.FC = () => {
  const { t } = useTranslation();
  const { profile } = useAuth();
  const { language } = useLanguage();

  const [crop, setCrop] = useState('Arecanut');
  const [harvestDate, setHarvestDate] = useState(
    new Date(Date.now() - 5 * 86400000).toISOString().split('T')[0]
  );
  const [taluk, setTaluk] = useState(profile?.taluk || 'Mangaluru');
  const [storageMethod, setStorageMethod] = useState('Jute bag');
  const [cropCondition, setCropCondition] = useState('Dry');
  const [quantityKg, setQuantityKg] = useState('');
  const [facilityDesc, setFacilityDesc] = useState('');

  const [loading, setLoading] = useState(false);
  const [storageResult, setStorageResult] = useState<any>(null);
  const [aiSuggestions, setAiSuggestions] = useState<any>(null);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const crops = ['Coconut', 'Rice', 'Arecanut', 'Cocoa'];
  const methods = [
    'Ventilated room',
    'Jute bag',
    'Warehouse',
    'Dark room',
    'Open air',
    'Closed container',
  ];
  const conditions = [
    'Fresh',
    'Dry',
    'Slightly spoiled',
    'Sprouted',
    'Damp',
    'Overripe',
    'Partially damaged',
  ];
  const taluks = [
    'Mangaluru', 'Bantwal', 'Belthangady', 'Puttur',
    'Sullia', 'Moodbidri', 'Kadaba', 'Mulki', 'Ullal'
  ];

  const handleGetRecommendations = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSavedSuccess(false);

    try {
      // 1. Fetch scientific storage rule analysis
      const rec = await api.recommendStorage({
        crop,
        harvest_date: harvestDate,
        storage_method: storageMethod,
        crop_condition: cropCondition,
        taluk,
        quantity_kg: quantityKg ? parseFloat(quantityKg) : undefined,
        storage_facility_description: facilityDesc || undefined,
      });
      setStorageResult(rec);

      // 2. Fetch AI post-harvest suggestions
      const aiData = await api.getAIStorageAdvice({
        crop,
        harvest_date: harvestDate,
        storage_method: storageMethod,
        crop_condition: cropCondition,
        taluk,
        language,
      });
      setAiSuggestions(aiData?.ai_suggestions || null);
    } catch (err: any) {
      setError("Unable to generate storage recommendations right now. Please verify inputs.");
    } finally {
      setLoading(false);
    }
  };

  const handleBookmark = async () => {
    if (!storageResult) return;
    try {
      await api.saveItem({
        itemType: 'Storage Assistant',
        itemId: `storage_${crop}_${Date.now()}`,
        title: `Storage Plan: ${crop} (${storageMethod})`,
        title_kn: `ಸಂಗ್ರಹಣಾ ಯೋಜನೆ: ${storageResult.crop_kn} (${storageMethod})`,
        crop,
        location: taluk,
        content: {
          ...storageResult,
          aiSuggestions,
        },
      });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (e) {
      console.error("Failed to bookmark storage", e);
    }
  };

  const isKn = language === 'kn';

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Title */}
      <div>
        <div className="flex items-center space-x-2 text-forest mb-1">
          <Warehouse className="w-6 h-6" />
          <span className="text-xs font-bold uppercase tracking-wider">Dakshina Kannada Post-Harvest Science</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900">
          {t('storage.title')}
        </h1>
        <p className="text-xs sm:text-sm text-gray-600 mt-1 max-w-2xl">
          {t('storage.subtitle')}
        </p>
      </div>

      {/* Main Grid: Form (Left) & Results (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Input Form Column (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-3xl p-6 sm:p-7 border border-cream-dark shadow-sm">
          <h2 className="text-lg font-bold text-gray-900 mb-4 pb-2 border-b border-gray-100">
            {t('storage.formTitle')}
          </h2>

          <form onSubmit={handleGetRecommendations} className="space-y-4">
            
            {/* Crop Select */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                {t('storage.cropLabel')} *
              </label>
              <select
                value={crop}
                onChange={(e) => setCrop(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl border border-gray-300 text-sm bg-white font-semibold text-forest focus:outline-none focus:ring-2 focus:ring-forest"
                required
              >
                {crops.map((c) => (
                  <option key={c} value={c}>
                    {t(`crops.${c}`)}
                  </option>
                ))}
              </select>
            </div>

            {/* Harvest Date */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                {t('storage.harvestDateLabel')} *
              </label>
              <div className="relative">
                <input
                  type="date"
                  max={new Date().toISOString().split('T')[0]}
                  value={harvestDate}
                  onChange={(e) => setHarvestDate(e.target.value)}
                  className="w-full px-4 py-2 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-forest"
                  required
                />
              </div>
            </div>

            {/* Taluk */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                {t('cropRec.talukLabel')}
              </label>
              <select
                value={taluk}
                onChange={(e) => setTaluk(e.target.value)}
                className="w-full px-4 py-2 rounded-xl border border-gray-300 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-forest"
              >
                {taluks.map((tlk) => (
                  <option key={tlk} value={tlk}>
                    {t(`taluks.${tlk}`)}
                  </option>
                ))}
              </select>
            </div>

            {/* Storage Method */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                {t('storage.methodLabel')} *
              </label>
              <select
                value={storageMethod}
                onChange={(e) => setStorageMethod(e.target.value)}
                className="w-full px-4 py-2 rounded-xl border border-gray-300 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-forest"
                required
              >
                {methods.map((m) => (
                  <option key={m} value={m}>
                    {t(`storageMethods.${m}`)}
                  </option>
                ))}
              </select>
            </div>

            {/* Crop Condition */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                {t('storage.conditionLabel')} *
              </label>
              <select
                value={cropCondition}
                onChange={(e) => setCropCondition(e.target.value)}
                className="w-full px-4 py-2 rounded-xl border border-gray-300 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-forest"
                required
              >
                {conditions.map((cd) => (
                  <option key={cd} value={cd}>
                    {t(`conditions.${cd}`)}
                  </option>
                ))}
              </select>
            </div>

            {/* Quantity */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                {t('storage.quantityLabel')}
              </label>
              <input
                type="number"
                min="1"
                value={quantityKg}
                onChange={(e) => setQuantityKg(e.target.value)}
                placeholder="e.g. 500"
                className="w-full px-4 py-2 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-forest"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-forest hover:bg-forest-light text-white font-bold text-sm transition-all shadow-md shadow-forest/20 flex items-center justify-center space-x-2 disabled:opacity-60 mt-2"
            >
              <span>{loading ? t('storage.analyzing') : t('storage.submitBtn')}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        </div>

        {/* Results Column (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          
          {error && (
            <div className="p-4 rounded-2xl bg-red-50 border border-red-200 text-red-700 text-sm flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {savedSuccess && (
            <div className="p-4 rounded-2xl bg-green-50 border border-green-200 text-green-700 text-sm flex items-center space-x-2">
              <CheckCircle2 className="w-5 h-5 shrink-0" />
              <span>Storage recommendation bookmarked to your Saved items!</span>
            </div>
          )}

          {!storageResult && !loading && (
            <div className="bg-white rounded-3xl p-10 border border-dashed border-gray-200 text-center space-y-3">
              <Warehouse className="w-12 h-12 text-forest/40 mx-auto" />
              <h3 className="font-bold text-gray-800 text-base">
                Ready for Storage Evaluation
              </h3>
              <p className="text-xs text-gray-500 max-w-md mx-auto">
                Submit your harvested crop conditions above to calculate safe shelf life, deadline dates, risk indicators, and AI post-harvest precautions.
              </p>
            </div>
          )}

          {storageResult && (
            <div className="space-y-6">
              
              {/* Primary Evaluation Card */}
              <div className="bg-white rounded-3xl p-6 sm:p-7 border border-cream-dark shadow-sm space-y-6">
                
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-xs font-bold text-forest uppercase tracking-wider block">
                      {isKn ? storageResult.crop_kn : storageResult.crop} • {storageResult.days_elapsed} Days Since Harvest
                    </span>
                    <h3 className="text-xl sm:text-2xl font-black text-gray-900 mt-1">
                      {t('storage.suitabilityTitle')}:{' '}
                      <span className={
                        storageResult.suitability === 'Suitable'
                          ? 'text-forest'
                          : storageResult.suitability === 'Needs Improvement'
                          ? 'text-amber-600'
                          : 'text-red-600'
                      }>
                        {isKn ? storageResult.suitability_kn : storageResult.suitability}
                      </span>
                    </h3>
                  </div>

                  <button
                    onClick={handleBookmark}
                    className="p-2 rounded-full border border-gray-200 hover:border-forest text-gray-500 hover:text-forest transition-colors shadow-sm"
                    title={t('common.bookmark')}
                  >
                    <Bookmark className="w-5 h-5" />
                  </button>
                </div>

                {/* Duration & Selling Deadline Callout */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="p-4 rounded-2xl bg-cream border border-cream-dark space-y-1">
                    <span className="text-[11px] font-bold text-gray-500 uppercase tracking-wider flex items-center space-x-1">
                      <Clock className="w-3.5 h-3.5 text-forest" />
                      <span>{t('storage.safeDuration')}</span>
                    </span>
                    <div className="text-2xl font-black text-gray-900">
                      ~{storageResult.remaining_days} {t('storage.daysRemaining')}
                    </div>
                    <span className="text-[11px] text-gray-500 block">
                      Total capacity: ~{storageResult.estimated_duration_days} days
                    </span>
                  </div>

                  <div className="p-4 rounded-2xl bg-cream border border-cream-dark space-y-1">
                    <span className="text-[11px] font-bold text-gray-500 uppercase tracking-wider flex items-center space-x-1">
                      <Calendar className="w-3.5 h-3.5 text-earth" />
                      <span>{t('storage.sellingDeadline')}</span>
                    </span>
                    <div className="text-2xl font-black text-earth">
                      {new Date(storageResult.estimated_deadline).toLocaleDateString(isKn ? 'kn-IN' : 'en-IN', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric'
                      })}
                    </div>
                    <span className="text-[10px] text-gray-400 block leading-tight">
                      {t('storage.deadlineNotice')}
                    </span>
                  </div>
                </div>

                {/* Risk Indicators Matrix */}
                <div>
                  <h4 className="font-bold text-xs text-gray-600 uppercase tracking-wider mb-2.5">
                    {t('storage.riskIndicators')}
                  </h4>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    {Object.entries(storageResult.risks).map(([riskKey, riskVal]) => {
                      const valStr = String(riskVal);
                      const badgeClass =
                        valStr === 'High'
                          ? 'bg-red-50 text-red-700 border-red-200'
                          : valStr === 'Medium'
                          ? 'bg-amber-50 text-amber-700 border-amber-200'
                          : 'bg-green-50 text-green-700 border-green-200';

                      return (
                        <div key={riskKey} className={`p-3 rounded-xl border text-center ${badgeClass}`}>
                          <span className="text-[10px] uppercase font-bold tracking-wider block opacity-75">
                            {riskKey} Risk
                          </span>
                          <span className="text-sm font-black block mt-0.5">{valStr}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Standard Handling Instructions */}
                <div>
                  <h4 className="font-bold text-xs text-gray-600 uppercase tracking-wider mb-2">
                    {t('storage.instructionsTitle')}
                  </h4>
                  <div className="space-y-2 text-xs sm:text-sm text-gray-700 bg-gray-50 p-4 rounded-2xl border border-gray-100">
                    {(isKn ? storageResult.instructions_kn : storageResult.instructions_en).map((inst: string, idx: number) => (
                      <div key={idx} className="flex items-start space-x-2">
                        <CheckCircle2 className="w-4 h-4 text-forest shrink-0 mt-0.5" />
                        <span>{inst}</span>
                      </div>
                    ))}
                  </div>
                </div>

              </div>

              {/* AI Storage Assistant Section */}
              <div className="bg-gradient-to-br from-forest-dark to-forest text-white rounded-3xl p-6 sm:p-7 shadow-lg space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Bot className="w-6 h-6 text-leaf-light" />
                    <h3 className="font-black text-lg text-white">
                      {t('storage.aiAssistantTitle')}
                    </h3>
                  </div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-white/10 text-leaf-light border border-white/20">
                    {aiSuggestions?.source || 'Verified Post-Harvest Engine'}
                  </span>
                </div>

                {aiSuggestions && (
                  <div className="space-y-4 text-xs sm:text-sm text-cream/90">
                    <p className="leading-relaxed bg-white/10 p-3.5 rounded-xl border border-white/10">
                      {isKn && aiSuggestions.summary_kn ? aiSuggestions.summary_kn : aiSuggestions.summary_en}
                    </p>

                    <div>
                      <strong className="block text-leaf-light font-bold mb-1.5 uppercase text-xs">
                        {t('storage.aiActionSteps')}:
                      </strong>
                      <div className="space-y-1.5">
                        {(isKn && aiSuggestions.action_steps_kn ? aiSuggestions.action_steps_kn : aiSuggestions.action_steps_en)?.map((step: string, i: number) => (
                          <div key={i} className="flex items-start space-x-2">
                            <ArrowRight className="w-3.5 h-3.5 text-leaf-light shrink-0 mt-0.5" />
                            <span>{step}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 text-xs">
                      <div className="p-3 bg-white/5 rounded-xl border border-white/10">
                        <span className="font-bold text-leaf-light block mb-1">
                          {t('storage.aiMoistureTip')}
                        </span>
                        <p>{isKn && aiSuggestions.moisture_management_kn ? aiSuggestions.moisture_management_kn : aiSuggestions.moisture_management_en}</p>
                      </div>
                      <div className="p-3 bg-white/5 rounded-xl border border-white/10">
                        <span className="font-bold text-leaf-light block mb-1">
                          {t('storage.aiPestTip')}
                        </span>
                        <p>{isKn && aiSuggestions.pest_prevention_kn ? aiSuggestions.pest_prevention_kn : aiSuggestions.pest_prevention_en}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

            </div>
          )}

        </div>

      </div>

    </div>
  );
};
