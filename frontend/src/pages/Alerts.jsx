import { useState, useEffect } from 'react';

function Alerts({ token }) {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchAlerts();
  }, [filter]);

  const fetchAlerts = async () => {
    try {
      let url = '/api/alerts?limit=100';
      if (filter !== 'all') {
        url += `&acknowledged=${filter === 'acknowledged'}`;
      }
      
      const res = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setAlerts(data);
      }
    } catch (err) {
      console.error('Failed to fetch alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAcknowledge = async (id) => {
    try {
      const res = await fetch(`/api/alerts/${id}/ack`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ acknowledged: true })
      });
      if (res.ok) {
        fetchAlerts();
      }
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
    }
  };

  if (loading) return <div className="spinner"></div>;

  return (
    <div>
      <div className="flex-between mb-4">
        <h1 className="page-title">Alerts</h1>
        <div className="flex gap-2">
          <button 
            onClick={() => setFilter('all')} 
            className={`btn ${filter === 'all' ? 'btn-primary' : 'btn-secondary'}`}
          >
            All
          </button>
          <button 
            onClick={() => setFilter('unacknowledged')} 
            className={`btn ${filter === 'unacknowledged' ? 'btn-primary' : 'btn-secondary'}`}
          >
            Unacknowledged
          </button>
          <button 
            onClick={() => setFilter('acknowledged')} 
            className={`btn ${filter === 'acknowledged' ? 'btn-primary' : 'btn-secondary'}`}
          >
            Acknowledged
          </button>
        </div>
      </div>

      {alerts.length === 0 ? (
        <div className="card">
          <p className="text-secondary">No alerts found.</p>
        </div>
      ) : (
        <div className="grid gap-2">
          {alerts.map(alert => (
            <div key={alert.id} className="card">
              <div className="flex-between mb-2">
                <div className="flex gap-2">
                  <span className={`badge badge-${alert.severity}`}>
                    {alert.severity.toUpperCase()}
                  </span>
                  <span className="badge badge-info">{alert.alert_type}</span>
                  {alert.is_acknowledged && (
                    <span className="badge badge-success">✓ Acknowledged</span>
                  )}
                </div>
                <span className="text-sm text-secondary">
                  {new Date(alert.created_at).toLocaleString()}
                </span>
              </div>
              
              <h3 className="font-semibold mb-1">{alert.title}</h3>
              <p className="text-sm text-secondary mb-2">{alert.description}</p>
              
              <div className="flex-between">
                <span className="text-sm">
                  Risk Score: <span className="font-bold">{alert.score.toFixed(1)}/10</span>
                </span>
                {!alert.is_acknowledged && (
                  <button 
                    onClick={() => handleAcknowledge(alert.id)} 
                    className="btn btn-secondary btn-sm"
                  >
                    Acknowledge
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Alerts;
