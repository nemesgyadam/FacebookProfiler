# Netlify Function Setup for OpenRouter API

This project uses a Netlify Function to proxy requests to the OpenRouter API, solving CORS issues and keeping your API key secure.

## How It Works

1. The React frontend sends requests to `/.netlify/functions/openrouter-proxy`
2. The Netlify Function forwards these requests to OpenRouter with your API key
3. OpenRouter responses are returned to the frontend

## Setup Instructions

### 1. Environment Variables

Add your OpenRouter API key to Netlify:

- Go to Netlify Dashboard → Site settings → Environment variables
- Add a new variable:
  ```
  OPENROUTER_API_KEY=your-api-key-here
  ```

### 2. Local Development

To test locally with Netlify Dev:

1. Install the Netlify CLI:
   ```
   npm install -g netlify-cli
   ```

2. Create a `.env` file in the project root with your API key:
   ```
   OPENROUTER_API_KEY=your-api-key-here
   ```

3. Run Netlify Dev:
   ```
   netlify dev
   ```

### 3. Deployment

Deploy to Netlify using their standard deployment process:

1. Connect your Git repository
2. Set the build settings as defined in `netlify.toml`
3. Ensure environment variables are set in the Netlify dashboard

## Files

- `netlify/functions/openrouter-proxy.js`: The serverless function that proxies requests
- `netlify.toml`: Configuration for Netlify builds and functions
- `react/src/utils/profileAnalyzer.js`: Updated to use the Netlify function

## Testing

After deployment, your React app will automatically use the Netlify function to communicate with OpenRouter, avoiding CORS issues and keeping your API key secure on the server side.
