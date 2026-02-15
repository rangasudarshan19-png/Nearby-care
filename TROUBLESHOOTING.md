# 🚨 TROUBLESHOOTING GUIDE

## Common Issues and Solutions

### ❌ "Network error. Please try again" on Login Page

**Problem:** Frontend can't connect to backend

**Solutions:**

1. **Check if backend is running:**
   - Look for a window titled "Nearby Care - Backend"
   - Or check http://localhost:5000 in browser (should see "Not Found" - that's OK!)

2. **Restart servers:**
   ```
   stop-servers.bat
   start-servers.bat
   ```

3. **Check ports are free:**
   ```
   netstat -ano | findstr ":5000"
   netstat -ano | findstr ":3000"
   ```
   If you see output, ports are in use. Run `stop-servers.bat`

---

### ❌ Backend Crashes Immediately

**Problem:** Python dependencies missing or database corrupt

**Solutions:**

1. **Reinstall dependencies:**
   ```
   cd backend
   C:\Users\Chait\OneDrive\Desktop\Abhi\.venv\Scripts\pip.exe install -r requirements.txt
   ```

2. **Recreate database:**
   ```
   cd backend
   del nearby_care.db
   C:\Users\Chait\OneDrive\Desktop\Abhi\.venv\Scripts\python.exe create_db.py
   ```

---

### ❌ Frontend Shows Blank Page

**Problem:** Node modules missing or corrupted

**Solutions:**

1. **Reinstall node_modules:**
   ```
   cd frontend
   rmdir /s /q node_modules
   npm install
   ```

2. **Clear npm cache:**
   ```
   npm cache clean --force
   npm install
   ```

---

### ❌ Port Already in Use

**Problem:** Another app is using port 5000 or 3000

**Solutions:**

1. **Find and kill the process:**
   ```
   netstat -ano | findstr ":5000"
   taskkill /F /PID [PID_NUMBER]
   ```

2. **Or just use our stop script:**
   ```
   stop-servers.bat
   ```

---

### ❌ "Module not found" Errors

**Problem:** Dependencies not installed

**Solutions:**

**For Backend:**
```
cd backend
C:\Users\Chait\OneDrive\Desktop\Abhi\.venv\Scripts\pip.exe install -r requirements.txt
```

**For Frontend:**
```
cd frontend
npm install
```

---

## 🔍 System Health Check

Run this to diagnose issues:
```
check-system.bat
```

---

## 🆘 Still Not Working?

### Complete Reset:

1. Stop everything:
   ```
   stop-servers.bat
   ```

2. Delete database:
   ```
   cd backend
   del nearby_care.db
   ```

3. Reinstall frontend dependencies:
   ```
   cd frontend
   rmdir /s /q node_modules
   npm install
   ```

4. Recreate database:
   ```
   cd backend
   C:\Users\Chait\OneDrive\Desktop\Abhi\.venv\Scripts\python.exe create_db.py
   ```

5. Start fresh:
   ```
   start-servers.bat
   ```

---

## 📞 Check Logs

### Backend Logs:
Look at the window titled "Nearby Care - Backend" for error messages

### Frontend Logs:
Look at the window titled "Nearby Care - Frontend" for error messages

### Browser Console:
Press `F12` in browser → Console tab → Look for red errors

---

## ✅ Verification Steps

After starting servers, check:

1. **Backend:** Open http://localhost:5000 
   - Should see: `{"error": "Not Found"}` (This is GOOD!)

2. **Frontend:** Open http://localhost:3000
   - Should see: Nearby Care login page

3. **Login Test:** Try logging in with:
   - Email: `admin@nearbycare.com`
   - Password: `admin123`

If all three work, you're good to go! 🎉
