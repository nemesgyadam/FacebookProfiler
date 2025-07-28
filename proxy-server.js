const express = require('express');
const cors = require('cors');
const fetch = require('node-fetch');
const dotenv = require('dotenv');
const app = express();

// Load environment variables from .env file
dotenv.config();

// Enable CORS for all routes
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 3001;

// OpenRouter proxy endpoint
app.post('/api/openrouter', async (req, res) => {
  try {
    const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;
    
    if (!OPENROUTER_API_KEY) {
      return res.status(500).json({ error: "API key not configured" });
    }

    const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(req.body)
    });

    const data = await response.json();
    
    return res.status(response.status).json(data);
  } catch (error) {
    console.error("Proxy server error:", error);
    return res.status(500).json({ error: error.message });
  }
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

app.listen(PORT, () => {
  console.log(`Proxy server running on port ${PORT}`);
});
