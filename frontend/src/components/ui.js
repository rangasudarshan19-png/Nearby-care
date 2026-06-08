import React from 'react';

export const Button = ({ children, className = '', variant = 'primary', ...props }) => (
  <button className={`btn btn-${variant} ${className}`.trim()} {...props}>
    {children}
  </button>
);

export const Alert = ({ type = 'info', children }) => {
  if (!children) return null;
  const className = type === 'error' ? 'error-message' : type === 'success' ? 'success-message' : 'info-message';
  return <div className={className}>{children}</div>;
};

export const Spinner = ({ label = 'Loading...', inline = false }) => (
  <div className={inline ? 'spinner-inline' : 'loading'}>
    <div className="spinner"></div>
    {inline ? <span>{label}</span> : <p>{label}</p>}
  </div>
);

export const EmptyState = ({ title, description, children }) => (
  <div className="empty-state">
    {title && <h3>{title}</h3>}
    {description && <p>{description}</p>}
    {!title && !description && (children || 'Nothing to show yet.')}
  </div>
);

export const Badge = ({ children, className = '' }) => (
  <span className={`admin-badge ${className}`.trim()}>{children}</span>
);
