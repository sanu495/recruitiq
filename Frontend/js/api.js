const API_BASE = 'http://127.0.0.1:8000';

// ── Token Management ──────────────────────────────────────────────────────────
const Token = {
  get:    ()      => localStorage.getItem('riq_token'),
  set:    (t)     => localStorage.setItem('riq_token', t),
  remove: ()      => localStorage.removeItem('riq_token'),
};

const User = {
  get:    ()      => JSON.parse(localStorage.getItem('riq_user') || 'null'),
  set:    (u)     => localStorage.setItem('riq_user', JSON.stringify(u)),
  remove: ()      => localStorage.removeItem('riq_user'),
};

// ── Core Fetch Wrapper ────────────────────────────────────────────────────────
async function apiCall(method, endpoint, body = null, isForm = false) {
  const headers = {};
  const token = Token.get();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const options = { method, headers };

  if (body) {
    if (isForm) {
      options.body = body;
    } else {
      headers['Content-Type'] = 'application/json';
      options.body = JSON.stringify(body);
    }
  }

  try {
    const res = await fetch(`${API_BASE}${endpoint}`, options);
    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      const msg = data.detail || `Error ${res.status}`;
      throw new Error(Array.isArray(msg) ? msg[0]?.msg || 'Validation error' : msg);
    }
    return data;
  } catch (err) {
    if (err.message === 'Failed to fetch') {
      throw new Error('Cannot connect to server. Make sure backend is running.');
    }
    throw err;
  }
}

// ── Auth ──────────────────────────────────────────────────────────────────────
const AuthAPI = {
  async register(name, email, phone, password, role) {
    return apiCall('POST', '/api/auth/register', { name, email, phone, password, role });
  },

  async login(email, password) {
    const form = new URLSearchParams();
    form.append('username', email);
    form.append('password', password);

    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Login failed');

    Token.set(data.access_token);
    User.set({ id: data.user_id, name: data.name, role: data.role, email: data.email });
    return data;
  },

  async me() {
    return apiCall('GET', '/api/auth/me');
  },

  logout() {
    Token.remove();
    User.remove();
    const root = window.location.pathname.includes('/dashboard/') || 
                 window.location.pathname.includes('/pages/') ? '../' : './';
    window.location.href = root + '/login';
},
};

// ── Jobs ──────────────────────────────────────────────────────────────────────
const JobsAPI = {
  list:       (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return apiCall('GET', `/api/jobs${q ? '?' + q : ''}`);
  },
  get:        (id)          => apiCall('GET',    `/api/jobs/${id}`),
  create:     (data)        => apiCall('POST',   '/api/jobs', data),
  update:     (id, data)    => apiCall('PUT',    `/api/jobs/${id}`, data),
  delete:     (id)          => apiCall('DELETE', `/api/jobs/${id}`),
  myPosted:   ()            => apiCall('GET',    '/api/jobs/my/posted'),
  setStatus:  (id, status)  => apiCall('PATCH',  `/api/jobs/${id}/status?status=${status}`),
};

// ── Applications ──────────────────────────────────────────────────────────────
const AppAPI = {
  apply: async (jobId, coverLetter, resumeFile) => {
    const form = new FormData();
    form.append('job_id', jobId);
    form.append('cover_letter', coverLetter);
    form.append('resume', resumeFile);
    return apiCall('POST', '/api/applications', form, true);
  },
  myApps:       ()         => apiCall('GET',    '/api/applications/my'),
  forJob:       (jobId)    => apiCall('GET',    `/api/applications/job/${jobId}`),
  get:          (id)       => apiCall('GET',    `/api/applications/${id}`),
  withdraw:     (id)       => apiCall('DELETE', `/api/applications/${id}`),
  addNote:      (id, note) => apiCall('POST',   `/api/applications/${id}/notes`, { note }),
  getNotes:     (id)       => apiCall('GET',    `/api/applications/${id}/notes`),
  screen:       (id)       => apiCall('POST',   `/api/applications/${id}/screen`),
  analysis:     (id)       => apiCall('GET',    `/api/applications/${id}/analysis`),
  exportCSV:    (jobId)    => `${API_BASE}/api/applications/job/${jobId}/export`,
};

// ── Pipeline ──────────────────────────────────────────────────────────────────
const PipelineAPI = {
  forJob:      (jobId)          => apiCall('GET',   `/api/pipeline/job/${jobId}`),
  updateStage: (appId, stage)   => apiCall('PATCH', `/api/pipeline/${appId}/stage`, { stage }),
  summary:     (jobId)          => apiCall('GET',   `/api/pipeline/job/${jobId}/summary`),
  overview:    ()               => apiCall('GET',   '/api/pipeline/overview'),
  bulkReject:  (jobId)          => apiCall('PATCH', `/api/pipeline/job/${jobId}/bulk-reject`),
};

// ── Analytics ─────────────────────────────────────────────────────────────────
const AnalyticsAPI = {
  overview:          () => apiCall('GET', '/api/analytics/overview'),
  pipelineBreakdown: () => apiCall('GET', '/api/analytics/pipeline-breakdown'),
  perJob:            () => apiCall('GET', '/api/analytics/applications-per-job'),
  aiScores:          () => apiCall('GET', '/api/analytics/ai-score-distribution'),
  topCandidates:     (jobId = null, limit = 10) => {
    const q = new URLSearchParams({ limit });
    if (jobId) q.append('job_id', jobId);
    return apiCall('GET', `/api/analytics/top-candidates?${q}`);
  },
  monthlyTrend:      () => apiCall('GET', '/api/analytics/monthly-trend'),
};

// ── Interviews ────────────────────────────────────────────────────────────────
const InterviewAPI = {
  schedule:  (data)   => apiCall('POST',  '/api/interviews', data),
  list:      ()       => apiCall('GET',   '/api/interviews'),
  get:       (id)     => apiCall('GET',   `/api/interviews/${id}`),
  update:    (id, d)  => apiCall('PUT',   `/api/interviews/${id}`, d),
  confirm:   (id)     => apiCall('PATCH', `/api/interviews/${id}/confirm`),
  cancel:    (id)     => apiCall('PATCH', `/api/interviews/${id}/cancel`),
  upcoming:  ()       => apiCall('GET',   '/api/interviews/upcoming/list'),
};

// ── Notifications ─────────────────────────────────────────────────────────────
const NotifAPI = {
  list:        ()   => apiCall('GET',   '/api/notifications'),
  unreadCount: ()   => apiCall('GET',   '/api/notifications/unread-count'),
  markRead:    (id) => apiCall('PATCH', `/api/notifications/${id}/read`),
  markAllRead: ()   => apiCall('PATCH', '/api/notifications/mark-all-read'),
  delete:      (id) => apiCall('DELETE',`/api/notifications/${id}`),
};