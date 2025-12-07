import { useState, useEffect } from 'react';

function Admin({ token }) {
  const [blacklist, setBlacklist] = useState([]);
  const [whitelist, setWhitelist] = useState([]);
  const [newIP, setNewIP] = useState('');
  const [reason, setReason] = useState('');
  const [activeTab, setActiveTab] = useState('blacklist');

  useEffect(() => {
    fetchLists();
  }, []);

  const fetchLists = async () => {
    try {
      const [blackRes, whiteRes] = await Promise.all([
        fetch('/api/admin/blacklist', { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch('/api/admin/whitelist', { headers: { 'Authorization': `Bearer ${token}` } })
      ]);
      
      if (blackRes.ok) {
        const data = await blackRes.json();
        setBlacklist(data.blacklist);
      }
      if (whiteRes.ok) {
        const data = await whiteRes.json();
        setWhitelist(data.whitelist);
      }
    } catch (err) {
      console.error('Failed to fetch lists:', err);
    }
  };

  const handleAdd = async (listType) => {
    if (!newIP) return;
    
    try {
      const res = await fetch(`/api/admin/${listType}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ ip_address: newIP, reason })
      });
      
      if (res.ok) {
        setNewIP('');
        setReason('');
        fetchLists();
      }
    } catch (err) {
      console.error(`Failed to add to ${listType}:`, err);
    }
  };

  const handleRemove = async (listType, ip) => {
    if (!confirm(`Remove ${ip} from ${listType}?`)) return;
    
    try {
      const res = await fetch(`/api/admin/${listType}/${ip}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (res.ok) {
        fetchLists();
      }
    } catch (err) {
      console.error(`Failed to remove from ${listType}:`, err);
    }
  };

  return (
    <div>
      <h1 className="page-title">Admin Panel</h1>

      <div className="flex gap-2 mb-4">
        <button 
          onClick={() => setActiveTab('blacklist')} 
          className={`btn ${activeTab === 'blacklist' ? 'btn-primary' : 'btn-secondary'}`}
        >
          IP Blacklist
        </button>
        <button 
          onClick={() => setActiveTab('whitelist')} 
          className={`btn ${activeTab === 'whitelist' ? 'btn-primary' : 'btn-secondary'}`}
        >
          IP Whitelist
        </button>
      </div>

      <div className="card mb-4">
        <h3 className="card-title">Add IP to {activeTab}</h3>
        <div className="flex gap-2">
          <input
            type="text"
            className="input"
            placeholder="IP Address (e.g., 192.168.1.1)"
            value={newIP}
            onChange={(e) => setNewIP(e.target.value)}
          />
          <input
            type="text"
            className="input"
            placeholder="Reason (optional)"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
          />
          <button onClick={() => handleAdd(activeTab)} className="btn btn-primary">
            Add
          </button>
        </div>
      </div>

      <div className="card">
        <h3 className="card-title">
          {activeTab === 'blacklist' ? 'Blacklisted IPs' : 'Whitelisted IPs'}
        </h3>
        
        {(activeTab === 'blacklist' ? blacklist : whitelist).length === 0 ? (
          <p className="text-secondary">No IPs in {activeTab}</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>IP Address</th>
                <th>Reason</th>
                <th>Added</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {(activeTab === 'blacklist' ? blacklist : whitelist).map(item => (
                <tr key={item.id}>
                  <td><code>{item.ip_address}</code></td>
                  <td className="text-sm">{item.reason || '-'}</td>
                  <td className="text-sm">{new Date(item.created_at).toLocaleDateString()}</td>
                  <td>
                    <button 
                      onClick={() => handleRemove(activeTab, item.ip_address)} 
                      className="btn btn-danger btn-sm"
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default Admin;
