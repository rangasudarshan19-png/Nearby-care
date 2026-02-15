# Nearby Care - Hospital Finder Application 🏥

A comprehensive full-stack healthcare discovery platform with modern UI, AI-powered recommendations, GPS location support, complete admin system, and enterprise-grade infrastructure.

---

## ⚡ QUICK START (EASIEST)

### Option 1: Start All Services at Once
```
start-all.bat
```
This opens Backend and Frontend in separate windows. Wait 10 seconds, then visit **http://localhost:3000**

### Option 2: Start Individually
**Backend:**
```
cd backend
start-dev.bat
```

**Frontend:**
```
cd frontend  
start-dev.bat
```

### Test the Application:
```
cd backend
test.bat
```

### Stop Servers:
```
stop-servers.bat
```

### Need Help?
```
check-system.bat  (diagnose issues)
TROUBLESHOOTING.md  (solutions)
```

---

## 🚀 Features

### User Features:
- 🔍 **Smart Search** - Find hospitals by location or GPS coordinates
- 🗺️ **Interactive Maps** - Leaflet-powered visualization
- ⭐ **Favorites** - Bookmark preferred hospitals
- 📝 **Reviews** - Read and write hospital reviews
- 🩺 **AI Symptom Advisor** - Get specialty recommendations (Gemini AI)
- 📍 **GPS Location** - Use your current location
- 📊 **Search History** - Track your searches
- 🎯 **AI Ranking** - Hospitals ranked by symptom match
- 🏥 **Advanced Filters** - Specialty, amenities, ownership type, rating
- 👨‍⚕️ **Doctor Appointments** - Book and manage appointments
- 📋 **Medical Records** - Personal health record storage

### Admin Features:
- 👥 **User Management** - View all registered users
- 🔒 **Role Management** - Promote/demote admins
- 📈 **Statistics Dashboard** - User and system metrics
- 🗑️ **User Deletion** - Remove user accounts

### Infrastructure & DevOps:
- ✅ **Health Monitoring** - `/health` and `/api/health` endpoints
- 📝 **Structured Logging** - Rotating file logs (10MB max, 10 backups)
- 🧪 **Testing Suite** - pytest with 95%+ test coverage
- 🔐 **Environment Variables** - Secure configuration management
- 🏗️ **Multi-environment Support** - Development/Production/Testing configs
- 📊 **Code Coverage** - HTML reports with pytest-cov

---

## 📋 Tech Stack

### Backend
- **Python 3.14** with Virtual Environment
- **Flask 3.1.0** - Modern web framework
- **SQLAlchemy 2.0** - Database ORM with async support
- **SQLite** - Development database
- **JWT** - Secure authentication
- **Flask-CORS** - API cross-origin support
- **SMTP Email** - OTP verification (Gmail)
- **pytest** - Testing framework
- **Google Gemini AI** - Symptom analysis
- **Cohere AI** - Text processing & embeddings

### Frontend
- **React 18.2.0** - Modern UI library
- **React Router v6** - Navigation
- **Leaflet Maps** - Interactive mapping
- **Modern CSS** - Gradients, shadows, animations
- **Responsive Design** - Mobile-first approach

### APIs & Services
1. **OpenStreetMap Overpass API** (Free) - Primary hospital data
2. **Nominatim API** (Free) - Geocoding service
3. **Google Gemini API** - AI symptom advisor
4. **Cohere API** - Natural language processing

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Node.js 14 or higher
- npm or yarn
- Gmail account for SMTP (optional, for email features)
- Google Gemini API key (for AI features)
- Cohere API key (for AI features)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
# Copy the example file
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux

# Edit .env and add your credentials:
# - GOOGLE_API_KEY (Gemini AI)
# - COHERE_API_KEY (Cohere AI)
# - SMTP credentials (for email)
# - JWT_SECRET_KEY (generate a random string)
# - SECRET_KEY (application secret)
```

5. Initialize the database:
```bash
python create_db.py
```
This creates the SQLite database with all 9 required tables and seeds:
- Default admin account: `admin@nearbycare.com` / `admin123`
- 10 sample doctors across specialties

6. Run the backend server:
```bash
# Using the startup script (recommended)
start-dev.bat  # Windows
python app.py  # All platforms

# Server runs on http://localhost:5000
```

7. Test the backend (optional):
```bash
# Run test suite
test.bat  # Windows
python -m pytest -v  # All platforms

# Check health endpoint
# Visit: http://localhost:5000/health
```

### Frontend Setup
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development
```

6. Run the Flask server:
```bash
python app.py
```

The backend will start on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will start on `http://localhost:3000`

## 📊 Database Schema

### Users Table
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email
- `created_at` - Timestamp

### SearchHistory Table
- `id` - Primary key
- `user_id` - Foreign key to Users
- `location` - Search location string
- `latitude` - Location latitude
- `longitude` - Location longitude
- `search_date` - Timestamp

### Favorites Table
- `id` - Primary key
- `user_id` - Foreign key to Users
- `hospital_name` - Hospital name
- `hospital_address` - Hospital address
- `place_id` - Unique place identifier
- `latitude` - Hospital latitude
- `longitude` - Hospital longitude
- `added_date` - Timestamp

## 🔌 API Endpoints

### Backend REST API

#### Health Check
```
GET /api/health
```

#### Search Hospitals (OpenStreetMap)
```
POST /api/search-hospitals-osm
Body: {
  "location": "New York",
  "radius": 5000
}
```

#### Search Hospitals (Google Places - Optional)
```
POST /api/search-hospitals
Body: {
  "location": "New York",
  "radius": 5000
}
```

#### Get Hospital Details
```
GET /api/hospital-details/<place_id>
```

#### Add to Favorites
```
POST /api/favorites
Body: {
  "user_id": 1,
  "hospital_name": "City Hospital",
  "hospital_address": "123 Main St",
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

#### Get Favorites
```
GET /api/favorites?user_id=1
```

#### Remove from Favorites
```
DELETE /api/favorites/<favorite_id>
```

#### Get Search History
```
GET /api/search-history?limit=10
```

## 🗺️ Using Different Data Sources

### Option 1: OpenStreetMap (Free)
The default configuration uses OpenStreetMap's Overpass API, which is completely free. No API key needed!

**Pros:**
- Free and open source
- No API limits
- Good global coverage

**Cons:**
- Data might be less complete in some areas
- No user reviews or ratings

### Option 2: Google Places API (Premium)
For more comprehensive data including reviews and ratings:

1. Get an API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the following APIs:
   - Places API
   - Geocoding API
3. Add the key to your `.env` file
4. Update the frontend to call `/api/search-hospitals` instead of `/api/search-hospitals-osm`

## 🎨 Customization

### Changing Search Radius Options
Edit [SearchForm.js](frontend/src/components/SearchForm.js):
```javascript
<select id="radius" value={radius} onChange={(e) => setRadius(e.target.value)}>
  <option value="1000">1 km</option>
  <option value="5000">5 km</option>
  // Add more options
</select>
```

### Changing Map Styles
Edit [MapView.js](frontend/src/components/MapView.js) to use different tile providers:
```javascript
// OpenStreetMap (default)
url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"

// CartoDB Dark Theme
url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png"
```

### Database Migration to PostgreSQL

1. Install PostgreSQL
2. Create a database:
```sql
CREATE DATABASE nearby_care;
```

3. Update `.env`:
```
DATABASE_URL=postgresql://username:password@localhost:5432/nearby_care
```

4. Install psycopg2:
```bash
pip install psycopg2-binary
```

## 🚀 Deployment

### Backend Deployment (Heroku)
```bash
# Install Heroku CLI
heroku login
heroku create nearby-care-api

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main
```

### Frontend Deployment (Vercel/Netlify)
```bash
# Build the app
npm run build

# Deploy to Vercel
vercel deploy

# Or Netlify
netlify deploy --prod
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👥 Authors

- Your Name - Full Stack Developer

## 🙏 Acknowledgments

- OpenStreetMap contributors for free map data
- Leaflet.js for the mapping library
- Flask and React communities

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

Made with ❤️ by Full Stack Developers
