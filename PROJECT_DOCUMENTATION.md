# Nearby Care — Complete Project Documentation

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [Project Structure](#3-project-structure)
4. [Setup & Installation](#4-setup--installation)
5. [Environment Variables](#5-environment-variables)
6. [Database Schema](#6-database-schema)
7. [Authentication Flow](#7-authentication-flow)
8. [API Endpoints](#8-api-endpoints)
9. [Frontend Architecture](#9-frontend-architecture)
10. [AI System](#10-ai-system)
11. [Admin System](#11-admin-system)
12. [External APIs](#12-external-apis)
13. [Testing](#13-testing)
14. [Deployment](#14-deployment)

---

## 1. Project Overview

**Nearby Care** is a full-stack healthcare discovery platform that helps users find hospitals, compare doctors, book appointments, and get AI-powered health guidance.

### Key Capabilities
- **Hospital Search** — Location-based search using OpenStreetMap data with advanced filters (type, emergency, specialty, amenities, ownership)
- **AI-Powered Recommendations** — Hospitals scored and ranked based on symptoms using Google Gemini and Cohere AI
- **AI Symptom Chat** — Conversational AI that assesses symptoms, suggests specialties, and recommends nearby hospitals
- **Doctor Directory** — Browse doctors by specialty, view qualifications, check available slots
- **Appointment Booking** — Book appointments with date/time selection, email confirmations
- **Reviews & Ratings** — Rate and review hospitals with moderation support
- **User Dashboard** — Favorites, search history, medical records, profile management
- **Admin Panel** — User management, appointment oversight, review moderation, announcements, audit logs
- **Email OTP Verification** — Secure sign-up with 6-digit OTP sent via Gmail SMTP
- **JWT Authentication** — Token-based security with role-based access control

---

## 2. Tech Stack

### Backend
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.14 | Runtime |
| Flask | 3.1.0 | Web framework |
| Flask-SQLAlchemy | 3.1.1 | ORM |
| SQLAlchemy | 2.0.36 | Database toolkit |
| SQLite | — | Database (development) |
| PyJWT | 2.9.0 | JWT token generation & validation |
| bcrypt | 4.2.1 | Password hashing |
| Cohere SDK | 5.20.2 | AI hospital scoring (backup) |
| google-generativeai | 0.3.2 | AI hospital scoring + symptom chat (primary) |
| python-dotenv | 1.0.1 | Environment variable loading |
| requests | 2.32.3 | HTTP client for external APIs |
| Flask-CORS | 5.0.0 | Cross-origin request handling |
| gunicorn | 21.2.0 | Production WSGI server |

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| React | 18.2 | UI framework |
| react-router-dom | 6.20.1 | Client-side routing |
| axios | 1.6.2 | HTTP client |
| Leaflet | 1.9.4 | Interactive maps |
| react-leaflet | 4.2.1 | React wrapper for Leaflet |

### Design
| Element | Value |
|---|---|
| Primary Color | `#0ea5e9` (Sky Blue) |
| Primary Dark | `#0284c7` |
| Dark Background | `#0c4a6e` |
| Font | Inter (Google Fonts) |
| CSS Architecture | Custom properties via Theme.css |

---

## 3. Project Structure

```
nearby-care/
├── README.md                    # Quick start guide
├── PROJECT_DOCUMENTATION.md     # This file
├── .gitignore                   # Git ignore rules
├── start-all.bat                # Start both servers
├── start-servers.bat            # Start services
├── stop-servers.bat             # Stop all services
├── check-system.bat             # Diagnostics
│
├── backend/
│   ├── app.py                   # Main Flask application (~3,180 lines)
│   │                            #   - Database models (14 tables)
│   │                            #   - All API routes (~50 endpoints)
│   │                            #   - AI integration (Gemini + Cohere)
│   │                            #   - Email services (SMTP)
│   │                            #   - Admin system
│   │                            #   - Doctor/Appointment management
│   ├── config.py                # App configuration (Dev/Prod/Test)
│   ├── requirements.txt         # Python dependencies
│   ├── create_admin.py          # Create admin user utility
│   ├── create_db.py             # Database initialization utility
│   ├── pytest.ini               # Test configuration
│   ├── .env                     # Environment variables (NOT in git)
│   ├── .env.example             # Sample environment template
│   ├── start.bat / start-dev.bat
│   └── tests/
│       ├── conftest.py          # Pytest fixtures
│       ├── test_auth.py         # Auth endpoint tests
│       ├── test_appointments.py # Appointment tests
│       ├── test_hospitals.py    # Hospital search tests
│       └── test_profile.py     # Profile endpoint tests
│
└── frontend/
    ├── package.json             # Node dependencies
    ├── .env                     # Frontend env (NOT in git)
    ├── .env.example             # Sample frontend env
    ├── start-dev.bat
    ├── public/
    │   └── index.html           # HTML entry point
    └── src/
        ├── App.js               # Root component + routing
        ├── config.js            # API URL configuration
        ├── index.js             # React entry point
        ├── index.css            # Global styles
        ├── pages/
        │   ├── LandingPage.js   # Public landing page
        │   ├── Login.js         # Login form
        │   ├── Signup.js        # Registration form
        │   ├── VerifyOTP.js     # OTP verification
        │   ├── Dashboard.js     # Main user dashboard
        │   └── AdminPanel.js    # Admin dashboard
        ├── components/
        │   ├── SearchForm.js       # Hospital search with filters
        │   ├── HospitalsList.js    # Search results list
        │   ├── HospitalDetails.js  # Hospital detail view
        │   ├── HospitalComparison.js # Side-by-side comparison
        │   ├── MapView.js          # Leaflet map with markers
        │   ├── DoctorsList.js      # Doctor directory
        │   ├── AppointmentBooking.js # Book appointments
        │   ├── MyAppointments.js   # Manage appointments
        │   ├── Favorites.js        # Saved hospitals
        │   ├── Reviews.js          # Hospital reviews
        │   ├── SearchHistory.js    # Past searches
        │   ├── SymptomAdvisor.js   # AI chat interface
        │   ├── UserProfile.js      # Profile management
        │   ├── EmergencyFinder.js  # Emergency services
        │   └── AdminRoute.js       # Admin route guard
        ├── styles/
        │   ├── Theme.css           # Design tokens & variables
        │   ├── LandingPage.css     # Landing page styles
        │   ├── Auth.css            # Login/Signup styles
        │   ├── Dashboard.css       # Dashboard & component styles
        │   └── AdminPanel.css      # Admin panel styles
        └── utils/
            └── emergencyNumbers.js # Emergency contact data
```

---

## 4. Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm 9+
- Gmail account with App Password enabled

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your actual API keys and SMTP credentials

# Start server
python app.py
# Server runs on http://localhost:5000
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Start development server
npm start
# App runs on http://localhost:3000
```

### Quick Start (Windows)
```bash
# From project root
start-all.bat
# Opens backend + frontend in separate windows
# Visit http://localhost:3000
```

---

## 5. Environment Variables

### Backend (`backend/.env`)
| Variable | Required | Description |
|---|---|---|
| `FLASK_ENV` | No | `development` / `production` / `testing` |
| `SECRET_KEY` | Yes | Flask secret key for session signing |
| `SMTP_SENDER` | Yes | Gmail sender address |
| `SMTP_APP_PASSWORD` | Yes | Gmail App Password (not regular password) |
| `GOOGLE_API_KEY` | Yes | Google Gemini AI API key |
| `COHERE_API_KEY` | Yes | Cohere AI API key |
| `JWT_SECRET_KEY` | Yes | Secret for JWT token signing |
| `CORS_ORIGINS` | No | Allowed origins (default: `http://localhost:3000`) |
| `LOG_LEVEL` | No | Logging level (default: `INFO`) |

### Frontend (`frontend/.env`)
| Variable | Required | Description |
|---|---|---|
| `REACT_APP_API_URL` | Yes | Backend API URL (default: `http://localhost:5000`) |

### How to Get API Keys
- **Gmail App Password**: Google Account → Security → 2-Step Verification → App Passwords
- **Google Gemini**: https://aistudio.google.com/apikey
- **Cohere**: https://dashboard.cohere.com/api-keys

---

## 6. Database Schema

The application uses **14 tables** in SQLite. Tables are auto-created on first startup via `db.create_all()`.

### Core Tables

**User** — Application users
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary Key |
| username | String(80) | Unique, required |
| email | String(120) | Unique, required |
| password_hash | String(255) | bcrypt hashed |
| is_verified | Boolean | Email verification status |
| is_admin | Boolean | Admin flag |
| role | String(20) | `user` or `admin` |
| status | String(20) | `active`, `suspended`, or `banned` |
| last_login | DateTime | Last login timestamp |
| login_count | Integer | Total login count |
| created_at | DateTime | Registration date |

**OTP** — One-time passwords for email verification
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary Key |
| email | String(120) | Target email |
| otp_code | String(6) | 6-digit code |
| expires_at | DateTime | Valid for 10 minutes |
| is_used | Boolean | Consumed flag |

### Hospital Data Tables

**Favorite** — User's saved hospitals
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary Key |
| user_id | Integer | FK → User |
| hospital_name | String(255) | Hospital name |
| hospital_address | String(255) | Address |
| latitude / longitude | Float | GPS coordinates |

**SearchHistory** — Past search locations
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary Key |
| user_id | Integer | FK → User |
| location | String(255) | Search query or "GPS" |
| latitude / longitude | Float | Coordinates |
| search_date | DateTime | When searched |

**Review** — Hospital ratings & reviews
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary Key |
| hospital_id | String(64) | OSM element ID |
| hospital_name | String(255) | Name for display |
| user_id | Integer | FK → User |
| rating | Integer | 1–5 stars |
| comment | Text | Review text |
| is_flagged | Boolean | Moderation flag |
| flag_reason | Text | Why flagged |
| moderated_by | Integer | Admin who moderated |

### Doctor & Appointment Tables

**Doctor** — Doctor directory (10 seeded at startup)
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary Key |
| name | String(150) | Doctor name |
| specialty | String(100) | Medical specialty |
| qualifications | String(255) | Degrees (MD, FACC, etc.) |
| experience_years | Integer | Years of experience |
| consultation_fee | Float | Fee in INR |
| hospital_name | String(255) | Associated hospital |
| rating | Float | Average rating |
| available_days | String(100) | JSON array of days |
| available_hours | String(50) | e.g., "09:00-17:00" |

**Appointment** — Booked appointments
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary Key |
| user_id | Integer | FK → User |
| doctor_id | Integer | FK → Doctor |
| appointment_date | Date | Appointment date |
| appointment_time | String(10) | e.g., "10:00" |
| status | String(20) | `scheduled`, `completed`, or `cancelled` |
| symptoms | Text | Patient's symptoms |
| notes | Text | Additional notes |
| deleted_by | Integer | Admin who deleted (soft delete) |

### User Health Tables

**UserProfile** — Medical profile
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary Key |
| user_id | Integer | FK → User (unique) |
| blood_type | String(5) | e.g., A+, O- |
| allergies | Text | Known allergies |
| chronic_conditions | Text | Ongoing conditions |
| emergency_contact | String(150) | Emergency person |
| emergency_phone | String(20) | Emergency phone |

**MedicalRecord** — Health records
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary Key |
| user_id | Integer | FK → User |
| title | String(255) | Record title |
| description | Text | Details |
| date | Date | Record date |

### Admin Tables

**AdminLog** — Audit trail of all admin actions
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary Key |
| admin_id | Integer | FK → User |
| action | String(100) | Action type (e.g., `delete_user`) |
| target_type | String(50) | Target entity type |
| target_id | Integer | Target entity ID |
| details | Text | JSON details |
| ip_address | String(45) | Admin's IP |

**Announcement** — Admin email announcements
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary Key |
| admin_id | Integer | FK → User |
| subject | String(255) | Email subject |
| message | Text | Email body |
| recipient_type | String(50) | `all`, `active`, `new`, `specific` |
| status | String(20) | `draft`, `scheduled`, `sent`, `failed` |
| recipients_count | Integer | Total recipients |
| delivery_count | Integer | Successfully delivered |

**DoctorProfile, DoctorAvailability, SystemSetting** — Extended doctor management and system configuration tables.

---

## 7. Authentication Flow

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐     ┌──────────┐
│   SIGNUP     │────▶│  SEND OTP    │────▶│  VERIFY OTP    │────▶│  LOGIN   │
│              │     │  via Email   │     │  6-digit code  │     │          │
│ POST /signup │     │  (10 min)    │     │ POST /verify   │     │POST /login│
└─────────────┘     └──────────────┘     └────────────────┘     └──────────┘
                                                │                      │
                                                ▼                      ▼
                                         ┌─────────────┐       ┌─────────────┐
                                         │  JWT Token   │       │  JWT Token   │
                                         │  (7 days)    │       │  (7 days)    │
                                         └─────────────┘       └─────────────┘
                                                │                      │
                                                └──────────┬───────────┘
                                                           ▼
                                                   ┌──────────────┐
                                                   │  Stored in   │
                                                   │ localStorage │
                                                   └──────────────┘
                                                           │
                                                           ▼
                                                   ┌──────────────┐
                                                   │ Authorization │
                                                   │ Bearer <token>│
                                                   └──────────────┘
```

### Signup Process
1. User submits username, email, and password
2. Server validates uniqueness, hashes password with bcrypt
3. Creates `User` record (is_verified = false)
4. Generates random 6-digit OTP, stores in `OTP` table (expires in 10 minutes)
5. Sends OTP to email via Gmail SMTP
6. User enters OTP → verified → receives JWT token

### JWT Token
- **Algorithm**: HS256
- **Payload**: `{ user_id, exp }`
- **Expiry**: 7 days
- **Header**: `Authorization: Bearer <token>`

### Password Security
- Hashed with **bcrypt** (12 salt rounds)
- Never stored in plaintext
- Minimum 6 characters enforced

---

## 8. API Endpoints

### Authentication (Public)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/signup` | Register new user → sends OTP email |
| POST | `/api/auth/verify-otp` | Verify OTP → returns JWT |
| POST | `/api/auth/resend-otp` | Resend new OTP |
| POST | `/api/auth/login` | Login → returns JWT + user info |
| GET | `/api/auth/me` | Get current user (requires token) |

### Hospital Search (Authenticated)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/search-hospitals-osm` | Search hospitals by location/GPS with AI scoring |
| POST | `/api/suggest-specialty` | Get specialty suggestion from symptoms |

### Favorites (Authenticated)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/favorites` | Save hospital to favorites |
| GET | `/api/favorites` | List favorites |

### Search History (Authenticated)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/search-history` | Get past searches (param: `limit`) |

### Reviews (Public read, Authenticated write)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/reviews?hospital_id=X` | List reviews for a hospital |
| POST | `/api/reviews` | Write a review (1–5 stars + comment) |
| DELETE | `/api/reviews/<id>` | Delete review (owner or admin) |
| GET | `/api/reviews/summary?hospital_id=X` | Average rating + count |

### Doctors (Authenticated)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/doctors` | List doctors (filter: `specialty`, `hospital_id`) |
| GET | `/api/doctors/<id>` | Doctor details |
| GET | `/api/specialties` | List all specialties |
| GET | `/api/doctors/<id>/available-slots?date=X` | Available time slots |

### Appointments (Authenticated)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/appointments` | List user's appointments |
| POST | `/api/appointments` | Book appointment → sends email confirmation |
| PUT | `/api/appointments/<id>` | Update status/date/time |
| DELETE | `/api/appointments/<id>` | Cancel appointment |

### User Profile (Authenticated)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/user/profile` | Get profile |
| POST | `/api/user/profile` | Update medical profile |
| PUT | `/api/user/update-name` | Change display name |
| POST | `/api/user/send-email-otp` | Send OTP for email change |
| POST | `/api/user/verify-email-otp` | Verify and change email |
| POST | `/api/user/change-password` | Change password |
| DELETE | `/api/user/delete-account` | Delete account + all data |

### Medical Records (Authenticated)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/user/medical-records` | List records |
| POST | `/api/user/medical-records` | Add record |
| DELETE | `/api/user/medical-records/<id>` | Delete record |

### AI Symptom Chat (Authenticated)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/symptom-chat` | Chat with AI about symptoms. Auto-suggests nearby hospitals if severe symptoms + location provided |

### Health Check (Public)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` or `/api/health` | Server status, DB connectivity, AI status |

### Admin Endpoints (Admin role required)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/admin/stats` | Dashboard statistics |
| GET | `/api/admin/users` | List all users (paginated, searchable) |
| GET | `/api/admin/users/<id>` | User details + activity |
| PUT | `/api/admin/users/<id>/role` | Change user role |
| PUT | `/api/admin/users/<id>/status` | Suspend/ban/activate user |
| DELETE | `/api/admin/users/<id>` | Delete user + all data |
| GET | `/api/admin/appointments` | All appointments (filterable) |
| DELETE | `/api/admin/appointments/<id>` | Soft-delete with reason |
| GET | `/api/admin/reviews` | All reviews (filter: flagged) |
| PUT | `/api/admin/reviews/<id>/flag` | Flag/unflag review |
| DELETE | `/api/admin/reviews/<id>` | Delete review |
| GET | `/api/admin/logs` | Admin audit logs |
| GET | `/api/admin/system/logs` | Application log file |
| POST | `/api/admin/announcements` | Create/send announcements |
| GET | `/api/admin/announcements` | List announcements |

---

## 9. Frontend Architecture

### Routing
| Path | Component | Access |
|---|---|---|
| `/` | LandingPage | Public |
| `/login` | Login | Public (redirects if authenticated) |
| `/signup` | Signup | Public (redirects if authenticated) |
| `/verify-otp` | VerifyOTP | Public |
| `/dashboard` | Dashboard | Authenticated only |
| `/admin` | AdminPanel | Admin only |

### Pages

**LandingPage** — Marketing landing page with feature highlights, how-it-works section, statistics, and CTA buttons. Sky-blue gradient hero section.

**Login** — Email/password form. On success, stores JWT in localStorage and redirects to dashboard (or admin panel if admin).

**Signup** — Registration form (username, email, password). Validates input, calls signup API, redirects to OTP verification.

**VerifyOTP** — 6-digit OTP input with auto-focus. Includes resend button with countdown timer. On success, auto-redirects to dashboard.

**Dashboard** — Main user interface. Contains a sidebar/tab navigation to switch between:
- SearchForm + HospitalsList + MapView (hospital search)
- Favorites
- SearchHistory
- MyAppointments
- DoctorsList + AppointmentBooking
- SymptomAdvisor (AI chat)
- Reviews
- UserProfile
- EmergencyFinder
- HospitalComparison

**AdminPanel** — Full admin dashboard with sidebar navigation:
- Overview (stats cards, quick metrics)
- Users (table with search, role/status management)
- Appointments (table with filters, soft-delete)
- Reviews (moderation, flag/unflag)
- Logs (audit trail viewer)
- Announcements (compose and send emails)

### Key Components

**SearchForm** — Location input with GPS auto-detect, symptom field, radius slider, and advanced filters (hospital type, emergency only, specialty, amenities, ownership, sort order).

**MapView** — Interactive Leaflet map showing hospital markers with popups (name, address, rating, distance). Click marker for details.

**SymptomAdvisor** — Chat interface with AI. Users describe symptoms, AI responds with assessment, suggested specialties, and recommended hospitals. Supports location sharing for automatic nearby hospital search.

**UserProfile** — Tabbed profile management: edit display name, change email (with OTP verification), change password, view/manage medical profile, and delete account.

---

## 10. AI System

### Architecture
The AI system uses a cascading fallback approach:

```
Hospital Search Scoring:
  1. Google Gemini (gemini-pro) ← Primary
  2. Cohere (command → command-light → command-nightly) ← Backup
  3. Keyword Matching ← Always works (no API needed)

Symptom Chat:
  Google Gemini (gemini-flash-latest) ← Primary
  Fallback error message ← If API fails
```

### Hospital AI Scoring
When a user searches with symptoms, each hospital receives an AI score (0–100):
- AI receives hospital names, tags, specialties, and user symptoms
- Returns matching score + reasoning for each hospital
- Hospitals sorted by AI relevance score
- If AI APIs fail, keyword matching maps 27 symptom keywords to specialties

### Symptom Chat
- Conversational AI using Google Gemini
- Maintains chat history (last 6 messages for context)
- Severity detection: if AI identifies severe symptoms AND user shares location, automatically searches nearby hospitals via Overpass API
- Returns AI response + optionally `suggested_hospitals` array

### Keyword Mapping (Fallback)
Maps symptoms to medical specialties:
- heart/chest → Cardiology
- tooth/dental → Dentistry
- bone/fracture → Orthopedics
- skin/rash → Dermatology
- eye/vision → Ophthalmology
- child/baby → Pediatrics
- mental/depression → Psychiatry
- And 20+ more mappings

---

## 11. Admin System

### Default Admin Account
- **Email**: admin@nearbycare.com
- **Password**: admin123
- Auto-created on first server startup

### Admin Capabilities

**User Management**
- View all users with pagination and search
- View individual user details + activity (recent appointments, searches)
- Change user role (user ↔ admin)
- Change user status (active / suspended / banned)
- Delete users and all their associated data

**Appointment Management**
- View all appointments across all users
- Filter by status (scheduled, completed, cancelled)
- Soft-delete appointments with reason (records who deleted and why)

**Review Moderation**
- View all reviews with flagged-only filter
- Flag inappropriate reviews with reason
- Unflag reviews after resolution
- Permanently delete reviews

**Announcements**
- Compose email announcements with subject and body
- Target recipients: All users, Active users (last 30 days), New users (last 7 days), or Specific users
- Save as draft or send immediately
- Track delivery counts

**Audit Logs**
- Every admin action logged with: admin ID, action type, target, details, IP address, timestamp
- Filterable by action type and admin
- Paginated log viewer

**System Logs**
- View application log file directly from admin panel
- Filter by log level (ERROR, WARNING, INFO)
- Configurable number of lines to display

### Security
- `@admin_required()` decorator on all admin routes
- Checks JWT token + `user.role == 'admin'`
- Admins cannot modify their own role/status
- Admins cannot delete themselves

---

## 12. External APIs

### OpenStreetMap — Nominatim (Geocoding)
- **URL**: `https://nominatim.openstreetmap.org/search`
- **Purpose**: Convert location text to latitude/longitude
- **Rate Limit**: 1 request/second (fair use)
- **No API key required**

### OpenStreetMap — Overpass API (Hospital Data)
- **URL**: `https://overpass-api.de/api/interpreter`
- **Purpose**: Query hospitals, clinics, and dentists within a radius
- **Data**: OSM tags (name, address, amenity type, emergency services, specialties, etc.)
- **No API key required**

### Google Gemini AI
- **Models**: `gemini-pro` (hospital scoring), `gemini-flash-latest` (symptom chat)
- **Free Tier**: 60 requests/minute, 1,500 requests/day
- **Purpose**: Score hospitals against symptoms, conversational symptom assessment
- **API Key**: Required (see Google AI Studio)

### Cohere AI
- **Models**: `command` → `command-light` → `command-nightly` (tried in order)
- **Free Tier**: ~100 requests/minute, 1,000 API calls/month
- **Purpose**: Backup AI for hospital scoring when Gemini fails
- **API Key**: Required (see Cohere Dashboard)

### Gmail SMTP
- **Server**: `smtp.gmail.com:465` (SSL)
- **Purpose**: Send OTP verification emails, appointment confirmations, admin announcements
- **Requires**: Gmail App Password (not regular password)

---

## 13. Testing

### Backend Tests (pytest)
```bash
cd backend
python -m pytest tests/ -v
```

Test files:
- `test_auth.py` — Signup, OTP verification, login, token validation
- `test_appointments.py` — Booking, listing, cancellation
- `test_hospitals.py` — Hospital search, favorites, reviews
- `test_profile.py` — Profile CRUD, medical records

### Manual Testing
```bash
# Quick test (Windows)
cd backend
test.bat
```

### Test Coverage
- 16 automated pytest tests
- 42 API endpoint tests verified manually
- All endpoints return correct status codes and response formats

---

## 14. Deployment

### Production Checklist
1. Set `FLASK_ENV=production` in `.env`
2. Generate strong `SECRET_KEY` and `JWT_SECRET_KEY`
3. Configure production database URL (PostgreSQL recommended)
4. Set `CORS_ORIGINS` to your production domain
5. Use gunicorn: `gunicorn -w 4 -b 0.0.0.0:5000 app:app`
6. Build frontend: `cd frontend && npm run build`
7. Serve frontend build with Nginx or similar
8. Enable HTTPS
9. Set up proper logging and monitoring

### Environment-Specific Config
- **Development**: Debug mode, SQLite, liberal CORS
- **Production**: No debug, PostgreSQL, restricted CORS, gunicorn
- **Testing**: In-memory SQLite, no email sending

---

*Last updated: February 2026*
