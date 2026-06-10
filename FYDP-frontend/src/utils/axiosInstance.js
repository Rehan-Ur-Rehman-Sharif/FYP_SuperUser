import axios from "axios";
import summaryApi from "../common";

// Derive the backend domain from the summaryApi login URL so we have one source of truth
const backendDomain = summaryApi.login.url.replace("/api/login", "");

const axiosInstance = axios.create({
  baseURL: backendDomain,
});

// Attach access token to every request automatically
axiosInstance.interceptors.request.use((config) => {
  try {
    const token = JSON.parse(localStorage.getItem("currentUser"))?.token;
    if (token) config.headers.Authorization = `Bearer ${token}`;
  } catch {
    // ignore
  }
  return config;
});

// On 401, try to refresh the access token once then retry
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;

    const isExpired =
      error.response?.status === 401 &&
      !original._retry;

    if (!isExpired) return Promise.reject(error);

    original._retry = true;

    try {
      const currentUser = JSON.parse(localStorage.getItem("currentUser")) || {};
      const { data } = await axios.post(`${backendDomain}/api/token/refresh/`, {
        refresh: currentUser.refresh,
      });

      // Save new access token
      currentUser.token = data.access;
      localStorage.setItem("currentUser", JSON.stringify(currentUser));

      // Retry original request with new token
      original.headers.Authorization = `Bearer ${data.access}`;
      return axiosInstance(original);
    } catch {
      // Refresh also failed — clear session and redirect to login
      localStorage.removeItem("currentUser");
      window.location.href = "/login";
      return Promise.reject(error);
    }
  }
);

export default axiosInstance;
