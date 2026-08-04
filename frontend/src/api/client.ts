/**
 * Axios API client with interceptors and error handling.
 */
import axios, { AxiosError, type AxiosInstance } from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data as Record<string, unknown>;
      const detail = data?.detail || "An error occurred";

      console.error(`API Error [${status}]:`, detail);

      if (status === 422) {
        throw new Error(`Validation error: ${JSON.stringify(detail)}`);
      }
      if (status === 404) {
        throw new Error("Resource not found");
      }
      throw new Error(String(detail));
    }
    if (error.request) {
      throw new Error("Network error: Unable to reach the server");
    }
    throw error;
  }
);

export default apiClient;
