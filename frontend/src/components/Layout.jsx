import { Link, useLocation } from 'react-router-dom';
import './Layout.css';

function Layout({ user, onLogout, children }) {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="container">
          <div className="navbar-content">
            <div className="navbar-brand">
              <h1>🎯 Boing</h1>
              <span className="navbar-subtitle">API Security Monitor</span>
            </div>
            
            <div className="navbar-links">
              <Link to="/" className={isActive('/') ? 'active' : ''}>
                Dashboard
              </Link>
              <Link to="/apis" className={isActive('/apis') ? 'active' : ''}>
                APIs
              </Link>
              <Link to="/alerts" className={isActive('/alerts') ? 'active' : ''}>
                Alerts
              </Link>
              <Link to="/logs" className={isActive('/logs') ? 'active' : ''}>
                Logs
              </Link>
              {user?.role === 'admin' && (
                <Link to="/admin" className={isActive('/admin') ? 'active' : ''}>
                  Admin
                </Link>
              )}
            </div>

            <div className="navbar-user">
              <span className="user-email">{user?.email}</span>
              <Link to="/settings" className="btn btn-secondary btn-sm">
                Settings
              </Link>
              <button onClick={onLogout} className="btn btn-secondary btn-sm">
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="main-content">
        <div className="container">
          {children}
        </div>
      </main>
    </div>
  );
}

export default Layout;
