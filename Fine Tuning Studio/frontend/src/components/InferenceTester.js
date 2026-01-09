import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import apiClient from '../services/api';

export const InferenceTester = () => {
  const { models } = useSelector(state => state.models);
  const [selectedModel, setSelectedModel] = useState('');
  const [inputText, setInputText] = useState('');
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [benchmarkResults, setBenchmarkResults] = useState(null);

  const handleTest = async () => {
    if (!selectedModel || !inputText.trim()) {
      setError('Please select a model and enter text');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.post('/inference/test', {
        model_id: parseInt(selectedModel),
        text: inputText,
        max_length: 100
      });

      setOutput(response.data.output);
    } catch (err) {
      setError(err.response?.data?.error || 'Inference failed');
    } finally {
      setLoading(false);
    }
  };

  const handleBenchmark = async () => {
    if (!selectedModel) {
      setError('Please select a model');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.post(`/inference/benchmark/${selectedModel}`, {
        text: inputText || 'Hello, how are you?',
        num_iterations: 5
      });

      setBenchmarkResults(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Benchmark failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '20px auto' }}>
      <h2>Inference Testing</h2>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
        <div>
          <h3>Test Input</h3>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            style={{ width: '100%', padding: '8px', marginBottom: '10px' }}
          >
            <option value="">Select Model</option>
            {models.map(model => (
              <option key={model.id} value={model.id}>{model.name}</option>
            ))}
          </select>

          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Enter text for inference"
            style={{ width: '100%', minHeight: '150px', padding: '8px', marginBottom: '10px' }}
          />

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
            <button
              onClick={handleTest}
              disabled={loading}
              style={{ padding: '10px', backgroundColor: '#007bff', color: 'white', border: 'none', cursor: 'pointer' }}
            >
              {loading ? 'Testing...' : 'Test'}
            </button>
            <button
              onClick={handleBenchmark}
              disabled={loading}
              style={{ padding: '10px', backgroundColor: '#28a745', color: 'white', border: 'none', cursor: 'pointer' }}
            >
              {loading ? 'Benchmarking...' : 'Benchmark'}
            </button>
          </div>

          {error && <div style={{ color: 'red', marginTop: '10px' }}>{error}</div>}
        </div>

        <div>
          <h3>Output</h3>
          <div style={{ minHeight: '150px', padding: '10px', backgroundColor: '#f9f9f9', borderRadius: '4px', overflowY: 'auto', maxHeight: '200px' }}>
            {output || 'Output will appear here'}
          </div>
        </div>
      </div>

      {benchmarkResults && (
        <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f9f9f9', borderRadius: '4px' }}>
          <h3>Benchmark Results</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '15px' }}>
            <div>
              <div style={{ fontSize: '12px', color: '#666' }}>Mean Latency</div>
              <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{benchmarkResults.latency_ms?.mean_latency_ms?.toFixed(2)} ms</div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: '#666' }}>Min Latency</div>
              <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{benchmarkResults.latency_ms?.min_latency_ms?.toFixed(2)} ms</div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: '#666' }}>Max Latency</div>
              <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{benchmarkResults.latency_ms?.max_latency_ms?.toFixed(2)} ms</div>
            </div>
            {benchmarkResults.memory && (
              <div>
                <div style={{ fontSize: '12px', color: '#666' }}>Peak Memory</div>
                <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{benchmarkResults.memory.peak_memory_gb?.toFixed(2)} GB</div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default InferenceTester;
