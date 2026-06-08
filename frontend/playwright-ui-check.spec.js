const { test, expect } = require('@playwright/test');

const user = {
  id: 2,
  username: 'ranga',
  email: 'rangasudarshan19@gmail.com',
  is_admin: false,
  role: 'user'
};

const admin = {
  id: 1,
  username: 'admin',
  email: 'admin@nearbycare.com',
  is_admin: true,
  role: 'admin'
};

async function mockCommonApi(page, currentUser) {
  await page.route('**/api/auth/me', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ user: currentUser })
  }));

  await page.route('**/api/symptom-chat', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({
      response: 'Drink fluids, rest, and monitor your temperature. Seek medical care if symptoms get worse or severe warning signs appear.',
      provider: 'local_fallback'
    })
  }));
}

function nextDateForUnavailableDay(availableShortDay) {
  const availableDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const availableIndex = availableDays.indexOf(availableShortDay);
  const date = new Date();
  date.setDate(date.getDate() + 1);

  for (let i = 0; i < 30; i += 1) {
    if (date.getDay() !== availableIndex) {
      return date.toISOString().split('T')[0];
    }
    date.setDate(date.getDate() + 1);
  }

  return date.toISOString().split('T')[0];
}

test('dashboard and symptom advisor render cleanly', async ({ page }) => {
  await mockCommonApi(page, user);
  await page.goto('http://localhost:3000/dashboard');
  await page.evaluate(({ user }) => {
    sessionStorage.setItem('token', 'ui-check-token');
    sessionStorage.setItem('user', JSON.stringify(user));
  }, { user });
  await page.reload();

  await expect(page.getByRole('button', { name: /Symptom Advisor/i })).toBeVisible();
  await page.getByRole('button', { name: /Symptom Advisor/i }).click();
  await expect(page.getByRole('heading', { name: /AI Health Assistant/i })).toBeVisible();
  await page.getByPlaceholder(/Describe your symptoms/i).fill('I have fever and headache');
  await page.locator('.btn-send').click();
  await expect(page.getByText(/Drink fluids/i)).toBeVisible();
  await page.screenshot({ path: '../Screenshots/playwright-dashboard-advisor.png', fullPage: true });
});

test('admin dashboard tabs render cleanly', async ({ page }) => {
  await mockCommonApi(page, admin);
  let adminDoctors = [{
    id: 501,
    name: 'Dr Existing',
    specialty: 'Cardiology',
    qualifications: 'MBBS, MD',
    experience_years: 9,
    consultation_fee: 600,
    hospital_id: '1001',
    hospital_name: 'Central Care Hospital',
    rating: 4.7,
    available_days: ['Mon', 'Wed'],
    available_hours: '09:00-17:00'
  }];
  page.on('dialog', dialog => dialog.accept());
  await page.route('**/api/admin/stats', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({
      users: { total: 2, active: 2, new_this_week: 1, suspended: 0 },
      appointments: { total: 1, scheduled: 1, cancelled: 0, recent_30_days: 1 },
      doctors: { total: 5, high_rated: 4 },
      searches: { total: 12, this_week: 4 }
    })
  }));
  await page.route('**/api/admin/users**', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ users: [admin, user] })
  }));
  await page.route('**/api/admin/appointments**', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ appointments: [] })
  }));
  await page.route('**/api/admin/logs**', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ logs: [] })
  }));
  await page.route('**/api/admin/announcements**', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ announcements: [] })
  }));
  await page.route('**/api/search-hospitals-osm', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({
      hospitals: [{
        id: 1001,
        name: 'Central Care Hospital',
        address: 'Main Road, Test City',
        latitude: 12.9,
        longitude: 77.6,
        distance: 1.2
      }],
      coordinates: { lat: 12.9, lon: 77.6 }
    })
  }));
  await page.route('**/api/admin/doctors**', route => {
    const method = route.request().method();
    if (method === 'GET') {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ doctors: adminDoctors })
      });
    }
    if (method === 'POST') {
      const payload = route.request().postDataJSON();
      adminDoctors = [{
        id: 502,
        ...payload,
        hospital_id: payload.hospital_id?.toString(),
        rating: Number(payload.rating || 0),
        consultation_fee: Number(payload.consultation_fee || 0)
      }, ...adminDoctors];
      return route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({ message: 'Doctor added successfully', doctor: adminDoctors[0] })
      });
    }
    if (method === 'DELETE') {
      adminDoctors = adminDoctors.filter(doctor => doctor.id !== 501);
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ message: 'Doctor deleted successfully', cancelled_appointments: 0 })
      });
    }
    return route.fallback();
  });

  await page.goto('http://localhost:3000/admin');
  await page.evaluate(({ admin }) => {
    sessionStorage.setItem('token', 'ui-check-admin-token');
    sessionStorage.setItem('user', JSON.stringify(admin));
  }, { admin });
  await page.reload();

  await expect(page.getByRole('heading', { name: /Dashboard Overview/i })).toBeVisible();
  await page.getByRole('button', { name: 'Users', exact: true }).click();
  await expect(page.getByText('admin@nearbycare.com')).toBeVisible();
  await page.getByRole('button', { name: 'Announcements', exact: true }).click();
  await expect(page.getByRole('heading', { name: /Send Email Announcement/i })).toBeVisible();
  await page.getByRole('button', { name: 'Doctors', exact: true }).click();
  await expect(page.getByRole('heading', { name: /Hospital Doctors/i })).toBeVisible();
  await expect(page.getByRole('heading', { name: /Existing Doctors/i })).toBeVisible();
  await expect(page.getByText('Dr Existing')).toBeVisible();
  await page.getByPlaceholder(/City, area/i).fill('Test City');
  await page.getByRole('button', { name: /Search Hospitals/i }).click();
  await page.getByRole('button', { name: /Central Care Hospital/i }).click();
  await page.locator('input[required]').first().fill('Dr Test');
  await page.getByPlaceholder(/Cardiology/i).fill('Cardiology');
  await page.getByRole('button', { name: 'Mon' }).click();
  await page.getByRole('button', { name: 'Add Doctor' }).click();
  await expect(page.getByText(/Doctor added successfully/i)).toBeVisible();
  await expect(page.getByText('Dr Test')).toBeVisible();
  await page.getByRole('row', { name: /Dr Existing/i }).getByRole('button', { name: 'Delete' }).click();
  await expect(page.getByText(/Doctor deleted successfully/i)).toBeVisible();
  await expect(page.getByText('Dr Existing')).not.toBeVisible();
  await page.screenshot({ path: '../Screenshots/playwright-admin.png', fullPage: true });
});

test('forgot password flow renders cleanly', async ({ page }) => {
  await page.route('**/api/auth/forgot-password/request', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ message: 'Password reset OTP sent successfully' })
  }));
  await page.route('**/api/auth/forgot-password/verify', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ message: 'OTP verified successfully' })
  }));
  await page.route('**/api/auth/forgot-password/reset', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ message: 'Password updated successfully' })
  }));

  await page.goto('http://localhost:3000/forgot-password');
  await page.getByLabel(/Registered Email/i).fill('user@example.com');
  await page.getByRole('button', { name: /Send OTP/i }).click();
  await expect(page.getByLabel(/Enter OTP/i)).toBeVisible();
  await page.getByLabel(/Enter OTP/i).fill('123456');
  await page.getByRole('button', { name: /Verify OTP/i }).click();
  await expect(page.getByLabel('New Password', { exact: true })).toBeVisible();
  await page.getByLabel('New Password', { exact: true }).fill('Newpass123!');
  await page.getByLabel('Confirm New Password', { exact: true }).fill('Newpass123!');
  await page.getByRole('button', { name: /Update Password/i }).click();
  await expect(page.getByText(/Password updated/i)).toBeVisible();
});

test('auth does not persist after closing all tabs', async ({ browser }) => {
  const context = await browser.newContext();
  const page = await context.newPage();
  await mockCommonApi(page, user);
  await page.route('**/api/auth/login', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ token: 'session-only-token', user })
  }));

  await page.goto('http://localhost:3000/login');
  await page.getByLabel(/Email/i).fill(user.email);
  await page.getByLabel(/Password/i).fill('Password123!');
  await page.getByRole('button', { name: /Sign In/i }).click();
  await expect(page.getByRole('button', { name: /Search Hospitals/i }).first()).toBeVisible();
  expect(await page.evaluate(() => sessionStorage.getItem('token'))).toBe('session-only-token');
  expect(await page.evaluate(() => localStorage.getItem('token'))).toBeNull();
  await context.close();

  const freshContext = await browser.newContext();
  const freshPage = await freshContext.newPage();
  await mockCommonApi(freshPage, user);
  await freshPage.goto('http://localhost:3000/dashboard');
  await expect(freshPage).toHaveURL(/\/login$/);
  await freshContext.close();
});

test('logout in one tab signs out other open tabs', async ({ browser }) => {
  const context = await browser.newContext();
  const firstTab = await context.newPage();
  const secondTab = await context.newPage();
  await mockCommonApi(firstTab, user);
  await mockCommonApi(secondTab, user);

  for (const page of [firstTab, secondTab]) {
    await page.goto('http://localhost:3000/dashboard');
    await page.evaluate(({ user }) => {
      sessionStorage.setItem('token', 'shared-session-token');
      sessionStorage.setItem('user', JSON.stringify(user));
    }, { user });
    await page.reload();
    await expect(page.getByRole('button', { name: /Search Hospitals/i }).first()).toBeVisible();
  }

  await firstTab.getByRole('button', { name: /Logout/i }).click();
  await expect(firstTab).toHaveURL(/\/login$/);
  await expect(secondTab).toHaveURL(/\/login$/, { timeout: 4000 });
  await context.close();
});

test('signup otp journey reaches dashboard', async ({ page }) => {
  await mockCommonApi(page, user);
  await page.route('**/api/auth/signup', route => route.fulfill({
    status: 201,
    contentType: 'application/json',
    body: JSON.stringify({ message: 'Signup successful. Please verify OTP sent to your email.' })
  }));
  await page.route('**/api/auth/verify-otp', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ message: 'Email verified successfully', token: 'signup-token', user })
  }));

  await page.goto('http://localhost:3000/signup');
  await page.getByLabel(/Username/i).fill('ranga');
  await page.getByLabel(/Email Address/i).fill('ranga@example.com');
  await page.getByLabel('Password', { exact: true }).fill('Strongpass123!');
  await page.getByLabel(/Confirm Password/i).fill('Strongpass123!');
  await page.getByRole('button', { name: /Sign Up/i }).click();
  await expect(page.getByRole('heading', { name: /Verify Your Email/i })).toBeVisible();
  await page.getByLabel(/Enter OTP/i).fill('123456');
  await page.getByRole('button', { name: /Verify Email/i }).click();
  await expect(page.getByText(/Email verified successfully/i)).toBeVisible();
  await expect(page.getByRole('button', { name: 'Search Hospitals' }).first()).toBeVisible({ timeout: 4000 });
});

test('doctor unavailable day cannot be booked', async ({ page }) => {
  const unavailableDate = nextDateForUnavailableDay('Mon');
  await mockCommonApi(page, user);
  await page.route('**/api/specialties', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ specialties: ['Cardiology'] })
  }));
  await page.route('**/api/doctors', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({
      doctors: [{
        id: 701,
        name: 'Dr Weekday',
        specialty: 'Cardiology',
        qualifications: 'MBBS',
        experience_years: 8,
        consultation_fee: 500,
        hospital_name: 'Central Care Hospital',
        rating: 4.6,
        available_days: ['Mon'],
        available_hours: '09:00-11:00'
      }]
    })
  }));
  await page.route('**/api/doctors/701/available-slots**', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ slots: ['09:00', '09:30'] })
  }));
  await page.route('**/api/appointments', route => route.fulfill({
    status: 201,
    contentType: 'application/json',
    body: JSON.stringify({ message: 'Appointment booked successfully' })
  }));

  await page.goto('http://localhost:3000/dashboard');
  await page.evaluate(({ user }) => {
    sessionStorage.setItem('token', 'ui-check-token');
    sessionStorage.setItem('user', JSON.stringify(user));
  }, { user });
  await page.reload();

  await page.getByRole('button', { name: /Find Doctors/i }).click();
  await expect(page.getByText('Dr Weekday')).toBeVisible();
  await page.getByRole('button', { name: /Book Appointment/i }).click();
  await page.getByLabel(/Select Date/i).fill(unavailableDate);
  await expect(page.locator('.error-text').filter({ hasText: /Doctor is not available on/i })).toBeVisible();
  await expect(page.getByRole('button', { name: /Confirm Booking/i })).toBeDisabled();
});
