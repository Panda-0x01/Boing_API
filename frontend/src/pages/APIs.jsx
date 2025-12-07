import { useState, useEffect } from 'react';

function APIs({ token }) {
  const [apis, setApis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ name: '', base_url: '', description: '' });

  useEffect(() => {
    fetchAPIs();
  }, []);

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
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>API Key</th>
                <th>Base URL</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {apis.map(api => (
                <tr key={api.id}>
                  <td className="font-semibold">{api.name}</td>
                  <td><code>{api.api_key}</code></td>
                  <td className="text-sm">{api.base_url || '-'}</td>
                  <td>
                    <span className={`badge ${api.is_active ? 'badge-success' : 'badge-danger'}`}>
                      {api.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="text-sm">{new Date(api.created_at).toLocaleDateString()}</td>
                  <td>
                    <button onClick={() => handleDelete(api.id)} className="btn btn-danger btn-sm">
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default APIs;
