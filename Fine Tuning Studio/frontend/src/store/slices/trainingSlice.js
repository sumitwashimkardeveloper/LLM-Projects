import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { trainingService } from '../../services/trainingService';

export const createTrainingJob = createAsyncThunk(
  'training/createJob',
  async (jobData, { rejectWithValue }) => {
    try {
      const response = await trainingService.createJob(jobData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to create job');
    }
  }
);

export const fetchTrainingJobs = createAsyncThunk(
  'training/fetchJobs',
  async (_, { rejectWithValue }) => {
    try {
      const response = await trainingService.listJobs();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to fetch jobs');
    }
  }
);

export const fetchTrainingJob = createAsyncThunk(
  'training/fetchJob',
  async (jobId, { rejectWithValue }) => {
    try {
      const response = await trainingService.getJob(jobId);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to fetch job');
    }
  }
);

export const startTrainingJob = createAsyncThunk(
  'training/startJob',
  async (jobId, { rejectWithValue }) => {
    try {
      const response = await trainingService.startTraining(jobId);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to start job');
    }
  }
);

export const pauseTrainingJob = createAsyncThunk(
  'training/pauseJob',
  async (jobId, { rejectWithValue }) => {
    try {
      const response = await trainingService.pauseTraining(jobId);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to pause job');
    }
  }
);

export const cancelTrainingJob = createAsyncThunk(
  'training/cancelJob',
  async (jobId, { rejectWithValue }) => {
    try {
      const response = await trainingService.cancelTraining(jobId);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to cancel job');
    }
  }
);

const trainingSlice = createSlice({
  name: 'training',
  initialState: {
    jobs: [],
    currentJob: null,
    checkpoints: [],
    loading: false,
    error: null
  },
  extraReducers: (builder) => {
    builder
      .addCase(createTrainingJob.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createTrainingJob.fulfilled, (state, action) => {
        state.loading = false;
        state.jobs.push(action.payload);
      })
      .addCase(createTrainingJob.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchTrainingJobs.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTrainingJobs.fulfilled, (state, action) => {
        state.loading = false;
        state.jobs = action.payload;
      })
      .addCase(fetchTrainingJobs.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchTrainingJob.fulfilled, (state, action) => {
        state.currentJob = action.payload;
        state.checkpoints = action.payload.checkpoints || [];
      })
      .addCase(startTrainingJob.fulfilled, (state) => {
        if (state.currentJob) {
          state.currentJob.status = 'running';
        }
      })
      .addCase(pauseTrainingJob.fulfilled, (state) => {
        if (state.currentJob) {
          state.currentJob.status = 'paused';
        }
      })
      .addCase(cancelTrainingJob.fulfilled, (state) => {
        if (state.currentJob) {
          state.currentJob.status = 'cancelled';
        }
      });
  }
});

export default trainingSlice.reducer;
