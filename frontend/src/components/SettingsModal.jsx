import { useState, useEffect } from 'react';
import './SettingsModal.css';

function SettingsModal({ token, user: initialUser, onClose, onLogout }) {
  const [activeSection, setActiveSection] = useState('general');
  const [user, setUser] = useState(initialUser);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  
  // Profile form
  const [email, setEmail] = useState(initialUser?.email || '');
  const [fullName, setFullName] = useState(initialUser?.full_name || '');
  
  // Password form
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');

    try {
      const res = await fetch('/api/profile/update', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, full_name: fullName })
      });

      if (res.ok) {
        setMessage('Profile updated successfully!');
      } else {
        const data = await res.json();
        setError(data.detail || 'Failed to update profile');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');

    if (newPassword !== confirmPassword) {
      setError('New passwords do not match');
      return;
    }

    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    try {
      const res = await fetch('/api/profile/change-password', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        })
      });

      if (res.ok) {
        setMessage('Password changed successfully!');
        setCurrentPassword('');
        setNewPassword('');
        setConfirmPassword('');
      } else {
        const data = await res.json();
        setError(data.detail || 'Failed to change password');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
  };

  const handleDeleteAccount = async () => {
    if (!confirm('Are you sure you want to delete your account? This action cannot be undone!')) {
      return;
    }

    try {
      const res = await fetch('/api/profile/delete', {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (res.ok) {
        alert('Account deleted successfully');
        onLogout();
      } else {
        const data = await res.json();
        setError(data.detail || 'Failed to delete account');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
  };

  return (
    <div className="settings-modal-overlay" onClick={onClose}>
      <div className="settings-modal" onClick={(e) => e.stopPropagation()}>
        <button className="settings-modal-close" onClick={onClose}>
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18 17.94 6M18 18 6.06 6"/>
          </svg>
        </button>

        <div className="settings-modal-content">
          <div className="settings-sidebar">
            <button
              className={`settings-nav-item ${activeSection === 'general' ? 'active' : ''}`}
              onClick={() => setActiveSection('general')}
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 13v-2a1 1 0 0 0-1-1h-.757l-.707-1.707.535-.536a1 1 0 0 0 0-1.414l-1.414-1.414a1 1 0 0 0-1.414 0l-.536.535L14 4.757V4a1 1 0 0 0-1-1h-2a1 1 0 0 0-1 1v.757l-1.707.707-.536-.535a1 1 0 0 0-1.414 0L4.929 6.343a1 1 0 0 0 0 1.414l.536.536L4.757 10H4a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1h.757l.707 1.707-.535.536a1 1 0 0 0 0 1.414l1.414 1.414a1 1 0 0 0 1.414 0l.536-.535 1.707.707V20a1 1 0 0 0 1 1h2a1 1 0 0 0 1-1v-.757l1.707-.708.536.536a1 1 0 0 0 1.414 0l1.414-1.414a1 1 0 0 0 0-1.414l-.535-.536.707-1.707H20a1 1 0 0 0 1-1Z"/>
                <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"/>
              </svg>
              <span>General</span>
            </button>

            <button
              className={`settings-nav-item ${activeSection === 'notifications' ? 'active' : ''}`}
              onClick={() => setActiveSection('notifications')}
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 5.365V3m0 2.365a5.338 5.338 0 0 1 5.133 5.368v1.8c0 2.386 1.867 2.982 1.867 4.175 0 .593 0 1.292-.538 1.292H5.538C5 18 5 17.301 5 16.708c0-1.193 1.867-1.789 1.867-4.175v-1.8A5.338 5.338 0 0 1 12 5.365ZM8.733 18c.094.852.306 1.54.944 2.112a3.48 3.48 0 0 0 4.646 0c.638-.572 1.236-1.26 1.33-2.112h-6.92Z"/>
              </svg>
              <span>Notifications</span>
            </button>

            <button
              className={`settings-nav-item ${activeSection === 'security' ? 'active' : ''}`}
              onClick={() => setActiveSection('security')}
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 14v3m-3-6V7a3 3 0 1 1 6 0v4m-8 0h10a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1v-7a1 1 0 0 1 1-1Z"/>
              </svg>
              <span>Security</span>
            </button>

            <button
              className={`settings-nav-item ${activeSection === 'account' ? 'active' : ''}`}
              onClick={() => setActiveSection('account')}
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <path stroke="currentColor" strokeWidth="2" d="M7 17v1a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1v-1a3 3 0 0 0-3-3h-4a3 3 0 0 0-3 3Zm8-9a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"/>
              </svg>
              <span>Account</span>
            </button>
          </div>

          <div className="settings-main">
            {message && <div className="alert alert-success">{message}</div>}
            {error && <div className="alert alert-error">{error}</div>}

            {activeSection === 'general' && (
              <div className="settings-section">
                <h2 className="settings-section-title">General</h2>
                
                <div className="settings-group">
                  <label className="settings-label">Email</label>
                  <input
                    type="email"
                    className="input"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>

                <div className="settings-group">
                  <label className="settings-label">Full Name</label>
                  <input
                    type="text"
                    className="input"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Your full name"
                  />
                </div>

                <div className="settings-group">
                  <label className="settings-label">Role</label>
                  <input
                    type="text"
                    className="input"
                    value={user?.role || 'user'}
                    disabled
                  />
                  <small className="settings-hint">Role cannot be changed</small>
                </div>

                <button onClick={handleUpdateProfile} className="btn btn-primary">
                  Save Changes
                </button>
              </div>
            )}

            {activeSection === 'notifications' && (
              <div className="settings-section">
                <h2 className="settings-section-title">Notifications</h2>
                <p className="settings-description">Manage your notification preferences</p>
                
                <div className="settings-group">
                  <div className="settings-toggle">
                    <div>
                      <label className="settings-label">Email Notifications</label>
                      <p className="settings-hint">Receive email alerts for critical threats</p>
                    </div>
                    <label className="toggle-switch">
                      <input type="checkbox" defaultChecked />
                      <span className="toggle-slider"></span>
                    </label>
                  </div>
                </div>

                <div className="settings-group">
                  <div className="settings-toggle">
                    <div>
                      <label className="settings-label">Alert Notifications</label>
                      <p className="settings-hint">Get notified when new alerts are detected</p>
                    </div>
                    <label className="toggle-switch">
                      <input type="checkbox" defaultChecked />
                      <span className="toggle-slider"></span>
                    </label>
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'security' && (
              <div className="settings-section">
                <h2 className="settings-section-title">Security</h2>
                
                <form onSubmit={handleChangePassword}>
                  <div className="settings-group">
                    <label className="settings-label">Current Password</label>
                    <input
                      type="password"
                      className="input"
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                    />
                  </div>

                  <div className="settings-group">
                    <label className="settings-label">New Password</label>
                    <input
                      type="password"
                      className="input"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      minLength={8}
                    />
                    <small className="settings-hint">Minimum 8 characters</small>
                  </div>

                  <div className="settings-group">
                    <label className="settings-label">Confirm New Password</label>
                    <input
                      type="password"
                      className="input"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      minLength={8}
                    />
                  </div>

                  <button type="submit" className="btn btn-primary">
                    Change Password
                  </button>
                </form>
              </div>
            )}

            {activeSection === 'account' && (
              <div className="settings-section">
                <h2 className="settings-section-title">Account</h2>
                
                <div className="settings-group">
                  <label className="settings-label">Account Created</label>
                  <input
                    type="text"
                    className="input"
                    value={new Date(user?.created_at).toLocaleString()}
                    disabled
                  />
                </div>

                <div className="settings-danger-zone">
                  <h3 className="settings-danger-title">Danger Zone</h3>
                  <p className="settings-description">
                    Once you delete your account, there is no going back. Please be certain.
                  </p>
                  <button onClick={handleDeleteAccount} className="btn btn-danger">
                    Delete Account
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default SettingsModal;
