import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;
const RAG_API_URL = process.env.RAG_API_URL || 'http://localhost:8000';

app.use(cors());
app.use(express.json());

// Health Check Endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'CampusSaathi AI Node Backend',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
});

// Chat / RAG proxy endpoint
app.post('/api/chat', async (req, res) => {
  const { message } = req.body;
  if (!message) {
    return res.status(400).json({ error: 'Message is required' });
  }

  try {
    const ragResponse = await fetch(`${RAG_API_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: message })
    });

    if (!ragResponse.ok) {
      throw new Error(`RAG API returned status ${ragResponse.status}`);
    }

    const data = await ragResponse.json();
    return res.json(data);
  } catch (err) {
    console.error('RAG Service error:', err.message);
    return res.status(503).json({
      error: 'RAG Service Unavailable',
      answer: 'The CampusSaathi AI knowledge base is currently offline or undergoing maintenance. Please ensure the Python RAG service is running at ' + RAG_API_URL,
      sources: []
    });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 CampusSaathi AI Backend running on port ${PORT}`);
});
