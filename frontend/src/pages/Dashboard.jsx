import { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './Dashboard.css';

function Dashboard({ token }) {
  const [metrics, setMetrics] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [ws, setWs] = useState(null);
  const [liveActivity, setLiveActivity] = useState([]);

  useEffect(() => {
    fetchMetrics();
    fetchAlerts();
    connectWebSocket();

    const interval = setInterval(fetchMetrics, 30000); // Refresh every 30s
    return () => {
      clearInterval(interval);
      if (ws) ws.close();
    };
  }, []);

  const connectWebSocket = () => {
    const websocket = new WebSocket(`ws://localhost:8000/ws/live`);
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'request_log') {
        setLiveActivity(prev => [data.data, ...prev].slice(0, 10));
      }
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    setWs(websocket);
  };

  const fetchMetrics = async () => {
    try {
      const res = await fetch('/api/metrics', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      });
      if (res.ok) {
        const data = await res.json();
        setMetrics(data);
      }
    } catch (err) {
      console.error('Failed to fetch metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAlerts = async () => {
    try {
      const res = await fetch('/api/alerts?limit=5', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setAlerts(data);
      }
    } catch (err) {
      console.error('Failed to fetch alerts:', err);
    }
  };

  if (loading) {
    return <div className="spinner"></div>;
  }

  return (
    <div className="dashboard">
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-description">Monitor your API traffic and security in real-time</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Total Requests</span>
            <svg className="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div className="stat-value">{metrics?.total_requests?.toLocaleString() || 0}</div>
          <p className="stat-change">All time requests</p>
        </div>
        
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Error Rate</span>
            <svg className="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div className="stat-value text-warning">{((metrics?.error_rate || 0) * 100).toFixed(1)}%</div>
          <p className="stat-change">4xx and 5xx responses</p>
        </div>
        
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Avg Latency</span>
            <svg className="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div className="stat-value">{metrics?.avg_latency_ms?.toFixed(0) || 0}ms</div>
          <p className="stat-change">Response time</p>
        </div>
        
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Suspicious</span>
            <svg className="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <div className="stat-value text-destructive">{metrics?.suspicious_requests || 0}</div>
          <p className="stat-change">Potential threats detected</p>
        </div>
      </div>

      <div className="charts-grid">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Requests Over Time</h3>
            <p className="card-description">Request volume trends</p>
          </div>
          <div className="card-content">
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={metrics?.requests_over_time || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="time" fontSize={12} stroke="hsl(var(--muted-foreground))" />
                <YAxis fontSize={12} stroke="hsl(var(--muted-foreground))" />
                <Tooltip contentStyle={{ background: 'hsl(var(--popover))', border: '1px solid hsl(var(--border))' }} />
                <Line type="monotone" dataKey="count" stroke="hsl(var(--primary))" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Top Endpoints</h3>
            <p className="card-description">Most accessed endpoints</p>
          </div>
          <div className="card-content">
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={metrics?.top_endpoints?.slice(0, 5) || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="endpoint" fontSize={11} stroke="hsl(var(--muted-foreground))" />
                <YAxis fontSize={12} stroke="hsl(var(--muted-foreground))" />
                <Tooltip contentStyle={{ background: 'hsl(var(--popover))', border: '1px solid hsl(var(--border))' }} />
                <Bar dataKey="count" fill="hsl(var(--primary))" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="live-monitor">
        <div className="monitor-header">
          <h3 className="monitor-title">
            <svg className="monitor-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Live Request Monitor
          </h3>
          <span className="live-badge">
            <span className="pulse-dot"></span>
            LIVE
          </span>
        </div>
        
        {liveActivity.length === 0 ? (
          <div className="empty-state">
            <svg className="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
            </svg>
            <p className="empty-title">Waiting for incoming requests</p>
            <p className="empty-description">Send requests to your monitored APIs to see live activity</p>
          </div>
        ) : (
          <div className="activity-list">
            {liveActivity.map((activity, idx) => (
              <div key={idx} className="activity-item">
                <div className="activity-header">
                  <div className="activity-method-group">
                    <span className={`method-badge method-${activity.method?.toLowerCase()}`}>
                      {activity.method}
                    </span>
                    <span className="activity-endpoint">{activity.endpoint}</span>
                  </div>
                  <div className="activity-status-group">
                    <span className={`status-badge status-${Math.floor(activity.status_code / 100)}xx`}>
                      {activity.status_code}
                    </span>
                    {activity.is_suspicious && (
                      <span className="suspicious-badge">
                        <svg className="suspicious-icon" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                        </svg>
                        THREAT
                      </span>
                    )}
                  </div>
                </div>
                <div className="activity-meta">
                  <span className="meta-item">
                    <svg className="meta-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                    </svg>
                    {activity.client_ip}
                  </span>
                  <span className="meta-item">
                    <svg className="meta-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {new Date(activity.timestamp * 1000).toLocaleTimeString()}
                  </span>
                  {activity.risk_score && (
                    <span className="risk-badge">
                      Risk: {activity.risk_score.toFixed(1)}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
