"""
Automated UI Screenshot Capture for Nearby Care
Takes screenshots of all pages for documentation
"""
from playwright.sync_api import sync_playwright
import os
import time

BASE_URL = "http://localhost:3000"
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "Screenshots")

USER_EMAIL = "Rangasudarshan19@gmail.com"
USER_PASSWORD = "123456"
ADMIN_EMAIL = "admin@nearbycare.com"
ADMIN_PASSWORD = "admin123"


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def snap(page, folder, name, wait=1.5):
    """Take a full-page screenshot"""
    time.sleep(wait)
    try:
        page.wait_for_load_state("networkidle", timeout=5000)
    except Exception:
        pass
    time.sleep(0.5)
    filepath = os.path.join(folder, f"{name}.png")
    page.screenshot(path=filepath, full_page=True)
    print(f"  Saved: {name}.png")


def capture_screenshots():
    ensure_dir(SCREENSHOT_DIR)
    user_dir = os.path.join(SCREENSHOT_DIR, "User")
    admin_dir = os.path.join(SCREENSHOT_DIR, "Admin")
    ensure_dir(user_dir)
    ensure_dir(admin_dir)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1.5
        )
        page = context.new_page()

        # ===== PUBLIC PAGES =====
        print("\n=== Public Pages ===")
        page.goto(BASE_URL, wait_until="networkidle")
        snap(page, user_dir, "01_Landing_Page")

        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3)")
        snap(page, user_dir, "02_Landing_Features", 0.5)

        page.evaluate("window.scrollTo(0, document.body.scrollHeight * 2 / 3)")
        snap(page, user_dir, "03_Landing_HowItWorks", 0.5)

        page.goto(f"{BASE_URL}/signup", wait_until="networkidle")
        snap(page, user_dir, "04_Signup_Page")

        page.goto(f"{BASE_URL}/login", wait_until="networkidle")
        snap(page, user_dir, "05_Login_Page")

        # ===== USER LOGIN =====
        print("\n=== User Login & Dashboard ===")
        page.goto(f"{BASE_URL}/login", wait_until="networkidle")
        page.fill('input[type="email"]', USER_EMAIL)
        page.fill('input[type="password"]', USER_PASSWORD)
        page.click('button[type="submit"]')
        page.wait_for_url("**/dashboard**", timeout=10000)
        time.sleep(2)

        # Dashboard default = Search Hospitals tab
        snap(page, user_dir, "06_Dashboard_Search")

        # Dashboard tabs with exact labels from Dashboard.js
        user_tabs = [
            ("Find Doctors", "07_Find_Doctors"),
            ("My Appointments", "08_My_Appointments"),
            ("Favorites", "09_Favorites"),
            ("Search History", "10_Search_History"),
            ("My Profile", "11_User_Profile"),
            ("Symptom Advisor", "12_Symptom_Advisor"),
        ]
        for label, fname in user_tabs:
            try:
                page.locator(f'button.tab:has-text("{label}")').click(timeout=5000)
                snap(page, user_dir, fname)
            except Exception as e:
                print(f"  Skipped: {fname} - {str(e)[:60]}")

        # Emergency modal (separate button, not a tab)
        try:
            page.locator("button.btn-emergency").click(timeout=5000)
            snap(page, user_dir, "13_Emergency_Finder")
        except Exception as e:
            print(f"  Skipped: Emergency - {str(e)[:60]}")

        # ===== ADMIN LOGIN =====
        print("\n=== Admin Login & Dashboard ===")
        page.evaluate("localStorage.clear()")
        page.goto(f"{BASE_URL}/login", wait_until="networkidle")
        time.sleep(1)
        page.fill('input[type="email"]', ADMIN_EMAIL)
        page.fill('input[type="password"]', ADMIN_PASSWORD)
        page.click('button[type="submit"]')
        time.sleep(3)
        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass

        # Overview is default tab
        snap(page, admin_dir, "01_Admin_Overview")

        # Admin sidebar tabs with exact labels from AdminPanel.js
        admin_tabs = [
            ("Users", "02_Admin_Users"),
            ("Appointments", "03_Admin_Appointments"),
            ("Announcements", "04_Admin_Announcements"),
            ("System Logs", "05_Admin_Logs"),
        ]
        for label, fname in admin_tabs:
            try:
                page.locator(f'button.nav-item:has-text("{label}")').click(timeout=5000)
                snap(page, admin_dir, fname)
            except Exception as e:
                print(f"  Skipped: {fname} - {str(e)[:60]}")

        browser.close()

    # Summary
    user_count = len([f for f in os.listdir(user_dir) if f.endswith(".png")])
    admin_count = len([f for f in os.listdir(admin_dir) if f.endswith(".png")])
    print(f"\n=== Done! {user_count} user + {admin_count} admin = {user_count + admin_count} total ===")


if __name__ == "__main__":
    capture_screenshots()
