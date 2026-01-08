import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import modelsReducer from './slices/modelsSlice';
import datasetReducer from './slices/datasetSlice';
import trainingReducer from './slices/trainingSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    models: modelsReducer,
    datasets: datasetReducer,
    training: trainingReducer,
  },
});

export default store;
