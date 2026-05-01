const API_BASE = localStorage.getItem('apiBase') || 'http://127.0.0.1:5000';

async function request(path, options = {}) {
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      ...options
    });
    const contentType = response.headers.get('content-type') || '';
    const payload = contentType.includes('application/json') ? await response.json() : { success: false, message: await response.text() };

    if (!response.ok || payload.success === false) {
      throw new Error(payload.message || `Request failed: ${response.status}`);
    }
    return payload;
  } catch (error) {
    throw new Error(error.message || 'No se pudo conectar con el backend.');
  }
}

window.api = {
  checkHealth: async () => request('/health'),
  createBackup: async (payload) => request('/api/backup/execute', { method: 'POST', body: JSON.stringify(payload) }),
  restoreBackup: async (payload) => request('/api/restore/execute', { method: 'POST', body: JSON.stringify(payload) }),
  getBackups: async (payload) => request('/api/restore/list', { method: 'POST', body: JSON.stringify(payload) }),
  getLogs: () => window.electronAPI?.readLogs?.() || Promise.resolve([])
};
