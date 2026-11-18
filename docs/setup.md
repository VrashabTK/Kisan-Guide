# KISSAN GUIDE — Setup and Configuration Guide

Welcome to **KISSAN GUIDE**, a dedicated agricultural platform built for farmers of **Dakshina Kannada (DK), Karnataka, India**.

This platform focuses strictly on the 4 primary regional crops:
1. **Coconut** (ತೆಂಗು)
2. **Rice / Paddy** (ಭತ್ತ)
3. **Arecanut** (ಅಡಿಕೆ)
4. **Cocoa** (ಕೋಕೋ)

Covering all 9 Taluks of Dakshina Kannada:
- **Mangaluru**, **Bantwal**, **Belthangady**, **Puttur**, **Sullia**, **Moodbidri**, **Kadaba**, **Mulki**, **Ullal**.

---

## 1. System Requirements

- **Python**: 3.11+
- **Node.js**: v18+ (tested on Node v24)
- **npm**: v9+
- **Firebase Account** (for production Authentication and Firestore persistence)

---

## 2. Local Environment Setup

### A. Clone & Structure
```bash
cd KISSAN_GUIDE
```

### B. Backend Setup
1. Create and activate a Python virtual environment (recommended):
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. Configure Environment Variables:
   Copy `backend/.env.example` to `backend/.env`:
   ```bash
   cp backend/.env.example backend/.env
   ```

4. Run the Backend API:
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```
   - Interactive Swagger API Documentation: `http://localhost:8000/docs`
   - ReDoc Documentation: `http://localhost:8000/redoc`
   - Health Check: `http://localhost:8000/api/health`

### C. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install npm dependencies:
   ```bash
   npm install
   ```

3. Configure Environment Variables:
   Copy `frontend/.env.example` to `frontend/.env`:
   ```bash
   cp .env.example .env
   ```

4. Run the Development Server:
   ```bash
   npm run dev
   ```
   Access the web application at `http://localhost:5173`.

---

## 3. External API Configurations

### Weather API (Zero-Configuration Default)
By default, KISSAN GUIDE connects out-of-the-box to **Open-Meteo**, a verified meteorological API that requires **no API key**. It automatically geolocates weather and forecasts for all 9 taluks in Dakshina Kannada.
- If you wish to configure an alternative weather API (e.g. OpenWeatherMap), set in `backend/.env`:
  ```ini
  WEATHER_PROVIDER=openweather
  WEATHER_API_KEY=your_openweather_api_key
  WEATHER_API_BASE_URL=https://api.openweathermap.org/data/2.5
  ```

### AI Provider Setup (Google Gemini)
The AI Storage Assistant and advisory generator use Google Gemini.
1. Obtain an API key from [Google AI Studio](https://aistudio.google.com/).
2. Add your key to `backend/.env`:
   ```ini
   AI_PROVIDER=gemini
   AI_API_KEY=your_gemini_api_key
   AI_MODEL=gemini-1.5-flash
   ```
*Note*: If `AI_API_KEY` is not provided, KISSAN GUIDE automatically falls back to certified agronomic expert rules so the system never breaks.

### Firebase Setup (Authentication, Firestore & Storage)
1. Visit the [Firebase Console](https://console.firebase.google.com/) and create a project named `kissan-guide`.
2. Enable **Authentication**:
   - Enable **Phone** authentication (for Indian mobile OTP).
   - Enable **Google** sign-in provider.
   - Enable **Email/Password** provider.
3. Enable **Cloud Firestore** and **Firebase Storage**.
4. Deploy Firestore security rules from `firebase/firestore.rules`:
   ```bash
   firebase deploy --only firestore:rules,firestore:indexes,storage:rules
   ```
5. In Project Settings -> Service Accounts, generate a private key (`serviceAccountKey.json`), save it to `backend/serviceAccountKey.json`, and set in `backend/.env`:
   ```ini
   FIREBASE_CREDENTIALS_PATH=serviceAccountKey.json
   ```
6. In Project Settings -> General -> Your Apps, copy your web configuration to `frontend/.env`:
   ```ini
   VITE_FIREBASE_API_KEY=AIzaSy...
   VITE_FIREBASE_AUTH_DOMAIN=kissan-guide.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=kissan-guide
   VITE_FIREBASE_STORAGE_BUCKET=kissan-guide.appspot.com
   VITE_FIREBASE_MESSAGING_SENDER_ID=...
   VITE_FIREBASE_APP_ID=...
   ```

*Note*: KISSAN GUIDE features a **Quick Demo** button on the sign-in page that allows full exploration even before external Firebase keys are provisioned.

---

## 4. Running Automated Tests

Run the backend verification suite:
```bash
python backend/tests/run_tests.py
```
This tests:
- Taluk coordinates & agro-ecological zones
- Crop suitability scoring algorithms for Coconut, Rice, Arecanut, Cocoa
- Post-harvest storage rules and penalty mechanics
- Meteorological severe weather alert threshold triggers
- FastAPI route validation, bookmarks flow, and farmer profile updating.
