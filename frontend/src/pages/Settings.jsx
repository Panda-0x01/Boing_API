import { useState, useEffect } from 'react';
import './Settings.css';

function Settings({ token, onLogout }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('profile');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  
  // Profile update form
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  
  // Password change form
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  useEffect(() => {
    fetchUser();
  }, []);

  const fetchUser = async () => {
    try {
      const res = await fetch('/api/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setUser(data);
        setEmail(data.email);
        setFullName(data.full_name || '');
      }
    } catch (err) {
      setError('Failed to load user data');
    } finally {
      setLoading(false);
    }
  };

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
        fetchUser();
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

    if (!confirm('This will permanently delete all your data. Are you absolutely sure?')) {
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

  if (loading) return <div className="spinner"></div>;

  return (
    <div className="settings-page">
      <h1 className="page-title">Settings</h1>

      <div className="settings-tabs">
        <button
          className={`tab-btn ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          Profile
        </button>
        <button
          className={`tab-btn ${activeTab === 'password' ? 'active' : ''}`}
          onClick={() => setActiveTab('password')}
        >
          Change Password
        </button>
        <button
          className={`tab-btn ${activeTab === 'danger' ? 'active' : ''}`}
          onClick={() => setActiveTab('danger')}
        >
          Danger Zone
        </button>
      </div>

      {message && <div className="alert alert-success">{message}</div>}
      {error && <div className="alert alert-error">{error}</div>}

      {activeTab === 'profile' && (
        <div className="card">
          <h3 className="card-title">Profile Information</h3>
          <form onSubmit={handleUpdateProfile}>
            <div className="form-group mb-2">
              <label className="label">Email</label>
              <input
                type="email"
                className="input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="form-group mb-2">
              <label className="label">Full Name</label>
              <input
                type="text"
                className="input"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Your full name"
              />
            </div>

            <div className="form-group mb-2">
              <label className="label">Role</label>
              <input
                type="text"
                className="input"
                value={user?.role || 'user'}
                disabled
              />
              <small className="text-secondary">Role cannot be changed</small>
            </div>

            <div className="form-group mb-3">
              <label className="label">Account Created</label>
              <input
                type="text"
                className="input"
                value={new Date(user?.created_at).toLocaleString()}
                disabled
              />
            </div>

            <button type="submit" className="btn btn-primary">
              Update Profile
            </button>
          </form>
        </div>
      )}

      {activeTab === 'password' && (
        <div className="card">
          <h3 className="card-title">Change Password</h3>
          <form onSubmit={handleChangePassword}>
            <div className="form-group mb-2">
              <label className="label">Current Password</label>
              <input
                type="password"
                className="input"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                required
              />
            </div>

            <div className="form-group mb-2">
              <label className="label">New Password</label>
              <input
                type="password"
                className="input"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                minLength={8}
              />
              <small className="text-secondary">Minimum 8 characters</small>
            </div>

            <div className="form-group mb-3">
              <label className="label">Confirm New Password</label>
              <input
                type="password"
                className="input"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={8}
              />
            </div>

            <button type="submit" className="btn btn-primary">
              Change Password
            </button>
          </form>
        </div>
      )}

      {activeTab === 'danger' && (
        <div className="card danger-zone">
          <h3 className="card-title text-danger">Danger Zone</h3>
          <p className="text-secondary mb-3">
            Once you delete your account, there is no going back. Please be certain.
          </p>

          <button onClick={handleDeleteAccount} className="btn btn-danger">
            Delete My Account
          </button>
        </div>
      )}
    </div>
  );
}

export default Settings;
