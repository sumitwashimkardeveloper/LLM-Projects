import React, { useState, useEffect } from 'react';
import apiClient from '../services/api';

export const ModelComparison = () => {
  const [jobIds, setJobIds] = useState([]);
  const [inputJobIds, setInputJobIds] = useState('');
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCompare = async () => {
    if (!inputJobIds.trim()) {
      setError('Please enter job IDs');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const ids = inputJobIds.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id));

      const response = await apiClient.post('/dashboard/jobs/compare', {
        job_ids: ids
      });

      setComparison(response.data);
      setJobIds(ids);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to compare jobs');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '20px auto' }}>
      <h2>Model Comparison</h2>

      <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#f9f9f9', borderRadius: '4px' }}>
        <label style={{ display: 'block', marginBottom: '10px' }}>
          Enter Job IDs (comma-separated):
        </label>
        <input
          type="text"
          value={inputJobIds}
          onChange={(e) => setInputJobIds(e.target.value)}
          placeholder="e.g., 1,2,3"
          style={{ width: '100%', padding: '8px', marginBottom: '10px', boxSizing: 'border-box' }}
        />
        <button
          onClick={handleCompare}
          disabled={loading}
          style={{ padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', cursor: 'pointer' }}
        >
          {loading ? 'Comparing...' : 'Compare'}
        </button>
        {error && <div style={{ color: 'red', marginTop: '10px' }}>{error}</div>}
      </div>

      {comparison && comparison.length > 0 && (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #ddd', backgroundColor: '#f9f9f9' }}>
              <th style={{ padding: '10px', textAlign: 'left' }}>Job Name</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>Type</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>Status</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>Progress</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>Current Loss</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>Best Loss</th>
            </tr>
          </thead>
          <tbody>
            {comparison.map((job, idx) => (
              <tr key={idx} style={{ borderBottom: '1px solid #ddd' }}>
                <td style={{ padding: '10px' }}>{job.name}</td>
                <td style={{ padding: '10px' }}>{job.training_type}</td>
                <td style={{ padding: '10px' }}>
                  <span style={{
                    backgroundColor: job.status === 'completed' ? '#28a745' : job.status === 'running' ? '#17a2b8' : '#dc3545',
                    color: 'white',
                    padding: '5px 10px',
                    borderRadius: '4px',
                    fontSize: '12px'
                  }}>
                    {job.status}
                  </span>
                </td>
                <td style={{ padding: '10px' }}>{Math.round(job.progress)}%</td>
                <td style={{ padding: '10px' }}>{job.current_loss?.toFixed(4) || '-'}</td>
                <td style={{ padding: '10px' }}>{job.best_loss?.toFixed(4) || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default ModelComparison;
