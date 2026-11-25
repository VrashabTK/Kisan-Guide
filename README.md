# KISSAN GUIDE — Full-Stack Agricultural Assistance Platform

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI_0.116-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React_18_+_TypeScript-61DAFB.svg?logo=react)](https://reactjs.org)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind_CSS_3.4-38B2AC.svg?logo=tailwind-css)](https://tailwindcss.com)
[![Vite](https://img.shields.io/badge/Bundler-Vite_5-646CFF.svg?logo=vite)](https://vitejs.dev)
[![Firebase](https://img.shields.io/badge/Auth_%26_DB-Firebase_Firestore-FFCA28.svg?logo=firebase)](https://firebase.google.com)
[![Tests](https://img.shields.io/badge/Backend%20Tests-28%20Passing-brightgreen.svg)]()
[![Validation Tests](https://img.shields.io/badge/Frontend%20Validation-15%20Passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-blue.svg)]()

> **KISSAN GUIDE** is an agricultural assistance web application designed specifically for farmers in **Dakshina Kannada (DK), Karnataka, India**.

---

## 🌾 Supported Crops & Coverage

KISSAN GUIDE strictly focuses on the 4 primary agricultural crops of the coastal Dakshina Kannada region:
1. 🥥 **Coconut** (*Cocos nucifera* / ತೆಂಗು)
2. 🌾 **Rice / Paddy** (*Oryza sativa* / ಭತ್ತ)
3. 🌴 **Arecanut** (*Areca catechu* / ಅಡಿಕೆ)
4. 🍫 **Cocoa** (*Theobroma cacao* / ಕೋಕೋ)

Covering all **9 Taluks** of Dakshina Kannada:
- **Mangaluru** (ಮಂಗಳೂರು)
- **Bantwal** (ಬಂಟ್ವಾಳ)
- **Belthangady** (ಬೆಳ್ತಂಗಡಿ)
- **Puttur** (ಪುತ್ತೂರು)
- **Sullia** (ಸುಳ್ಯ)
- **Moodbidri** (ಮೂಡುಬಿದಿರೆ)
- **Kadaba** (ಕಡಬ)
- **Mulki** (ಮುಲ್ಕಿ)
- **Ullal** (ಉಳ್ಳಾಲ)

---

## 🚀 Key Features

### 1. 🌱 My Farm — Personal Farm Management & Intelligent Daily Monitoring (NEW)
- **Central Cultivation Command Center**: Tracks real farmer plots across Dakshina Kannada.
- **Dual Independent Timelines**:
  - **Actual Crop Farming Timeline**: Represents true age/days of cultivation (e.g., Crop Day 15, Day 30).
  - **KISSAN GUIDE Monitoring Timeline**: Independent counter from registration day (Monitoring Day 1, 2, ...).
- **Flexible Late Registration**: Farmers can join on Day 15, Day 30, or pick a past start date. The system immediately delivers stage-appropriate Day 15 tasks instead of restarting from Day 1.
- **Visual Growth-Stage Progression**: Comprehensive stages for Rice (seasonal) and perennial Coconut, Arecanut, and Cocoa.
- **Daily Farming Tasks**: Dynamic tasks with explanation, priority, rationale, and live weather adaptation (e.g., rain delays spraying/irrigation).
- **Farmer Confirmations & Skips**: Mark "Done" with timestamps or "Skip" with structured reasons (heavy rainfall, labour shortage, etc.).
- **Progress Correction Audit Log**: Allows updating farming day or stage with a permanent audit trail.
- **Daily Field Observations & Harvest Batches**: Record soil moisture, pest symptoms, and harvest quantities directly connected to each farm.
- **Multi-Farm Support**: Seamlessly manage multiple separate plots (e.g. Rice 2 acres, Arecanut 1 acre) with isolated timelines.

### 1. Robust Authentication System
- **Mobile Phone Authentication** with 6-digit SMS OTP verification (Firebase Phone Auth with reCAPTCHA).
- **Google OAuth Login** via Firebase Authentication.
- **Email & Password Authentication** with confirmation and password reset.
- **Quick Demo Mode** for testing without cloud credentials.
- Persistent session management and protected routes.

### 2. Personalized Farmer Dashboard
- Warm personalized greeting: `"Namaskara, [Farmer Name]!"` / `"ನಮಸ್ಕಾರ, [Farmer Name]!"`.
- Live weather snapshot (temperature, humidity, rainfall, wind).
- 3 primary interactive feature cards with hover transitions:
  - **CROP RECOMMENDATION**
  - **WEATHER ASSISTANT**
  - **STORAGE ASSISTANT**
- Today's farming routine advisory and active weather alerts summary.

### 3. Scientific Crop Recommendation Module
- Evaluates farmer's taluk, soil type, irrigation, and water availability (**Low**, **Moderate**, **High**).
- Analyzes live weather and seasonal calendars (South-West Monsoon, North-East Monsoon, Kharif, Rabi).
- Generates:
  - Scientifically justified **Suitability Score** (0–100%).
  - Optimal **Plantation Starting Window**.
  - Agronomic pre-planting pit preparation guidelines.
  - Weather warnings and alternative crop rankings.

### 4. Weather Assistant & Farming Routines
- Localized weather metrics: temperature, feels-like, humidity, precipitation, wind speed, UV index, and atmospheric pressure.
- **24-Hour hourly timeline** and **4-day daily outlook**.
- **Farming routines** organized by agronomic category:
  - Irrigation
  - Field Drainage
  - Fertilizer Precautions
  - Crop Protection (e.g. Bordeaux mixture against *Phytophthora* fruit rot / Mahali)
  - Sun-drying and post-harvest care.
- **Severe Weather Alert Engine**: Threshold-based detection for thunderstorms, torrential rainfall, high winds, and heat stress.

### 5. Post-Harvest Storage Assistant & AI Guidance
- Analyzes crop condition (**Fresh**, **Dry**, **Damp**, **Slightly spoiled**, **Sprouted**, **Partially damaged**).
- Evaluates storage method (**Ventilated room**, **Jute bag**, **Warehouse**, **Dark room**, **Open air**, **Closed container**).
- Computes:
  - **Storage Suitability** (*Suitable*, *Needs Improvement*, *Not Recommended*).
  - **Estimated Safe Storage Duration** and remaining days.
  - **Recommended Selling Deadline** date.
  - 4-point Risk Matrix (**Moisture**, **Spoilage**, **Pest**, **Temperature**).
- **AI Storage Assistant**: Integrated Google Gemini AI providing practical, certified steps in English and Kannada.

### 6. Full English & Kannada Localization
- Complete native translation across all UI elements, labels, buttons, cards, warnings, error states, and advisories using `i18next`.
- One-click language switcher (`English` ⇄ `ಕನ್ನಡ`).
- Font rendering tuned with **Noto Sans Kannada**.

### 7. Bookmarking / Saved Guidelines
- Save any crop recommendation, weather routine, or storage plan with a single click.
- Filter bookmarks by category and access offline.

### 8. Farmer Profile Management
- Update personal contact details, location, preferred language, years of experience, and primary crops.
- Configure granular notification preferences (Thunderstorms, Heavy Rain, Heat, Wind, General Advisories).

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, TypeScript, Vite 5, Tailwind CSS 3.4, Lucide React, i18next, React Router 6, Zod |
| **Backend** | Python 3.11, FastAPI 0.116, Uvicorn, Pydantic v2, HTTPX |
| **Authentication** | Firebase Authentication (Phone OTP, Google OAuth, Email/Password) |
| **Database** | Cloud Firestore, Firebase Storage |
| **External APIs** | Open-Meteo API (Live Weather & Forecasts), Google Gemini API (AI Suggestions) |
| **Deployment** | Vercel (Frontend), Render (Backend) |

---

## 📂 Project Directory Structure

```
KISSAN_GUIDE/
├── frontend/
│   ├── src/
│   │   ├── components/         # Navbar, Footer, NotificationModal, ProtectedRoute
│   │   ├── contexts/           # AuthContext, LanguageContext, NotificationContext
│   │   ├── localization/       # en.json, kn.json, i18n.ts
│   │   ├── pages/
│   │   │   ├── Login/          # Split-screen Phone OTP, Google & Email auth
│   │   │   ├── Dashboard/      # Central overview & feature cards
│   │   │   ├── CropRecommendation/ # DK crop suitability engine
│   │   │   ├── WeatherAssistant/   # Forecasts, routines & alert triggers
│   │   │   ├── StorageAssistant/   # Post-harvest shelf life & AI guidance
│   │   │   ├── Profile/        # Farmer details & notification preferences
│   │   │   └── Saved/          # Bookmarked advisories & plans
│   │   ├── services/           # api.ts (REST client), firebase.ts (SDK)
│   │   ├── App.tsx             # Route definitions
│   │   └── main.tsx            # React root
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── .env.example
│
├── backend/
│   ├── app/
│   │   ├── agricultural_rules/ # Scientifically verified rules for DK crops & storage
│   │   ├── api/routes/         # Auth, Crops, Weather, Storage, AI, Saved, Notifications
│   │   ├── core/               # Settings & Firebase security verification
│   │   ├── schemas/            # Pydantic v2 validation models
│   │   ├── services/           # WeatherService, CropService, StorageService, AIService
│   │   └── main.py             # FastAPI entrypoint
│   ├── tests/                  # Automated test suite (14 passing tests)
│   ├── requirements.txt
│   └── .env.example
│
├── firebase/
│   ├── firestore.rules         # Security rules enforcing strict user isolation
│   ├── firestore.indexes.json  # Composite Firestore indexes
│   └── storage.rules           # Profile image upload constraints
│
├── docs/
│   ├── setup.md                # Comprehensive local setup guide
│   ├── architecture.md         # System architecture & sequence diagrams
│   └── deployment.md           # Production deployment guide (Render & Vercel)
│
├── render.yaml                 # Render Infrastructure-as-Code blueprint
├── vercel.json                 # Vercel SPA configuration
└── README.md
```

---

## ⚡ One-Click Startup (Recommended)

To start the entire application without opening separate terminal windows:

👉 **Simply double-click `RUN.bat` directly in the `KISSAN_GUIDE` root folder.**

`RUN.bat` automatically:
1. Detects Python (3.10+) and Node.js (18+)/npm.
2. Checks port availability (ports 8000 and 5173).
3. Creates and activates the Python virtual environment (`.\venv`).
4. Installs backend dependencies (`pip install -r backend\requirements.txt`).
5. Installs frontend dependencies (`npm install` inside `frontend\`).
6. Starts the **FastAPI Backend** with `--reload` in its own persistent terminal window.
7. Starts the **React/Vite Frontend** with Hot Module Replacement (HMR) in its own terminal window.
8. Automatically waits for the frontend server to become responsive.
9. Automatically opens your default web browser to [http://localhost:5173](http://localhost:5173).

---

## 🛠️ Manual Terminal Startup

### 1. Backend
```bash
# In project root
python -m venv venv
venv\Scripts\activate   # On Windows
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env

# Run FastAPI Server
uvicorn backend.app.main:app --reload --port 8000
```
API Documentation will be live at:
- `http://localhost:8000/docs` (Swagger UI)
- `http://localhost:8000/redoc` (ReDoc)

### 2. Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🧪 Running Automated Tests

Run the complete backend automated test suite:
```bash
python -u backend/tests/run_tests.py
```
**Test Results**: 14 tests covering crop suitability algorithms, storage shelf-life calculation, meteorological alert triggers, token authentication, and Firestore data operations.

---

## 🚢 Deployment

Detailed deployment guides are available in [docs/deployment.md](file:///docs/deployment.md).

- **Backend**: Deployed on [Render](https://render.com) using `render.yaml`.
- **Frontend**: Deployed on [Vercel](https://vercel.com) using `vercel.json`.
- **Database**: Cloud Firestore with security rules from `firebase/firestore.rules`.

---

## 📜 License & Disclaimers

Advisory guidance is based on tropical agronomic standards for Dakshina Kannada. Farmers are encouraged to consult their local Raitha Samparka Kendras (RSK) for site-specific soil testing.

Built with ❤️ for Indian Farmers.
