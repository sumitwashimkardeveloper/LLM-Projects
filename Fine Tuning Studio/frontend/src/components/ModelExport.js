import React, { useState } from 'react';
import apiClient from '../services/api';

export const ModelExport = ({ jobId }) => {
  const [format, setFormat] = useState('huggingface');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [repoName, setRepoName] = useState('');

  const handleExport = async () => {
    if (format === 'huggingface' && !repoName.trim()) {
      setError('Repository name is required for HuggingFace export');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const payload = format === 'huggingface' ? { repo_name: repoName } : {};
      const response = await apiClient.post(
        `/export/jobs/${jobId}/export/${format}`,
        payload
      );

      setSuccess(response.data.message);
      if (format === 'huggingface') {
        setRepoName('');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Export failed');
    } finally {
      setLoading(false);
    }
  };

  const handleMerge = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await apiClient.post(`/export/jobs/${jobId}/merge`);
      setSuccess(response.data.message);
    } catch (err) {
      setError(err.response?.data?.error || 'Merge failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '20px auto' }}>
      <h2>Export Model</h2>

      {error && <div style={{ color: 'red', marginBottom: '10px', padding: '10px', backgroundColor: '#ffe6e6', borderRadius: '4px' }}>{error}</div>}
      {success && <div style={{ color: 'green', marginBottom: '10px', padding: '10px', backgroundColor: '#e6ffe6', borderRadius: '4px' }}>{success}</div>}

      <div style={{ marginBottom: '20px' }}>
        <h3>Merge Adapters</h3>
        <p>Merge LoRA adapters with base model</p>
        <button
          onClick={handleMerge}
          disabled={loading}
          style={{ padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', cursor: 'pointer' }}
        >
          {loading ? 'Merging...' : 'Merge Adapters'}
        </button>
      </div>

      <div style={{ marginBottom: '20px', padding: '15px', border: '1px solid #ddd', borderRadius: '4px' }}>
        <h3>Export Format</h3>
        <select
          value={format}
          onChange={(e) => setFormat(e.target.value)}
          style={{ width: '100%', padding: '8px', marginBottom: '10px' }}
        >
          <option value="huggingface">HuggingFace Hub</option>
          <option value="onnx">ONNX</option>
          <option value="torchscript">TorchScript</option>
          <option value="ggml">GGML</option>
        </select>

        {format === 'huggingface' && (
          <input
            type="text"
            placeholder="Repository name (e.g., my-username/my-model)"
            value={repoName}
            onChange={(e) => setRepoName(e.target.value)}
            style={{ width: '100%', padding: '8px', marginBottom: '10px', boxSizing: 'border-box' }}
          />
        )}

        <button
          onClick={handleExport}
          disabled={loading}
          style={{ padding: '10px 20px', backgroundColor: '#28a745', color: 'white', border: 'none', cursor: 'pointer', width: '100%' }}
        >
          {loading ? 'Exporting...' : `Export as ${format.toUpperCase()}`}
        </button>
      </div>

      <div style={{ padding: '15px', backgroundColor: '#f9f9f9', borderRadius: '4px' }}>
        <h4>Export Formats</h4>
        <ul style={{ fontSize: '12px', color: '#666' }}>
          <li><strong>HuggingFace:</strong> Upload to HuggingFace Model Hub</li>
          <li><strong>ONNX:</strong> Cross-platform inference format</li>
          <li><strong>TorchScript:</strong> Optimized PyTorch format</li>
          <li><strong>GGML:</strong> Quantized format for CPU inference</li>
        </ul>
      </div>
    </div>
  );
};

export default ModelExport;
