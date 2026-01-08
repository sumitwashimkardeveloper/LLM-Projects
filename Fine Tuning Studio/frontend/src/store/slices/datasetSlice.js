import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { datasetService } from '../../services/datasetService';

export const uploadDataset = createAsyncThunk(
  'datasets/upload',
  async (payload, { rejectWithValue }) => {
    try {
      const response = await datasetService.uploadDataset(
        payload.file,
        payload.name,
        payload.description
      );
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Upload failed');
    }
  }
);

export const fetchDatasets = createAsyncThunk(
  'datasets/fetchAll',
  async (_, { rejectWithValue }) => {
    try {
      const response = await datasetService.listDatasets();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to fetch datasets');
    }
  }
);

export const fetchDatasetPreview = createAsyncThunk(
  'datasets/preview',
  async (datasetId, { rejectWithValue }) => {
    try {
      const response = await datasetService.previewDataset(datasetId);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to preview dataset');
    }
  }
);

export const splitDataset = createAsyncThunk(
  'datasets/split',
  async ({ datasetId, trainRatio, valRatio, testRatio }, { rejectWithValue }) => {
    try {
      const response = await datasetService.splitDataset(
        datasetId,
        trainRatio,
        valRatio,
        testRatio
      );
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to split dataset');
    }
  }
);

const datasetSlice = createSlice({
  name: 'datasets',
  initialState: {
    datasets: [],
    preview: null,
    loading: false,
    error: null,
    uploadProgress: 0
  },
  extraReducers: (builder) => {
    builder
      .addCase(uploadDataset.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(uploadDataset.fulfilled, (state, action) => {
        state.loading = false;
        state.datasets.push(action.payload);
      })
      .addCase(uploadDataset.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchDatasets.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDatasets.fulfilled, (state, action) => {
        state.loading = false;
        state.datasets = action.payload;
      })
      .addCase(fetchDatasets.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchDatasetPreview.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchDatasetPreview.fulfilled, (state, action) => {
        state.loading = false;
        state.preview = action.payload;
      })
      .addCase(fetchDatasetPreview.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(splitDataset.fulfilled, (state, action) => {
        const idx = state.datasets.findIndex(d => d.id === action.payload.dataset_id);
        if (idx !== -1) {
          state.datasets[idx].train_samples = action.payload.train_samples;
          state.datasets[idx].val_samples = action.payload.val_samples;
          state.datasets[idx].test_samples = action.payload.test_samples;
        }
      });
  }
});

export default datasetSlice.reducer;
