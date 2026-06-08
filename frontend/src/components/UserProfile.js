import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_URL } from '../config';
import { validatePassword, PASSWORD_RULE_MESSAGE } from '../utils/passwordValidation';
import { clearAuthSession, getAuthToken } from '../utils/authStorage';
import '../styles/Dashboard.css';

function UserProfile() {
  const [user, setUser] = useState({ name: '', email: '' });
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(null);
  
  // Name editing
  const [editingName, setEditingName] = useState(false);
  const [newName, setNewName] = useState('');
  
  // Email update with OTP
  const [editingEmail, setEditingEmail] = useState(false);
  const [newEmail, setNewEmail] = useState('');
  const [emailOtp, setEmailOtp] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [otpLoading, setOtpLoading] = useState(false);
  
  // Password change
  const [changingPassword, setChangingPassword] = useState(false);
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  
  // Account deletion
  const [deletingAccount, setDeletingAccount] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState('');

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const token = getAuthToken();
      const response = await axios.get(`${API_URL}/api/user/profile`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log('Profile API Response:', response.data);
      
      const userName = response.data.user?.name || response.data.user?.username || response.data.name || response.data.username || '';
      const userEmail = response.data.user?.email || response.data.email || '';
      
      console.log('Extracted userName:', userName, 'userEmail:', userEmail);
      
      setUser({ 
        name: userName, 
        email: userEmail 
      });
      setNewName(userName);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching user data:', error);
      console.error('Error response:', error.response?.data);
      if (error.response?.status === 401 || error.response?.status === 403) {
        clearAuthSession({ broadcast: true });
      }
      setMessage('Failed to load profile');
      setLoading(false);
    }
  };

  const handleNameUpdate = async (e) => {
    e.preventDefault();
    if (!newName.trim()) {
      setMessage('Name cannot be empty');
      return;
    }

    try {
      const token = getAuthToken();
      await axios.put(`${API_URL}/api/user/update-name`, 
        { name: newName },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      setUser({ ...user, name: newName });
      setEditingName(false);
      setMessage('Name updated successfully.');
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      console.error('Error updating name:', error);
      setMessage('Failed to update name');
    }
  };

  const handleSendEmailOtp = async () => {
    if (!newEmail.trim() || !newEmail.includes('@')) {
      setMessage('Please enter a valid email address');
      return;
    }

    setOtpLoading(true);
    try {
      const token = getAuthToken();
      await axios.post(`${API_URL}/api/user/send-email-otp`, 
        { new_email: newEmail },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      setOtpSent(true);
      setMessage('OTP sent to your new email address.');
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      console.error('Error sending OTP:', error);
      setMessage(error.response?.data?.error || 'Failed to send OTP');
    } finally {
      setOtpLoading(false);
    }
  };

  const handleVerifyEmailOtp = async (e) => {
    e.preventDefault();
    if (!emailOtp.trim()) {
      setMessage('Please enter the OTP');
      return;
    }

    try {
      const token = getAuthToken();
      await axios.post(`${API_URL}/api/user/verify-email-otp`, 
        { new_email: newEmail, otp: emailOtp },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      setUser({ ...user, email: newEmail });
      setEditingEmail(false);
      setOtpSent(false);
      setEmailOtp('');
      setNewEmail('');
      setMessage('Email updated successfully.');
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      console.error('Error verifying OTP:', error);
      setMessage(error.response?.data?.error || 'Invalid or expired OTP');
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    
    if (!passwordData.currentPassword || !passwordData.newPassword) {
      setMessage('Please fill all password fields');
      return;
    }
    
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setMessage('New passwords do not match');
      return;
    }
    
    if (!validatePassword(passwordData.newPassword)) {
      setMessage(PASSWORD_RULE_MESSAGE);
      return;
    }

    try {
      const token = getAuthToken();
      await axios.post(`${API_URL}/api/user/change-password`, 
        { 
          current_password: passwordData.currentPassword,
          new_password: passwordData.newPassword 
        },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      setChangingPassword(false);
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
      setMessage('Password changed successfully.');
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      console.error('Error changing password:', error);
      setMessage(error.response?.data?.error || 'Failed to change password');
    }
  };

  const handleDeleteAccount = async () => {
    if (deleteConfirmText !== 'DELETE') {
      setMessage('Please type DELETE to confirm account deletion');
      return;
    }

    if (!window.confirm('Are you absolutely sure? This action cannot be undone!')) {
      return;
    }

    try {
      const token = getAuthToken();
      await axios.delete(`${API_URL}/api/user/delete-account`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      clearAuthSession({ broadcast: true });
      window.location.href = '/';
    } catch (error) {
      console.error('Error deleting account:', error);
      setMessage(error.response?.data?.error || 'Failed to delete account');
    }
  };

  if (loading) {
    return <div className="loading">Loading profile...</div>;
  }

  return (
    <div className="user-profile-container">
      {message && (
        <div className={`message ${message.includes('Failed') || message.includes('cannot') || message.includes('Invalid') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}

      <div className="profile-section">
        <div className="section-header">
          <h2>👤 Personal Details</h2>
        </div>

        {/* Name Section */}
        <div className="profile-item">
          <div className="profile-item-header">
            <h3>Name</h3>
            {!editingName ? (
              <button onClick={() => setEditingName(true)} className="btn-edit-small">
                Edit
              </button>
            ) : (
              <button onClick={() => { setEditingName(false); setNewName(user.name); }} className="btn-cancel-small">
                Cancel
              </button>
            )}
          </div>
          
          {!editingName ? (
            <p className="profile-value">{user.name || 'Not set'}</p>
          ) : (
            <form onSubmit={handleNameUpdate} className="inline-edit-form">
              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="Enter your name"
                className="form-input"
              />
              <button type="submit" className="btn-save-small">💾 Save</button>
            </form>
          )}
        </div>

        {/* Email Section */}
        <div className="profile-item">
          <div className="profile-item-header">
            <h3>Email</h3>
            {!editingEmail ? (
              <button onClick={() => setEditingEmail(true)} className="btn-edit-small">
                Change
              </button>
            ) : (
              <button onClick={() => { setEditingEmail(false); setOtpSent(false); setEmailOtp(''); setNewEmail(''); }} className="btn-cancel-small">
                Cancel
              </button>
            )}
          </div>
          
          {!editingEmail ? (
            <p className="profile-value">{user.email}</p>
          ) : !otpSent ? (
            <div className="inline-edit-form">
              <input
                type="email"
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
                placeholder="Enter new email address"
                className="form-input"
              />
              <button 
                type="button" 
                onClick={handleSendEmailOtp} 
                disabled={otpLoading}
                className="btn-save-small"
              >
                {otpLoading ? '⏳ Sending...' : '📤 Send OTP'}
              </button>
            </div>
          ) : (
            <form onSubmit={handleVerifyEmailOtp} className="inline-edit-form">
              <input
                type="text"
                value={emailOtp}
                onChange={(e) => setEmailOtp(e.target.value)}
                placeholder="Enter OTP sent to new email"
                className="form-input"
                maxLength="6"
              />
              <button type="submit" className="btn-save-small">Verify</button>
            </form>
          )}
        </div>

        {/* Password Section */}
        <div className="profile-item">
          <div className="profile-item-header">
            <h3>Password</h3>
            {!changingPassword ? (
              <button onClick={() => setChangingPassword(true)} className="btn-edit-small">
                Change
              </button>
            ) : (
              <button onClick={() => { setChangingPassword(false); setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' }); }} className="btn-cancel-small">
                Cancel
              </button>
            )}
          </div>
          
          {!changingPassword ? (
            <p className="profile-value">••••••••</p>
          ) : (
            <form onSubmit={handlePasswordChange} className="password-change-form">
              <div className="form-group">
                <label>Current Password</label>
                <input
                  type="password"
                  value={passwordData.currentPassword}
                  onChange={(e) => setPasswordData({...passwordData, currentPassword: e.target.value})}
                  placeholder="Enter current password"
                  className="form-input"
                />
              </div>
              <div className="form-group">
                <label>New Password</label>
                <input
                  type="password"
                  value={passwordData.newPassword}
                  onChange={(e) => setPasswordData({...passwordData, newPassword: e.target.value})}
                  placeholder="Use a strong password"
                  className="form-input"
                />
                <small>{PASSWORD_RULE_MESSAGE}</small>
              </div>
              <div className="form-group">
                <label>Confirm New Password</label>
                <input
                  type="password"
                  value={passwordData.confirmPassword}
                  onChange={(e) => setPasswordData({...passwordData, confirmPassword: e.target.value})}
                  placeholder="Re-enter new password"
                  className="form-input"
                />
              </div>
              <button type="submit" className="btn-save-small">Change Password</button>
            </form>
          )}
        </div>
      </div>

      {/* Account Deletion */}
      <div className="profile-section" style={{ borderColor: '#dc3545', marginTop: '30px' }}>
        <div className="section-header">
          <h2>Delete Account</h2>
        </div>
        
        {!deletingAccount ? (
          <div>
            <p style={{ color: '#666', marginBottom: '15px' }}>
              Permanently delete your account and all associated data. This action cannot be undone.
            </p>
            <button onClick={() => setDeletingAccount(true)} className="btn-danger">
              Delete My Account
            </button>
          </div>
        ) : (
          <div className="delete-account-form">
            <p className="warning-text">
              This will permanently delete your account and all associated data. This action cannot be undone.
            </p>
            <div className="form-group">
              <label>Type <strong>DELETE</strong> to confirm:</label>
              <input
                type="text"
                value={deleteConfirmText}
                onChange={(e) => setDeleteConfirmText(e.target.value)}
                placeholder="Type DELETE"
                className="form-input"
              />
            </div>
            <div className="danger-actions">
              <button onClick={handleDeleteAccount} className="btn-danger">
                Permanently Delete Account
              </button>
              <button onClick={() => { setDeletingAccount(false); setDeleteConfirmText(''); }} className="btn-cancel">
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default UserProfile;
