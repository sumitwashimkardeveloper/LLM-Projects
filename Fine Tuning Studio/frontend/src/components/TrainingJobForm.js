import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { createTrainingJob } from '../store/slices/trainingSlice';
import { fetchModels } from '../store/slices/modelsSlice';
import { fetchDatasets } from '../store/slices/datasetSlice';

export const TrainingJobForm = () => {
  const dispatch = useDispatch();
  const { models } = useSelector(state => state.models);
  const { datasets } = useSelector(state => state.datasets);
  const { loading, error } = useSelector(state => state.training);

  const [formData, setFormData] = useState({
    name: '',
    model_id: '',
    dataset_id: '',
    training_type: 'lora',
    learning_rate: 2e-4,
    batch_size: 4,
    num_epochs: 3,
    lora_r: 8,
    lora_alpha: 16,
    lora_dropout: 0.05,
    use_4bit: false,
    use_8bit: false,
    save_steps: 500
  });

  useEffect(() => {
    dispatch(fetchModels());
    dispatch(fetchDatasets());
  }, [dispatch]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : (name.includes('_') && !name.includes('name') ? parseFloat(value) : value)
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.name || !formData.model_id || !formData.dataset_id) {
      alert('Please fill in all required fields');
      return;
    }
    dispatch(createTrainingJob(formData));
    setFormData({
      name: '',
      model_id: '',
      dataset_id: '',
      training_type: 'lora',
      learning_rate: 2e-4,
      batch_size: 4,
      num_epochs: 3,
      lora_r: 8,
      lora_alpha: 16,
      lora_dropout: 0.05,
      use_4bit: false,
      use_8bit: false,
      save_steps: 500
    });
  };

  return (
    <div style={{ maxWidth: '600px', margin: '20px auto' }}>
      <h2>Create Training Job</h2>
      {error && <div style={{ color: 'red', marginBottom: '10px' }}>{error}</div>}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          name="name"
          placeholder="Job name"
          value={formData.name}
          onChange={handleChange}
          required
          style={{ display: 'block', width: '100%', marginBottom: '10px', padding: '8px' }}
        />

        <select
          name="model_id"
          value={formData.model_id}
          onChange={handleChange}
          required
          style={{ display: 'block', width: '100%', marginBottom: '10px', padding: '8px' }}
        >
          <option value="">Select Model</option>
          {models.map(model => (
            <option key={model.id} value={model.id}>{model.name}</option>
          ))}
        </select>

        <select
          name="dataset_id"
          value={formData.dataset_id}
          onChange={handleChange}
          required
          style={{ display: 'block', width: '100%', marginBottom: '10px', padding: '8px' }}
        >
          <option value="">Select Dataset</option>
          {datasets.map(dataset => (
            <option key={dataset.id} value={dataset.id}>{dataset.name}</option>
          ))}
        </select>

        <select
          name="training_type"
          value={formData.training_type}
          onChange={handleChange}
          style={{ display: 'block', width: '100%', marginBottom: '10px', padding: '8px' }}
        >
          <option value="lora">LoRA</option>
          <option value="qlora">QLoRA</option>
          <option value="peft">PEFT</option>
        </select>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '10px' }}>
          <input
            type="number"
            name="learning_rate"
            placeholder="Learning rate"
            value={formData.learning_rate}
            onChange={handleChange}
            step="1e-5"
            style={{ padding: '8px' }}
          />
          <input
            type="number"
            name="batch_size"
            placeholder="Batch size"
            value={formData.batch_size}
            onChange={handleChange}
            style={{ padding: '8px' }}
          />
          <input
            type="number"
            name="num_epochs"
            placeholder="Epochs"
            value={formData.num_epochs}
            onChange={handleChange}
            style={{ padding: '8px' }}
          />
          <input
            type="number"
            name="save_steps"
            placeholder="Save steps"
            value={formData.save_steps}
            onChange={handleChange}
            style={{ padding: '8px' }}
          />
        </div>

        <div style={{ marginBottom: '10px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <input
            type="number"
            name="lora_r"
            placeholder="LoRA R"
            value={formData.lora_r}
            onChange={handleChange}
            style={{ padding: '8px' }}
          />
          <input
            type="number"
            name="lora_alpha"
            placeholder="LoRA Alpha"
            value={formData.lora_alpha}
            onChange={handleChange}
            style={{ padding: '8px' }}
          />
          <input
            type="number"
            name="lora_dropout"
            placeholder="LoRA Dropout"
            value={formData.lora_dropout}
            onChange={handleChange}
            step="0.01"
            style={{ padding: '8px' }}
          />
        </div>

        <div style={{ marginBottom: '10px' }}>
          <label>
            <input
              type="checkbox"
              name="use_4bit"
              checked={formData.use_4bit}
              onChange={handleChange}
            />
            Use 4-bit Quantization
          </label>
          <label style={{ marginLeft: '20px' }}>
            <input
              type="checkbox"
              name="use_8bit"
              checked={formData.use_8bit}
              onChange={handleChange}
            />
            Use 8-bit Quantization
          </label>
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{ padding: '10px 20px', backgroundColor: '#28a745', color: 'white', border: 'none', cursor: 'pointer', width: '100%' }}
        >
          {loading ? 'Creating...' : 'Create Training Job'}
        </button>
      </form>
    </div>
  );
};

export default TrainingJobForm;
