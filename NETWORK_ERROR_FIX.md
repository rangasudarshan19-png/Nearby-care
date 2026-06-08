# Network Error Fix Guide - Nearby Care App

## Problem
Getting "Network error. Please try again. Error: Failed to fetch" when trying to sign up or use the app.

## Common Causes & Solutions

### 1. **Backend Server Not Running** (Most Common)
The frontend is trying to connect to `http://localhost:5000` but the backend server isn't running.

**Fix:**
```bash
# Option 1: Use the single startup script
RUN.bat

# Option 2: Manual startup in separate terminal windows
# Terminal 1 - Backend:
cd backend
python app.py

# Terminal 2 - Frontend:
cd frontend
npm start
```

**Check if backend is running:**
- Open browser and go to `http://localhost:5000`
- You should see API routes listed
- Or check if port 5000 is listening: `netstat -ano | findstr :5000`

---

### 2. **Python Dependencies Not Installed**
Backend needs Flask, SQLAlchemy, etc.

**Fix:**
```bash
cd backend
pip install -r requirements.txt
```

If pip fails, try:
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**Verify installation:**
```bash
python -c "import flask; import flask_cors; print('OK')"
```

---

### 3. **Database Not Created**
Backend needs the SQLite database to exist.

**Fix:**
```bash
cd backend
python create_db.py
```

This will create `nearby_care.db` with all tables.

**Verify:**
- Check if file exists: `nearby_care.db` should appear in backend folder
- Should be ~50KB after creation

---

### 4. **Node/npm Dependencies Not Installed**
Frontend needs React and other packages.

**Fix:**
```bash
cd frontend
npm install
```

**Verify:**
```bash
npm --version
node --version
```

---

### 5. **Port Already in Use**
Another app might be using port 5000 or 3000.

**Fix:**
```bash
# Check what's using port 5000 (Windows):
netstat -ano | findstr :5000

# Kill the process (if safe):
taskkill /PID <process_id> /F

# Or use different ports in code:
# Backend: python app.py (edit app.py to change port)
# Frontend: PORT=3001 npm start
```

---

### 6. **CORS Configuration Issue**
Frontend and backend aren't communicating due to CORS settings.

**Current config allows:**
- `http://localhost:3000` ✓
- `http://localhost:3001` ✓
- `http://127.0.0.1:3000` ✓

**If frontend is on different URL:**
- Edit `backend/config.py`
- Update `CORS_ORIGINS` line with your frontend URL

---

## Quick Diagnostic Steps

Run these in order:

1. **Check Python:**
   ```bash
   python --version
   ```

2. **Check Node/npm:**
   ```bash
   npm --version
   ```

3. **Verify backend dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   python -c "import flask; print('OK')"
   ```

4. **Create database:**
   ```bash
   cd backend
   python create_db.py
   ```

5. **Test backend start:**
   ```bash
   cd backend
   python app.py
   ```
   - Should show: "Running on http://0.0.0.0:5000"
   - Keep this running and open new terminal

6. **Test frontend:**
   ```bash
   cd frontend
   npm start
   ```
   - Browser should open at http://localhost:3000

7. **Test connection:**
   - Try signing up
   - Check browser DevTools Console for exact error

---

## Error Messages & Meanings

| Error | Cause | Fix |
|-------|-------|-----|
| `ERR_CONNECTION_REFUSED` | Backend not running | Start backend with `python app.py` |
| `Failed to fetch` | Network unreachable | Check backend is on correct port |
| `CORS error` | Frontend/backend URL mismatch | Update CORS_ORIGINS in config.py |
| `ModuleNotFoundError: flask` | Dependencies not installed | Run `pip install -r requirements.txt` |
| `no such table: user` | Database not created | Run `python create_db.py` |
| `Port 5000 already in use` | Another process using port | Kill that process or change port |

---

## Full Fresh Start (Nuclear Option)

If nothing works:

```bash
# Clean up
cd backend
del nearby_care.db  (delete database)
rmdir /s /q __pycache__
pip uninstall -y -r requirements.txt

# Reinstall everything
pip install -r requirements.txt
python create_db.py

# Clean frontend
cd ../frontend
rmdir /s /q node_modules
del package-lock.json
npm install

# Start fresh
cd ..
RUN.bat
```

---

## Default Admin Account

After backend starts, default admin is created:
- **Email:** `admin@nearbycare.com`
- **Password:** `admin123`
- ⚠️ Change this in production!

---

## Need More Help?

Check these logs:
- `backend/logs/app.log` - Backend logs
- Browser Console - Frontend errors (F12 → Console tab)
- Terminal windows - Live output from servers

---

## Quick Fixes Checklist

- [ ] Python installed? (`python --version`)
- [ ] Node.js installed? (`npm --version`)
- [ ] Backend dependencies installed? (`pip install -r requirements.txt`)
- [ ] Database created? (`nearby_care.db` exists in backend folder)
- [ ] Backend running? (Start with `cd backend && python app.py`)
- [ ] Frontend running? (Start with `cd frontend && npm start`)
- [ ] Can access `http://localhost:5000`? 
- [ ] Can access `http://localhost:3000`?
- [ ] Ports 5000 and 3000 not blocked by firewall?

