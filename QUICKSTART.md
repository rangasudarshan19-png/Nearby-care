# Quick Start Guide - Nearby Care

## 🚀 EASIEST WAY TO START (Recommended)

### Just Double-Click This File:
```
start-servers.bat
```

That's it! Both servers will start automatically.
- Backend will run on http://localhost:5000
- Frontend will open on http://localhost:3000

### If You Get Errors, Run:
```
check-system.bat
```

### To Stop Servers:
```
stop-servers.bat
```

---

## 🔧 Manual Setup (First Time Only)

### Step 1: Setup Backend
```bash
# Navigate to backend
cd backend

# Install Python dependencies (using virtual environment)
C:\Users\Chait\OneDrive\Desktop\Abhi\.venv\Scripts\pip.exe install -r requirements.txt

# Create database
C:\Users\Chait\OneDrive\Desktop\Abhi\.venv\Scripts\python.exe create_db.py
```

### Step 2: Setup Frontend
```bash
# Navigate to frontend
cd frontend

# Install Node dependencies
npm install
```

### Step 3: Start Using start-servers.bat
```
start-servers.bat
```

## 🎯 What You Get

- ✅ Hospital search by location
- ✅ Interactive map with markers
- ✅ Search radius customization (1-20km)
- ✅ Save favorite hospitals
- ✅ View search history
- ✅ Get directions to hospitals
- ✅ Free OpenStreetMap data (no API key needed!)

## 🔑 Optional: Google Places API

For premium features (ratings, reviews, photos):

1. Get API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Add to `backend/.env`:
   ```
   GOOGLE_PLACES_API_KEY=your_key_here
   ```
3. Update frontend to use `/api/search-hospitals` endpoint

## 📱 Features Overview

### Search Tab
- Enter location name
- Select search radius
- View hospitals on map
- See detailed information

### Favorites Tab
- View saved hospitals
- Remove from favorites
- Get directions

### History Tab
- Recent searches
- Quick re-search
- Location coordinates

## 🛠️ Tech Stack
- **Backend**: Python + Flask
- **Frontend**: React.js
- **Database**: SQLite (default)
- **Maps**: Leaflet + OpenStreetMap
- **APIs**: Overpass API (free)

## 📞 Need Help?

Check the main README.md for detailed documentation!
