# 🏥 Nearby Care - Complete Healthcare Finder

A full-stack hospital finder application with authentication, email verification, and real-time hospital search.

## 🎯 New Features

### ✨ Landing Page
- Beautiful hero section with call-to-action
- Feature showcase
- How it works section
- Benefits and testimonials
- Responsive design

### 🔐 Authentication System
- **Sign Up** with email verification
- **Email OTP Verification** via SMTP
- **Secure Login** with JWT tokens
- **Password encryption** with bcrypt
- Protected routes and API endpoints

### 📧 Email Verification
- Automatic OTP generation
- Beautifully designed email templates
- OTP expiry (10 minutes)
- Resend OTP functionality
- Using Gmail SMTP

### 🏥 Hospital Search (Protected)
- Search hospitals by location
- Interactive map view
- Save favorites
- Search history tracking
- Emergency services indicators

## 🚀 Quick Start

### Backend Setup
```bash
cd backend

# Install dependencies (already done)
pip install -r requirements.txt

# Run server
python app.py
```
Backend runs on: **http://localhost:5000**

### Frontend Setup
```bash
cd frontend

# Install dependencies (already done)
npm install

# Run React app
npm start
```
Frontend runs on: **http://localhost:3000**

## 📱 User Flow

1. **Landing Page** (/)
   - View features and benefits
   - Click "Sign Up" or "Login"

2. **Sign Up** (/signup)
   - Enter username, email, password
   - System sends OTP to email

3. **Verify OTP** (/verify-otp)
   - Enter 6-digit OTP from email
   - Account activated upon verification

4. **Dashboard** (/dashboard)
   - Search for hospitals
   - View on interactive map
   - Save to favorites
   - View search history

## 🔑 API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/verify-otp` - Verify email with OTP
- `POST /api/auth/resend-otp` - Resend OTP
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user (protected)

### Hospital Search
- `POST /api/search-hospitals-osm` - Search hospitals (protected)
- `POST /api/favorites` - Add to favorites (protected)
- `GET /api/favorites` - Get user favorites (protected)
- `DELETE /api/favorites/:id` - Remove from favorites (protected)
- `GET /api/search-history` - Get search history (protected)

## 📧 Email Configuration

The app uses Gmail SMTP for sending OTP emails:
- **Email**: nnearbycare@gmail.com
- **App Password**: afst bmbk aizi fjry (configured in backend)

## 🗄️ Database Schema

### Users Table
- id, username, email, password_hash
- is_verified, created_at

### OTP Table
- id, email, otp_code
- created_at, expires_at, is_used

### SearchHistory Table
- id, user_id, location
- latitude, longitude, search_date

### Favorites Table
- id, user_id, hospital_name
- hospital_address, place_id
- latitude, longitude, added_date

## 🎨 Pages Structure

```
src/
├── pages/
│   ├── LandingPage.js      # Home page with features
│   ├── Login.js            # Login form
│   ├── Signup.js           # Registration form
│   ├── VerifyOTP.js        # OTP verification
│   └── Dashboard.js        # Main app (hospital search)
├── components/
│   ├── SearchForm.js       # Location search input
│   ├── HospitalsList.js    # List of results
│   ├── MapView.js          # Interactive map
│   ├── Favorites.js        # Saved hospitals
│   └── SearchHistory.js    # Recent searches
└── styles/
    ├── LandingPage.css     # Landing page styles
    ├── Auth.css            # Login/signup styles
    └── Dashboard.css       # Dashboard styles
```

## 🔒 Security Features

- ✅ Password hashing with bcrypt
- ✅ JWT token authentication
- ✅ Email verification required
- ✅ OTP expiry mechanism
- ✅ Protected API routes
- ✅ CORS configuration
- ✅ Secure token storage

## 🌟 Technologies Used

### Backend
- **Flask** - Python web framework
- **SQLAlchemy** - ORM
- **Flask-Mail** - Email sending
- **PyJWT** - Token authentication
- **bcrypt** - Password hashing
- **SQLite** - Database

### Frontend
- **React** - UI library
- **React Router** - Navigation
- **Leaflet** - Interactive maps
- **CSS3** - Styling

### APIs
- **OpenStreetMap** - Hospital data (Free)
- **Nominatim** - Geocoding (Free)
- **Gmail SMTP** - Email delivery

## 📖 How to Use

### 1. First Time Setup
1. Open http://localhost:3000
2. You'll see the landing page
3. Click "Sign Up" to create account

### 2. Registration
1. Fill in username, email, password
2. Check your email for OTP
3. Enter the 6-digit OTP
4. You'll be logged in automatically

### 3. Using the App
1. Enter any location (city, area, address)
2. Choose search radius (1-20km)
3. Click "Search Hospitals"
4. View results on map and list
5. Add favorites for quick access
6. View your search history

## 🎉 What's Working

✅ Landing page with features  
✅ User registration  
✅ Email OTP verification  
✅ Login authentication  
✅ JWT token management  
✅ Hospital search with auth  
✅ Interactive maps  
✅ Favorites system  
✅ Search history  
✅ Logout functionality  
✅ Protected routes  
✅ Email sending via SMTP  

## 📧 Email Template

Users receive a beautifully formatted HTML email with:
- Nearby Care branding
- Large OTP display
- Expiry information
- Professional footer

## 🐛 Troubleshooting

### Email not received?
- Check spam folder
- Verify email address is correct
- Click "Resend OTP"

### Cannot login?
- Make sure email is verified
- Check password is correct
- Try password reset (if implemented)

### Search not working?
- Make sure you're logged in
- Check internet connection
- Try a different location

## 🚀 Deployment Notes

### Backend
- Update `SECRET_KEY` in production
- Use PostgreSQL instead of SQLite
- Enable HTTPS
- Configure email settings

### Frontend
- Build: `npm run build`
- Deploy to Vercel/Netlify
- Update API URL for production

## 📝 Future Enhancements

- Password reset functionality
- Profile page with settings
- Hospital reviews and ratings
- Directions integration
- Mobile app version
- Social login (Google, Facebook)

## 📞 Support

For issues or questions:
- Email: nnearbycare@gmail.com
- Check the FAQ section
- Review API documentation

---

**Made with ❤️ using Python Flask + React.js**

© 2025 Nearby Care. All rights reserved.
