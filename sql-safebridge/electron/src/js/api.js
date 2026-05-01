const API_BASE = localStorage.getItem('apiBase') || 'http://127.0.0.1:8000';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }
  const contentType = response.headers.get('content-type') || '';
  return contentType.includes('application/json') ? response.json() : response.text();
}

window.api = {
  createBackup: () => request('/backup', { method: 'POST' }),
  restoreBackup: (name) => request('/restore', { method: 'POST', body: JSON.stringify({ name }) }),
  getBackups: () => request('/backup'),
  getLogs: () => window.electronAPI?.readLogs?.() || Promise.resolve([])
};
