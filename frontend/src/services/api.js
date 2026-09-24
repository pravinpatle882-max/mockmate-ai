// API Client service for backend communications
const API_BASE_URL = window.location.origin;

class ApiService {
  getToken() {
    return localStorage.getItem("ai_interview_token");
  }

  setAuth(token, name, email) {
    localStorage.setItem("ai_interview_token", token);
    localStorage.setItem("ai_interview_user", JSON.stringify({ name, email }));
  }

  clearAuth() {
    localStorage.removeItem("ai_interview_token");
    localStorage.removeItem("ai_interview_user");
  }

  getUser() {
    const raw = localStorage.getItem("ai_interview_user");
    return raw ? JSON.parse(raw) : null;
  }

  isAuthenticated() {
    return !!this.getToken();
  }

  async request(endpoint, options = {}) {
    const token = this.getToken();
    const headers = { ...options.headers };

    if (!(options.body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const config = {
      ...options,
      headers
    };

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
      if (response.status === 401) {
        this.clearAuth();
        window.dispatchEvent(new Event("auth-changed"));
        throw new Error("Session expired. Please log in again.");
      }
      
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "API request failed");
      }
      return data;
    } catch (err) {
      console.error(`API Error on ${endpoint}:`, err);
      throw err;
    }
  }

  async register(name, email, password) {
    const res = await this.request("/auth/register", {
      method: "POST",
      body: JSON.stringify({ name, email, password })
    });
    this.setAuth(res.access_token, res.user_name, res.user_email);
    window.dispatchEvent(new Event("auth-changed"));
    return res;
  }

  async login(email, password) {
    const res = await this.request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });
    this.setAuth(res.access_token, res.user_name, res.user_email);
    window.dispatchEvent(new Event("auth-changed"));
    return res;
  }

  async getMe() {
    return await this.request("/auth/me");
  }

  async uploadResume(file) {
    const formData = new FormData();
    formData.append("file", file);
    return await this.request("/resume/upload", {
      method: "POST",
      body: formData
    });
  }

  async loadSampleResume() {
    return await this.request("/resume/sample", {
      method: "POST"
    });
  }

  async getCurrentResume() {
    return await this.request("/resume/current");
  }

  async createInterview({ domain, difficulty, num_questions, mode, use_resume_skills }) {
    return await this.request("/interview/create", {
      method: "POST",
      body: JSON.stringify({ domain, difficulty, num_questions, mode, use_resume_skills })
    });
  }

  async submitAnswer(interview_id, question_id, answer) {
    return await this.request("/interview/submit-answer", {
      method: "POST",
      body: JSON.stringify({ interview_id, question_id, answer })
    });
  }

  async completeInterview(interview_id) {
    return await this.request(`/interview/complete/${interview_id}`, {
      method: "POST"
    });
  }

  async getInterviewHistory() {
    return await this.request("/interview/history");
  }

  async getInterviewDetails(id) {
    return await this.request(`/interview/${id}`);
  }

  async getDashboardData() {
    return await this.request("/dashboard");
  }

  async transcribeSpeech(audioBlob) {
    const formData = new FormData();
    if (audioBlob) {
      formData.append("file", audioBlob, "recording.webm");
    }
    return await this.request("/speech/transcribe", {
      method: "POST",
      body: formData
    });
  }

  getPdfUrl(interview_id) {
    return `${API_BASE_URL}/interview/${interview_id}/pdf`;
  }
}

window.api = new ApiService();
