export type SupportedCrop = 'Coconut' | 'Rice' | 'Arecanut' | 'Cocoa';

export interface CropStage {
  id: string;
  name_en: string;
  name_kn: string;
  start_day: number;
  end_day: number;
  description_en: string;
  description_kn: string;
}

export interface Farm {
  id: string;
  user_id: string;
  name?: string;
  crop: SupportedCrop;
  taluk: string;
  area: number;
  area_unit?: string;
  cultivation_start_date?: string;
  initial_farming_day?: number;
  monitoring_start_date: string;
  current_stage: string;
  variety?: string;
  cultivation_method?: string;
  soil_type?: string;
  water_availability?: string;
  notes?: string;
  current_crop_day: number;
  current_monitoring_day: number;
  today_activities_count?: number;
  today_pending_count?: number;
  today_completed_count?: number;
  today_skipped_count?: number;
  stages?: CropStage[];
  weather_snapshot?: any;
  weather_alerts?: any[];
  created_at: number;
  updated_at: number;
}

export interface FarmActivity {
  id: string;
  farm_id: string;
  calendar_date: string;
  crop_day: number;
  monitoring_day: number;
  stage: string;
  title_en: string;
  title_kn: string;
  description_en: string;
  description_kn: string;
  why_necessary_en: string;
  why_necessary_kn: string;
  timing_conditions_en?: string;
  timing_conditions_kn?: string;
  priority: 'high' | 'medium' | 'low';
  weather_influence_en?: string;
  weather_influence_kn?: string;
  status: 'pending' | 'completed' | 'skipped';
  completed_at?: number;
  skipped_at?: number;
  skip_reason?: string;
  is_recurring?: boolean;
}

export interface FarmObservation {
  id: string;
  farm_id: string;
  calendar_date: string;
  crop_day: number;
  monitoring_day: number;
  field_condition?: string;
  soil_moisture?: string;
  water_availability?: string;
  crop_appearance?: string;
  pest_symptoms?: string;
  rainfall_notes?: string;
  additional_notes?: string;
  photo_url?: string;
  created_at: number;
}

export interface FarmHarvest {
  id: string;
  farm_id: string;
  harvest_date: string;
  quantity_kg: number;
  quality_grade?: string;
  storage_method?: string;
  notes?: string;
  created_at: number;
}
