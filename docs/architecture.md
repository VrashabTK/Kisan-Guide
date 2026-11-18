# KISSAN GUIDE — Architecture & Technical Design

## 1. Executive Summary

**KISSAN GUIDE** is an agricultural assistance web application designed specifically for the agro-ecological and climatic conditions of **Dakshina Kannada (DK), Karnataka, India**.

The platform is strictly bounded to the 4 prominent crops cultivated in the district:
1. **Coconut** (*Cocos nucifera*)
2. **Rice / Paddy** (*Oryza sativa*)
3. **Arecanut** (*Areca catechu*)
4. **Cocoa** (*Theobroma cacao*)

Across all 9 taluks: **Mangaluru**, **Bantwal**, **Belthangady**, **Puttur**, **Sullia**, **Moodbidri**, **Kadaba**, **Mulki**, and **Ullal**.

---

## 2. High-Level System Architecture

```mermaid
flowchart TD
    User["Farmer in Dakshina Kannada (Mobile / Desktop)"]
    
    subgraph Frontend ["Frontend Layer (Vite + React 18 + TS)"]
        UI["Tailwind CSS + Lucide Icons (Noto Sans Kannada)"]
        AuthCtx["Auth Context (Firebase Client SDK)"]
        LangCtx["Language Context (i18next English/Kannada)"]
        NotifCtx["Notification Context & Modals"]
    end
    
    subgraph Backend ["Backend API Layer (FastAPI + Python 3.11)"]
        Sec["Security Middleware (Firebase Token Verifier)"]
        CropSvc["Crop Recommendation Service"]
        WeatherSvc["Weather & Advisory Service"]
        StorageSvc["Post-Harvest Storage Service"]
        AISvc["AI Assistant Service (Gemini + Rule Engine)"]
        NotifSvc["Alert & Notification Engine"]
    end

    subgraph Database ["Persistence Layer (Firebase)"]
        FS_Users[("users")]
        FS_Recs[("crop_recommendations")]
        FS_Storage[("storage_records")]
        FS_Saved[("saved_items")]
        FS_Notifs[("notifications")]
    end

    subgraph External ["External Services"]
        OpenMeteo["Open-Meteo Meteorological Feed"]
        Gemini["Google Gemini AI API"]
        FB_Auth["Firebase Authentication (Phone OTP, Google, Email)"]
    end

    User --> UI
    UI --> AuthCtx
    UI --> LangCtx
    UI --> NotifCtx
    AuthCtx --> FB_Auth
    
    UI -->|Bearer Token + REST| Sec
    Sec --> CropSvc
    Sec --> WeatherSvc
    Sec --> StorageSvc
    Sec --> AISvc
    Sec --> NotifSvc
    
    WeatherSvc --> OpenMeteo
    CropSvc --> WeatherSvc
    StorageSvc --> WeatherSvc
    AISvc --> Gemini
    
    CropSvc --> FS_Recs
    StorageSvc --> FS_Storage
    Sec --> FS_Users
    NotifSvc --> FS_Notifs
    Backend --> FS_Saved
```

---

## 3. Core Modules & Agronomic Workflows

### 3.1 Crop Recommendation Pipeline
```mermaid
sequenceDiagram
    autonumber
    Farmer->>Frontend: Select Taluk, Water Availability, Soil Type
    Frontend->>Backend: POST /api/v1/crops/recommend
    Backend->>WeatherSvc: Fetch Live Weather & 4-Day Rain Forecast
    WeatherSvc-->>Backend: Return Temperature, Humidity, Rainfall
    Backend->>CropRules: Evaluate DK Agro-Ecological Match
    Note over Backend,CropRules: Assesses Water Req (35%), Temp (25%), Season (25%), Taluk Fit (15%)
    CropRules-->>Backend: Ranked Scores, Plantation Windows, Precautions
    Backend->>Firestore: Persist recommendation to history
    Backend-->>Frontend: JSON with primary crop & alternative comparisons
    Frontend-->>Farmer: Render Bilingual Result Card
```

### 3.2 Post-Harvest Storage & AI Assistant Pipeline
```mermaid
sequenceDiagram
    autonumber
    Farmer->>Frontend: Enter Crop, Harvest Date, Storage Method, Condition
    Frontend->>Backend: POST /api/v1/storage/recommend
    Backend->>WeatherSvc: Fetch Ambient Temperature & Relative Humidity
    Backend->>StorageRules: Evaluate Shelf Life & Risk Matrix
    StorageRules-->>Backend: Suitable/Unsuitable, Remaining Days, Deadline Date
    Backend->>AISvc: Request tailored Gemini instructions
    AISvc-->>Backend: Action steps, moisture management, pest prevention
    Backend-->>Frontend: Evaluation metrics + AI guidance
    Frontend-->>Farmer: Display Risk Indicators & Storage Guidelines
```

### 3.3 Severe Weather Alert Pipeline
- Weather service queries Open-Meteo every 15 minutes (with in-memory cache).
- Analyzes meteorological thresholds:
  - **Thunderstorm / Lightning**: WMO Codes 95, 96, 99.
  - **Heavy Rainfall**: >64.5 mm/day or >20 mm in single hourly snapshot.
  - **High Wind**: >45 km/h coastal gusts.
  - **Excessive Heat**: >35°C in coastal humid environment.
- Formulates alert levels (**Informational**, **Moderate**, **Severe**, **Critical**).
- Dispatches in-app notifications respecting user preferences.

---

## 4. Security Architecture

1. **Token Authentication**:
   - Every protected request includes a Firebase ID token: `Authorization: Bearer <id_token>`.
   - The backend validates the cryptographically signed JWT via Firebase Admin SDK.
   - The verified Firebase UID is extracted server-side and never trusted from client-supplied request bodies.
2. **Database Isolation**:
   - Firestore security rules strictly constrain reads and updates to documents where `request.auth.uid == userId`.
3. **No Commits of Secrets**:
   - Sensitive keys are exclusively configured through environment variables (`AI_API_KEY`, `FIREBASE_CREDENTIALS_PATH`, `WEATHER_API_KEY`).
