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
              <svg className="brand-logo" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                <path stroke="currentColor" strokeLinejoin="round" d="m17 13 3.4641-2V7L17 5l-3.4641 2v4M17 13l-3.4641-2M17 13v4l-7.00001 4M17 13V9m0 4-7.00001 4m3.53591-6L10.5 12.7348M9.99999 21l-3.4641-2.1318M9.99999 21v-4m-3.4641 2v-.1318m0 0V15L10.5 12.7348m-3.96411 6.1334L3.5 17V5m0 0L7 3l3.5 2m-7 0 2.99999 2M10.5 5v7.7348M10.5 5 6.49999 7M17 9l3.5-2M17 9l-3.5-2M9.99999 17l-3.5-2m0 .5V7"/>
              </svg>
              <h1>Boing</h1>
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
