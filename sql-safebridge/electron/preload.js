const { contextBridge } = require('electron');
const fs = require('fs');
const path = require('path');

function parseLogLine(line) {
  const [date, action, status] = line.split('|').map((x) => (x || '').trim());
  return { date, action, status };
}

contextBridge.exposeInMainWorld('electronAPI', {
  readLogs: async () => {
    try {
      const logsDir = path.resolve(__dirname, '..', 'logs');
      if (!fs.existsSync(logsDir)) return [];
      const files = fs.readdirSync(logsDir).filter((f) => f.endsWith('.log'));
      const records = [];
      for (const file of files) {
        const content = fs.readFileSync(path.join(logsDir, file), 'utf8');
        content.split('\n').filter(Boolean).forEach((line) => records.push(parseLogLine(line)));
      }
      return records.sort((a, b) => (a.date < b.date ? 1 : -1)).slice(0, 200);
    } catch {
      return [];
    }
  }
});
