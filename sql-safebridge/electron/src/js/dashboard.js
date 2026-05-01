const state = { backups: [], selectedBackup: null, restoring: false };

const qs = (id) => document.getElementById(id);

function toast(message, tone = 'info') {
  const el = document.createElement('div');
  el.className = 'toast';
  el.style.borderLeftColor = tone === 'error' ? 'var(--error)' : tone === 'success' ? 'var(--success)' : 'var(--primary)';
  el.textContent = message;
  qs('toastContainer').appendChild(el);
  setTimeout(() => el.remove(), 3200);
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
}

function toggleTheme() {
  applyTheme(document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
}

function statusBadge(status = 'in progress') {
  const cls = status.includes('success') ? 'success' : status.includes('error') ? 'error' : 'progressing';
  return `<span class="status ${cls}">${status}</span>`;
}

function renderBackups() {
  const body = qs('backupTableBody');
  const restoreSelect = qs('restoreSelect');
  body.innerHTML = '';
  restoreSelect.innerHTML = '';
  state.backups.forEach((item) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${item.name}</td><td>${item.date || '-'}</td><td>${item.size || '-'}</td><td>${statusBadge(item.status || 'success')}</td>`;
    body.appendChild(tr);
    const op = document.createElement('option');
    op.value = item.name;
    op.textContent = `${item.name} (${item.date || '-'})`;
    restoreSelect.appendChild(op);
  });

  qs('totalBackups').textContent = String(state.backups.length);
  if (state.backups[0]) qs('lastBackupStatus').innerHTML = statusBadge(state.backups[0].status || 'success');
  const totalMb = state.backups.reduce((acc, b) => acc + Number((b.size || '0').replace(/[^\d.]/g, '')), 0);
  qs('storageUsage').textContent = `${Math.round(totalMb)} MB`;
  qs('storageBar').style.width = `${Math.min(100, totalMb / 10)}%`;
}

async function loadBackups() {
  try {
    const data = await window.api.getBackups();
    state.backups = Array.isArray(data) ? data : (data.backups || []);
    renderBackups();
  } catch (e) { toast(`Failed to load backups: ${e.message}`, 'error'); }
}

async function createBackup() {
  const btn = qs('createBackupBtn');
  btn.disabled = true; qs('backupLoading').classList.remove('hidden');
  try {
    await window.api.createBackup();
    toast('Backup created successfully', 'success');
    await loadBackups();
  } catch (e) {
    toast(`Backup failed: ${e.message}`, 'error');
  } finally {
    btn.disabled = false; qs('backupLoading').classList.add('hidden');
  }
}

async function loadHistory() {
  const rows = await window.api.getLogs();
  const body = qs('historyTableBody'); body.innerHTML = '';
  rows.forEach((log) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${log.date || '-'}</td><td>${log.action || '-'}</td><td>${statusBadge(log.status || '-')}</td>`;
    body.appendChild(tr);
  });
}

function switchSection(sectionId) {
  document.querySelectorAll('.section').forEach((s) => s.classList.toggle('active', s.id === sectionId));
  document.querySelectorAll('.nav-item').forEach((n) => n.classList.toggle('active', n.dataset.section === sectionId));
}

function setupEvents() {
  qs('themeToggle').addEventListener('click', toggleTheme);
  qs('themeToggleSettings').addEventListener('click', toggleTheme);
  qs('createBackupBtn').addEventListener('click', createBackup);
  document.querySelectorAll('.nav-item').forEach((item) => item.addEventListener('click', () => switchSection(item.dataset.section)));

  qs('restoreBtn').addEventListener('click', () => qs('confirmModal').showModal());
  qs('cancelRestore').addEventListener('click', () => qs('confirmModal').close());
  qs('confirmRestore').addEventListener('click', async () => {
    const selected = qs('restoreSelect').value;
    if (!selected) return toast('Select a backup first', 'error');
    if (state.restoring) return;
    state.restoring = true; qs('restoreProgress').classList.remove('hidden'); qs('confirmModal').close();
    try {
      await window.api.restoreBackup(selected);
      qs('lastRestore').textContent = new Date().toLocaleString();
      toast('Restore completed', 'success');
    } catch (e) {
      const msg = e.message.includes('exists') ? 'Restore blocked: target DB already exists.' : `Restore failed: ${e.message}`;
      toast(msg, 'error');
    } finally {
      state.restoring = false; qs('restoreProgress').classList.add('hidden');
    }
  });
}

(async function init() {
  applyTheme(localStorage.getItem('theme') || 'light');
  setupEvents();
  await loadBackups();
  await loadHistory();
})();
