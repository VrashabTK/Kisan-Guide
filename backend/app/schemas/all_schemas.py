from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class UserProfileUpdate(BaseModel):
    fullName: Optional[str] = None
    phoneNumber: Optional[str] = None
    taluk: Optional[str] = None
    district: Optional[str] = "Dakshina Kannada"
    state: Optional[str] = "Karnataka"
    preferredLanguage: Optional[str] = "en"
    selected_crop: Optional[str] = None
    selectedCrop: Optional[str] = None
    primaryCrops: Optional[List[str]] = None
    farmingExperienceYears: Optional[int] = None
    profilePicture: Optional[str] = None

class SignUpRequest(BaseModel):
    identifier: str = Field(..., description="Email address or 10-digit Indian mobile number")
    password: str = Field(..., min_length=6, description="Password (minimum 6 characters)")
    confirm_password: Optional[str] = None
    full_name: Optional[str] = None
    taluk: Optional[str] = "Mangaluru"

class LoginRequest(BaseModel):
    identifier: str = Field(..., description="Email address or 10-digit Indian mobile number")
    password: str = Field(..., description="User password")

class ForgotPasswordRequest(BaseModel):
    identifier: str = Field(..., description="Registered email address or mobile number")

class ResetPasswordRequest(BaseModel):
    token: str = Field(..., description="Password reset verification token")
    new_password: str = Field(..., min_length=6, description="New password")
    confirm_new_password: Optional[str] = None

class CropPreferenceUpdate(BaseModel):
    crop: str = Field(..., description="Coconut, Rice, Arecanut, or Cocoa")

class CropRecommendationRequest(BaseModel):
    taluk: str = Field(..., description="Taluk in Dakshina Kannada")
    water_availability: str = Field(..., description="Low, Moderate, or High")
    soil_type: Optional[str] = None
    irrigation_available: Optional[bool] = None
    previous_crop: Optional[str] = None
    plantation_area_acres: Optional[float] = None

class StorageRecommendationRequest(BaseModel):
    crop: str = Field(..., description="Coconut, Rice, Arecanut, or Cocoa")
    harvest_date: str = Field(..., description="YYYY-MM-DD")
    storage_method: str = Field(..., description="Storage method")
    crop_condition: str = Field(..., description="Condition of harvested crop")
    taluk: Optional[str] = "Mangaluru"
    quantity_kg: Optional[float] = None
    storage_facility_description: Optional[str] = None

class AIStorageAssistantRequest(BaseModel):
    crop: str
    harvest_date: str
    storage_method: str
    crop_condition: str
    taluk: Optional[str] = "Mangaluru"
    language: Optional[str] = "en"

class WeatherAdvisoryRequest(BaseModel):
    taluk: str = "Mangaluru"
    crop: Optional[str] = "All"

class SavedItemCreate(BaseModel):
    itemType: str = Field(..., description="Crop Recommendation, Weather Assistant, or Storage Assistant")
    itemId: str
    title: str
    title_kn: Optional[str] = None
    crop: Optional[str] = None
    location: Optional[str] = None
    content: Dict[str, Any]

class NotificationPreferencesUpdate(BaseModel):
    thunderstormEnabled: Optional[bool] = True
    rainfallEnabled: Optional[bool] = True
    heatEnabled: Optional[bool] = True
    windEnabled: Optional[bool] = True
    generalAdvisoryEnabled: Optional[bool] = True
    pushEnabled: Optional[bool] = False

# ==================== Farm Management Schemas ====================

class FarmCreate(BaseModel):
    name: Optional[str] = None
    crop: str = Field(..., description="Coconut, Rice, Arecanut, or Cocoa")
    taluk: str = Field(..., description="Taluk in Dakshina Kannada")
    area: float = Field(..., gt=0, description="Area of farm")
    area_unit: Optional[str] = "acre"
    cultivation_start_date: Optional[str] = None
    initial_farming_day: Optional[int] = Field(1, ge=1)
    current_stage: Optional[str] = None
    variety: Optional[str] = None
    cultivation_method: Optional[str] = None
    soil_type: Optional[str] = None
    water_availability: Optional[str] = "Moderate"
    notes: Optional[str] = None
    confirmation_started: Optional[bool] = True

class FarmUpdate(BaseModel):
    name: Optional[str] = None
    crop: Optional[str] = None
    taluk: Optional[str] = None
    area: Optional[float] = None
    area_unit: Optional[str] = None
    variety: Optional[str] = None
    cultivation_method: Optional[str] = None
    soil_type: Optional[str] = None
    water_availability: Optional[str] = None
    notes: Optional[str] = None

class FarmProgressCorrectionRequest(BaseModel):
    new_crop_day: Optional[int] = Field(None, ge=1)
    new_stage: Optional[str] = None
    reason: Optional[str] = None

class ActivityActionRequest(BaseModel):
    reason: Optional[str] = None

class ObservationCreate(BaseModel):
    farm_id: str
    calendar_date: Optional[str] = None
    field_condition: Optional[str] = None
    soil_moisture: Optional[str] = None
    water_availability: Optional[str] = None
    crop_appearance: Optional[str] = None
    pest_symptoms: Optional[str] = None
    rainfall_notes: Optional[str] = None
    additional_notes: Optional[str] = None
    photo_url: Optional[str] = None

class HarvestCreate(BaseModel):
    farm_id: str
    harvest_date: str
    quantity_kg: float = Field(..., gt=0)
    quality_grade: Optional[str] = "Grade A"
    storage_method: Optional[str] = None
    notes: Optional[str] = None
