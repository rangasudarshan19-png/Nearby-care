import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import '../styles/Auth.css';
import { apiPost } from '../utils/apiClient';
import { Alert } from '../components/ui';
import { validatePassword, PASSWORD_RULE_MESSAGE } from '../utils/passwordValidation';

function ForgotPassword() {
  const [step, setStep] = useState('email');
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [passwords, setPasswords] = useState({ newPassword: '', confirmPassword: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const requestOtp = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      await apiPost('/api/auth/forgot-password/request', { email });
      setSuccess('OTP sent to your registered email.');
      setStep('otp');
    } catch (err) {
      setError(err.message || 'Failed to send OTP');
    } finally {
      setLoading(false);
    }
  };

  const verifyOtp = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      await apiPost('/api/auth/forgot-password/verify', { email, otp });
      setSuccess('OTP verified. Enter a new password.');
      setStep('password');
    } catch (err) {
      setError(err.message || 'OTP verification failed');
    } finally {
      setLoading(false);
    }
  };

  const resetPassword = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (passwords.newPassword !== passwords.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (!validatePassword(passwords.newPassword)) {
      setError(PASSWORD_RULE_MESSAGE);
      return;
    }

    setLoading(true);

    try {
      await apiPost('/api/auth/forgot-password/reset', {
        email,
        otp,
        new_password: passwords.newPassword
      });
      setSuccess('Password updated. Please sign in with your new password.');
      setTimeout(() => navigate('/login'), 1400);
    } catch (err) {
      setError(err.message || 'Failed to reset password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container" style={{backgroundImage: 'url(/images/auth-bg.png)'}}>
      <div className="auth-card">
        <div className="auth-header">
          <div className="logo">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"></path>
              <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
            <h1>Nearby Care</h1>
          </div>
          <h2>Reset Password</h2>
          <p>Use your registered email to receive a one-time code.</p>
        </div>

        <Alert type="error">{error}</Alert>
        <Alert type="success">{success}</Alert>

        {step === 'email' && (
          <form onSubmit={requestOtp} className="auth-form">
            <div className="form-group">
              <label htmlFor="email">Registered Email</label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="you@example.com"
              />
            </div>
            <button type="submit" className="btn-submit" disabled={loading}>
              {loading ? 'Sending OTP...' : 'Send OTP'}
            </button>
          </form>
        )}

        {step === 'otp' && (
          <form onSubmit={verifyOtp} className="auth-form">
            <div className="form-group">
              <label htmlFor="otp">Enter OTP</label>
              <input
                type="text"
                id="otp"
                value={otp}
                onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                required
                placeholder="000000"
                className="otp-input"
                maxLength="6"
              />
              <small>Enter the 6-digit code sent to {email}</small>
            </div>
            <button type="submit" className="btn-submit" disabled={loading || otp.length !== 6}>
              {loading ? 'Verifying...' : 'Verify OTP'}
            </button>
          </form>
        )}

        {step === 'password' && (
          <form onSubmit={resetPassword} className="auth-form">
            <div className="form-group">
              <label htmlFor="newPassword">New Password</label>
              <input
                type="password"
                id="newPassword"
                value={passwords.newPassword}
                onChange={(e) => setPasswords({ ...passwords, newPassword: e.target.value })}
                required
                placeholder="Use a strong password"
              />
              <small>{PASSWORD_RULE_MESSAGE}</small>
            </div>
            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm New Password</label>
              <input
                type="password"
                id="confirmPassword"
                value={passwords.confirmPassword}
                onChange={(e) => setPasswords({ ...passwords, confirmPassword: e.target.value })}
                required
                placeholder="Re-enter your new password"
              />
            </div>
            <button type="submit" className="btn-submit" disabled={loading}>
              {loading ? 'Updating...' : 'Update Password'}
            </button>
          </form>
        )}

        <div className="auth-footer">
          <p><Link to="/login">Back to Sign In</Link></p>
        </div>
      </div>
    </div>
  );
}

export default ForgotPassword;
