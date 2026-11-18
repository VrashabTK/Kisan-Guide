# KISSAN GUIDE — Production Deployment Guide

This guide details deploying **KISSAN GUIDE** into production:
- **Backend API**: [Render](https://render.com) (FastAPI / Python)
- **Frontend SPA**: [Vercel](https://vercel.com) (Vite / React / Tailwind)
- **Database & Auth**: [Firebase](https://firebase.google.com) (Firestore & Authentication)

---

## 1. Backend Deployment (Render)

### Option A: Using `render.yaml` Blueprint (Recommended)
1. Fork or push the `KISSAN_GUIDE` repository to GitHub or GitLab.
2. In the Render Dashboard, navigate to **Blueprints** -> **New Blueprint Instance**.
3. Select your repository. Render will automatically detect `render.yaml`.
4. Configure Secret Environment Variables in the Render UI:
   - `AI_API_KEY`: Your Google Gemini API Key.
   - `FIREBASE_CREDENTIALS_PATH`: Path or secret file for your Firebase service account JSON.
   - `CORS_ORIGINS`: Your Vercel frontend URL (e.g. `https://kissan-guide.vercel.app`).
5. Click **Apply**. Render will build and deploy the service.
6. Verify your live health check: `https://<your-render-subdomain>.onrender.com/api/health`.

### Option B: Manual Web Service Setup on Render
- **Environment**: Python 3.11
- **Build Command**: `pip install -r backend/requirements.txt`
- **Start Command**: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path**: `/api/health`

---

## 2. Frontend Deployment (Vercel)

1. In the Vercel Dashboard, select **Add New Project** and import your repository.
2. Configure Project Settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
3. Add Environment Variables in Vercel:
   - `VITE_API_BASE_URL`: Your Render backend URL + `/api/v1` (e.g., `https://kissan-guide.onrender.com/api/v1`)
   - `VITE_FIREBASE_API_KEY`: Your Firebase Web API key
   - `VITE_FIREBASE_AUTH_DOMAIN`: `kissan-guide.firebaseapp.com`
   - `VITE_FIREBASE_PROJECT_ID`: `kissan-guide`
   - `VITE_FIREBASE_STORAGE_BUCKET`: `kissan-guide.appspot.com`
   - `VITE_FIREBASE_MESSAGING_SENDER_ID`: `...`
   - `VITE_FIREBASE_APP_ID`: `...`
4. Click **Deploy**. Vercel will build the frontend assets using `vercel.json` for client-side routing.

---

## 3. Firebase Production Setup

1. **Firestore Rules**:
   Deploy the production rules:
   ```bash
   firebase deploy --only firestore:rules,firestore:indexes,storage:rules
   ```
2. **Authorized Domains in Firebase**:
   In Firebase Console -> Authentication -> Settings -> Authorized Domains, add:
   - Your Vercel domain: `<your-app>.vercel.app`
   - Custom domains (if applicable).
3. **Phone Authentication**:
   In Firebase Console -> Authentication -> Sign-in method -> Phone, enable phone sign-in and configure SMS templates or test phone numbers for app review.
