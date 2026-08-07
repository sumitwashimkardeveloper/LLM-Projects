import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import modelsReducer from './slices/modelsSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    models: modelsReducer,
  },
});

export default store;
