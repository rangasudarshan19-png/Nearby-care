import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import '../styles/Auth.css';
import { apiPost } from '../utils/apiClient';
import { Alert } from '../components/ui';

function VerifyOTP({ onLogin }) {
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const email = location.state?.email;

  useEffect(() => {
    if (!email) {
      navigate('/signup');
    }
  }, [email, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await apiPost('/api/auth/verify-otp', { email, otp });
      setSuccess('Email verified successfully!');
      onLogin(data.token, data.user);
      setTimeout(() => {
        navigate('/dashboard');
      }, 1500);
    } catch (err) {
      setError(err.message || 'Verification failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleResendOTP = async () => {
    setError('');
    setSuccess('');
    setResending(true);

    try {
      await apiPost('/api/auth/resend-otp', { email });
      setSuccess('OTP sent successfully! Check your email.');
    } catch (err) {
      setError(err.message || 'Failed to resend OTP. Please try again.');
    } finally {
      setResending(false);
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
          <h2>Verify Your Email</h2>
          <p>We've sent a 6-digit OTP to</p>
          <p className="email-highlight">{email}</p>
        </div>

        {error && <Alert type="error">{error}</Alert>}
        {success && <Alert type="success">{success}</Alert>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="otp">Enter OTP</label>
            <input
              type="text"
              id="otp"
              name="otp"
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
              required
              placeholder="000000"
              className="otp-input"
              maxLength="6"
            />
            <small>Enter the 6-digit code sent to your email</small>
          </div>

          <button type="submit" className="btn-submit" disabled={loading || otp.length !== 6}>
            {loading ? 'Verifying...' : 'Verify Email'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Didn't receive the code?{' '}
            <button 
              onClick={handleResendOTP} 
              disabled={resending}
              className="link-button"
            >
              {resending ? 'Sending...' : 'Resend OTP'}
            </button>
          </p>
          <p><Link to="/signup">Back to Sign Up</Link></p>
        </div>
      </div>
    </div>
  );
}

export default VerifyOTP;
