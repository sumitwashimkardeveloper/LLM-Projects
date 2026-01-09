import React, { useState, useEffect } from 'react';
import apiClient from '../services/api';

export const AlertsPanel = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [jobFilter, setJobFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 10000);
    return () => clearInterval(interval);
  }, [jobFilter, typeFilter]);

  const fetchAlerts = async () => {
    try {
      const params = new URLSearchParams();
      if (jobFilter) params.append('job_id', jobFilter);
      if (typeFilter) params.append('type', typeFilter);

      const response = await apiClient.get(`/alerts?${params.toString()}`);
      setAlerts(response.data);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    const colors = {
      'info': '#17a2b8',
      'warning': '#ffc107',
      'error': '#dc3545',
      'success': '#28a745'
    };
    return colors[severity] || '#6c757d';
  };

  const getAlertIcon = (alertType) => {
    const icons = {
      'job_started': '▶️',
      'job_completed': '✓',
      'job_failed': '✗',
      'resource_limit': '⚠️',
      'training_error': '❌'
    };
    return icons[alertType] || '●';
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '20px auto' }}>
      <h2>Alerts & Notifications</h2>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '20px' }}>
        <input
          type="text"
          placeholder="Filter by Job ID"
          value={jobFilter}
          onChange={(e) => setJobFilter(e.target.value)}
          style={{ padding: '8px' }}
        />
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          style={{ padding: '8px' }}
        >
          <option value="">All Alert Types</option>
          <option value="job_started">Job Started</option>
          <option value="job_completed">Job Completed</option>
          <option value="resource_limit">Resource Limit</option>
          <option value="training_error">Training Error</option>
        </select>
      </div>

      {loading ? (
        <div>Loading alerts...</div>
      ) : alerts.length === 0 ? (
        <div style={{ textAlign: 'center', color: '#666' }}>No alerts</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {alerts.map((alert, idx) => (
            <div
              key={idx}
              style={{
                padding: '15px',
                border: `2px solid ${getSeverityColor(alert.severity)}`,
                borderRadius: '4px',
                backgroundColor: '#f9f9f9'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <div>
                  <div style={{ fontSize: '14px', fontWeight: 'bold' }}>
                    {getAlertIcon(alert.type)} {alert.type.replace(/_/g, ' ').toUpperCase()}
                  </div>
                  <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
                    {alert.message}
                  </div>
                  {alert.job_id && (
                    <div style={{ fontSize: '11px', color: '#999', marginTop: '5px' }}>
                      Job ID: {alert.job_id}
                    </div>
                  )}
                </div>
                <div style={{ fontSize: '11px', color: '#999' }}>
                  {new Date(alert.timestamp).toLocaleString()}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AlertsPanel;
