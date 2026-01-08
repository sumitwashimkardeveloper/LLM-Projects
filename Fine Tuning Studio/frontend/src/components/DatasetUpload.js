import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { uploadDataset } from '../store/slices/datasetSlice';

export const DatasetUpload = () => {
  const dispatch = useDispatch();
  const { loading, error } = useSelector(state => state.datasets);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    file: null
  });

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: files ? files[0] : value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.file) {
      alert('Please select a file');
      return;
    }
    dispatch(uploadDataset({
      file: formData.file,
      name: formData.name || formData.file.name,
      description: formData.description
    }));
    setFormData({ name: '', description: '', file: null });
  };

  return (
    <div style={{ maxWidth: '500px', margin: '20px auto' }}>
      <h2>Upload Dataset</h2>
      {error && <div style={{ color: 'red', marginBottom: '10px' }}>{error}</div>}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          name="name"
          placeholder="Dataset name (optional)"
          value={formData.name}
          onChange={handleChange}
          style={{ display: 'block', width: '100%', marginBottom: '10px', padding: '8px' }}
        />
        <textarea
          name="description"
          placeholder="Description (optional)"
          value={formData.description}
          onChange={handleChange}
          style={{ display: 'block', width: '100%', marginBottom: '10px', padding: '8px', minHeight: '80px' }}
        />
        <input
          type="file"
          name="file"
          onChange={handleChange}
          accept=".csv,.json,.jsonl,.parquet"
          style={{ display: 'block', marginBottom: '10px' }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{ padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', cursor: 'pointer' }}
        >
          {loading ? 'Uploading...' : 'Upload Dataset'}
        </button>
      </form>
    </div>
  );
};

export default DatasetUpload;
