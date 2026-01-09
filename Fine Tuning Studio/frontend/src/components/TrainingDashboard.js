import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchTrainingJob } from '../store/slices/trainingSlice';
import apiClient from '../services/api';

export const TrainingDashboard = ({ jobId }) => {
  const dispatch = useDispatch();
  const { currentJob } = useSelector(state => state.training);
  const [metrics, setMetrics] = useState(null);
  const [recentMetrics, setRecentMetrics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dispatch(fetchTrainingJob(jobId));

    const metricsInterval = setInterval(async () => {
      try {
        const response = await apiClient.get(`/dashboard/jobs/${jobId}/metrics/recent`);
        setRecentMetrics(response.data);
      } catch (error) {
        console.error('Error fetching metrics:', error);
      }
    }, 5000);

    return () => clearInterval(metricsInterval);
  }, [jobId, dispatch]);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get(`/dashboard/jobs/${jobId}/metrics`);
        setMetrics(response.data);
      } catch (error) {
        console.error('Error fetching metrics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, [jobId]);

  if (loading) return <div>Loading metrics...</div>;

  return (
    <div style={{ maxWidth: '1200px', margin: '20px auto' }}>
      <h2>Training Dashboard - {currentJob?.name}</h2>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '15px', marginBottom: '20px' }}>
        <div style={{ padding: '15px', backgroundColor: '#f0f0f0', borderRadius: '4px' }}>
          <div style={{ fontSize: '12px', color: '#666' }}>Status</div>
          <div style={{ fontSize: '20px', fontWeight: 'bold' }}>{currentJob?.status}</div>
        </div>
        <div style={{ padding: '15px', backgroundColor: '#f0f0f0', borderRadius: '4px' }}>
          <div style={{ fontSize: '12px', color: '#666' }}>Progress</div>
          <div style={{ fontSize: '20px', fontWeight: 'bold' }}>{Math.round(currentJob?.progress || 0)}%</div>
        </div>
        <div style={{ padding: '15px', backgroundColor: '#f0f0f0', borderRadius: '4px' }}>
          <div style={{ fontSize: '12px', color: '#666' }}>Current Loss</div>
          <div style={{ fontSize: '20px', fontWeight: 'bold' }}>{currentJob?.current_loss?.toFixed(4) || 'N/A'}</div>
        </div>
        <div style={{ padding: '15px', backgroundColor: '#f0f0f0', borderRadius: '4px' }}>
          <div style={{ fontSize: '12px', color: '#666' }}>Best Loss</div>
          <div style={{ fontSize: '20px', fontWeight: 'bold' }}>{currentJob?.best_loss?.toFixed(4) || 'N/A'}</div>
        </div>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h3>Training Progress</h3>
        <div style={{ width: '100%', height: '30px', backgroundColor: '#e9ecef', borderRadius: '4px', overflow: 'hidden' }}>
          <div style={{
            width: `${currentJob?.progress || 0}%`,
            height: '100%',
            backgroundColor: '#007bff',
            transition: 'width 0.3s'
          }} />
        </div>
        <div style={{ marginTop: '10px', fontSize: '12px', color: '#666' }}>
          Step {currentJob?.current_step} / {currentJob?.total_steps}
        </div>
      </div>

      {metrics && (
        <div style={{ marginBottom: '20px' }}>
          <h3>Metrics Summary</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
            <div style={{ padding: '15px', border: '1px solid #ddd', borderRadius: '4px' }}>
              <div style={{ fontSize: '12px', color: '#666' }}>Min Loss</div>
              <div style={{ fontSize: '18px' }}>{metrics.min_loss?.toFixed(4)}</div>
            </div>
            <div style={{ padding: '15px', border: '1px solid #ddd', borderRadius: '4px' }}>
              <div style={{ fontSize: '12px', color: '#666' }}>Max Loss</div>
              <div style={{ fontSize: '18px' }}>{metrics.max_loss?.toFixed(4)}</div>
            </div>
            <div style={{ padding: '15px', border: '1px solid #ddd', borderRadius: '4px' }}>
              <div style={{ fontSize: '12px', color: '#666' }}>Avg Loss</div>
              <div style={{ fontSize: '18px' }}>{metrics.avg_loss?.toFixed(4)}</div>
            </div>
            <div style={{ padding: '15px', border: '1px solid #ddd', borderRadius: '4px' }}>
              <div style={{ fontSize: '12px', color: '#666' }}>Total Steps</div>
              <div style={{ fontSize: '18px' }}>{metrics.total_steps}</div>
            </div>
          </div>
        </div>
      )}

      {recentMetrics.length > 0 && (
        <div>
          <h3>Recent Metrics</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #ddd' }}>
                <th style={{ padding: '10px', textAlign: 'left' }}>Step</th>
                <th style={{ padding: '10px', textAlign: 'left' }}>Loss</th>
                <th style={{ padding: '10px', textAlign: 'left' }}>Eval Loss</th>
                <th style={{ padding: '10px', textAlign: 'left' }}>Accuracy</th>
                <th style={{ padding: '10px', textAlign: 'left' }}>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {recentMetrics.slice(-10).map((metric, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid #ddd' }}>
                  <td style={{ padding: '10px' }}>{metric.step}</td>
                  <td style={{ padding: '10px' }}>{metric.loss?.toFixed(4)}</td>
                  <td style={{ padding: '10px' }}>{metric.eval_loss?.toFixed(4) || '-'}</td>
                  <td style={{ padding: '10px' }}>{metric.accuracy?.toFixed(4) || '-'}</td>
                  <td style={{ padding: '10px', fontSize: '12px' }}>{new Date(metric.timestamp).toLocaleTimeString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default TrainingDashboard;
