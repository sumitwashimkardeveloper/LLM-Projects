import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { modelsAPI } from '../../services/api';

export const fetchSupportedModels = createAsyncThunk(
  'models/fetchSupportedModels',
  async (_, { rejectWithValue }) => {
    try {
      const response = await modelsAPI.getSupportedModels();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to fetch models');
    }
  }
);

export const fetchModels = createAsyncThunk(
  'models/fetchModels',
  async (_, { rejectWithValue }) => {
    try {
      const response = await modelsAPI.listModels();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to fetch models');
    }
  }
);

export const createModel = createAsyncThunk(
  'models/createModel',
  async (modelData, { rejectWithValue }) => {
    try {
      const response = await modelsAPI.createModel(modelData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to create model');
    }
  }
);

const modelsSlice = createSlice({
  name: 'models',
  initialState: {
    supportedModels: {},
    models: [],
    loading: false,
    error: null,
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchSupportedModels.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSupportedModels.fulfilled, (state, action) => {
        state.loading = false;
        state.supportedModels = action.payload;
      })
      .addCase(fetchSupportedModels.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchModels.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchModels.fulfilled, (state, action) => {
        state.loading = false;
        state.models = action.payload;
      })
      .addCase(fetchModels.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(createModel.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createModel.fulfilled, (state, action) => {
        state.loading = false;
        state.models.push(action.payload);
      })
      .addCase(createModel.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export default modelsSlice.reducer;
