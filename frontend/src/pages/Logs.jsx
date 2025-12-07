import { useState, useEffect } from 'react';

function Logs({ token }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [suspiciousOnly, setSuspiciousOnly] = useState(false);

  useEffect(() => {
    fetchLogs();
  }, [suspiciousOnly]);

  const fetchLogs = async () => {
    try {
      const res = await fetch('/api/logs/query', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          suspicious_only: suspiciousOnly,
          limit: 100,
          offset: 0
        })
      });
      if (res.ok) {
        const data = await res.json();
        setLogs(data.logs);
      }
    } catch (err) {
      console.error('Failed to fetch logs:', err);
    } finally {
      setLoading(false);
    }
  };

  const exportLogs = async () => {
    try {
      const res = await fetch('/api/logs/export', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          suspicious_only: suspiciousOnly,
          limit: 1000,
          offset: 0
        })
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `boing_logs_${Date.now()}.csv`;
        a.click();
      }
    } catch (err) {
      console.error('Failed to export logs:', err);
    }
  };

  if (loading) return <div className="spinner"></div>;

  return (
    <div>
      <div className="flex-between mb-4">
        <h1 className="page-title">Request Logs</h1>
        <div className="flex gap-2">
          <button 
            onClick={() => setSuspiciousOnly(!suspiciousOnly)} 
            className={`btn ${suspiciousOnly ? 'btn-primary' : 'btn-secondary'}`}
          >
            {suspiciousOnly ? 'Show All' : 'Suspicious Only'}
          </button>
          <button onClick={exportLogs} className="btn btn-secondary">
            Export CSV
          </button>
        </div>
      </div>

      {logs.length === 0 ? (
        <div className="card">
          <p className="text-secondary">No logs found.</p>
        </div>
      ) : (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Method</th>
                <th>Endpoint</th>
                <th>Client IP</th>
                <th>Status</th>
                <th>Latency</th>
                <th>Suspicious</th>
              </tr>
            </thead>
            <tbody>
              {logs.map(log => (
                <tr key={log.id}>
                  <td className="text-sm">
                    {new Date(log.timestamp * 1000).toLocaleString()}
                  </td>
                  <td>
                    <span className="method-badge">{log.method}</span>
                  </td>
                  <td className="text-sm">{log.endpoint}</td>
                  <td className="text-sm">{log.client_ip}</td>
                  <td>
                    <span className={log.status_code >= 400 ? 'text-danger' : 'text-success'}>
                      {log.status_code}
                    </span>
                  </td>
                  <td className="text-sm">{log.latency_ms?.toFixed(0) || '-'}ms</td>
                  <td>
                    {log.is_suspicious ? (
                      <span className="badge badge-danger">⚠ Yes</span>
                    ) : (
                      <span className="badge badge-success">✓ No</span>
                    )}
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

export default Logs;
