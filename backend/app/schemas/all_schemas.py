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
