import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Sprout,
  Plus,
  Calendar,
  Clock,
  CheckCircle2,
  AlertTriangle,
  MapPin,
  ChevronRight,
  Edit3,
  CalendarDays,
  FileText,
  Package,
  Layers,
  CloudRain,
  Thermometer,
  Wind,
  Info,
  Check,
  RotateCcw,
  Trash2,
  ExternalLink,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { useFarm } from '../../contexts/FarmContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { api } from '../../services/api';
import { FarmActivity, FarmObservation, FarmHarvest } from '../../types/farm';
import { FarmRegistrationModal } from './FarmRegistrationModal';

const SKIP_REASONS = [
  { en: 'Heavy rainfall occurred', kn: 'ಭಾರಿ ಮಳೆಯಾಗಿದೆ' },
  { en: 'Lack of water / dry soil', kn: 'ನೀರಿನ ಕೊರತೆ / ಒಣ ಮಣ್ಣು' },
  { en: 'Labour unavailable', kn: 'ಆಳುಗಳು / ಕಾರ್ಮಿಕರು ಸಿಗಲಿಲ್ಲ' },
  { en: 'Equipment / machinery unavailable', kn: 'ಯಂತ್ರೋಪಕರಣಗಳು ಲಭ್ಯವಿಲ್ಲ' },
  { en: 'Activity not required today', kn: 'ಇಂದು ಈ ಕೆಲಸದ ಅಗತ್ಯವಿಲ್ಲ' },
  { en: 'Other agricultural reason', kn: 'ಇತರ ಕೃಷಿ ಕಾರಣ' },
];

export const MyFarmPage: React.FC = () => {
  const { t } = useTranslation();
  const { language } = useLanguage();
  const {
    farms,
    selectedFarm,
    selectedFarmId,
    setSelectedFarmId,
    isLoading,
    refreshFarms,
    todayActivities,
    markDone,
    markSkipped,
    addFarmModalOpen,
    setAddFarmModalOpen,
    openAddFarmModalWithCrop,
  } = useFarm();

  // Active view tab
  const [activeTab, setActiveTab] = useState<'today' | 'history' | 'observations' | 'harvest'>('today');

  // Skip modal state
  const [skipModalOpen, setSkipModalOpen] = useState(false);
  const [selectedActivityForSkip, setSelectedActivityForSkip] = useState<FarmActivity | null>(null);
  const [selectedSkipReason, setSelectedSkipReason] = useState(SKIP_REASONS[0].en);
  const [customSkipReason, setCustomSkipReason] = useState('');

  // Progress correction modal state
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editCropDay, setEditCropDay] = useState(1);
  const [editStage, setEditStage] = useState('');
  const [editReason, setEditReason] = useState('');
  const [isUpdatingProgress, setIsUpdatingProgress] = useState(false);

  // History Tab state
  const [historyDate, setHistoryDate] = useState(new Date().toISOString().split('T')[0]);
  const [historyResult, setHistoryResult] = useState<any>(null);
  const [loadingHistory, setLoadingHistory] = useState(false);

  // Observations Tab state
  const [observations, setObservations] = useState<FarmObservation[]>([]);
  const [obsFieldCondition, setObsFieldCondition] = useState('');
  const [obsMoisture, setObsMoisture] = useState('Adequate');
  const [obsPestSymptoms, setObsPestSymptoms] = useState('');
  const [obsNotes, setObsNotes] = useState('');
  const [isSavingObs, setIsSavingObs] = useState(false);

  // Harvest Tab state
  const [harvests, setHarvests] = useState<FarmHarvest[]>([]);
  const [harvDate, setHarvDate] = useState(new Date().toISOString().split('T')[0]);
  const [harvQuantity, setHarvQuantity] = useState('100');
  const [harvGrade, setHarvGrade] = useState('Grade A');
  const [harvStorage, setHarvStorage] = useState('Ventilated room in Jute bags');
  const [harvNotes, setHarvNotes] = useState('');
  const [isSavingHarv, setIsSavingHarv] = useState(false);

  // Sync edit modal defaults when selected farm changes
  useEffect(() => {
    if (selectedFarm) {
      setEditCropDay(selectedFarm.current_crop_day || 1);
      setEditStage(selectedFarm.current_stage || '');
    }
  }, [selectedFarm]);

  // Load observations and harvests when active tab changes
  useEffect(() => {
    if (!selectedFarm) return;
    if (activeTab === 'observations') {
      api.getFarmObservations(selectedFarm.id)
        .then((res) => { if (Array.isArray(res)) setObservations(res); })
        .catch((e) => console.error(e));
    } else if (activeTab === 'harvest') {
      api.getFarmHarvests(selectedFarm.id)
        .then((res) => { if (Array.isArray(res)) setHarvests(res); })
        .catch((e) => console.error(e));
    }
  }, [activeTab, selectedFarm?.id]);

  // Load history when date changes
  useEffect(() => {
    if (!selectedFarm || activeTab !== 'history') return;
    setLoadingHistory(true);
    api.getActivitiesHistory(selectedFarm.id, historyDate)
      .then((res) => {
        setHistoryResult(res);
      })
      .catch((e) => console.error(e))
      .finally(() => setLoadingHistory(false));
  }, [historyDate, activeTab, selectedFarm?.id]);

  const handleSkipConfirm = async () => {
    if (!selectedActivityForSkip) return;
    const finalReason = customSkipReason.trim() || selectedSkipReason;
    try {
      await markSkipped(selectedActivityForSkip.id, finalReason);
      setSkipModalOpen(false);
      setSelectedActivityForSkip(null);
      setCustomSkipReason('');
    } catch (e) {
      console.error(e);
    }
  };

  const handleProgressCorrection = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFarm) return;
    setIsUpdatingProgress(true);
    try {
      await api.correctFarmProgress(selectedFarm.id, {
        new_crop_day: editCropDay,
        new_stage: editStage || undefined,
        reason: editReason.trim() || 'Manual farmer progress correction',
      });
      await refreshFarms();
      setEditModalOpen(false);
      setEditReason('');
    } catch (e) {
      console.error(e);
    } finally {
      setIsUpdatingProgress(false);
    }
  };

  const handleAddObservation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFarm) return;
    setIsSavingObs(true);
    try {
      const created = await api.createFarmObservation(selectedFarm.id, {
        field_condition: obsFieldCondition.trim() || undefined,
        soil_moisture: obsMoisture,
        pest_symptoms: obsPestSymptoms.trim() || undefined,
        additional_notes: obsNotes.trim() || undefined,
      });
      setObservations((prev) => [created, ...prev]);
      setObsFieldCondition('');
      setObsPestSymptoms('');
      setObsNotes('');
    } catch (e) {
      console.error(e);
    } finally {
      setIsSavingObs(false);
    }
  };

  const handleAddHarvest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFarm) return;
    setIsSavingHarv(true);
    try {
      const created = await api.createFarmHarvest(selectedFarm.id, {
        harvest_date: harvDate,
        quantity_kg: parseFloat(harvQuantity) || 0,
        quality_grade: harvGrade,
        storage_method: harvStorage,
        notes: harvNotes.trim() || undefined,
      });
      setHarvests((prev) => [created, ...prev]);
      setHarvNotes('');
    } catch (e) {
      console.error(e);
    } finally {
      setIsSavingHarv(false);
    }
  };

  const handleDeleteFarm = async (farmId: string) => {
    const msg = language === 'kn'
      ? 'ಈ ಜಮೀನನ್ನು ಅಳಿಸಲು ನೀವು ಖಚಿತವಾಗಿ ಬಯಸುವಿರಾ?'
      : 'Are you sure you want to remove this farm?';
    if (!window.confirm(msg)) return;
    try {
      await api.deleteFarm(farmId);
      await refreshFarms();
    } catch (e) {
      console.error(e);
    }
  };

  // If farmer has no farms yet, display welcoming empty state
  if (!isLoading && farms.length === 0) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-12 animate-fade-in">
        <div className="bg-white rounded-3xl p-8 sm:p-12 text-center shadow-xl border border-emerald-100 max-w-2xl mx-auto">
          <div className="w-20 h-20 bg-emerald-100 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-inner">
            <Sprout className="w-10 h-10 text-emerald-600" />
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 mb-3">
            {language === 'kn' ? 'ನನ್ನ ಜಮೀನು ನಿರ್ವಹಣೆಗೆ ಸ್ವಾಗತ' : 'Welcome to My Farm'}
          </h1>
          <p className="text-gray-600 text-sm sm:text-base leading-relaxed mb-8">
            {language === 'kn'
              ? 'ದಕ್ಷಿಣ ಕನ್ನಡದ ರೈತರಿಗಾಗಿ ವಿನ್ಯಾಸಗೊಳಿಸಲಾದ ನಿಮ್ಮ ವೈಯಕ್ತಿಕ ಕೃಷಿ ನಿರ್ವಹಣಾ ವ್ಯವಸ್ಥೆ. ನೀವು ಕೃಷಿಯನ್ನು ಇಂದು ಪ್ರಾರಂಭಿಸಿರಲಿ ಅಥವಾ 15 ದಿನಗಳ ಹಿಂದೆಯೇ ಆರಂಭಿಸಿರಲಿ, KISSAN GUIDE ನಿಮ್ಮ ನೈಜ ಬೆಳವಣಿಗೆಯ ಹಂತಕ್ಕೆ ತಕ್ಕಂತೆ ದೈನಂದಿನ ಕೆಲಸಗಳನ್ನು ಮಾರ್ಗದರ್ಶನ ಮಾಡುತ್ತದೆ.'
              : 'Your personal digital farm manager for Dakshina Kannada. Whether you started farming today or 15 days ago, KISSAN GUIDE tracks your real cultivation stage, adapts to local weather, and guides your daily agricultural activities until harvest.'}
          </p>

          <button
            onClick={() => openAddFarmModalWithCrop()}
            className="inline-flex items-center space-x-3 px-8 py-4 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-2xl shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-0.5 text-base"
          >
            <Plus className="w-5 h-5" />
            <span>{language === 'kn' ? 'ಕೃಷಿ ಪ್ರಾರಂಭಿಸಿ / ಮೊದಲ ಜಮೀನು ಸೇರಿಸಿ' : 'Start Farming / Add Your Farm'}</span>
          </button>

          <div className="mt-8 pt-8 border-t border-gray-100 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs text-gray-500 font-medium">
            <div className="p-3 bg-gray-50 rounded-xl">🌾 {language === 'kn' ? 'ಭತ್ತ (Rice)' : 'Rice (Paddy)'}</div>
            <div className="p-3 bg-gray-50 rounded-xl">🌴 {language === 'kn' ? 'ತೆಂಗು (Coconut)' : 'Coconut Palm'}</div>
            <div className="p-3 bg-gray-50 rounded-xl">🌿 {language === 'kn' ? 'ಅಡಿಕೆ (Arecanut)' : 'Arecanut Garden'}</div>
            <div className="p-3 bg-gray-50 rounded-xl">🍫 {language === 'kn' ? 'ಕೋಕೋ (Cocoa)' : 'Cocoa Intercrop'}</div>
          </div>
        </div>

        <FarmRegistrationModal
          isOpen={addFarmModalOpen}
          onClose={() => setAddFarmModalOpen(false)}
        />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8 animate-fade-in text-gray-900">
      {/* 1. Multi-Farm Selector & Actions Bar */}
      <div className="bg-white p-4 sm:p-6 rounded-3xl shadow-sm border border-emerald-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center space-x-3 overflow-x-auto pb-2 md:pb-0 scrollbar-none">
          <div className="flex items-center space-x-1.5 shrink-0 pr-2 border-r border-gray-200">
            <Sprout className="w-5 h-5 text-emerald-600" />
            <span className="text-xs font-bold uppercase tracking-wider text-gray-500">
              {language === 'kn' ? 'ನನ್ನ ಜಮೀನುಗಳು' : 'My Farms'}:
            </span>
          </div>

          {farms.map((farm) => {
            const isSel = farm.id === selectedFarm?.id;
            return (
              <button
                key={farm.id}
                onClick={() => setSelectedFarmId(farm.id)}
                className={`px-4 py-2 rounded-2xl text-xs font-bold shrink-0 transition-all flex items-center space-x-2 ${
                  isSel
                    ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/20'
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                }`}
              >
                <span>
                  {farm.crop === 'Rice' ? '🌾' : farm.crop === 'Coconut' ? '🌴' : farm.crop === 'Arecanut' ? '🌿' : '🍫'}
                </span>
                <span>{farm.name || `${farm.crop} (${farm.taluk})`}</span>
                <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${isSel ? 'bg-white/20 text-white' : 'bg-gray-200 text-gray-600'}`}>
                  {language === 'kn' ? `ದಿನ ${farm.current_crop_day}` : `Day ${farm.current_crop_day}`}
                </span>
              </button>
            );
          })}
        </div>

        <div className="flex items-center space-x-3 shrink-0">
          <button
            onClick={() => openAddFarmModalWithCrop()}
            className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-emerald-50 hover:bg-emerald-100 text-emerald-700 font-bold text-xs transition-colors border border-emerald-200 shadow-sm"
          >
            <Plus className="w-4 h-4" />
            <span>{language === 'kn' ? 'ಹೊಸ ಜಮೀನು ಸೇರಿಸಿ' : '+ Add New Farm'}</span>
          </button>
        </div>
      </div>

      {selectedFarm && (
        <>
          {/* 2. Main Farm Hero & Dual Timelines Card */}
          <div className="bg-gradient-to-br from-emerald-800 via-emerald-700 to-green-800 rounded-3xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden">
            {/* Background pattern */}
            <div className="absolute right-0 top-0 bottom-0 opacity-10 pointer-events-none transform translate-x-12 translate-y-6 text-9xl">
              {selectedFarm.crop === 'Rice' ? '🌾' : selectedFarm.crop === 'Coconut' ? '🌴' : selectedFarm.crop === 'Arecanut' ? '🌿' : '🍫'}
            </div>

            <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
              <div>
                <div className="flex flex-wrap items-center gap-2 mb-2">
                  <span className="bg-white/20 backdrop-blur-md px-3 py-1 rounded-full text-xs font-bold text-emerald-100 flex items-center space-x-1">
                    <MapPin className="w-3.5 h-3.5" />
                    <span>{selectedFarm.taluk}, Dakshina Kannada</span>
                  </span>
                  <span className="bg-white/20 backdrop-blur-md px-3 py-1 rounded-full text-xs font-bold text-emerald-100">
                    {selectedFarm.area} {selectedFarm.area_unit || 'acre'}
                  </span>
                  {selectedFarm.variety && (
                    <span className="bg-white/20 backdrop-blur-md px-3 py-1 rounded-full text-xs font-medium text-emerald-100">
                      {language === 'kn' ? 'ತಳಿ: ' : 'Variety: '}{selectedFarm.variety}
                    </span>
                  )}
                </div>

                <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight">
                  {selectedFarm.name || `${selectedFarm.crop} Farm`}
                </h1>

                <div className="mt-3 flex items-center space-x-2 text-emerald-100 text-sm">
                  <Layers className="w-4 h-4 text-emerald-300" />
                  <span className="font-medium">
                    {language === 'kn' ? 'ಪ್ರಸ್ತುತ ಹಂತ: ' : 'Cultivation Stage: '}
                    <strong className="text-white underline decoration-emerald-400 font-bold">
                      {selectedFarm.current_stage}
                    </strong>
                  </span>
                </div>
              </div>

              {/* DUAL TIMELINE HIGHLIGHT BOX */}
              <div className="flex items-center gap-4 bg-black/20 backdrop-blur-md p-4 sm:p-5 rounded-2xl border border-white/10 shrink-0">
                {/* 1. Actual Crop Farming Timeline */}
                <div className="text-center px-4 border-r border-white/20">
                  <span className="text-[11px] uppercase tracking-wider font-semibold text-emerald-200 block">
                    {language === 'kn' ? 'ನಿಜವಾದ ಬೆಳೆ ದಿನ' : 'Actual Crop Day'}
                  </span>
                  <span className="text-3xl sm:text-4xl font-extrabold text-white block mt-0.5">
                    {language === 'kn' ? `ದಿನ ${selectedFarm.current_crop_day}` : `Day ${selectedFarm.current_crop_day}`}
                  </span>
                  <span className="text-[10px] text-emerald-300 block mt-0.5">
                    {language === 'kn' ? 'ಕೃಷಿ ಪ್ರಾರಂಭವಾದಾಗಿನಿಂದ' : 'From start of farming'}
                  </span>
                </div>

                {/* 2. App Monitoring Timeline */}
                <div className="text-center px-4">
                  <span className="text-[11px] uppercase tracking-wider font-semibold text-emerald-200 block">
                    {language === 'kn' ? 'ಕಿಸಾನ್ ಗೈಡ್ ದಿನ' : 'Monitoring Day'}
                  </span>
                  <span className="text-3xl sm:text-4xl font-extrabold text-emerald-300 block mt-0.5">
                    {language === 'kn' ? `ದಿನ ${selectedFarm.current_monitoring_day}` : `Day ${selectedFarm.current_monitoring_day}`}
                  </span>
                  <span className="text-[10px] text-emerald-300 block mt-0.5">
                    {language === 'kn' ? 'ಅಪ್ಲಿಕೇಶನ್ ಮೇಲ್ವಿಚಾರಣೆ' : 'App monitoring tracked'}
                  </span>
                </div>

                <button
                  onClick={() => setEditModalOpen(true)}
                  title={language === 'kn' ? 'ದಿನ ಅಥವಾ ಹಂತ ತಿದ್ದುಪಡಿ ಮಾಡಿ' : 'Edit farming day or stage'}
                  className="p-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white transition-colors"
                >
                  <Edit3 className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Quick summary footer */}
            <div className="mt-6 pt-4 border-t border-white/10 flex flex-wrap items-center justify-between gap-4 text-xs text-emerald-100">
              <div className="flex items-center space-x-4">
                <span>
                  {language === 'kn' ? 'ಇಂದಿನ ಉಳಿದ ಕೆಲಸಗಳು: ' : "Today's Pending Tasks: "}
                  <strong className="text-white font-bold">{selectedFarm.today_pending_count || 0}</strong>
                </span>
                <span>•</span>
                <span>
                  {language === 'kn' ? 'ಪೂರ್ಣಗೊಂಡಿದೆ: ' : 'Completed: '}
                  <strong className="text-white font-bold">{selectedFarm.today_completed_count || 0}</strong>
                </span>
              </div>

              {selectedFarm.weather_snapshot?.temperature && (
                <div className="flex items-center space-x-3 bg-white/10 px-3 py-1.5 rounded-xl">
                  <span className="flex items-center space-x-1">
                    <Thermometer className="w-3.5 h-3.5 text-amber-300" />
                    <span>{selectedFarm.weather_snapshot.temperature}°C</span>
                  </span>
                  <span>•</span>
                  <span className="flex items-center space-x-1">
                    <CloudRain className="w-3.5 h-3.5 text-sky-300" />
                    <span>{selectedFarm.weather_snapshot.condition_en}</span>
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* 3. Visual Growth-Stage Timeline */}
          {selectedFarm.stages && selectedFarm.stages.length > 0 && (
            <div className="bg-white p-6 rounded-3xl shadow-sm border border-emerald-100">
              <h3 className="text-sm font-bold text-gray-700 uppercase tracking-wider mb-4 flex items-center space-x-2">
                <Layers className="w-4 h-4 text-emerald-600" />
                <span>{language === 'kn' ? 'ಬೆಳೆ ಜೀವನಚಕ್ರ ಮತ್ತು ಬೆಳವಣಿಗೆಯ ಹಂತಗಳು' : 'Crop Growth Stages & Lifecycle'}</span>
              </h3>

              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                {selectedFarm.stages.map((st, idx) => {
                  const isCurrent = st.name_en === selectedFarm.current_stage;
                  return (
                    <div
                      key={st.id}
                      className={`p-3.5 rounded-2xl border transition-all ${
                        isCurrent
                          ? 'bg-emerald-50 border-emerald-600 ring-2 ring-emerald-500/20 shadow-sm'
                          : 'bg-gray-50/70 border-gray-200'
                      }`}
                    >
                      <div className="flex items-center justify-between text-[11px] text-gray-500 font-semibold mb-1">
                        <span>{language === 'kn' ? `ಹಂತ ${idx + 1}` : `Stage ${idx + 1}`}</span>
                        {isCurrent && (
                          <span className="px-1.5 py-0.5 rounded-full bg-emerald-600 text-white font-bold text-[9px]">
                            {language === 'kn' ? 'ಪ್ರಸ್ತುತ' : 'CURRENT'}
                          </span>
                        )}
                      </div>
                      <h4 className={`text-xs font-bold leading-tight ${isCurrent ? 'text-emerald-900' : 'text-gray-800'}`}>
                        {language === 'kn' ? st.name_kn : st.name_en}
                      </h4>
                      <p className="text-[10px] text-gray-500 mt-1 line-clamp-2">
                        {language === 'kn' ? st.description_kn : st.description_en}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* 4. Main Tab Navigation */}
          <div className="flex border-b border-gray-200 space-x-2 overflow-x-auto scrollbar-none">
            <button
              onClick={() => setActiveTab('today')}
              className={`py-3 px-5 text-sm font-bold border-b-2 transition-all flex items-center space-x-2 shrink-0 ${
                activeTab === 'today'
                  ? 'border-emerald-600 text-emerald-800'
                  : 'border-transparent text-gray-500 hover:text-gray-800'
              }`}
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>{language === 'kn' ? 'ಇಂದಿನ ಕೃಷಿ ಚಟುವಟಿಕೆಗಳು' : "Today's Activities"}</span>
              <span className="ml-1.5 px-2 py-0.5 rounded-full text-xs bg-emerald-100 text-emerald-800">
                {todayActivities.length}
              </span>
            </button>

            <button
              onClick={() => setActiveTab('history')}
              className={`py-3 px-5 text-sm font-bold border-b-2 transition-all flex items-center space-x-2 shrink-0 ${
                activeTab === 'history'
                  ? 'border-emerald-600 text-emerald-800'
                  : 'border-transparent text-gray-500 hover:text-gray-800'
              }`}
            >
              <CalendarDays className="w-4 h-4" />
              <span>{language === 'kn' ? 'ಇತಿಹಾಸ ಮತ್ತು ಕ್ಯಾಲೆಂಡರ್' : 'History & Calendar'}</span>
            </button>

            <button
              onClick={() => setActiveTab('observations')}
              className={`py-3 px-5 text-sm font-bold border-b-2 transition-all flex items-center space-x-2 shrink-0 ${
                activeTab === 'observations'
                  ? 'border-emerald-600 text-emerald-800'
                  : 'border-transparent text-gray-500 hover:text-gray-800'
              }`}
            >
              <FileText className="w-4 h-4" />
              <span>{language === 'kn' ? 'ದೈನಂದಿನ ಅವಲೋಕನಗಳು' : 'Farmer Observations'}</span>
            </button>

            <button
              onClick={() => setActiveTab('harvest')}
              className={`py-3 px-5 text-sm font-bold border-b-2 transition-all flex items-center space-x-2 shrink-0 ${
                activeTab === 'harvest'
                  ? 'border-emerald-600 text-emerald-800'
                  : 'border-transparent text-gray-500 hover:text-gray-800'
              }`}
            >
              <Package className="w-4 h-4" />
              <span>{language === 'kn' ? 'ಕೊಯ್ಲು ಮತ್ತು ಶೇಖರಣೆ' : 'Harvest & Storage Batches'}</span>
            </button>
          </div>

          {/* TAB 1: TODAY'S ACTIVITIES */}
          {activeTab === 'today' && (
            <div className="space-y-4">
              {todayActivities.length === 0 ? (
                <div className="p-10 bg-white rounded-3xl text-center border border-gray-100 text-gray-500">
                  <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
                  <h4 className="text-base font-bold text-gray-800 mb-1">
                    {language === 'kn' ? 'ಇಂದಿನ ಎಲ್ಲ ಕೆಲಸಗಳು ಪೂರ್ಣಗೊಂಡಿವೆ!' : "All today's tasks completed!"}
                  </h4>
                  <p className="text-xs text-gray-500">
                    {language === 'kn'
                      ? 'ನಿಮ್ಮ ಕೃಷಿ ನಿರ್ವಹಣೆ ಹಳಿ ತಪ್ಪದೆ ಮುಂದುವರಿದಿದೆ. ನಾಳೆ ಹೊಸ ಶಿಫಾರಸುಗಳನ್ನು ಪರಿಶೀಲಿಸಿ.'
                      : 'Your cultivation progress is right on track. Check back tomorrow for updated recommendations.'}
                  </p>
                </div>
              ) : (
                todayActivities.map((act) => {
                  const isDone = act.status === 'completed';
                  const isSkipped = act.status === 'skipped';

                  return (
                    <div
                      key={act.id}
                      className={`p-6 rounded-3xl border transition-all ${
                        isDone
                          ? 'bg-emerald-50/60 border-emerald-300 opacity-90'
                          : isSkipped
                          ? 'bg-gray-50 border-gray-200 opacity-75'
                          : 'bg-white border-emerald-100 shadow-sm hover:shadow-md'
                      }`}
                    >
                      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                        <div className="space-y-2 flex-1">
                          {/* Tags */}
                          <div className="flex flex-wrap items-center gap-2">
                            <span
                              className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full ${
                                act.priority === 'high'
                                  ? 'bg-red-100 text-red-800'
                                  : act.priority === 'medium'
                                  ? 'bg-amber-100 text-amber-800'
                                  : 'bg-blue-100 text-blue-800'
                              }`}
                            >
                              {act.priority.toUpperCase()} PRIORITY
                            </span>

                            <span className="text-[10px] font-semibold text-gray-500 bg-gray-100 px-2.5 py-0.5 rounded-full">
                              {language === 'kn' ? `ಬೆಳೆ ದಿನ ${act.crop_day}` : `Crop Day ${act.crop_day}`}
                            </span>

                            {isDone && (
                              <span className="text-[10px] font-bold bg-emerald-600 text-white px-2.5 py-0.5 rounded-full flex items-center space-x-1">
                                <Check className="w-3 h-3" />
                                <span>{language === 'kn' ? 'ಪೂರ್ಣಗೊಂಡಿದೆ' : 'COMPLETED'}</span>
                              </span>
                            )}

                            {isSkipped && (
                              <span className="text-[10px] font-bold bg-gray-500 text-white px-2.5 py-0.5 rounded-full">
                                {language === 'kn' ? 'ಮುಂದೂಡಲಾಗಿದೆ' : 'SKIPPED'}
                              </span>
                            )}
                          </div>

                          {/* Title */}
                          <h3 className={`text-base sm:text-lg font-extrabold ${isDone ? 'line-through text-gray-600' : 'text-gray-900'}`}>
                            {language === 'kn' ? act.title_kn : act.title_en}
                          </h3>

                          {/* Description */}
                          <p className="text-xs sm:text-sm text-gray-600 leading-relaxed">
                            {language === 'kn' ? act.description_kn : act.description_en}
                          </p>

                          {/* Why is this necessary? */}
                          <div className="p-3 bg-amber-50/70 border border-amber-200/80 rounded-2xl text-xs text-amber-900 flex items-start space-x-2">
                            <Info className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                            <div>
                              <strong className="font-bold">
                                {language === 'kn' ? 'ಏಕೆ ಅಗತ್ಯ?: ' : 'Why is this necessary? '}
                              </strong>
                              <span>{language === 'kn' ? act.why_necessary_kn : act.why_necessary_en}</span>
                            </div>
                          </div>

                          {/* Weather influence alert if applicable */}
                          {act.weather_influence_en && act.weather_influence_en !== 'Standard agronomic conditions.' && (
                            <div className="p-3 bg-sky-50 border border-sky-200 text-xs text-sky-900 rounded-2xl flex items-start space-x-2">
                              <CloudRain className="w-4 h-4 text-sky-600 shrink-0 mt-0.5" />
                              <div>
                                <strong className="font-bold">{language === 'kn' ? 'ಹವಾಮಾನ ಸೂಚನೆ: ' : 'Weather Adaptation: '}</strong>
                                <span>{language === 'kn' ? act.weather_influence_kn : act.weather_influence_en}</span>
                              </div>
                            </div>
                          )}

                          {isSkipped && act.skip_reason && (
                            <p className="text-xs text-gray-500 italic">
                              {language === 'kn' ? 'ಕಾರಣ: ' : 'Skip reason: '}{act.skip_reason}
                            </p>
                          )}
                        </div>

                        {/* Action Buttons: Done / Skip */}
                        {!isDone && !isSkipped && (
                          <div className="flex md:flex-col items-center gap-2 shrink-0">
                            <button
                              onClick={() => markDone(act.id)}
                              className="w-full sm:w-auto px-6 py-3 rounded-2xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md hover:shadow-lg transition-all flex items-center justify-center space-x-2"
                            >
                              <CheckCircle2 className="w-4 h-4" />
                              <span>{language === 'kn' ? 'ಪೂರ್ಣಗೊಳಿಸಿ' : 'Mark Done'}</span>
                            </button>

                            <button
                              onClick={() => {
                                setSelectedActivityForSkip(act);
                                setSkipModalOpen(true);
                              }}
                              className="w-full sm:w-auto px-4 py-2 rounded-xl text-gray-500 hover:text-gray-800 hover:bg-gray-100 text-xs font-semibold transition-colors text-center"
                            >
                              {language === 'kn' ? 'ಮುಂದೂಡಿ' : 'Skip / Postpone'}
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          )}

          {/* TAB 2: FARM HISTORY & CALENDAR */}
          {activeTab === 'history' && (
            <div className="bg-white p-6 rounded-3xl border border-emerald-100 shadow-sm space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-gray-100">
                <div>
                  <h3 className="text-base font-bold text-gray-900">
                    {language === 'kn' ? 'ಕೃಷಿ ಇತಿಹಾಸ ಕ್ಯಾಲೆಂಡರ್' : 'Farming History & Calendar'}
                  </h3>
                  <p className="text-xs text-gray-500">
                    {language === 'kn'
                      ? 'ಹಿಂದಿನ ಯಾವುದೇ ದಿನಾಂಕವನ್ನು ಆರಿಸಿ ಆ ದಿನದ ಕೃಷಿ ಕೆಲಸಗಳು ಮತ್ತು ಅವಲೋಕನಗಳನ್ನು ಪರಿಶೀಲಿಸಿ.'
                      : 'Select any past date to inspect recommended activities, completed tasks, and weather notes.'}
                  </p>
                </div>

                <div className="flex items-center space-x-2">
                  <Calendar className="w-4 h-4 text-emerald-600" />
                  <input
                    type="date"
                    max={new Date().toISOString().split('T')[0]}
                    value={historyDate}
                    onChange={(e) => setHistoryDate(e.target.value)}
                    className="px-3 py-2 rounded-xl border border-gray-300 text-xs font-bold text-gray-800"
                  />
                </div>
              </div>

              {loadingHistory ? (
                <div className="py-12 text-center text-gray-500 text-sm">
                  {language === 'kn' ? 'ಇತಿಹಾಸವನ್ನು ಲೋಡ್ ಮಾಡಲಾಗುತ್ತಿದೆ...' : 'Loading history...'}
                </div>
              ) : historyResult?.is_prior_to_monitoring ? (
                /* RESPECTFUL LATE-JOIN HISTORICAL NOTICE */
                <div className="p-8 text-center bg-gray-50 rounded-2xl border border-gray-200 text-gray-600">
                  <Info className="w-10 h-10 text-emerald-600 mx-auto mb-3" />
                  <h4 className="text-sm font-bold text-gray-800 mb-1">
                    {language === 'kn' ? 'ಮೇಲ್ವಿಚಾರಣೆಗೂ ಮುಂಚಿನ ದಿನಾಂಕ' : 'Date Prior to App Monitoring'}
                  </h4>
                  <p className="text-xs max-w-lg mx-auto text-gray-500 leading-relaxed">
                    {language === 'kn'
                      ? `ಈ ದಿನಾಂಕವು ಕಿಸಾನ್ ಗೈಡ್ ಮೇಲ್ವಿಚಾರಣೆ ಪ್ರಾರಂಭವಾಗುವುದಕ್ಕೂ ಮುಂಚಿನದ್ದಾಗಿದೆ (${selectedFarm.monitoring_start_date}). ಆ ಅವಧಿಯಲ್ಲಿ ಅಪ್ಲಿಕೇಶನ್ ದಾಖಲೆಗಳನ್ನು ಸಂಗ್ರಹಿಸಿರಲಿಲ್ಲ.`
                      : `This date is prior to when KISSAN GUIDE monitoring began on this farm (${selectedFarm.monitoring_start_date}). We do not fabricate past activity records before monitoring started.`}
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center space-x-4 text-xs font-semibold text-gray-600 bg-emerald-50/50 p-3 rounded-xl border border-emerald-100">
                    <span>
                      {language === 'kn' ? 'ಬೆಳೆ ದಿನ: ' : 'Crop Day: '}
                      <strong className="text-emerald-800">{historyResult?.crop_day || 'N/A'}</strong>
                    </span>
                    <span>•</span>
                    <span>
                      {language === 'kn' ? 'ಮೇಲ್ವಿಚಾರಣಾ ದಿನ: ' : 'Monitoring Day: '}
                      <strong className="text-emerald-800">{historyResult?.monitoring_day || 'N/A'}</strong>
                    </span>
                  </div>

                  {historyResult?.activities?.length === 0 ? (
                    <p className="text-xs text-gray-500 py-6 text-center">
                      {language === 'kn' ? 'ಈ ದಿನಾಂಕದಲ್ಲಿ ಯಾವುದೇ ದಾಖಲಿತ ಚಟುವಟಿಕೆಗಳಿಲ್ಲ.' : 'No recorded activities for this date.'}
                    </p>
                  ) : (
                    historyResult?.activities?.map((act: FarmActivity) => (
                      <div key={act.id} className="p-4 rounded-2xl border border-gray-200 bg-white space-y-1">
                        <div className="flex items-center justify-between">
                          <h4 className="text-sm font-bold text-gray-800">
                            {language === 'kn' ? act.title_kn : act.title_en}
                          </h4>
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                            act.status === 'completed'
                              ? 'bg-emerald-100 text-emerald-800'
                              : act.status === 'skipped'
                              ? 'bg-gray-100 text-gray-700'
                              : 'bg-blue-100 text-blue-800'
                          }`}>
                            {act.status.toUpperCase()}
                          </span>
                        </div>
                        <p className="text-xs text-gray-600">{language === 'kn' ? act.description_kn : act.description_en}</p>
                        {act.skip_reason && (
                          <p className="text-[11px] text-gray-500 italic mt-1">
                            {language === 'kn' ? 'ಕಾರಣ: ' : 'Reason: '}{act.skip_reason}
                          </p>
                        )}
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          )}

          {/* TAB 3: OBSERVATIONS */}
          {activeTab === 'observations' && (
            <div className="space-y-6">
              {/* Add Observation Form */}
              <form onSubmit={handleAddObservation} className="bg-white p-6 rounded-3xl border border-emerald-100 shadow-sm space-y-4">
                <h3 className="text-sm font-bold text-gray-800 flex items-center space-x-2">
                  <FileText className="w-4 h-4 text-emerald-600" />
                  <span>{language === 'kn' ? 'ಇಂದಿನ ಹೊಲದ ಅವಲೋಕನ ದಾಖಲಿಸಿ' : 'Record Daily Field Observation'}</span>
                </h3>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">
                      {language === 'kn' ? 'ಹೊಲದ ಸ್ಥಿತಿ' : 'Field Condition'}
                    </label>
                    <input
                      type="text"
                      placeholder={language === 'kn' ? 'ಉದಾ: ಕಳೆ ತೆಗೆಯಲಾಗಿದೆ, ಮಣ್ಣು ಹದವಾಗಿದೆ' : 'e.g. Weeded, good soil tilth'}
                      value={obsFieldCondition}
                      onChange={(e) => setObsFieldCondition(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl border border-gray-300 text-xs"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">
                      {language === 'kn' ? 'ಮಣ್ಣಿನ ತೇವಾಂಶ' : 'Soil Moisture'}
                    </label>
                    <select
                      value={obsMoisture}
                      onChange={(e) => setObsMoisture(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl border border-gray-300 text-xs bg-white"
                    >
                      <option value="Wet">{language === 'kn' ? 'ಹೆಚ್ಚು ತೇವ / ನೀರು ನಿಂತಿದೆ' : 'Wet / Saturated'}</option>
                      <option value="Adequate">{language === 'kn' ? 'ಹದವಾದ ತೇವಾಂಶ' : 'Adequate Moisture'}</option>
                      <option value="Dry">{language === 'kn' ? 'ಒಣ ಮಣ್ಣು / ನೀರುಣಿಸಬೇಕು' : 'Dry / Needs Irrigation'}</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    {language === 'kn' ? 'ಕೀಟ ಅಥವಾ ರೋಗದ ಲಕ್ಷಣಗಳು' : 'Pest or Disease Symptoms Observed'}
                  </label>
                  <input
                    type="text"
                    placeholder={language === 'kn' ? 'ಉದಾ: ಕೊಳೆರೋಗದ ಆರಂಭಿಕ ಚುಕ್ಕೆಗಳು, ಹುಳುಗಳ ಹಾವಳಿ' : 'e.g. Minor leaf folding, no fungal spots'}
                    value={obsPestSymptoms}
                    onChange={(e) => setObsPestSymptoms(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl border border-gray-300 text-xs"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    {language === 'kn' ? 'ಹೆಚ್ಚುವರಿ ಟಿಪ್ಪಣಿ' : 'Additional Notes'}
                  </label>
                  <textarea
                    rows={2}
                    placeholder={language === 'kn' ? 'ಉದಾ: ಮುಂಗಾರು ಮಳೆ ಹದವಾಗಿ ಸುರಿದಿದೆ' : 'e.g. Organic compost applied to 20 palms'}
                    value={obsNotes}
                    onChange={(e) => setObsNotes(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl border border-gray-300 text-xs"
                  />
                </div>

                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={isSavingObs}
                    className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition-all disabled:opacity-50"
                  >
                    {isSavingObs ? 'Saving...' : language === 'kn' ? 'ಅವಲೋಕನ ಉಳಿಸಿ' : 'Save Observation'}
                  </button>
                </div>
              </form>

              {/* Past Observations List */}
              <div className="bg-white p-6 rounded-3xl border border-emerald-100 shadow-sm space-y-3">
                <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">
                  {language === 'kn' ? 'ಹಿಂದಿನ ಅವಲೋಕನಗಳು' : 'Observation History'}
                </h4>

                {observations.length === 0 ? (
                  <p className="text-xs text-gray-400 py-4 text-center">
                    {language === 'kn' ? 'ಇನ್ನೂ ಯಾವುದೇ ಅವಲೋಕನ ದಾಖಲಾಗಿಲ್ಲ.' : 'No observations recorded yet.'}
                  </p>
                ) : (
                  observations.map((obs) => (
                    <div key={obs.id} className="p-3.5 rounded-2xl bg-gray-50 border border-gray-100 text-xs space-y-1">
                      <div className="flex items-center justify-between text-gray-500 text-[11px]">
                        <span>{obs.calendar_date} • {language === 'kn' ? `ಬೆಳೆ ದಿನ ${obs.crop_day}` : `Crop Day ${obs.crop_day}`}</span>
                        <span className="font-semibold text-emerald-700">{obs.soil_moisture}</span>
                      </div>
                      {obs.field_condition && (
                        <p className="text-gray-800"><strong>{language === 'kn' ? 'ಸ್ಥಿತಿ: ' : 'Condition: '}</strong>{obs.field_condition}</p>
                      )}
                      {obs.pest_symptoms && (
                        <p className="text-amber-800"><strong>{language === 'kn' ? 'ಕೀಟ/ರೋಗ: ' : 'Pest/Disease: '}</strong>{obs.pest_symptoms}</p>
                      )}
                      {obs.additional_notes && <p className="text-gray-600">{obs.additional_notes}</p>}
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* TAB 4: HARVEST BATCHES */}
          {activeTab === 'harvest' && (
            <div className="space-y-6">
              <form onSubmit={handleAddHarvest} className="bg-white p-6 rounded-3xl border border-emerald-100 shadow-sm space-y-4">
                <h3 className="text-sm font-bold text-gray-800 flex items-center space-x-2">
                  <Package className="w-4 h-4 text-emerald-600" />
                  <span>{language === 'kn' ? 'ಕೊಯ್ಲು ದಾಖಲಿಸಿ' : 'Record Harvest Batch'}</span>
                </h3>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">
                      {language === 'kn' ? 'ಕೊಯ್ಲು ದಿನಾಂಕ' : 'Harvest Date'}
                    </label>
                    <input
                      type="date"
                      value={harvDate}
                      onChange={(e) => setHarvDate(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl border border-gray-300 text-xs"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">
                      {language === 'kn' ? 'ಪ್ರಮಾಣ (ಕೆಜಿ)' : 'Harvest Quantity (kg)'}
                    </label>
                    <input
                      type="number"
                      step="1"
                      min="1"
                      required
                      value={harvQuantity}
                      onChange={(e) => setHarvQuantity(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl border border-gray-300 text-xs"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">
                      {language === 'kn' ? 'ಗುಣಮಟ್ಟದ ಗ್ರೇಡ್' : 'Quality Grade'}
                    </label>
                    <select
                      value={harvGrade}
                      onChange={(e) => setHarvGrade(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl border border-gray-300 text-xs bg-white"
                    >
                      <option value="Grade A">Grade A (Premium / ಮೊದಲ ದರ್ಜೆ)</option>
                      <option value="Grade B">Grade B (Standard / ಸಾಧಾರಣ)</option>
                      <option value="Grade C">Grade C (Commercial / ವಾಣಿಜ್ಯ)</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    {language === 'kn' ? 'ಶೇಖರಣಾ ವಿಧಾನ' : 'Storage Method'}
                  </label>
                  <input
                    type="text"
                    value={harvStorage}
                    onChange={(e) => setHarvStorage(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl border border-gray-300 text-xs"
                  />
                </div>

                <div className="flex justify-between items-center pt-2">
                  <Link
                    to="/storage-assistant"
                    className="text-xs text-emerald-700 font-semibold hover:underline flex items-center space-x-1"
                  >
                    <span>{language === 'kn' ? 'ಶೇಖರಣಾ ಮಾರ್ಗದರ್ಶನ ಪರಿಶೀಲಿಸಿ' : 'View Storage Assistant Guidelines'}</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </Link>

                  <button
                    type="submit"
                    disabled={isSavingHarv}
                    className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition-all disabled:opacity-50"
                  >
                    {isSavingHarv ? 'Saving...' : language === 'kn' ? 'ಕೊಯ್ಲು ಉಳಿಸಿ' : 'Save Harvest Record'}
                  </button>
                </div>
              </form>

              {/* Harvest History */}
              <div className="bg-white p-6 rounded-3xl border border-emerald-100 shadow-sm space-y-3">
                <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">
                  {language === 'kn' ? 'ಕೊಯ್ಲು ದಾಖಲೆಗಳ ಪಟ್ಟಿ' : 'Harvest Records List'}
                </h4>

                {harvests.length === 0 ? (
                  <p className="text-xs text-gray-400 py-4 text-center">
                    {language === 'kn' ? 'ಇನ್ನೂ ಯಾವುದೇ ಕೊಯ್ಲು ದಾಖಲಾಗಿಲ್ಲ.' : 'No harvest records saved yet.'}
                  </p>
                ) : (
                  harvests.map((h) => (
                    <div key={h.id} className="p-3.5 rounded-2xl bg-gray-50 border border-gray-100 text-xs flex items-center justify-between">
                      <div>
                        <div className="font-bold text-gray-800 text-sm">
                          {h.quantity_kg} kg • {h.quality_grade}
                        </div>
                        <div className="text-gray-500 text-[11px] mt-0.5">
                          {h.harvest_date} • {h.storage_method}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* Delete Farm Option in Footer */}
          <div className="flex justify-end pt-6">
            <button
              onClick={() => handleDeleteFarm(selectedFarm.id)}
              className="text-xs text-red-600 hover:text-red-700 font-semibold flex items-center space-x-1 px-3 py-1.5 rounded-lg hover:bg-red-50 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>{language === 'kn' ? 'ಈ ಜಮೀನನ್ನು ಅಳಿಸಿ' : 'Remove This Farm'}</span>
            </button>
          </div>
        </>
      )}

      {/* MODAL 1: FARM REGISTRATION */}
      <FarmRegistrationModal
        isOpen={addFarmModalOpen}
        onClose={() => setAddFarmModalOpen(false)}
      />

      {/* MODAL 2: SKIP ACTIVITY WITH REASON */}
      {skipModalOpen && selectedActivityForSkip && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-black bg-opacity-50 flex items-center justify-center p-4 backdrop-blur-sm animate-fade-in">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl border border-gray-100">
            <h3 className="text-base font-bold text-gray-900">
              {language === 'kn' ? 'ಚಟುವಟಿಕೆ ಮುಂದೂಡಲು ಕಾರಣ' : 'Reason for Skipping / Postponing'}
            </h3>
            <p className="text-xs text-gray-600">
              {language === 'kn' ? selectedActivityForSkip.title_kn : selectedActivityForSkip.title_en}
            </p>

            <div className="space-y-2">
              {SKIP_REASONS.map((r) => (
                <label key={r.en} className="flex items-center space-x-2.5 p-2.5 rounded-xl border border-gray-200 cursor-pointer hover:bg-gray-50">
                  <input
                    type="radio"
                    name="skipReason"
                    value={r.en}
                    checked={selectedSkipReason === r.en}
                    onChange={(e) => setSelectedSkipReason(e.target.value)}
                    className="text-emerald-600 focus:ring-emerald-500"
                  />
                  <span className="text-xs text-gray-700">{language === 'kn' ? r.kn : r.en}</span>
                </label>
              ))}
            </div>

            <textarea
              rows={2}
              placeholder={language === 'kn' ? 'ಇತರ ಕಾರಣವಿದ್ದರೆ ನಮೂದಿಸಿ (ಐಚ್ಛಿಕ)...' : 'Other specific reason (optional)...'}
              value={customSkipReason}
              onChange={(e) => setCustomSkipReason(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-gray-300 text-xs"
            />

            <div className="flex justify-end space-x-2 pt-2">
              <button
                type="button"
                onClick={() => setSkipModalOpen(false)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-600 hover:bg-gray-100"
              >
                {language === 'kn' ? 'ರದ್ದು' : 'Cancel'}
              </button>
              <button
                type="button"
                onClick={handleSkipConfirm}
                className="px-5 py-2 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs shadow"
              >
                {language === 'kn' ? 'ದೃಢೀಕರಿಸಿ' : 'Confirm Skip'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 3: PROGRESS CORRECTION (FARMING DAY / STAGE) */}
      {editModalOpen && selectedFarm && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-black bg-opacity-50 flex items-center justify-center p-4 backdrop-blur-sm animate-fade-in">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl border border-gray-100">
            <h3 className="text-base font-bold text-gray-900 flex items-center space-x-2">
              <Edit3 className="w-5 h-5 text-emerald-600" />
              <span>{language === 'kn' ? 'ಕೃಷಿ ದಿನ ಅಥವಾ ಹಂತ ತಿದ್ದುಪಡಿ' : 'Edit Farming Day / Update Stage'}</span>
            </h3>
            <p className="text-xs text-gray-500">
              {language === 'kn'
                ? 'ಪ್ರಾರಂಭದ ಮಾಹಿತಿ ತಪ್ಪಾಗಿ ನಮೂದಿಸಲ್ಪಟ್ಟಿದ್ದರೆ ಸರಿಪಡಿಸಿ. ಎಲ್ಲ ಬದಲಾವಣೆಗಳನ್ನು ಆಡಿಟ್ ಇತಿಹಾಸದಲ್ಲಿ ದಾಖಲಿಸಲಾಗುತ್ತದೆ.'
                : 'Correct your farming day or cultivation stage. Every correction is permanently recorded in the audit history.'}
            </p>

            <form onSubmit={handleProgressCorrection} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  {language === 'kn' ? 'ಹೊಸ ಕೃಷಿ ದಿನ' : 'New Farming Day'}
                </label>
                <input
                  type="number"
                  min="1"
                  max="40000"
                  required
                  value={editCropDay}
                  onChange={(e) => setEditCropDay(parseInt(e.target.value) || 1)}
                  className="w-full px-3 py-2 rounded-xl border border-gray-300 text-sm font-bold text-emerald-800"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  {language === 'kn' ? 'ಹೊಸ ಬೆಳವಣಿಗೆಯ ಹಂತ' : 'New Cultivation Stage'}
                </label>
                <select
                  value={editStage}
                  onChange={(e) => setEditStage(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-gray-300 text-xs bg-white"
                >
                  {selectedFarm.stages?.map((st) => (
                    <option key={st.id} value={st.name_en}>
                      {language === 'kn' ? st.name_kn : st.name_en}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  {language === 'kn' ? 'ತಿದ್ದುಪಡಿ ಕಾರಣ (ಐಚ್ಛಿಕ)' : 'Reason for Correction'}
                </label>
                <input
                  type="text"
                  placeholder={language === 'kn' ? 'ಉದಾ: ಹಿಂದಿನ ದಿನಾಂಕ ತಪ್ಪಾಗಿ ದಾಖಲಿಸಲಾಗಿತ್ತು' : 'e.g. Corrected day based on field diary'}
                  value={editReason}
                  onChange={(e) => setEditReason(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-gray-300 text-xs"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2 border-t border-gray-100">
                <button
                  type="button"
                  onClick={() => setEditModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-600 hover:bg-gray-100"
                >
                  {language === 'kn' ? 'ರದ್ದು' : 'Cancel'}
                </button>
                <button
                  type="submit"
                  disabled={isUpdatingProgress}
                  className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow disabled:opacity-50"
                >
                  {isUpdatingProgress ? 'Updating...' : language === 'kn' ? 'ಬದಲಾವಣೆ ಉಳಿಸಿ' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
