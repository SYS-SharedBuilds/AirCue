const express = require('express');
const cors = require('cors');
const path = require('path');
const { spawn } = require('child_process');
const dotenv = require('dotenv');

// Load environment variables from repo root .env
dotenv.config({ path: path.resolve(__dirname, '../../.env') });

const app = express();
const PORT = process.env.PORT || 5001;
const REPO_ROOT = path.resolve(__dirname, '../..');
const PYTHON_PATH = path.join(REPO_ROOT, '.venv/bin/python3');
const BRIDGE_SCRIPT = path.join(__dirname, 'bridge.py');

app.use(cors());
app.use(express.json());

// Serve static pregenerated audio clips from /clips
app.use('/clips', express.static(path.join(REPO_ROOT, 'clips')));

// Serve production React static build if present
const CLIENT_DIST = path.join(REPO_ROOT, 'web/client/dist');
app.use(express.static(CLIENT_DIST));

// Helper to invoke python bridge asynchronously
function callBridge(action, payload = {}) {
  return new Promise((resolve, reject) => {
    const payloadStr = JSON.stringify(payload);
    const proc = spawn(PYTHON_PATH, [BRIDGE_SCRIPT, action, payloadStr], {
      cwd: REPO_ROOT,
      env: { ...process.env },
    });

    let stdout = '';
    let stderr = '';

    proc.stdout.on('data', (chunk) => {
      stdout += chunk.toString();
    });

    proc.stderr.on('data', (chunk) => {
      stderr += chunk.toString();
    });

    proc.on('close', (code) => {
      if (code !== 0) {
        return reject(new Error(stderr || `Bridge exited with code ${code}`));
      }
      try {
        const parsed = JSON.parse(stdout.trim());
        resolve(parsed);
      } catch (err) {
        reject(new Error(`Failed to parse bridge JSON: ${stdout.slice(0, 200)}`));
      }
    });
  });
}

// 1. Health & status
app.get('/api/status', async (req, res) => {
  try {
    const data = await callBridge('status');
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 2. Locations list
app.get('/api/locations', async (req, res) => {
  try {
    const data = await callBridge('locations');
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 3. Telemetry records & summary stats for a location
app.get('/api/telemetry', async (req, res) => {
  try {
    const location = req.query.location || 'Vijay Nagar Scheme-78, Indore - Glenmark';
    const limit = parseInt(req.query.limit || '150', 10);
    const data = await callBridge('telemetry', { location, limit });
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 4. Conversational Model Grounded on AQI Dataset
app.post('/api/chat', async (req, res) => {
  try {
    const data = await callBridge('chat_conversational', req.body);
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 5. LLM Spoken Announcement Generation (Trigger Based)
app.post('/api/llm/announcement', async (req, res) => {
  try {
    const data = await callBridge('generate_announcement', req.body);
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 5. LLM Zero-shot Decision Evaluation
app.post('/api/llm/decision', async (req, res) => {
  try {
    const data = await callBridge('generate_decision', req.body);
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 6. Audio Clip Preview / Synthesizer
app.post('/api/clips/preview', async (req, res) => {
  try {
    const data = await callBridge('clip_preview', req.body);
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Fallback to React index.html for client-side routing
app.use((req, res, next) => {
  if (req.method !== 'GET' || req.path.startsWith('/api') || req.path.startsWith('/clips')) {
    return next();
  }
  const indexPath = path.join(CLIENT_DIST, 'index.html');
  res.sendFile(indexPath, (err) => {
    if (err) next();
  });
});

// Start Express Server
app.listen(PORT, () => {
  console.log(`[AirCue Node Server] Running on http://localhost:${PORT}`);
  console.log(`[AirCue Node Server] Python Runtime: ${PYTHON_PATH}`);
});
