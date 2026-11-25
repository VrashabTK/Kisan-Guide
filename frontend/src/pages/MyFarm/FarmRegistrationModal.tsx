import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { X, Sprout, Calendar, MapPin, AlertCircle, CheckCircle2, Info, Layers } from 'lucide-react';
import { SupportedCrop, CropStage } from '../../types/farm';
import { api } from '../../services/api';
import { useLanguage } from '../../contexts/LanguageContext';
import { useFarm } from '../../contexts/FarmContext';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  initialCrop?: SupportedCrop | null;
}

const DK_TALUKS = [
  { en: 'Mangaluru', kn: 'ಮಂಗಳೂರು' },
  { en: 'Bantwal', kn: 'ಬಂಟ್ವಾಳ' },
  { en: 'Belthangady', kn: 'ಬೆಳ್ತಂಗಡಿ' },
  { en: 'Puttur', kn: 'ಪುತ್ತೂರು' },
  { en: 'Sullia', kn: 'ಸುಳ್ಯ' },
  { en: 'Moodbidri', kn: 'ಮೂಡುಬಿದಿರೆ' },
  { en: 'Kadaba', kn: 'ಕಡಬ' },
  { en: 'Mulki', kn: 'ಮುಲ್ಕಿ' },
  { en: 'Ullal', kn: 'ಉಳ್ಳಾಲ' },
];

const CROPS: { id: SupportedCrop; en: string; kn: string; emoji: string }[] = [
  { id: 'Rice', en: 'Rice (Paddy)', kn: 'ಭತ್ತ', emoji: '🌾' },
  { id: 'Coconut', en: 'Coconut', kn: 'ತೆಂಗು', emoji: '🌴' },
  { id: 'Arecanut', en: 'Arecanut', kn: 'ಅಡಿಕೆ', emoji: '🌿' },
  { id: 'Cocoa', en: 'Cocoa', kn: 'ಕೋಕೋ', emoji: '🍫' },
];

export const FarmRegistrationModal: React.FC<Props> = ({ isOpen, onClose, initialCrop }) => {
  const { t } = useTranslation();
  const { language } = useLanguage();
  const { refreshFarms, setSelectedFarmId } = useFarm();

  const [farmName, setFarmName] = useState('');
  const [selectedCrop, setSelectedCrop] = useState<SupportedCrop>(initialCrop || 'Rice');
  const [taluk, setTaluk] = useState('Bantwal');
  const [area, setArea] = useState('2.0');
  const [areaUnit, setAreaUnit] = useState('acre');
  const [waterAvailability, setWaterAvailability] = useState('Moderate');

  // Late join options: 'startDate' vs 'manualDay'
  const [joinOption, setJoinOption] = useState<'startDate' | 'manualDay'>('manualDay');
  const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0]);
  const [farmingDay, setFarmingDay] = useState(15); // Default to day 15 for convenient late registration

  // Stages
  const [stages, setStages] = useState<CropStage[]>([]);
  const [selectedStage, setSelectedStage] = useState('');
  const [stageWarning, setStageWarning] = useState<string | null>(null);

  // Optional crop details
  const [variety, setVariety] = useState('');
  const [cultivationMethod, setCultivationMethod] = useState('');
  const [soilType, setSoilType] = useState('Laterite');
  const [notes, setNotes] = useState('');

  // Mandatory confirmation
  const [confirmedStarted, setConfirmedStarted] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Load stages when crop changes
  useEffect(() => {
    if (initialCrop) {
      setSelectedCrop(initialCrop);
    }
  }, [initialCrop]);

  useEffect(() => {
    let isMounted = true;
    api.getCropStages(selectedCrop)
      .then((res) => {
        if (isMounted && res.stages && res.stages.length > 0) {
          setStages(res.stages);
          setSelectedStage(res.stages[0].name_en);
        }
      })
      .catch((err) => console.error('Failed to load crop stages:', err));
    return () => { isMounted = false; };
  }, [selectedCrop]);

  // Compute calculated day if user picks start date
  useEffect(() => {
    if (joinOption === 'startDate' && startDate) {
      try {
        const s = new Date(startDate);
        const now = new Date();
        const diffDays = Math.max(1, Math.floor((now.getTime() - s.getTime()) / (1000 * 60 * 60 * 24)) + 1);
        setFarmingDay(diffDays);
      } catch (_) {}
    }
  }, [joinOption, startDate]);

  // Check stage consistency gently
  useEffect(() => {
    if (!stages.length || !selectedStage) {
      setStageWarning(null);
      return;
    }
    const current = stages.find((s) => s.name_en === selectedStage);
    if (!current) return;

    if (farmingDay < current.start_day - 10 || farmingDay > current.end_day + 15) {
      const typical = stages.find((s) => s.start_day <= farmingDay && s.end_day >= farmingDay) || stages[0];
      setStageWarning(
        language === 'kn'
          ? `ಸೂಚನೆ: ಬೆಳೆ ದಿನ ${farmingDay} ಸಾಮಾನ್ಯವಾಗಿ '${typical.name_kn}' ಹಂತದಲ್ಲಿರುತ್ತದೆ. ಆದರೆ ನಿಮ್ಮ ಹೊಲದ ವಾಸ್ತವ ಅವಲೋಕನಕ್ಕೆ ನಾವು ಆದ್ಯತೆ ನೀಡುತ್ತೇವೆ.`
          : `Note: Day ${farmingDay} is usually in the '${typical.name_en}' stage for ${selectedCrop}. If this represents your field observation, you can proceed.`
      );
    } else {
      setStageWarning(null);
    }
  }, [farmingDay, selectedStage, stages, selectedCrop, language]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!confirmedStarted) {
      setErrorMsg(
        language === 'kn'
          ? 'ದಯವಿಟ್ಟು ಕೃಷಿ ಪ್ರಾರಂಭವಾಗಿದೆ ಎಂದು ದೃಢೀಕರಿಸಿ.'
          : 'Please confirm that cultivation is actively ongoing or has started.'
      );
      return;
    }

    const numArea = parseFloat(area);
    if (isNaN(numArea) || numArea <= 0) {
      setErrorMsg(language === 'kn' ? 'ದಯವಿಟ್ಟು ಮಾನ್ಯವಾದ ವಿಸ್ತೀರ್ಣ ನಮೂದಿಸಿ.' : 'Please enter a valid farm area.');
      return;
    }

    setIsSubmitting(true);
    setErrorMsg(null);

    try {
      const payload: any = {
        name: farmName.trim() || `${selectedCrop} Farm (${taluk})`,
        crop: selectedCrop,
        taluk,
        area: numArea,
        area_unit: areaUnit,
        initial_farming_day: farmingDay,
        current_stage: selectedStage,
        water_availability: waterAvailability,
        variety: variety.trim() || undefined,
        cultivation_method: cultivationMethod.trim() || undefined,
        soil_type: soilType || undefined,
        notes: notes.trim() || undefined,
      };

      if (joinOption === 'startDate') {
        payload.cultivation_start_date = startDate;
      }

      const res = await api.createFarm(payload);
      await refreshFarms();
      if (res && res.id) {
        setSelectedFarmId(res.id);
      }
      onClose();
    } catch (err: any) {
      console.error('Farm creation error:', err);
      setErrorMsg(err.message || 'Failed to register farm. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black bg-opacity-50 flex items-center justify-center p-4 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-emerald-100">
        {/* Header */}
        <div className="bg-gradient-to-r from-emerald-700 via-emerald-600 to-green-700 text-white p-6 rounded-t-2xl relative">
          <button
            onClick={onClose}
            className="absolute top-5 right-5 text-white/80 hover:text-white bg-white/10 hover:bg-white/20 p-2 rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
          <div className="flex items-center space-x-3">
            <div className="bg-white/20 p-2.5 rounded-xl backdrop-blur-md">
              <Sprout className="w-6 h-6 text-emerald-100" />
            </div>
            <div>
              <h2 className="text-xl font-bold">
                {language === 'kn' ? 'ನನ್ನ ಜಮೀನು ಸೇರಿಸಿ / ಕೃಷಿ ಪ್ರಾರಂಭಿಸಿ' : 'Start Farming / Add New Farm'}
              </h2>
              <p className="text-xs text-emerald-100 mt-0.5">
                {language === 'kn'
                  ? 'ದಕ್ಷಿಣ ಕನ್ನಡ ಜಿಲ್ಲೆಯ ಬೆಳೆಗಳ ವೈಯಕ್ತಿಕ ಕೃಷಿ ನಿರ್ವಹಣೆ ಮತ್ತು ದೈನಂದಿನ ಮಾರ್ಗದರ್ಶನ'
                  : 'Personalized farm management & stage-based daily task tracking for Dakshina Kannada'}
              </p>
            </div>
          </div>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6 text-gray-800">
          {errorMsg && (
            <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm flex items-start space-x-2">
              <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* 1. Crop Selection (Strictly 4 DK Crops) */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              {language === 'kn' ? 'ಬೆಳೆ ಆಯ್ಕೆಮಾಡಿ (ಕೇವಲ 4 ಬೆಳೆಗಳು)' : 'Select Crop (DK Focused)'} *
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {CROPS.map((c) => (
                <button
                  key={c.id}
                  type="button"
                  onClick={() => setSelectedCrop(c.id)}
                  className={`p-3 rounded-xl border text-center transition-all ${
                    selectedCrop === c.id
                      ? 'border-emerald-600 bg-emerald-50 text-emerald-800 font-bold shadow-sm ring-2 ring-emerald-500/20'
                      : 'border-gray-200 hover:border-gray-300 bg-white text-gray-700'
                  }`}
                >
                  <span className="text-2xl block mb-1">{c.emoji}</span>
                  <span className="text-xs font-semibold block">{language === 'kn' ? c.kn : c.en}</span>
                </button>
              ))}
            </div>
          </div>

          {/* 2. Taluk and Area */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                {language === 'kn' ? 'ದಕ್ಷಿಣ ಕನ್ನಡ ತಾಲೂಕು' : 'Dakshina Kannada Taluk'} *
              </label>
              <div className="relative">
                <MapPin className="w-4 h-4 text-gray-400 absolute left-3 top-3.5" />
                <select
                  value={taluk}
                  onChange={(e) => setTaluk(e.target.value)}
                  className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-gray-300 focus:ring-2 focus:ring-emerald-500 text-sm bg-white"
                >
                  {DK_TALUKS.map((t) => (
                    <option key={t.en} value={t.en}>
                      {language === 'kn' ? t.kn : t.en}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                {language === 'kn' ? 'ಜಮೀನಿನ ಹೆಸರು (ಐಚ್ಛಿಕ)' : 'Farm Name (Optional)'}
              </label>
              <input
                type="text"
                placeholder={language === 'kn' ? 'ಉದಾ: ನದಿಬದಿಯ ಗದ್ದೆ' : 'e.g., Riverview Paddy Plot'}
                value={farmName}
                onChange={(e) => setFarmName(e.target.value)}
                className="w-full px-3 py-2.5 rounded-xl border border-gray-300 focus:ring-2 focus:ring-emerald-500 text-sm"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                {language === 'kn' ? 'ವಿಸ್ತೀರ್ಣ' : 'Farm Area'} *
              </label>
              <input
                type="number"
                step="0.1"
                min="0.1"
                required
                value={area}
                onChange={(e) => setArea(e.target.value)}
                className="w-full px-3 py-2.5 rounded-xl border border-gray-300 focus:ring-2 focus:ring-emerald-500 text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                {language === 'kn' ? 'ಪ್ರಮಾಣ' : 'Area Unit'}
              </label>
              <select
                value={areaUnit}
                onChange={(e) => setAreaUnit(e.target.value)}
                className="w-full px-3 py-2.5 rounded-xl border border-gray-300 focus:ring-2 focus:ring-emerald-500 text-sm bg-white"
              >
                <option value="acre">{language === 'kn' ? 'ಎಕರೆ (Acre)' : 'Acre'}</option>
                <option value="hectare">{language === 'kn' ? 'ಹೆಕ್ಟೇರ್ (Hectare)' : 'Hectare'}</option>
                <option value="guntha">{language === 'kn' ? 'ಗುಂಟೆ (Guntha)' : 'Guntha'}</option>
                <option value="cent">{language === 'kn' ? 'ಸೆಂಟ್ (Cent)' : 'Cent'}</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                {language === 'kn' ? 'ನೀರಿನ ಲಭ್ಯತೆ' : 'Water Availability'}
              </label>
              <select
                value={waterAvailability}
                onChange={(e) => setWaterAvailability(e.target.value)}
                className="w-full px-3 py-2.5 rounded-xl border border-gray-300 focus:ring-2 focus:ring-emerald-500 text-sm bg-white"
              >
                <option value="High">{language === 'kn' ? 'ಉತ್ತಮ (High)' : 'High (Borewell/River)'}</option>
                <option value="Moderate">{language === 'kn' ? 'ಸಾಧಾರಣ (Moderate)' : 'Moderate'}</option>
                <option value="Low">{language === 'kn' ? 'ಕಡಿಮೆ (Low / Rainfed)' : 'Low (Rainfed)'}</option>
              </select>
            </div>
          </div>

          {/* 3. LATE REGISTRATION & FARMING TIMELINE SECTION */}
          <div className="p-4 bg-emerald-50/60 rounded-2xl border border-emerald-200/80 space-y-4">
            <div>
              <h3 className="text-sm font-bold text-emerald-900 flex items-center space-x-2">
                <Calendar className="w-4 h-4 text-emerald-600" />
                <span>
                  {language === 'kn' ? 'ಕೃಷಿ ಯಾವಾಗ ಪ್ರಾರಂಭವಾಯಿತು?' : 'When did you start cultivation?'}
                </span>
              </h3>
              <p className="text-xs text-emerald-800/80 mt-1">
                {language === 'kn'
                  ? 'ನೀವು ಈಗಾಗಲೇ ಕೃಷಿ ಆರಂಭಿಸಿದ್ದರೆ ಹಿಂದಿನ ದಿನ ನಮೂದಿಸಬಹುದು. ಅಪ್ಲಿಕೇಶನ್ ನಿಮ್ಮ ಇಂದಿನ ಹಂತಕ್ಕೆ ತಕ್ಕಂತೆ ಚಟುವಟಿಕೆಗಳನ್ನು ನೀಡುತ್ತದೆ.'
                  : 'Joined midway? Enter your current farming day or past start date. The system will guide you from your current stage without resetting to Day 1!'}
              </p>
            </div>

            {/* Toggle Start Date vs Manual Day */}
            <div className="flex bg-white rounded-xl p-1 border border-emerald-200">
              <button
                type="button"
                onClick={() => setJoinOption('manualDay')}
                className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
                  joinOption === 'manualDay'
                    ? 'bg-emerald-600 text-white shadow'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {language === 'kn' ? 'ಪ್ರಸ್ತುತ ಕೃಷಿ ದಿನ ನಮೂದಿಸಿ (ದಿನ 15, 30...)' : 'Enter Current Farming Day (e.g. Day 15)'}
              </button>
              <button
                type="button"
                onClick={() => setJoinOption('startDate')}
                className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
                  joinOption === 'startDate'
                    ? 'bg-emerald-600 text-white shadow'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {language === 'kn' ? 'ಪ್ರಾರಂಭ ದಿನಾಂಕ ಆಯ್ಕೆಮಾಡಿ' : 'Pick Cultivation Start Date'}
              </button>
            </div>

            {joinOption === 'manualDay' ? (
              <div className="space-y-3">
                <div className="flex flex-wrap gap-2">
                  {[1, 5, 10, 15, 20, 30, 45, 60].map((d) => (
                    <button
                      key={d}
                      type="button"
                      onClick={() => setFarmingDay(d)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-medium border ${
                        farmingDay === d
                          ? 'bg-emerald-600 text-white border-emerald-600 shadow-sm'
                          : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'
                      }`}
                    >
                      {language === 'kn' ? `ದಿನ ${d}` : `Day ${d}`}
                    </button>
                  ))}
                </div>

                <div className="flex items-center space-x-3">
                  <span className="text-xs text-gray-600 font-medium">
                    {language === 'kn' ? 'ಅಥವಾ ನೇರವಾಗಿ ನಮೂದಿಸಿ:' : 'Or enter custom day:'}
                  </span>
                  <div className="w-28">
                    <input
                      type="number"
                      min="1"
                      max="40000"
                      value={farmingDay}
                      onChange={(e) => setFarmingDay(Math.max(1, parseInt(e.target.value) || 1))}
                      className="w-full px-3 py-1.5 rounded-lg border border-gray-300 text-xs font-bold text-emerald-800 bg-white"
                    />
                  </div>
                  <span className="text-xs text-emerald-700">
                    {language === 'kn' ? `(ಬೆಳೆ ದಿನ ${farmingDay})` : `(Current Crop Day ${farmingDay})`}
                  </span>
                </div>
              </div>
            ) : (
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  {language === 'kn' ? 'ಕೃಷಿ ಪ್ರಾರಂಭವಾದ ದಿನಾಂಕ' : 'Actual Cultivation Start Date'}
                </label>
                <input
                  type="date"
                  max={new Date().toISOString().split('T')[0]}
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-gray-300 text-sm bg-white"
                />
                <p className="text-xs text-emerald-700 mt-1">
                  {language === 'kn'
                    ? `ಲೆಕ್ಕಾಚಾರ ಮಾಡಿದ ಕೃಷಿ ದಿನ: ದಿನ ${farmingDay}`
                    : `Calculated Current Crop Farming Day: Day ${farmingDay}`}
                </p>
              </div>
            )}
          </div>

          {/* 4. Cultivation Stage Confirmation */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1 flex items-center justify-between">
              <span>{language === 'kn' ? 'ಪ್ರಸ್ತುತ ಬೆಳವಣಿಗೆಯ ಹಂತ ದೃಢೀಕರಿಸಿ' : 'Confirm Current Cultivation Stage'} *</span>
              <span className="text-xs text-emerald-600 font-normal">
                {language === 'kn' ? 'ನಿಮ್ಮ ಹೊಲದಲ್ಲಿ ಕಂಡುಬಂದ ಹಂತ' : 'As observed in your field'}
              </span>
            </label>

            <select
              value={selectedStage}
              onChange={(e) => setSelectedStage(e.target.value)}
              className="w-full px-3 py-2.5 rounded-xl border border-gray-300 focus:ring-2 focus:ring-emerald-500 text-sm bg-white"
            >
              {stages.map((st) => (
                <option key={st.id} value={st.name_en}>
                  {language === 'kn' ? `${st.name_kn} (${st.name_en})` : `${st.name_en} (${st.name_kn})`}
                </option>
              ))}
            </select>

            {stageWarning && (
              <div className="mt-2 p-3 bg-amber-50 border border-amber-200 text-amber-800 rounded-xl text-xs flex items-start space-x-2 animate-fade-in">
                <Info className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                <span>{stageWarning}</span>
              </div>
            )}
          </div>

          {/* 5. Optional Crop Specifics */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                {language === 'kn' ? 'ತಳಿ (ಐಚ್ಛಿಕ)' : 'Crop Variety (Optional)'}
              </label>
              <input
                type="text"
                placeholder={
                  selectedCrop === 'Rice'
                    ? 'e.g. MO4, Jaya, Jyothi'
                    : selectedCrop === 'Arecanut'
                    ? 'e.g. Mangala, Sumangala, Mohitnagar'
                    : selectedCrop === 'Coconut'
                    ? 'e.g. West Coast Tall, COD'
                    : 'e.g. Criollo, Forastero'
                }
                value={variety}
                onChange={(e) => setVariety(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-gray-300 text-xs"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                {language === 'kn' ? 'ಕೃಷಿ ಪದ್ಧತಿ (ಐಚ್ಛಿಕ)' : 'Cultivation Method (Optional)'}
              </label>
              <input
                type="text"
                placeholder={
                  selectedCrop === 'Rice'
                    ? 'e.g. Transplanting, SRI'
                    : selectedCrop === 'Cocoa'
                    ? 'e.g. Intercropped under Arecanut'
                    : 'e.g. Basin mulching'
                }
                value={cultivationMethod}
                onChange={(e) => setCultivationMethod(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-gray-300 text-xs"
              />
            </div>
          </div>

          {/* 6. Explicit Confirmation Checkbox */}
          <div className="pt-2">
            <label className="flex items-start space-x-3 cursor-pointer p-3 bg-gray-50 rounded-xl border border-gray-200">
              <input
                type="checkbox"
                checked={confirmedStarted}
                onChange={(e) => setConfirmedStarted(e.target.checked)}
                className="w-4 h-4 text-emerald-600 rounded border-gray-300 focus:ring-emerald-500 mt-0.5"
              />
              <span className="text-xs text-gray-700 font-medium">
                {language === 'kn'
                  ? 'ನಾನು ಈ ಜಮೀನಿನಲ್ಲಿ ಕೃಷಿಯನ್ನು ಸಕ್ರಿಯವಾಗಿ ಪ್ರಾರಂಭಿಸಿದ್ದೇನೆ ಎಂದು ದೃಢೀಕರಿಸುತ್ತೇನೆ.'
                  : 'I explicitly confirm that cultivation is actively ongoing or has started on this farm.'}
              </span>
            </label>
          </div>

          {/* Submit and Cancel Buttons */}
          <div className="flex items-center justify-end space-x-3 pt-3 border-t border-gray-100">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-5 py-2.5 rounded-xl border border-gray-300 text-gray-700 font-medium text-sm hover:bg-gray-50 transition-colors"
            >
              {language === 'kn' ? 'ರದ್ದುಮಾಡಿ' : 'Cancel'}
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !confirmedStarted}
              className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {isSubmitting ? (
                <span>{language === 'kn' ? 'ನೋಂದಾಯಿಸಲಾಗುತ್ತಿದೆ...' : 'Registering...'}</span>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  <span>
                    {language === 'kn'
                      ? 'ಕೃಷಿ ಪ್ರಾರಂಭಿಸಿ / ಜಮೀನು ಉಳಿಸಿ'
                      : 'Start Farming / Save Farm'}
                  </span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
