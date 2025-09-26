import { LangfuseClient } from "@langfuse/client";

/**
 * Langfuse client configuration and prompt management
 */
class LangfuseManager {
  constructor() {
    this.client = null;
    this.prompts = new Map();
    this.initialized = false;
  }

  /**
   * Initialize Langfuse client with environment variables
   */
  initialize() {
    try {
      // Get configuration from environment variables
      const secretKey = process.env.REACT_APP_LANGFUSE_SECRET_KEY || "sk-lf-eb9377c7-f9ca-464c-b9ba-6b2f0e1860e3";
      const publicKey = process.env.REACT_APP_LANGFUSE_PUBLIC_KEY || "pk-lf-1c808f57-b0f9-4756-8ed4-0050ac4feb1d";
      const baseUrl = process.env.REACT_APP_LANGFUSE_BASE_URL || "https://cloud.langfuse.com";

      console.log('Initializing Langfuse client...');
      console.log('Base URL:', baseUrl);
      console.log('Public Key:', publicKey);

      this.client = new LangfuseClient({
        secretKey,
        publicKey,
        baseUrl
      });

      this.initialized = true;
      console.log('✅ Langfuse client initialized successfully');
      return true;
    } catch (error) {
      console.error('❌ Failed to initialize Langfuse client:', error);
      return false;
    }
  }

  /**
   * Load all available prompts from Langfuse using the REST API
   */
  async loadPrompts() {
    if (!this.initialized) {
      console.warn('Langfuse client not initialized. Attempting to initialize...');
      if (!this.initialize()) {
        throw new Error('Failed to initialize Langfuse client');
      }
    }

    try {
      console.log('🔄 Loading all prompts from Langfuse via REST API...');
      
      // Clear existing prompts
      this.prompts.clear();

      // Use direct REST API call since SDK methods are not working
      const baseUrl = process.env.REACT_APP_LANGFUSE_BASE_URL || "https://cloud.langfuse.com";
      const secretKey = process.env.REACT_APP_LANGFUSE_SECRET_KEY || "sk-lf-eb9377c7-f9ca-464c-b9ba-6b2f0e1860e3";
      const publicKey = process.env.REACT_APP_LANGFUSE_PUBLIC_KEY || "pk-lf-1c808f57-b0f9-4756-8ed4-0050ac4feb1d";
      
      // Create Basic Auth header
      const authHeader = 'Basic ' + btoa(publicKey + ':' + secretKey);
      
      console.log('🌐 Making direct REST API call to:', `${baseUrl}/api/public/v2/prompts`);
      
      const response = await fetch(`${baseUrl}/api/public/v2/prompts`, {
        method: 'GET',
        headers: {
          'Authorization': authHeader,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`REST API error: ${response.status} ${response.statusText}`);
      }

      const promptsList = await response.json();
      console.log('Raw prompts REST API response:', promptsList);

      if (promptsList && promptsList.data && Array.isArray(promptsList.data)) {
        // Process each prompt metadata
        for (const promptMeta of promptsList.data) {
          try {
            console.log(`🔍 Loading full prompt data for: ${promptMeta.name}`);
            
            // Get the full prompt data using the prompt.get method
            const fullPrompt = await this.client.prompt.get(promptMeta.name);
            
            if (fullPrompt) {
              this.prompts.set(fullPrompt.name, {
                id: fullPrompt.id || promptMeta.id,
                name: fullPrompt.name || promptMeta.name,
                version: fullPrompt.version || promptMeta.version,
                prompt: fullPrompt.prompt,
                config: fullPrompt.config || {},
                labels: fullPrompt.labels || promptMeta.labels || [],
                tags: fullPrompt.tags || promptMeta.tags || [],
                createdAt: fullPrompt.createdAt || promptMeta.createdAt,
                updatedAt: fullPrompt.updatedAt || promptMeta.updatedAt
              });
              console.log(`✅ Loaded prompt: ${fullPrompt.name} (v${fullPrompt.version})`);
            }
          } catch (promptError) {
            console.warn(`⚠️ Failed to load full data for prompt "${promptMeta.name}":`, promptError);
          }
        }
      } else {
        console.warn('⚠️ No prompts found or unexpected API response format');
      }

      console.log(`✅ Successfully loaded ${this.prompts.size} prompts from Langfuse`);
      this.logAvailablePrompts();
      
      return Array.from(this.prompts.values());
    } catch (error) {
      console.error('❌ Failed to load prompts from Langfuse API:', error);
      
      // Fallback: If API fails, we can't get prompts dynamically
      console.log('🔄 API failed, prompts will need to be loaded individually when requested');
      return [];
    }
  }

  /**
   * Get a specific prompt by name
   */
  async getPrompt(name, options = {}) {
    try {
      console.log(`🔍 Getting prompt: ${name}${options.version ? ` (version: ${options.version})` : ''}${options.label ? ` (label: ${options.label})` : ''}`);
      
      const prompt = await this.client.prompt.get(name, options);
      
      if (prompt) {
        console.log(`✅ Retrieved prompt: ${name}`);
        return {
          id: prompt.id || name,
          name: prompt.name || name,
          version: prompt.version || 1,
          prompt: prompt.prompt,
          config: prompt.config || {},
          labels: prompt.labels || [],
          tags: prompt.tags || []
        };
      } else {
        console.warn(`⚠️ Prompt not found: ${name}`);
        return null;
      }
    } catch (error) {
      console.error(`❌ Failed to get prompt ${name}:`, error);
      throw error;
    }
  }

  /**
   * Log all available prompts to console
   */
  logAvailablePrompts() {
    console.log('\n📋 Available Prompts in Langfuse:');
    console.log('================================');
    
    if (this.prompts.size === 0) {
      console.log('No prompts available');
      return;
    }

    this.prompts.forEach((prompt, name) => {
      console.log(`\n🏷️  Name: ${name}`);
      console.log(`   ID: ${prompt.id}`);
      console.log(`   Version: ${prompt.version}`);
      console.log(`   Labels: ${prompt.labels.join(', ') || 'None'}`);
      console.log(`   Tags: ${prompt.tags.join(', ') || 'None'}`);
      console.log(`   Created: ${new Date(prompt.createdAt).toLocaleDateString()}`);
      console.log(`   Updated: ${new Date(prompt.updatedAt).toLocaleDateString()}`);
      
      // Show first 100 characters of prompt content
      if (prompt.prompt) {
        const content = typeof prompt.prompt === 'string' ? prompt.prompt : JSON.stringify(prompt.prompt);
        const preview = content.length > 100 ? content.substring(0, 100) + '...' : content;
        console.log(`   Preview: ${preview}`);
      }
    });
    
    console.log('\n================================');
  }

  /**
   * Get all loaded prompts
   */
  getAllPrompts() {
    return Array.from(this.prompts.values());
  }

  /**
   * Check if a prompt exists
   */
  hasPrompt(name) {
    return this.prompts.has(name);
  }

  /**
   * Get prompt names
   */
  getPromptNames() {
    return Array.from(this.prompts.keys());
  }
}

// Create singleton instance
const langfuseManager = new LangfuseManager();

export default langfuseManager;
