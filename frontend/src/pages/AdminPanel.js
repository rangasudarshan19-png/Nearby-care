import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/AdminPanel.css';

const API = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);

  const [users, setUsers] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [logs, setLogs] = useState([]);
  const [announcements, setAnnouncements] = useState([]);

  const [usersPage, setUsersPage] = useState(1);
  const [appointmentsPage, setAppointmentsPage] = useState(1);
  const [logsPage, setLogsPage] = useState(1);

  const [announcementForm, setAnnouncementForm] = useState({ subject: '', message: '', target: 'all' });
  const [deleteReason, setDeleteReason] = useState('');
  const [selectedItem, setSelectedItem] = useState(null);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) setCurrentUser(JSON.parse(userData));
  }, []);

  useEffect(() => {
    if (!isLoggingOut) fetchAdminStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (isLoggingOut) return;
    if (activeTab === 'users') fetchUsers();
    if (activeTab === 'appointments') fetchAppointments();
    if (activeTab === 'logs') fetchLogs();
    if (activeTab === 'announcements') fetchAnnouncements();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab, usersPage, appointmentsPage, logsPage]);

  const auth = () => ({ headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } });

  const handleAuthError = (err) => {
    if (err.response?.status === 401 || err.response?.status === 403) {
      localStorage.clear();
      navigate('/login', { replace: true });
      return true;
    }
    return false;
  };

  const showMsg = (setter, msg, duration = 3000) => {
    setter(msg);
    setTimeout(() => setter(''), duration);
  };

  const fetchAdminStats = async () => {
    if (isLoggingOut) return;
    try {
      const res = await axios.get(`${API}/api/admin/stats`, auth());
      setStats(res.data);
      setLoading(false);
    } catch (err) {
      if (handleAuthError(err)) return;
      setError(err.response?.data?.error || 'Failed to fetch stats');
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    if (isLoggingOut) return;
    try {
      const res = await axios.get(`${API}/api/admin/users?page=${usersPage}`, auth());
      setUsers(res.data.users || []);
    } catch (err) { if (!handleAuthError(err)) setError('Failed to fetch users'); }
  };

  const fetchAppointments = async () => {
    if (isLoggingOut) return;
    try {
      const res = await axios.get(`${API}/api/admin/appointments?page=${appointmentsPage}`, auth());
      setAppointments(res.data.appointments || []);
    } catch (err) { if (!handleAuthError(err)) setError('Failed to fetch appointments'); }
  };

  const fetchLogs = async () => {
    if (isLoggingOut) return;
    try {
      const res = await axios.get(`${API}/api/admin/logs?page=${logsPage}`, auth());
      setLogs(res.data.logs || []);
    } catch (err) { if (!handleAuthError(err)) setError('Failed to fetch logs'); }
  };

  const fetchAnnouncements = async () => {
    if (isLoggingOut) return;
    try {
      const res = await axios.get(`${API}/api/admin/announcements`, auth());
      setAnnouncements(res.data.announcements || []);
    } catch (err) { if (!handleAuthError(err)) setError('Failed to fetch announcements'); }
  };

  const updateUserRole = async (userId, newRole) => {
    try {
      await axios.put(`${API}/api/admin/users/${userId}/role`, { role: newRole }, auth());
      showMsg(setSuccess, 'User role updated successfully');
      fetchUsers();
    } catch { showMsg(setError, 'Failed to update user role'); }
  };

  const updateUserStatus = async (userId, newStatus) => {
    try {
      await axios.put(`${API}/api/admin/users/${userId}/status`, { status: newStatus }, auth());
      showMsg(setSuccess, 'User status updated successfully');
      fetchUsers();
    } catch { showMsg(setError, 'Failed to update user status'); }
  };

  const deleteUser = async (userId, userEmail) => {
    if (!window.confirm(`Delete user ${userEmail}? This removes all their data and cannot be undone.`)) return;
    try {
      await axios.delete(`${API}/api/admin/users/${userId}`, auth());
      showMsg(setSuccess, 'User deleted successfully');
      fetchUsers();
    } catch (err) { showMsg(setError, err.response?.data?.error || 'Failed to delete user'); }
  };

  const deleteAppointment = async (appointmentId) => {
    if (!deleteReason.trim()) { showMsg(setError, 'Please provide a reason for deletion'); return; }
    try {
      await axios.delete(`${API}/api/admin/appointments/${appointmentId}`, { data: { reason: deleteReason }, ...auth() });
      showMsg(setSuccess, 'Appointment deleted successfully');
      setSelectedItem(null);
      setDeleteReason('');
      fetchAppointments();
    } catch { showMsg(setError, 'Failed to delete appointment'); }
  };

  const sendAnnouncement = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/api/admin/announcements`, announcementForm, auth());
      showMsg(setSuccess, 'Announcement sent successfully');
      setAnnouncementForm({ subject: '', message: '', target: 'all' });
      fetchAnnouncements();
    } catch { showMsg(setError, 'Failed to send announcement'); }
  };

  const handleLogout = () => {
    setIsLoggingOut(true);
    setLoading(false);
    localStorage.clear();
    window.location.href = '/login';
  };

  if (loading && !isLoggingOut) {
    return (
      <div className="admin-loading">
        <div className="spinner"></div>
        Loading admin dashboard...
      </div>
    );
  }

  const navItems = [
    { id: 'overview', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>, label: 'Dashboard' },
    { id: 'users', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>, label: 'Users' },
    { id: 'appointments', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>, label: 'Appointments' },
    { id: 'announcements', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></svg>, label: 'Announcements' },
    { id: 'logs', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>, label: 'System Logs' },
  ];

  return (
    <div className="admin-layout">
      {/* Sidebar */}
      <aside className="admin-sidebar">
        <div className="sidebar-brand">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
            <polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
          <h2>Admin Panel</h2>
        </div>

        <div className="sidebar-user">
          <p className="user-label">Logged in as</p>
          <p className="user-name">{currentUser?.username}</p>
          <p className="user-role">{currentUser?.role}</p>
        </div>

        <nav className="sidebar-nav">
          {navItems.map(item => (
            <button
              key={item.id}
              className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              {item.icon}
              {item.label}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button className="btn-admin-logout" onClick={handleLogout}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="admin-main">
        <h1>
          {activeTab === 'overview' && 'Dashboard Overview'}
          {activeTab === 'users' && 'User Management'}
          {activeTab === 'appointments' && 'Appointment Management'}
          {activeTab === 'announcements' && 'Announcements'}
          {activeTab === 'logs' && 'System Logs'}
        </h1>

        {error && <div className="admin-alert error">{error}</div>}
        {success && <div className="admin-alert success">{success}</div>}

        {/* Overview Tab */}
        {activeTab === 'overview' && stats && (
          <>
            <div className="overview-grid">
              <div className="overview-card users">
                <h3>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
                  Users
                </h3>
                <div className="stat-number">{stats.users.total}</div>
                <div className="stat-details">
                  <p>Active: {stats.users.active}</p>
                  <p>New this week: {stats.users.new_this_week}</p>
                  <p>Suspended: {stats.users.suspended}</p>
                </div>
              </div>
              <div className="overview-card appointments">
                <h3>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                  Appointments
                </h3>
                <div className="stat-number">{stats.appointments.total}</div>
                <div className="stat-details">
                  <p>Scheduled: {stats.appointments.scheduled}</p>
                  <p>Cancelled: {stats.appointments.cancelled}</p>
                  <p>Last 30 days: {stats.appointments.recent_30_days}</p>
                </div>
              </div>
              <div className="overview-card doctors">
                <h3>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                  Doctors
                </h3>
                <div className="stat-number">{stats.doctors.total}</div>
                <div className="stat-details">
                  <p>High rated (4.0+): {stats.doctors.high_rated}</p>
                </div>
              </div>
              <div className="overview-card searches">
                <h3>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                  Searches
                </h3>
                <div className="stat-number">{stats.searches.total}</div>
                <div className="stat-details">
                  <p>This week: {stats.searches.this_week}</p>
                </div>
              </div>
            </div>

            <div className="quick-actions-card">
              <h3>Quick Actions</h3>
              <div className="quick-actions-btns">
                <button className="quick-btn users" onClick={() => setActiveTab('users')}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
                  Manage Users
                </button>
                <button className="quick-btn appointments" onClick={() => setActiveTab('appointments')}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                  View Appointments
                </button>
                <button className="quick-btn announcements" onClick={() => setActiveTab('announcements')}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/></svg>
                  Send Announcement
                </button>
                <button className="quick-btn logs" onClick={() => setActiveTab('logs')}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                  View Logs
                </button>
              </div>
            </div>
          </>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="data-card">
            <div className="data-card-header"><h3>All Users</h3></div>
            <div className="data-card-body">
              {users.length === 0 ? (
                <p className="empty-state">No users found</p>
              ) : (
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>ID</th><th>Username</th><th>Email</th><th>Role</th>
                      <th>Status</th><th>Logins</th><th>Last Login</th><th>Verified</th><th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map(u => {
                      const isMe = currentUser && (Number(u.id) === Number(currentUser.id) || u.email === currentUser.email);
                      return (
                        <tr key={u.id}>
                          <td>{u.id}</td>
                          <td><strong>{u.username}</strong></td>
                          <td>{u.email}</td>
                          <td>
                            {isMe ? (
                              <span className="admin-badge role-admin">{u.role}</span>
                            ) : (
                              <select className="admin-select" value={u.role} onChange={(e) => updateUserRole(u.id, e.target.value)}>
                                <option value="user">User</option>
                                <option value="admin">Admin</option>
                              </select>
                            )}
                          </td>
                          <td>
                            {isMe ? (
                              <span className="admin-badge status-active">{u.status || 'Active'}</span>
                            ) : (
                              <select className="admin-select" value={u.status} onChange={(e) => updateUserStatus(u.id, e.target.value)}>
                                <option value="active">Active</option>
                                <option value="suspended">Suspended</option>
                                <option value="banned">Banned</option>
                              </select>
                            )}
                          </td>
                          <td>{u.login_count || 0}</td>
                          <td>{u.last_login ? new Date(u.last_login).toLocaleDateString() : 'Never'}</td>
                          <td>
                            <span className={`admin-badge ${u.is_verified ? 'verified' : 'unverified'}`}>
                              {u.is_verified ? '✓ Verified' : '✗ Unverified'}
                            </span>
                          </td>
                          <td>
                            {!isMe && (
                              <button className="btn-admin danger" onClick={() => deleteUser(u.id, u.email)}>
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
                                Delete
                              </button>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              )}
            </div>
            <div className="data-card-footer">
              <div className="pagination">
                <button className="btn-admin primary" onClick={() => setUsersPage(Math.max(1, usersPage - 1))} disabled={usersPage === 1}>Previous</button>
                <span className="page-info">Page {usersPage}</span>
                <button className="btn-admin primary" onClick={() => setUsersPage(usersPage + 1)} disabled={users.length < 10}>Next</button>
              </div>
            </div>
          </div>
        )}

        {/* Appointments Tab */}
        {activeTab === 'appointments' && (
          <div className="data-card">
            <div className="data-card-header"><h3>All Appointments</h3></div>
            <div className="data-card-body">
              {appointments.length === 0 ? (
                <p className="empty-state">No appointments found</p>
              ) : (
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>ID</th><th>User</th><th>Hospital</th><th>Date</th><th>Time</th><th>Status</th><th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {appointments.map(apt => (
                      <tr key={apt.id}>
                        <td>{apt.id}</td>
                        <td>{apt.user_email || `User #${apt.user_id}`}</td>
                        <td>{apt.hospital_name}</td>
                        <td>{new Date(apt.appointment_date).toLocaleDateString()}</td>
                        <td>{apt.appointment_time}</td>
                        <td>
                          <span className={`admin-badge ${apt.status === 'scheduled' ? 'status-scheduled' : 'status-cancelled'}`}>
                            {apt.status}
                          </span>
                        </td>
                        <td>
                          {!apt.is_deleted ? (
                            <button className="btn-admin danger" onClick={() => setSelectedItem(apt.id)}>Delete</button>
                          ) : (
                            <span className="admin-badge status-cancelled">Deleted</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}

              {selectedItem && (
                <div className="delete-confirm-box">
                  <h4>Delete Appointment #{selectedItem}</h4>
                  <textarea
                    placeholder="Reason for deletion (required)"
                    value={deleteReason}
                    onChange={(e) => setDeleteReason(e.target.value)}
                  />
                  <div className="delete-confirm-actions">
                    <button className="btn-admin danger" onClick={() => deleteAppointment(selectedItem)}>Confirm Delete</button>
                    <button className="btn-admin secondary" onClick={() => { setSelectedItem(null); setDeleteReason(''); }}>Cancel</button>
                  </div>
                </div>
              )}
            </div>
            <div className="data-card-footer">
              <div className="pagination">
                <button className="btn-admin primary" onClick={() => setAppointmentsPage(Math.max(1, appointmentsPage - 1))} disabled={appointmentsPage === 1}>Previous</button>
                <span className="page-info">Page {appointmentsPage}</span>
                <button className="btn-admin primary" onClick={() => setAppointmentsPage(appointmentsPage + 1)} disabled={appointments.length < 10}>Next</button>
              </div>
            </div>
          </div>
        )}

        {/* Announcements Tab */}
        {activeTab === 'announcements' && (
          <>
            <div className="data-card" style={{marginBottom: 20}}>
              <div className="data-card-header"><h3>Send Email Announcement</h3></div>
              <div className="data-card-body" style={{padding: 24}}>
                <form onSubmit={sendAnnouncement} className="admin-form">
                  <div className="form-group">
                    <label>Subject</label>
                    <input type="text" value={announcementForm.subject} onChange={(e) => setAnnouncementForm({...announcementForm, subject: e.target.value})} required />
                  </div>
                  <div className="form-group">
                    <label>Message</label>
                    <textarea value={announcementForm.message} onChange={(e) => setAnnouncementForm({...announcementForm, message: e.target.value})} required />
                  </div>
                  <div className="form-group">
                    <label>Target Audience</label>
                    <select value={announcementForm.target} onChange={(e) => setAnnouncementForm({...announcementForm, target: e.target.value})}>
                      <option value="all">All Users</option>
                      <option value="active">Active Users Only</option>
                      <option value="new">New Users (This Week)</option>
                    </select>
                  </div>
                  <button type="submit" className="btn-admin success">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                    Send Announcement
                  </button>
                </form>
              </div>
            </div>

            <div className="data-card">
              <div className="data-card-header"><h3>Recent Announcements</h3></div>
              <div className="data-card-body" style={{padding: 20}}>
                {announcements.length === 0 ? (
                  <p className="empty-state">No announcements yet</p>
                ) : (
                  <div className="announcements-grid">
                    {announcements.map(ann => (
                      <div key={ann.id} className="announcement-card">
                        <div className="announcement-header">
                          <strong>{ann.subject}</strong>
                          <span className="date">{new Date(ann.sent_at).toLocaleString()}</span>
                        </div>
                        <p>{ann.message}</p>
                        <div className="announcement-meta">
                          Target: {ann.target_audience} &middot; Sent by: {ann.sent_by_username}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </>
        )}

        {/* Logs Tab */}
        {activeTab === 'logs' && (
          <div className="data-card">
            <div className="data-card-header"><h3>Admin Activity Logs</h3></div>
            <div className="data-card-body">
              {logs.length === 0 ? (
                <p className="empty-state">No logs found</p>
              ) : (
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>Timestamp</th><th>Admin</th><th>Action</th><th>Details</th><th>IP Address</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs.map(log => (
                      <tr key={log.id}>
                        <td>{new Date(log.timestamp).toLocaleString()}</td>
                        <td>{log.admin_username}</td>
                        <td><span className="admin-badge action-badge">{log.action}</span></td>
                        <td style={{maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis'}}>
                          {log.details && log.details !== 'null' && log.details !== ''
                            ? (typeof log.details === 'string' ? log.details : JSON.stringify(log.details))
                            : '-'}
                        </td>
                        <td>{log.ip_address || 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
            <div className="data-card-footer">
              <div className="pagination">
                <button className="btn-admin primary" onClick={() => setLogsPage(Math.max(1, logsPage - 1))} disabled={logsPage === 1}>Previous</button>
                <span className="page-info">Page {logsPage}</span>
                <button className="btn-admin primary" onClick={() => setLogsPage(logsPage + 1)} disabled={logs.length < 20}>Next</button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AdminDashboard;
