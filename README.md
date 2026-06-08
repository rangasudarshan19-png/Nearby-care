# Nearby Care

Nearby Care is a full-stack hospital finder application with a Flask backend and React frontend.

## Start The App

Use the single batch file in the project root:

```bat
RUN.bat
```

`RUN.bat` starts everything:

- Flask backend at http://localhost:5000
- React frontend at http://localhost:3000
- Browser opens automatically at http://localhost:3000

Keep the Backend and Frontend command windows open while using the app. Close those windows to stop the servers.

## Requirements

- Python available in PATH
- Node.js and npm available in PATH

If `frontend/node_modules` is missing, `RUN.bat` installs frontend packages automatically.

## Backend

Manual backend commands:

```bat
cd backend
python app.py
```

Run backend tests:

```bat
cd backend
python -m pytest
```

## Frontend

Manual frontend commands:

```bat
cd frontend
npm start
```

Build frontend:

```bat
cd frontend
npm run build
```

Run frontend tests:

```bat
cd frontend
npm test -- --watchAll=false
```

## Environment

Set these in `backend/.env` when you need real integrations:

- `SMTP_SENDER` and `SMTP_APP_PASSWORD` for email and OTP delivery
- `GOOGLE_API_KEY` for Gemini-backed features
- `COHERE_API_KEY` for Cohere-backed ranking

Production also requires:

- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `DATABASE_URL`

## Verified Status

Latest local verification:

- Backend tests: 22 passing
- Backend syntax check: passing
- Frontend build: passing
- Frontend test command: passing, with no frontend test files present yet
