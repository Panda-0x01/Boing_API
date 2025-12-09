import { useState, useEffect } from 'react';
import './APIs.css';

function APIs({ token }) {
  const [apis, setApis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ name: '', base_url: '', description: '' });
  const [apiMetrics, setApiMetrics] = useState({});

  useEffect(() => {
    fetchAPIs();
  }, []);

  useEffect(() => {
    if (apis.length > 0) {
      fetchAllApiMetrics();
    }
  }, [apis]);

  const fetchAPIs = async () => {
    try {
      const res = await fetch('/api/apis', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setApis(data);
      }
    } catch (err) {
      console.error('Failed to fetch APIs:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAllApiMetrics = async () => {
    const metricsData = {};
    for (const api of apis) {
      try {
        const res = await fetch('/api/metrics', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ api_id: api.id })
        });
        if (res.ok) {
          const data = await res.json();
          metricsData[api.id] = data;
        }
      } catch (err) {
        console.error(`Failed to fetch metrics for API ${api.id}:`, err);
      }
    }
    setApiMetrics(metricsData);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/apis', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      if (res.ok) {
        setShowForm(false);
        setFormData({ name: '', base_url: '', description: '' });
        fetchAPIs();
      }
    } catch (err) {
      console.error('Failed to create API:', err);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this API?')) return;
    
    try {
      const res = await fetch(`/api/apis/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        fetchAPIs();
      }
    } catch (err) {
      console.error('Failed to delete API:', err);
    }
  };

  if (loading) return <div className="spinner"></div>;

  return (
    <div>
      <div className="flex-between mb-4">
        <h1 className="page-title">Monitored APIs</h1>
        <button onClick={() => setShowForm(!showForm)} className="btn btn-primary">
          {showForm ? 'Cancel' : '+ Add API'}
        </button>
      </div>

      {showForm && (
        <div className="card mb-4">
          <h3 className="card-title">Register New API</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group mb-2">
              <label className="label">API Name</label>
              <input
                type="text"
                className="input"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                required
              />
            </div>
            <div className="form-group mb-2">
              <label className="label">Base URL (optional)</label>
              <input
                type="url"
                className="input"
                value={formData.base_url}
                onChange={(e) => setFormData({...formData, base_url: e.target.value})}
                placeholder="https://api.example.com"
              />
            </div>
            <div className="form-group mb-3">
              <label className="label">Description (optional)</label>
              <textarea
                className="input"
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                rows={3}
              />
            </div>
            <button type="submit" className="btn btn-primary">Create API</button>
          </form>
        </div>
      )}

      {apis.length === 0 ? (
        <div className="card">
          <p className="text-secondary">No APIs registered yet. Click "Add API" to get started.</p>
        </div>
      ) : (
        <div className="apis-grid">
          {apis.map(api => {
            const metrics = apiMetrics[api.id];
            return (
              <div key={api.id} className="api-card">
                <div className="api-card-header">
                  <div>
                    <h3 className="api-card-title">{api.name}</h3>
                    <p className="api-card-url">{api.base_url || 'No base URL'}</p>
                  </div>
                  <span className={`badge ${api.is_active ? 'badge-success' : 'badge-danger'}`}>
                    {api.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>

                <div className="api-card-key">
                  <label className="api-key-label">API Key:</label>
                  <code className="api-key-code">{api.api_key}</code>
                </div>

                {metrics ? (
                  <div className="api-metrics-grid">
                    <div className="api-metric">
                      <span className="api-metric-label">Total Requests</span>
                      <span className="api-metric-value">{metrics.total_requests?.toLocaleString() || 0}</span>
                    </div>
                    <div className="api-metric">
                      <span className="api-metric-label">Error Rate</span>
                      <span className="api-metric-value text-warning">
                        {((metrics.error_rate || 0) * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="api-metric">
                      <span className="api-metric-label">Avg Latency</span>
                      <span className="api-metric-value">{metrics.avg_latency_ms?.toFixed(0) || 0}ms</span>
                    </div>
                    <div className="api-metric">
                      <span className="api-metric-label">Threats</span>
                      <span className="api-metric-value text-destructive">
                        {metrics.suspicious_requests || 0}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="api-metrics-loading">Loading metrics...</div>
                )}

                <div className="api-card-footer">
                  <span className="api-card-date">
                    Created {new Date(api.created_at).toLocaleDateString()}
                  </span>
                  <button onClick={() => handleDelete(api.id)} className="btn btn-danger btn-sm">
                    Delete
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default APIs;
