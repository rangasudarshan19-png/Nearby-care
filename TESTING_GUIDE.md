# Quick Testing Guide - Phase 1 & 2 Features

## 🚀 Getting Started

1. **Backend:** Running on http://localhost:5000 ✓
2. **Frontend:** Running on http://localhost:3000 ✓
3. **Login with test account** or create new one

---

## ✅ Feature Testing Checklist

### 1. Advanced Hospital Filtering (Phase 1 #1)
**Location:** Search tab

**Test Steps:**
1. Enter a location (e.g., "New York")
2. Click "▼ Advanced Filters"
3. Test each filter:
   - **Hospital Type:** Select "hospital" → should filter results
   - **Min Rating:** Select "4" → only 4+ star hospitals
   - **Emergency Only:** Check box → only emergency hospitals
4. Verify results update in real-time

**Expected:** Filters work correctly, results match criteria

---

### 2. Hospital Details Page (Phase 1 #2)
**Location:** Search results

**Test Steps:**
1. Search for hospitals
2. Click "View Details" on any hospital card
3. Verify modal shows:
   - Hospital name, address, phone
   - Tabbed interface (Info/Doctors/Reviews)
4. Click "Doctors" tab → see doctors list
5. Click "Reviews" tab → see reviews
6. Click "Book Appointment" on a doctor
7. Close modal with X

**Expected:** All tabs work, data displays correctly, booking modal opens

---

### 3. Doctor Information & Search (Phase 1 #3)
**Location:** Doctors tab

**Test Steps:**
1. Click "Doctors" tab in dashboard
2. Verify 10 sample doctors display
3. Test specialty filter:
   - Select "Cardiology" → Dr. Sarah Johnson only
   - Select "Neurology" → Dr. Michael Chen only
   - Select "All Specialties" → all 10 doctors
4. Click "Book Appointment" on any doctor
5. Verify booking modal opens

**Expected:** Filter works, all doctors display correctly, booking initiates

---

### 4. Hospital Comparison (Phase 1 #5)
**Location:** Search results

**Test Steps:**
1. Search for hospitals (need at least 2 results)
2. Click "📊 Compare Hospitals" button
3. Select 2-3 hospitals using checkboxes
4. Click "Compare" button
5. Verify comparison table shows:
   - Name, Type, Distance, Rating, Reviews
   - Address, Phone, Website, Email
   - Emergency services, Hours, Doctors count
6. Test "Remove" button on a hospital
7. Close comparison modal

**Expected:** Comparison shows all attributes, remove works, max 3 hospitals

---

### 5. Emergency Services Locator (Phase 1 #6)
**Location:** Dashboard header

**Test Steps:**
1. Click "🚨 Emergency" button (pulsing red button)
2. Allow location access when prompted
3. Verify emergency modal shows:
   - Your current location detected
   - Nearest 5 emergency hospitals
   - Sorted by distance (nearest first)
   - Hospital name, address, phone, distance
4. Click 📞 911 button → verify call initiated
5. Click directions icon → verify Google Maps opens
6. Close modal

**Expected:** GPS works, hospitals sorted correctly, actions functional

---

### 6. Appointment Booking System (Phase 2 #9)

**Test Steps:**

**Part A - Book Appointment:**
1. Go to "Doctors" tab
2. Click "Book Appointment" on Dr. Sarah Johnson
3. Verify booking modal shows:
   - Doctor name & specialty
   - Hospital name
   - Date picker (next 30 days)
4. Select a date (e.g., tomorrow)
5. Verify time slots display (9:00 AM - 5:00 PM, 30-min intervals)
6. Click a time slot (e.g., 10:00 AM)
7. Add symptoms: "Chest pain, shortness of breath"
8. Add notes: "First-time visit"
9. Click "Book Appointment"
10. Verify success message and email notification

**Part B - View Appointments:**
1. Click "Appointments" tab
2. Verify appointment displays with:
   - Doctor name: Dr. Sarah Johnson
   - Specialty: Cardiology
   - Hospital name
   - Date & time: Tomorrow, 10:00 AM
   - Status: Scheduled (green badge)
   - Symptoms and notes
3. Test filter:
   - Click "Upcoming" → see appointment
   - Click "Completed" → empty
   - Click "Cancelled" → empty
   - Click "All" → see appointment

**Part C - Cancel Appointment:**
1. In "Appointments" tab
2. Click "Cancel Appointment" button
3. Confirm cancellation
4. Verify:
   - Status changes to "Cancelled" (red badge)
   - Button disappears or changes to "Cancelled"
5. Click "Cancelled" filter → see appointment

**Expected:** 
- Booking works, slots accurate, email sent
- Appointments display correctly with status badges
- Filters work properly
- Cancellation updates status

---

### 7. User Profile & Medical History (Phase 2 #10)

**Test Steps:**

**Part A - Update Profile:**
1. Click "My Profile" tab (new tab with 👤 icon)
2. Verify empty profile shows
3. Click "✏️ Edit Profile" button
4. Fill out form:
   - **Blood Type:** Select "O+"
   - **Emergency Contact:** "John Doe"
   - **Emergency Phone:** "+1 234 567 8900"
   - **Allergies:** "Penicillin, Pollen, Peanuts"
   - **Chronic Conditions:** "Hypertension, Type 2 Diabetes"
5. Click "💾 Save Changes"
6. Verify success message
7. Click "✖️ Cancel" to exit edit mode
8. Verify all fields show saved data (read-only)

**Part B - Add Medical Records:**
1. Scroll to "Medical Records" section
2. Verify "0 records" badge
3. Fill "Add New Record" form:
   - **Title:** "Annual Physical Exam"
   - **Date:** Today's date
   - **Description:** "Routine checkup. Blood pressure: 120/80. All vitals normal. Recommended exercise."
4. Click "➕ Add Record"
5. Verify success message and record appears

**Part C - Add More Records:**
1. Add second record:
   - **Title:** "Blood Test Results"
   - **Date:** 1 week ago
   - **Description:** "Complete blood count normal. Cholesterol slightly elevated at 210 mg/dL."
2. Add third record:
   - **Title:** "X-Ray - Chest"
   - **Date:** 2 months ago
   - **Description:** "No abnormalities detected. Lungs clear."
3. Verify all 3 records display

**Part D - Manage Records:**
1. Verify record cards show:
   - Title
   - Date (formatted: Month DD, YYYY)
   - Description
   - "Added: " timestamp
   - Delete button
2. Verify newest record is at top (sorted by date)
3. Verify "3 records" badge updated
4. Click "🗑️ Delete" on oldest record
5. Confirm deletion
6. Verify record removed and count updated to "2 records"

**Expected:**
- Profile saves and displays correctly
- Blood type dropdown works
- Medical records add, display, and delete properly
- Records sorted by date (newest first)
- Record count badge accurate
- Form validation prevents empty submissions

---

## 🧪 Cross-Feature Testing

### Test Integrated Workflows:

**Workflow 1: Emergency to Appointment**
1. Click "🚨 Emergency"
2. Find nearest hospital
3. Click hospital card
4. View doctors at that hospital
5. Book appointment with a doctor
6. Check appointment in "Appointments" tab

**Workflow 2: Search to Comparison to Booking**
1. Search "Los Angeles hospitals"
2. Compare 3 hospitals
3. Choose best one
4. View details
5. Browse doctors
6. Book appointment

**Workflow 3: Profile Setup Before Appointment**
1. Go to "My Profile"
2. Add blood type and allergies
3. Add past medical records
4. Go to "Doctors"
5. Book appointment (doctor can see profile)

---

## 📊 Database Verification

**Check if data persists:**

1. Book an appointment → refresh page → verify still there
2. Add medical record → refresh page → verify still there
3. Update profile → refresh page → verify saved
4. Add favorite hospital → refresh page → verify in favorites

---

## 🐛 Known Issues to Verify Fixed

1. ✓ Protobuf compatibility with Python 3.14 (downgraded to 3.20.3)
2. ✓ Cohere pydantic warnings (upgraded to 5.20.2)
3. ✓ Database creation with new models
4. ✓ Email notifications working

---

## 📧 Email Testing

**Verify appointment confirmation emails:**

1. Book appointment
2. Check email inbox for confirmation
3. Verify email contains:
   - Doctor name
   - Specialty
   - Hospital name
   - Date
   - Time
   - "Nearby Care" branding

**Note:** Uses Gmail SMTP (nnearbycare@gmail.com)

---

## 🎨 UI/UX Testing

**Visual checks:**

1. ✓ Emergency button has pulsing animation
2. ✓ Status badges have correct colors (green/blue/red)
3. ✓ Modals overlay properly
4. ✓ Tabs highlight active tab
5. ✓ Forms have proper validation messages
6. ✓ Loading spinners show during API calls
7. ✓ Success/error messages display
8. ✓ Responsive design on smaller screens

---

## 🔍 Edge Cases to Test

1. **No hospitals found** → verify message displays
2. **No available slots** → verify message shown
3. **Book same slot twice** → verify second booking prevented
4. **GPS denied** → verify manual entry works
5. **Empty fields in forms** → verify validation errors
6. **Delete last medical record** → verify empty state
7. **Filter with no results** → verify "no doctors" message

---

## 📈 Performance Checks

1. Search response time < 2 seconds
2. Modal opens instantly
3. Tab switching smooth (no lag)
4. Form submissions < 1 second
5. No console errors in browser DevTools

---

## ✅ Final Checklist

- [ ] All 10 features tested
- [ ] No console errors
- [ ] All API endpoints working
- [ ] Email notifications received
- [ ] Database persists data
- [ ] UI responsive and polished
- [ ] Error handling graceful
- [ ] User flows intuitive

---

## 📞 Support

**If issues found:**
1. Check browser console for errors
2. Check backend terminal for API errors
3. Verify database file exists: `backend/instance/nearby_care.db`
4. Verify both servers running (backend on 5000, frontend on 3000)

**Quick fixes:**
- Refresh page
- Clear browser cache
- Restart backend server
- Check network tab for failed requests

---

**Testing Status:** Ready for comprehensive testing  
**All features:** Implemented and deployed  
**Documentation:** Complete  

Happy Testing! 🎉
