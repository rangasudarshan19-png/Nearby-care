import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_URL } from '../config';
import '../styles/Dashboard.css';

function AdminDashboard({ user, onLogout }) {
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    if (!user?.is_admin) {
      navigate('/dashboard');
      return;
    }
    fetchData();
  }, [user, navigate]);

  const fetchData = async () => {
    const token = localStorage.getItem('token');
    setLoading(true);
    
    try {
      const [usersRes, statsRes] = await Promise.all([
        fetch(`${API_URL}/api/admin/users`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_URL}/api/admin/stats`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      if (usersRes.ok && statsRes.ok) {
        const usersData = await usersRes.json();
        const statsData = await statsRes.json();
        setUsers(usersData.users);
        setStats(statsData);
      } else {
        setError('Failed to load admin data');
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId, username) => {
    if (!window.confirm(`Delete user ${username}? This cannot be undone.`)) {
      return;
    }

    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API_URL}/api/admin/users/${userId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (res.ok) {
        setMessage(`User ${username} deleted successfully`);
        fetchData();
        setTimeout(() => setMessage(''), 3000);
      } else {
        const data = await res.json();
        setError(data.error || 'Delete failed');
      }
    } catch (err) {
      setError('Network error');
    }
  };

  const handleToggleAdmin = async (userId, username, isCurrentlyAdmin) => {
    const action = isCurrentlyAdmin ? 'remove admin from' : 'promote to admin';
    if (!window.confirm(`${action} ${username}?`)) {
      return;
    }

    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API_URL}/api/admin/users/${userId}/promote`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ is_admin: !isCurrentlyAdmin })
      });

      if (res.ok) {
        const data = await res.json();
        setMessage(data.message);
        fetchData();
        setTimeout(() => setMessage(''), 3000);
      } else {
        const data = await res.json();
        setError(data.error || 'Action failed');
      }
    } catch (err) {
      setError('Network error');
    }
  };

  const handleLogoutClick = () => {
    onLogout();
    navigate('/');
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading admin panel...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-container admin-dashboard">
      <header className="dashboard-header admin-header">
        <div className="header-content">
          <div className="admin-logo">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
            <h1>Admin Panel</h1>
          </div>
          <div className="user-info">
            <button onClick={() => navigate('/dashboard')} className="btn btn-secondary">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
              </svg>
              Back to Dashboard
            </button>
            <button onClick={handleLogoutClick} className="btn btn-logout">
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="dashboard-main admin-main">
        {error && <div className="error">{error}</div>}
        {message && <div className="success">{message}</div>}

        {stats && (
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon users">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                  <circle cx="9" cy="7" r="4"></circle>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                </svg>
              </div>
              <div className="stat-content">
                <h3>Total Users</h3>
                <p className="stat-number">{stats.total_users}</p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon verified">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
              </div>
              <div className="stat-content">
                <h3>Verified Users</h3>
                <p className="stat-number">{stats.verified_users}</p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon admin">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                  <path d="M2 17l10 5 10-5"></path>
                  <path d="M2 12l10 5 10-5"></path>
                </svg>
              </div>
              <div className="stat-content">
                <h3>Admin Users</h3>
                <p className="stat-number">{stats.admin_users}</p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon searches">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="11" cy="11" r="8"></circle>
                  <path d="m21 21-4.35-4.35"></path>
                </svg>
              </div>
              <div className="stat-content">
                <h3>Total Searches</h3>
                <p className="stat-number">{stats.total_searches}</p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon favorites">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                </svg>
              </div>
              <div className="stat-content">
                <h3>Total Favorites</h3>
                <p className="stat-number">{stats.total_favorites}</p>
              </div>
            </div>
          </div>
        )}

        <div className="users-section">
          <div className="section-header">
            <h2>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
              </svg>
              User Management
            </h2>
            <span className="user-count">{users.length} total users</span>
          </div>
          <div className="users-table-container">
            <table className="users-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Status</th>
                  <th>Role</th>
                  <th>Joined</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id}>
                    <td className="user-id">#{u.id}</td>
                    <td className="username">
                      <div className="user-avatar">{u.username.charAt(0).toUpperCase()}</div>
                      <span>{u.username}</span>
                    </td>
                    <td className="email">{u.email}</td>
                    <td>
                      <span className={`badge ${u.is_verified ? 'verified' : 'unverified'}`}>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          {u.is_verified ? (
                            <polyline points="20 6 9 17 4 12"></polyline>
                          ) : (
                            <>
                              <line x1="18" y1="6" x2="6" y2="18"></line>
                              <line x1="6" y1="6" x2="18" y2="18"></line>
                            </>
                          )}
                        </svg>
                        {u.is_verified ? 'Verified' : 'Unverified'}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${u.is_admin ? 'admin-badge' : 'user-badge'}`}>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          {u.is_admin ? (
                            <path d="M12 2L2 7l10 5 10-5-10-5z M2 17l10 5 10-5 M2 12l10 5 10-5"></path>
                          ) : (
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2 M12 3a4 4 0 1 0 0 8 4 4 0 0 0 0-8z"></path>
                          )}
                        </svg>
                        {u.is_admin ? 'Admin' : 'User'}
                      </span>
                    </td>
                    <td className="date">{new Date(u.created_at).toLocaleDateString()}</td>
                    <td className="actions-cell">
                      {u.id !== user.id && (
                        <>
                          <button
                            className="btn-action promote"
                            onClick={() => handleToggleAdmin(u.id, u.username, u.is_admin)}
                            title={u.is_admin ? 'Remove admin' : 'Promote to admin'}
                          >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              {u.is_admin ? (
                                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                              ) : (
                                <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                              )}
                            </svg>
                          </button>
                          <button
                            className="btn-action delete"
                            onClick={() => handleDeleteUser(u.id, u.username)}
                            title="Delete user"
                          >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <polyline points="3 6 5 6 21 6"></polyline>
                              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                            </svg>
                          </button>
                        </>
                      )}
                      {u.id === user.id && (
                        <span className="you-badge">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                          </svg>
                          You
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;
