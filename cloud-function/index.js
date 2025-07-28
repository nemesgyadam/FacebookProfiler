const fetch = require('node-fetch');

/**
 * HTTP Cloud Function for proxying requests to OpenRouter API
 * 
 * @param {Object} req Cloud Function request context.
 * @param {Object} res Cloud Function response context.
 */
exports.openRouterProxy = (req, res) => {
  // Enable CORS
  res.set('Access-Control-Allow-Origin', '*');
  
  // Handle preflight requests (OPTIONS)
  if (req.method === 'OPTIONS') {
    res.set('Access-Control-Allow-Methods', 'POST');
    res.set('Access-Control-Allow-Headers', 'Content-Type');
    res.set('Access-Control-Max-Age', '3600');
    res.status(204).send('');
    return;
  }
  
  // Only allow POST requests
  if (req.method !== 'POST') {
    res.status(405).send('Method Not Allowed');
    return;
  }

  // Get API key from environment variable
  const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;
  
  if (!OPENROUTER_API_KEY) {
    res.status(500).json({ error: "API key not configured" });
    return;
  }

  // Forward the request to OpenRouter
  fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(req.body)
  })
  .then(response => response.json())
  .then(data => {
    res.status(200).json(data);
  })
  .catch(error => {
    console.error("Error:", error);
    res.status(500).json({ error: error.message });
  });
};
