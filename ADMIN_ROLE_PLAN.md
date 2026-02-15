# Admin Role Implementation Plan

## Overview
Comprehensive admin dashboard with advanced management capabilities, analytics, and system monitoring.

---

## 1. Core Admin Features (Requested)

### 1.1 Appointment Management
- **Delete Appointments**: Remove appointments with reason tracking
- **View All Appointments**: Filter by status, date, user, doctor
- **Cancel Bulk Appointments**: Cancel multiple appointments (e.g., doctor unavailable)
- **Appointment Analytics**: View booking trends, cancellation rates

### 1.2 Email Announcements
- **Broadcast Emails**: Send announcements to all users or specific segments
- **Scheduled Emails**: Schedule emails for future delivery
- **Email Templates**: Pre-built templates for common announcements
- **Email History**: Track all sent announcements with delivery status
- **User Segmentation**: Target specific user groups (active users, new signups, etc.)

### 1.3 User Role Management
- **Promote to Admin**: Grant admin privileges to existing users
- **Revoke Admin**: Remove admin access from users
- **View Admin Activity**: Log all admin actions for audit trail
- **Permission Levels**: Different admin tiers (super admin, moderator, support)

### 1.4 System Logs Viewer
- **Application Logs**: View real-time and historical app logs
- **Error Tracking**: Filter by error severity (ERROR, WARNING, INFO)
- **Search & Filter**: Search logs by date, user, endpoint, error message
- **Download Logs**: Export logs for external analysis
- **Log Retention**: Configure log retention policies

---

## 2. Additional Admin Features

### 2.1 User Management
- **View All Users**: Paginated list with search and filters
- **User Details**: View complete user profile, activity, appointments
- **Suspend/Ban Users**: Temporarily or permanently disable accounts
- **Reset Passwords**: Force password reset for security issues
- **Verify Users**: Manually verify user accounts
- **Export User Data**: GDPR compliance - export user data on request

### 2.2 Doctor Management
- **Add Doctors**: Create new doctor profiles with specialties, availability
- **Edit Doctor Info**: Update doctor details, schedules, fees
- **Delete Doctors**: Remove doctors (with appointment handling)
- **Doctor Verification**: Approve/verify doctor credentials
- **Availability Management**: Set working hours, holidays, time slots
- **Doctor Analytics**: Performance metrics, patient ratings

### 2.3 Review Moderation
- **View All Reviews**: List all hospital and doctor reviews
- **Flag Inappropriate**: Mark reviews for manual review
- **Delete Reviews**: Remove spam, abusive, or fake reviews
- **Respond to Reviews**: Admin responses to user feedback
- **Review Analytics**: Sentiment analysis, trending issues

### 2.4 Hospital/Facility Management
- **Verify Hospitals**: Approve hospital listings from Google API
- **Update Hospital Info**: Add/edit amenities, services, contact info
- **Feature Hospitals**: Mark top-rated or partner hospitals
- **Hospital Analytics**: View search trends, favorite counts

### 2.5 Analytics Dashboard
- **User Metrics**: Total users, active users, new signups, retention
- **Appointment Stats**: Bookings per day/week/month, cancellation rates
- **Search Analytics**: Popular searches, location trends
- **Revenue Metrics**: (If payment integration) Revenue tracking
- **System Health**: API response times, database size, error rates
- **Geographic Insights**: User distribution by location

### 2.6 System Monitoring
- **Health Dashboard**: Real-time system status (database, APIs, services)
- **API Usage**: Track API calls to external services (Google, Cohere)
- **Performance Metrics**: Response times, slow queries
- **Database Stats**: Table sizes, query performance
- **Alerts & Notifications**: Email/SMS alerts for critical issues

### 2.7 Content Management
- **FAQ Management**: Add/edit/delete FAQ entries
- **Announcement Banners**: Display site-wide notifications
- **Terms & Privacy**: Update legal documents
- **Help Center**: Manage support articles

### 2.8 Backup & Data Export
- **Database Backups**: Manual and scheduled backups
- **Export Reports**: CSV/Excel exports for all data entities
- **Data Retention**: Configure data retention policies
- **Audit Trail**: Complete log of all admin actions

---

## 3. Database Schema Changes

### 3.1 New Tables

```sql
-- Admin activity logging
CREATE TABLE admin_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,
    action VARCHAR(100) NOT NULL,  -- 'delete_appointment', 'send_announcement', 'grant_admin', etc.
    target_type VARCHAR(50),        -- 'user', 'appointment', 'doctor', etc.
    target_id INTEGER,
    details TEXT,                   -- JSON details of the action
    ip_address VARCHAR(45),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES user(id)
);

-- Email announcements
CREATE TABLE announcements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,
    subject VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    recipient_type VARCHAR(50),     -- 'all', 'active', 'new', 'specific'
    recipient_ids TEXT,             -- JSON array of user IDs for specific targeting
    scheduled_at DATETIME,          -- NULL for immediate send
    sent_at DATETIME,
    status VARCHAR(20),             -- 'draft', 'scheduled', 'sent', 'failed'
    recipients_count INTEGER,
    delivery_count INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES user(id)
);

-- Doctor profiles
CREATE TABLE doctor_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    specialty VARCHAR(100) NOT NULL,
    hospital_name VARCHAR(255),
    hospital_address TEXT,
    qualification VARCHAR(255),
    experience_years INTEGER,
    consultation_fee DECIMAL(10, 2),
    phone VARCHAR(20),
    email VARCHAR(255),
    bio TEXT,
    verified BOOLEAN DEFAULT FALSE,
    rating DECIMAL(3, 2),
    total_reviews INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Doctor availability
CREATE TABLE doctor_availability (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,  -- 0=Monday, 6=Sunday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    slot_duration INTEGER DEFAULT 30,  -- minutes
    is_available BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (doctor_id) REFERENCES doctor_profiles(id)
);

-- System settings
CREATE TABLE system_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    updated_by INTEGER,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (updated_by) REFERENCES user(id)
);
```

### 3.2 Modify Existing Tables

```sql
-- Add role and status to user table
ALTER TABLE user ADD COLUMN role VARCHAR(20) DEFAULT 'user';  -- 'user', 'admin', 'super_admin'
ALTER TABLE user ADD COLUMN status VARCHAR(20) DEFAULT 'active';  -- 'active', 'suspended', 'banned'
ALTER TABLE user ADD COLUMN last_login DATETIME;
ALTER TABLE user ADD COLUMN login_count INTEGER DEFAULT 0;

-- Add deletion tracking to appointments
ALTER TABLE appointment ADD COLUMN deleted_by INTEGER;
ALTER TABLE appointment ADD COLUMN deleted_at DATETIME;
ALTER TABLE appointment ADD COLUMN deletion_reason TEXT;

-- Add moderation to reviews
ALTER TABLE review ADD COLUMN is_flagged BOOLEAN DEFAULT FALSE;
ALTER TABLE review ADD COLUMN flag_reason TEXT;
ALTER TABLE review ADD COLUMN moderated_by INTEGER;
ALTER TABLE review ADD COLUMN moderated_at DATETIME;
```

---

## 4. API Endpoints

### 4.1 Admin Authentication
```
POST   /api/admin/login              - Admin login with role verification
GET    /api/admin/verify              - Verify admin token and permissions
```

### 4.2 User Management
```
GET    /api/admin/users               - List all users (paginated, searchable)
GET    /api/admin/users/:id           - Get user details
PUT    /api/admin/users/:id/role      - Update user role
PUT    /api/admin/users/:id/status    - Suspend/activate user
DELETE /api/admin/users/:id           - Delete user account
POST   /api/admin/users/:id/reset-password  - Force password reset
GET    /api/admin/users/:id/activity  - Get user activity log
POST   /api/admin/users/:id/export    - Export user data (GDPR)
```

### 4.3 Appointment Management
```
GET    /api/admin/appointments        - List all appointments (filtered)
DELETE /api/admin/appointments/:id    - Delete appointment with reason
POST   /api/admin/appointments/bulk-cancel  - Cancel multiple appointments
GET    /api/admin/appointments/stats  - Appointment analytics
```

### 4.4 Email Announcements
```
POST   /api/admin/announcements       - Create announcement
GET    /api/admin/announcements       - List all announcements
GET    /api/admin/announcements/:id   - Get announcement details
PUT    /api/admin/announcements/:id   - Update announcement
DELETE /api/admin/announcements/:id   - Delete announcement
POST   /api/admin/announcements/:id/send  - Send announcement immediately
GET    /api/admin/announcements/:id/stats - Delivery statistics
```

### 4.5 Doctor Management
```
POST   /api/admin/doctors             - Create doctor profile
GET    /api/admin/doctors             - List all doctors
GET    /api/admin/doctors/:id         - Get doctor details
PUT    /api/admin/doctors/:id         - Update doctor profile
DELETE /api/admin/doctors/:id         - Delete doctor
PUT    /api/admin/doctors/:id/verify  - Verify doctor credentials
POST   /api/admin/doctors/:id/availability  - Set availability schedule
GET    /api/admin/doctors/:id/stats   - Doctor performance metrics
```

### 4.6 Review Moderation
```
GET    /api/admin/reviews             - List all reviews (flagged first)
PUT    /api/admin/reviews/:id/flag    - Flag review
DELETE /api/admin/reviews/:id         - Delete review
POST   /api/admin/reviews/:id/respond - Admin response to review
GET    /api/admin/reviews/stats       - Review analytics
```

### 4.7 Analytics
```
GET    /api/admin/analytics/users     - User metrics
GET    /api/admin/analytics/appointments  - Appointment stats
GET    /api/admin/analytics/searches  - Search trends
GET    /api/admin/analytics/revenue   - Revenue metrics
GET    /api/admin/analytics/geo       - Geographic distribution
GET    /api/admin/analytics/dashboard - Combined dashboard metrics
```

### 4.8 System Logs
```
GET    /api/admin/logs                - Get application logs (paginated)
GET    /api/admin/logs/errors         - Get error logs only
GET    /api/admin/logs/search         - Search logs
GET    /api/admin/logs/download       - Download log file
GET    /api/admin/logs/admin-activity - Admin action audit trail
```

### 4.9 System Monitoring
```
GET    /api/admin/system/health       - System health status
GET    /api/admin/system/performance  - Performance metrics
GET    /api/admin/system/database     - Database statistics
GET    /api/admin/system/api-usage    - External API usage stats
POST   /api/admin/system/backup       - Trigger database backup
```

### 4.10 Settings
```
GET    /api/admin/settings            - Get all system settings
PUT    /api/admin/settings/:key       - Update setting
POST   /api/admin/settings            - Create new setting
```

---

## 5. Frontend Components

### 5.1 Admin Dashboard Layout
```
src/pages/admin/
├── AdminLayout.js           - Main admin layout with sidebar
├── Dashboard.js             - Overview with key metrics
├── Users/
│   ├── UserList.js          - User management table
│   ├── UserDetails.js       - Individual user details
│   └── UserRoles.js         - Role assignment interface
├── Appointments/
│   ├── AppointmentList.js   - All appointments view
│   └── AppointmentStats.js  - Analytics charts
├── Announcements/
│   ├── AnnouncementList.js  - List announcements
│   ├── CreateAnnouncement.js - Compose email
│   └── AnnouncementStats.js - Delivery metrics
├── Doctors/
│   ├── DoctorList.js        - Doctor management
│   ├── DoctorForm.js        - Add/edit doctor
│   └── AvailabilityEditor.js - Set schedules
├── Reviews/
│   ├── ReviewModerator.js   - Review moderation
│   └── ReviewStats.js       - Sentiment analysis
├── Analytics/
│   ├── UserAnalytics.js     - User metrics dashboard
│   ├── AppointmentAnalytics.js
│   └── SearchAnalytics.js   - Search trends
├── Logs/
│   ├── LogViewer.js         - Real-time log viewer
│   ├── ErrorLogs.js         - Error tracking
│   └── AdminActivityLog.js  - Audit trail
└── Settings/
    ├── SystemSettings.js    - Configuration panel
    └── BackupRestore.js     - Backup management
```

### 5.2 Admin Sidebar Navigation
```jsx
- Dashboard
- Users
  - All Users
  - Admin Roles
  - Suspended Users
- Appointments
  - All Appointments
  - Analytics
- Announcements
  - Create New
  - History
- Doctors
  - Doctor List
  - Add Doctor
  - Verification Queue
- Reviews
  - Moderate Reviews
  - Flagged Reviews
- Analytics
  - User Metrics
  - Appointment Stats
  - Search Trends
  - Revenue
- System
  - Logs
  - Health Monitor
  - Settings
  - Backups
```

---

## 6. Security & Permissions

### 6.1 Role Hierarchy
1. **Super Admin**: Full access to all features
2. **Admin**: Most features except user role changes
3. **Moderator**: Limited to content moderation (reviews, users)
4. **Support**: Read-only access to user data and logs

### 6.2 Security Measures
- **Two-Factor Authentication**: Required for admin accounts
- **IP Whitelisting**: Restrict admin access by IP
- **Session Timeout**: Auto-logout after inactivity
- **Action Confirmation**: Require confirmation for destructive actions
- **Audit Logging**: Log all admin actions with timestamps
- **Rate Limiting**: Prevent abuse of admin endpoints
- **Encryption**: Encrypt sensitive data in transit and at rest

### 6.3 Protected Routes
```python
# Middleware decorator
def admin_required(level='admin'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentication required'}), 401
            if current_user.role not in ['admin', 'super_admin']:
                return jsonify({'error': 'Admin access required'}), 403
            if level == 'super_admin' and current_user.role != 'super_admin':
                return jsonify({'error': 'Super admin access required'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

---

## 7. Implementation Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Database schema updates
- [ ] Admin role system and middleware
- [ ] Basic admin dashboard layout
- [ ] Admin login and authentication

### Phase 2: Core Features (Week 3-4)
- [ ] User management (view, suspend, role assignment)
- [ ] Appointment deletion with tracking
- [ ] Email announcement system
- [ ] Admin activity logging

### Phase 3: Extended Features (Week 5-6)
- [ ] Doctor management (CRUD operations)
- [ ] Review moderation
- [ ] Analytics dashboard (basic metrics)
- [ ] Log viewer implementation

### Phase 4: Advanced Features (Week 7-8)
- [ ] Advanced analytics (charts, trends)
- [ ] System monitoring dashboard
- [ ] Backup and export functionality
- [ ] Scheduled announcements

### Phase 5: Polish & Testing (Week 9-10)
- [ ] UI/UX improvements
- [ ] Security hardening
- [ ] Performance optimization
- [ ] Comprehensive testing
- [ ] Documentation

---

## 8. Technical Stack

### Backend
- **Flask-Admin**: Admin panel scaffolding (optional)
- **Celery**: Background tasks for email sending
- **Redis**: Task queue for Celery
- **SQLAlchemy**: Database ORM
- **Pandas**: Data export and analytics
- **Matplotlib/Plotly**: Chart generation

### Frontend
- **Recharts**: Analytics charts and graphs
- **React-Table**: Advanced data tables
- **React-Quill**: Rich text editor for announcements
- **React-DatePicker**: Date range selection
- **React-Select**: Multi-select for user targeting

### Email Service
- **SendGrid** or **AWS SES**: Bulk email delivery
- **Mailgun**: Alternative email service
- **Email Templates**: Handlebars or Jinja2

---

## 9. Email Announcement Features

### 9.1 Recipient Targeting
```python
# User segments
SEGMENTS = {
    'all': "All users",
    'active': "Active users (logged in last 30 days)",
    'new': "New users (registered last 7 days)",
    'inactive': "Inactive users (no login for 90 days)",
    'verified': "Verified email users",
    'with_appointments': "Users with appointments",
    'specific': "Specific user IDs"
}
```

### 9.2 Email Templates
- Welcome Announcement
- System Maintenance Notice
- New Feature Release
- Policy Updates
- Promotional Offers
- Survey/Feedback Request

### 9.3 Scheduling Options
- Send immediately
- Schedule for specific date/time
- Recurring announcements (weekly, monthly)
- A/B testing variants

---

## 10. Monitoring & Alerts

### 10.1 Alert Types
- High error rate (>5% of requests)
- Database connection failures
- External API failures (Google Maps, Cohere)
- Low disk space
- High memory usage
- Unusual user activity (mass deletions, spam)

### 10.2 Alert Channels
- Email notifications to admin
- SMS alerts for critical issues
- Slack/Discord webhooks
- Dashboard notifications

---

## 11. Testing Strategy

### 11.1 Unit Tests
- Admin authentication and authorization
- Role-based access control
- Email sending functionality
- Data export functions

### 11.2 Integration Tests
- Admin API endpoints
- Database operations
- Email delivery
- Audit logging

### 11.3 E2E Tests
- Admin login flow
- User role assignment
- Email announcement creation and sending
- Appointment deletion with tracking

---

## 12. Documentation

### 12.1 Admin User Guide
- How to access admin panel
- Feature walkthroughs
- Best practices
- Troubleshooting

### 12.2 API Documentation
- All admin endpoints
- Request/response examples
- Authentication requirements
- Rate limits

### 12.3 Developer Guide
- Admin feature development
- Adding new admin routes
- Extending permissions system
- Custom analytics queries

---

## 13. Future Enhancements

### 13.1 Advanced Analytics
- Machine learning predictions (appointment no-shows)
- User churn prediction
- Revenue forecasting
- Anomaly detection

### 13.2 Automation
- Auto-suspend inactive users
- Auto-delete old data
- Auto-scale resources
- Smart recommendations

### 13.3 Integration
- CRM integration (Salesforce, HubSpot)
- Payment gateway admin panel
- SMS notifications
- Push notifications

### 13.4 Mobile App
- Admin mobile app for on-the-go management
- Push notifications for alerts
- Quick actions (suspend user, delete review)

---

## 14. Compliance & Legal

### 14.1 GDPR Compliance
- Right to access (export user data)
- Right to deletion (delete user account)
- Data retention policies
- Consent management

### 14.2 HIPAA Compliance (if storing medical data)
- Encrypted storage
- Access controls
- Audit trails
- Data breach protocols

### 14.3 Audit Trail
- Track all data access
- Log all modifications
- Record admin actions
- Timestamp all events

---

## 15. Cost Considerations

### 15.1 Services
- Email service (SendGrid): $15-100/month
- Redis (managed): $10-50/month
- Storage for backups: $5-20/month
- Monitoring service: $0-50/month

### 15.2 Development Time
- Phase 1-2: 80-100 hours
- Phase 3-4: 60-80 hours
- Phase 5: 40-60 hours
- **Total**: 180-240 hours (~6-8 weeks)

---

## Next Steps

1. **Review and prioritize features** based on immediate needs
2. **Set up development environment** for admin features
3. **Create database migrations** for new tables
4. **Implement Phase 1** foundation (authentication, basic layout)
5. **Iteratively add features** from Phase 2 onwards
6. **Test thoroughly** with security focus
7. **Deploy and monitor** admin panel usage

---

**Document Version**: 1.0  
**Created**: January 26, 2026  
**Status**: Planning Phase  
**Priority**: High
