import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchTrainingJobs, startTrainingJob, pauseTrainingJob, cancelTrainingJob } from '../store/slices/trainingSlice';

export const TrainingJobList = () => {
  const dispatch = useDispatch();
  const { jobs, loading } = useSelector(state => state.training);

  useEffect(() => {
    dispatch(fetchTrainingJobs());
  }, [dispatch]);

  const handleStartJob = (jobId) => {
    dispatch(startTrainingJob(jobId));
  };

  const handlePauseJob = (jobId) => {
    dispatch(pauseTrainingJob(jobId));
  };

  const handleCancelJob = (jobId) => {
    dispatch(cancelTrainingJob(jobId));
  };

  const getStatusColor = (status) => {
    const colors = {
      'queued': '#ffc107',
      'running': '#17a2b8',
      'completed': '#28a745',
      'failed': '#dc3545',
      'paused': '#6c757d',
      'cancelled': '#6c757d'
    };
    return colors[status] || '#6c757d';
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '20px auto' }}>
      <h2>Training Jobs</h2>
      {loading && <p>Loading...</p>}
      {jobs.length === 0 ? (
        <p>No training jobs found</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #ddd' }}>
              <th style={{ padding: '10px', textAlign: 'left' }}>Name</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>Status</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>Progress</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>Type</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map(job => (
              <tr key={job.id} style={{ borderBottom: '1px solid #ddd' }}>
                <td style={{ padding: '10px' }}>{job.name}</td>
                <td style={{ padding: '10px' }}>
                  <span style={{
                    backgroundColor: getStatusColor(job.status),
                    color: 'white',
                    padding: '5px 10px',
                    borderRadius: '4px',
                    fontSize: '12px'
                  }}>
                    {job.status}
                  </span>
                </td>
                <td style={{ padding: '10px' }}>
                  <div style={{ width: '100px', height: '20px', backgroundColor: '#e9ecef', borderRadius: '4px', overflow: 'hidden' }}>
                    <div style={{
                      width: `${job.progress}%`,
                      height: '100%',
                      backgroundColor: '#007bff',
                      transition: 'width 0.3s'
                    }} />
                  </div>
                  <small>{Math.round(job.progress)}%</small>
                </td>
                <td style={{ padding: '10px' }}>{job.training_type}</td>
                <td style={{ padding: '10px' }}>
                  {job.status === 'queued' && (
                    <button onClick={() => handleStartJob(job.id)} style={{ marginRight: '5px', padding: '5px 10px' }}>
                      Start
                    </button>
                  )}
                  {job.status === 'running' && (
                    <button onClick={() => handlePauseJob(job.id)} style={{ marginRight: '5px', padding: '5px 10px' }}>
                      Pause
                    </button>
                  )}
                  {job.status === 'running' && (
                    <button onClick={() => handleCancelJob(job.id)} style={{ padding: '5px 10px', backgroundColor: '#dc3545', color: 'white' }}>
                      Cancel
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default TrainingJobList;
