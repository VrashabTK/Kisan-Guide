import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Sprout,
  Tractor,
  MapPin,
  Droplets,
  Calendar,
  ShieldCheck,
  AlertTriangle,
  Bookmark,
  CheckCircle2,
  ArrowRight,
  Sparkles,
  Info
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { useCrop } from '../../contexts/CropContext';
import { useFarm } from '../../contexts/FarmContext';
import { SupportedCrop } from '../../types/farm';
import { api } from '../../services/api';

export const CropRecommendationPage: React.FC = () => {
  const { t } = useTranslation();
  const { profile } = useAuth();
  const { language } = useLanguage();
  const { selectedCrop, setSelectedCrop } = useCrop();
  const { openAddFarmModalWithCrop } = useFarm();

  const [taluk, setTaluk] = useState(profile?.taluk || 'Mangaluru');
  const [waterAvailability, setWaterAvailability] = useState('Moderate');
  const [soilType, setSoilType] = useState('');
  const [irrigationAvailable, setIrrigationAvailable] = useState<boolean>(true);
  const [previousCrop, setPreviousCrop] = useState('');
  const [areaAcres, setAreaAcres] = useState<string>('');

  const [loading, setLoading] = useState(false);
  const [recommendationResult, setRecommendationResult] = useState<any>(null);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [cropSelectedNotice, setCropSelectedNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const taluks = [
    'Mangaluru', 'Bantwal', 'Belthangady', 'Puttur',
    'Sullia', 'Moodbidri', 'Kadaba', 'Mulki', 'Ullal'
  ];

  const handleGetRecommendation = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSavedSuccess(false);

    try {
      const res = await api.recommendCrops({
        taluk,
        water_availability: waterAvailability,
        soil_type: soilType || undefined,
        irrigation_available: irrigationAvailable,
        previous_crop: previousCrop || undefined,
        plantation_area_acres: areaAcres ? parseFloat(areaAcres) : undefined,
      });
      setRecommendationResult(res);
    } catch (err: any) {
      setError(t('cropRec.unableToRecommend'));
    } finally {
      setLoading(false);
    }
  };

  const handleBookmark = async (cropData: any) => {
    try {
      await api.saveItem({
        itemType: 'Crop Recommendation',
        itemId: `crop_${cropData.crop}_${Date.now()}`,
        title: `Recommended: ${cropData.crop} (${taluk})`,
        title_kn: `ಶಿಫಾರಸು: ${cropData.crop_kn} (${cropData.taluk_kn})`,
        crop: cropData.crop,
        location: taluk,
        content: cropData,
      });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      console.error("Failed to bookmark recommendation", err);
    }
  };

  const handleSelectCrop = async (cropName: string, localizedName?: string) => {
    await setSelectedCrop(cropName, true);
    const displayName = localizedName || cropName;
    const msg = language === 'kn'
      ? `${displayName} ಅನ್ನು ಹವಾಮಾನ ಮತ್ತು ಶೇಖರಣಾ ಸಹಾಯಕರಲ್ಲಿ ಸಕ್ರಿಯ ಬೆಳೆಯಾಗಿ ಆಯ್ಕೆಮಾಡಲಾಗಿದೆ!`
      : `${cropName} has been selected! It is now the default crop across Weather and Storage assistants.`;
    setCropSelectedNotice(msg);
    setTimeout(() => setCropSelectedNotice(null), 4000);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Page Title */}
      <div>
        <div className="flex items-center space-x-2 text-forest mb-1">
          <Sprout className="w-6 h-6" />
          <span className="text-xs font-bold uppercase tracking-wider">Dakshina Kannada Agronomy</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900">
          {t('cropRec.title')}
        </h1>
        <p className="text-xs sm:text-sm text-gray-600 mt-1 max-w-2xl">
          {t('cropRec.subtitle')}
        </p>
      </div>

      {/* Main Grid: Form (Left) & Results (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Form Column (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-3xl p-6 sm:p-7 border border-cream-dark shadow-sm">
          <h2 className="text-lg font-bold text-gray-900 mb-4 pb-2 border-b border-gray-100">
            {t('cropRec.formTitle')}
          </h2>

          <form onSubmit={handleGetRecommendation} className="space-y-4">
            
            {/* Taluk */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                {t('cropRec.talukLabel')} *
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                  <MapPin className="w-4 h-4 text-forest" />
                </div>
                <select
                  value={taluk}
                  onChange={(e) => setTaluk(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-300 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-forest/30 focus:border-forest"
                  required
                >
                  {taluks.map((tlk) => (
                    <option key={tlk} value={tlk}>
                      {t(`taluks.${tlk}`)}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Water Availability */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                {t('cropRec.waterLabel')} *
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                  <Droplets className="w-4 h-4 text-blue-500" />
                </div>
                <select
                  value={waterAvailability}
                  onChange={(e) => setWaterAvailability(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-300 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-forest/30 focus:border-forest"
                  required
                >
                  <option value="Low">{t('waterLevels.Low')} (Seasonal rain only / Low borewell)</option>
                  <option value="Moderate">{t('waterLevels.Moderate')} (Adequate borewell / pond)</option>
                  <option value="High">{t('waterLevels.High')} (River valley / Abundant water)</option>
                </select>
              </div>
              <p className="text-[11px] text-gray-400 mt-1">
                {t('cropRec.waterDesc')}
              </p>
            </div>

            {/* Soil Type (Optional) */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                {t('cropRec.soilLabel')}
              </label>
              <input
                type="text"
                value={soilType}
                onChange={(e) => setSoilType(e.target.value)}
                placeholder={t('cropRec.soilPlaceholder')}
                className="w-full px-4 py-2 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-forest/30 focus:border-forest"
              />
            </div>

            {/* Irrigation Available */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                {t('cropRec.irrigationLabel')}
              </label>
              <div className="flex space-x-4">
                <label className="flex items-center space-x-2 text-sm text-gray-700 cursor-pointer">
                  <input
                    type="radio"
                    name="irrigation"
                    checked={irrigationAvailable === true}
                    onChange={() => setIrrigationAvailable(true)}
                    className="text-forest focus:ring-forest"
                  />
                  <span>{t('cropRec.yes')}</span>
                </label>
                <label className="flex items-center space-x-2 text-sm text-gray-700 cursor-pointer">
                  <input
                    type="radio"
                    name="irrigation"
                    checked={irrigationAvailable === false}
                    onChange={() => setIrrigationAvailable(false)}
                    className="text-forest focus:ring-forest"
                  />
                  <span>{t('cropRec.no')}</span>
                </label>
              </div>
            </div>

            {/* Plantation Area */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                {t('cropRec.areaLabel')}
              </label>
              <input
                type="number"
                step="0.5"
                min="0.1"
                value={areaAcres}
                onChange={(e) => setAreaAcres(e.target.value)}
                placeholder="e.g. 2.5"
                className="w-full px-4 py-2 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-forest/30 focus:border-forest"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-forest hover:bg-forest-light text-white font-bold text-sm transition-all shadow-md shadow-forest/20 flex items-center justify-center space-x-2 disabled:opacity-60 mt-2"
            >
              <span>{loading ? t('cropRec.evaluating') : t('cropRec.submitBtn')}</span>
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
              <span>{t('cropRec.bookmarkSuccess')}</span>
            </div>
          )}

          {cropSelectedNotice && (
            <div className="p-4 rounded-2xl bg-forest/10 border-2 border-forest/30 text-forest-dark text-sm flex items-center space-x-2.5 animate-pulse">
              <CheckCircle2 className="w-5 h-5 text-forest shrink-0" />
              <span className="font-semibold">{cropSelectedNotice}</span>
            </div>
          )}

          {!recommendationResult && !loading && (
            <div className="bg-white rounded-3xl p-10 border border-dashed border-gray-200 text-center space-y-3">
              <Sprout className="w-12 h-12 text-forest/40 mx-auto" />
              <h3 className="font-bold text-gray-800 text-base">
                Ready for Soil & Weather Evaluation
              </h3>
              <p className="text-xs text-gray-500 max-w-md mx-auto">
                Fill in your farm details and click "Get Crop Recommendations" to trigger our scientific suitability engine for Dakshina Kannada.
              </p>
            </div>
          )}

          {recommendationResult && (
            <div className="space-y-6">
              
              {/* Primary Recommended Crop Card */}
              {(() => {
                const primary = recommendationResult.primary_recommendation;
                const isKn = language === 'kn';
                const cropName = isKn ? primary.crop_kn : primary.crop;
                const plantingWindow = isKn ? primary.plantation_window_kn : primary.plantation_window_en;
                const reasons = isKn ? primary.reasons_kn : primary.reasons_en;
                const precautions = isKn ? primary.precautions_kn : primary.precautions_en;
                const warnings = isKn ? primary.warnings_kn : primary.warnings_en;

                return (
                  <div className="bg-white rounded-3xl border-2 border-forest/30 shadow-lg shadow-forest/5 overflow-hidden">
                    
                    {/* Top Hero Image & Badge */}
                    <div className="relative h-48 sm:h-56 bg-forest-dark overflow-hidden">
                      <img
                        src={primary.image}
                        alt={primary.crop}
                        className="w-full h-full object-cover opacity-85"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-transparent" />
                      
                      <div className="absolute top-4 left-4">
                        <span className="px-3 py-1 rounded-full bg-leaf text-white text-xs font-extrabold uppercase tracking-wider flex items-center space-x-1 shadow">
                          <Sparkles className="w-3.5 h-3.5" />
                          <span>{t('cropRec.primaryTag')}</span>
                        </span>
                      </div>

                      <div className="absolute top-4 right-4">
                        <button
                          onClick={() => handleBookmark(primary)}
                          className="p-2 rounded-full bg-white/20 backdrop-blur hover:bg-white text-white hover:text-forest transition-colors shadow"
                          title={t('common.bookmark')}
                        >
                          <Bookmark className="w-5 h-5" />
                        </button>
                      </div>

                      <div className="absolute bottom-4 left-4 right-4 text-white flex items-end justify-between">
                        <div>
                          <h2 className="text-2xl sm:text-3xl font-black">{cropName}</h2>
                          <p className="text-xs text-cream/90 italic">{primary.scientific_name}</p>
                        </div>
                        
                        {/* Suitability Score Pill */}
                        <div className="bg-forest/90 backdrop-blur px-3.5 py-1.5 rounded-2xl border border-white/20 text-center">
                          <span className="text-[10px] text-cream block uppercase font-bold">Suitability</span>
                          <span className="text-xl font-black text-leaf-light">{primary.suitability_score}%</span>
                        </div>
                      </div>
                    </div>

                    {/* Content Section */}
                    <div className="p-6 sm:p-7 space-y-5">

                      {/* Active Crop Selection Action Button */}
                      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 p-3.5 rounded-2xl bg-forest/5 border border-forest/20">
                        <div className="flex items-center space-x-2">
                          <Sprout className="w-5 h-5 text-forest shrink-0" />
                          <span className="text-xs font-semibold text-gray-700">
                            {selectedCrop === primary.crop
                              ? (isKn ? 'ಈ ಬೆಳೆ ಪ್ರಸ್ತುತ ನಿಮ್ಮ ಸಕ್ರಿಯ ಬೆಳೆಯಾಗಿದೆ.' : 'This crop is currently your active crop.')
                              : (isKn ? 'ಹವಾಮಾನ ಮತ್ತು ಶೇಖರಣಾ ಸಹಾಯಕರಲ್ಲಿ ಬಳಸಲು ಆಯ್ಕೆಮಾಡಿ.' : 'Use this as your active crop across Weather and Storage.')}
                          </span>
                        </div>
                        <div className="flex flex-wrap items-center gap-2">
                          <button
                            type="button"
                            onClick={() => openAddFarmModalWithCrop(primary.crop as SupportedCrop)}
                            className="px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center justify-center space-x-1.5 shadow-sm bg-emerald-600 hover:bg-emerald-700 text-white"
                          >
                            <Tractor className="w-3.5 h-3.5" />
                            <span>{isKn ? 'ಕೃಷಿ ಪ್ರಾರಂಭಿಸಿ' : 'Start Farming'}</span>
                          </button>
                          <button
                            type="button"
                            onClick={() => handleSelectCrop(primary.crop, cropName)}
                            className={`w-full sm:w-auto px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center justify-center space-x-1.5 shadow-sm ${
                              selectedCrop === primary.crop
                                ? 'bg-leaf text-white cursor-default'
                                : 'bg-forest hover:bg-forest-light text-white'
                            }`}
                          >
                            {selectedCrop === primary.crop ? (
                              <>
                                <CheckCircle2 className="w-3.5 h-3.5" />
                                <span>{isKn ? 'ಆಯ್ಕೆಮಾಡಲಾಗಿದೆ' : 'Currently Selected'}</span>
                              </>
                            ) : (
                              <>
                                <Sprout className="w-3.5 h-3.5" />
                                <span>{isKn ? 'ಸಕ್ರಿಯ ಬೆಳೆಯಾಗಿ ಆಯ್ಕೆಮಾಡಿ' : 'Select as Active Crop'}</span>
                              </>
                            )}
                          </button>
                        </div>
                      </div>
                      
                      {/* Plantation Window Highlight */}
                      <div className="p-4 rounded-2xl bg-cream border border-cream-dark">
                        <div className="flex items-center space-x-2 text-forest mb-1 font-bold text-xs uppercase tracking-wider">
                          <Calendar className="w-4 h-4" />
                          <span>{t('cropRec.plantingWindow')}</span>
                        </div>
                        <p className="text-sm font-bold text-gray-900">{plantingWindow}</p>
                      </div>

                      {/* Agronomic Reasons */}
                      <div>
                        <h4 className="font-bold text-xs text-gray-500 uppercase tracking-wider mb-2">
                          {t('cropRec.whyRecommended')}
                        </h4>
                        <ul className="space-y-1.5 text-xs sm:text-sm text-gray-700">
                          {reasons.map((r: string, idx: number) => (
                            <li key={idx} className="flex items-start space-x-2">
                              <CheckCircle2 className="w-4 h-4 text-forest shrink-0 mt-0.5" />
                              <span>{r}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Precautions */}
                      <div>
                        <h4 className="font-bold text-xs text-gray-500 uppercase tracking-wider mb-2">
                          {t('cropRec.prePlantingConditions')}
                        </h4>
                        <div className="space-y-1.5 text-xs sm:text-sm text-gray-700 bg-gray-50 p-4 rounded-2xl border border-gray-100">
                          {precautions.map((p: string, idx: number) => (
                            <div key={idx} className="flex items-start space-x-2">
                              <ShieldCheck className="w-4 h-4 text-leaf shrink-0 mt-0.5" />
                              <span>{p}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Warnings if any */}
                      {warnings && warnings.length > 0 && (
                        <div className="p-3.5 rounded-2xl bg-amber-50 border border-amber-200 text-amber-900 text-xs">
                          <div className="flex items-center space-x-1.5 font-bold mb-1">
                            <AlertTriangle className="w-4 h-4 text-amber-600" />
                            <span>{t('cropRec.warnings')}</span>
                          </div>
                          <ul className="list-disc list-inside space-y-1">
                            {warnings.map((w: string, idx: number) => (
                              <li key={idx}>{w}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                    </div>

                  </div>
                );
              })()}

              {/* Alternative Supported Crops List */}
              <div className="bg-white rounded-3xl p-6 sm:p-7 border border-cream-dark shadow-sm">
                <h3 className="font-bold text-base text-gray-900 mb-4">
                  {t('cropRec.otherOptions')}
                </h3>
                
                <div className="space-y-3">
                  {recommendationResult.all_recommendations.slice(1).map((alt: any) => {
                    const isKn = language === 'kn';
                    return (
                      <div
                        key={alt.crop}
                        className="p-4 rounded-2xl border border-gray-100 hover:border-forest/20 hover:bg-cream/40 transition-all flex items-center justify-between gap-4"
                      >
                        <div className="flex items-center space-x-3">
                          <img
                            src={alt.image}
                            alt={alt.crop}
                            className="w-12 h-12 rounded-xl object-cover shrink-0"
                          />
                          <div>
                            <h4 className="font-bold text-sm text-gray-900">
                              {isKn ? alt.crop_kn : alt.crop}
                            </h4>
                            <p className="text-[11px] text-gray-500">
                              {isKn ? alt.plantation_window_kn : alt.plantation_window_en}
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center space-x-2 shrink-0">
                          <button
                            type="button"
                            onClick={() => openAddFarmModalWithCrop(alt.crop as SupportedCrop)}
                            className="px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center space-x-1 bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm"
                            title={isKn ? 'ಈ ಬೆಳೆಯನ್ನು ನನ್ನ ಜಮೀನಿನಲ್ಲಿ ಕೃಷಿ ಮಾಡಲು ಪ್ರಾರಂಭಿಸಿ' : 'Start cultivating this crop in My Farm'}
                          >
                            <Tractor className="w-3.5 h-3.5" />
                            <span>{isKn ? 'ಕೃಷಿ ಪ್ರಾರಂಭಿಸಿ' : 'Start Farming'}</span>
                          </button>
                          <button
                            type="button"
                            onClick={() => handleSelectCrop(alt.crop, isKn ? alt.crop_kn : alt.crop)}
                            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center space-x-1 ${
                              selectedCrop === alt.crop
                                ? 'bg-leaf text-white'
                                : 'bg-gray-100 hover:bg-forest hover:text-white text-gray-700'
                            }`}
                          >
                            {selectedCrop === alt.crop ? (
                              <>
                                <CheckCircle2 className="w-3.5 h-3.5" />
                                <span>{isKn ? 'ಆಯ್ಕೆಯಾಗಿದೆ' : 'Selected'}</span>
                              </>
                            ) : (
                              <span>{isKn ? 'ಆಯ್ಕೆಮಾಡಿ' : 'Select'}</span>
                            )}
                          </button>
                          <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-forest/10 text-forest">
                            {alt.suitability_score}%
                          </span>
                          <button
                            onClick={() => handleBookmark(alt)}
                            className="p-1.5 rounded-lg text-gray-400 hover:text-forest hover:bg-white"
                            title="Bookmark"
                          >
                            <Bookmark className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

            </div>
          )}

        </div>

      </div>

    </div>
  );
};
