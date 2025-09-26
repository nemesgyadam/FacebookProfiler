import langfuseManager from './langfuseClient';

/**
 * Facebook Profile Analyzer using OpenRouter with Langfuse prompts
 * Analyzes JSON files from Facebook data and generates psychological profile
 */

class ProfileAnalyzer {
  constructor() {
    // Using the deployed Google Cloud Function URL
    this.baseUrl = 'https://openrouter-proxy-456775528821.europe-west1.run.app/';
    this.model = 'google/gemini-2.5-pro';
    this.temperature = 0.7;
    this.prompt = null;
    
    // Constants for chunking large datasets
    this.MAX_CHUNK_SIZE = 3500000; // ~3.5MB per chunk (~1M tokens at 3.5 chars per token)
    this.MAX_FILES_PER_CHUNK = 100; // Max files to include in a single chunk
    
    // Retry configuration
    this.MAX_RETRIES = 3;
    this.RETRY_DELAY = 2000; // 2 seconds between retries
  }

  /**
   * Load the profiler prompt from Langfuse
   * @param {string} promptName - Name of the prompt to load from Langfuse
   */
  async loadPrompt(promptName = 'facebook-profiler') {
    try {
      console.log(`🔄 Loading prompt "${promptName}" from Langfuse...`);
      
      // Try to get prompt from Langfuse
      const langfusePrompt = await langfuseManager.getPrompt(promptName);
      
      if (langfusePrompt && langfusePrompt.prompt) {
        // Extract the actual prompt content
        const promptContent = typeof langfusePrompt.prompt === 'string' 
          ? langfusePrompt.prompt 
          : langfusePrompt.prompt.content || JSON.stringify(langfusePrompt.prompt);
          
        this.prompt = promptContent;
        console.log(`✅ Loaded prompt "${promptName}" from Langfuse (${promptContent.length} characters)`);
        return this.prompt;
      } else {
        console.warn(`⚠️ Prompt "${promptName}" not found in Langfuse, falling back to local file...`);
        
        // Fallback to local file
        const response = await fetch('/profiler_prompt.txt');
        if (!response.ok) {
          throw new Error(`Failed to load fallback prompt: ${response.statusText}`);
        }
        this.prompt = await response.text();
        console.log('✅ Loaded fallback prompt from local file');
        return this.prompt;
      }
    } catch (error) {
      console.error('❌ Error loading prompt:', error);
      throw error;
    }
  }

  /**
   * Process JSON files and extract content
   * @param {Object} jsonFiles - Object containing filename: content pairs
   * @returns {Array} Array of data chunks, each containing formatted data strings
   */
  processJsonFiles(jsonFiles) {
    let totalFiles = 0;
    let totalChars = 0;
    let chunks = [];
    let currentChunk = "";
    let filesInCurrentChunk = 0;

    console.log("Processing files (JSON and HTML)...");

    // Sort files by size (smallest first) to optimize chunking
    const sortedEntries = Object.entries(jsonFiles).sort((a, b) => {
      return (a[1]?.length || 0) - (b[1]?.length || 0);
    });

    for (const [filename, content] of sortedEntries) {
      try {
        let formattedContent;
        
        // Check if it's JSON or HTML based on filename
        if (filename.toLowerCase().endsWith('.json')) {
          // Parse JSON content if it's a string
          const jsonData = typeof content === 'string' ? JSON.parse(content) : content;
          formattedContent = JSON.stringify(jsonData, null, 2);
        } else if (filename.toLowerCase().endsWith('.html')) {
          // For HTML files, use content directly but truncate if too long
          formattedContent = typeof content === 'string' ? content : String(content);
          // Truncate very long HTML files to prevent token overflow
          if (formattedContent.length > 50000) {
            formattedContent = formattedContent.substring(0, 50000) + '\n\n[Content truncated due to length...]';
          }
        } else {
          // For other file types, treat as text
          formattedContent = typeof content === 'string' ? content : String(content);
        }
        
        const fileEntry = `\n\n### FILE: ${filename}\n\n${formattedContent}`;
        
        // Check if adding this file would exceed chunk size
        if ((currentChunk.length + fileEntry.length > this.MAX_CHUNK_SIZE) || 
            (filesInCurrentChunk >= this.MAX_FILES_PER_CHUNK && currentChunk.length > 0)) {
          // Save current chunk and start a new one
          chunks.push(currentChunk);
          currentChunk = fileEntry;
          filesInCurrentChunk = 1;
        } else {
          // Add to current chunk
          currentChunk += fileEntry;
          filesInCurrentChunk++;
        }
        
        totalChars += fileEntry.length;
        totalFiles++;
        
        if (totalFiles % 5 === 0) {
          console.log(`Processed ${totalFiles} files (${totalChars} characters)...`);
        }
      } catch (error) {
        console.error(`Error processing file ${filename}:`, error);
      }
    }

    // Add the last chunk if it's not empty
    if (currentChunk.length > 0) {
      chunks.push(currentChunk);
    }

    console.log(`Processed ${totalFiles} files (JSON/HTML) into ${chunks.length} chunks`);
    console.log(`Total characters: ${totalChars}`);
    console.log(`Estimated tokens: ${Math.floor(totalChars / 4)}`);

    return chunks;
  }

  /**
   * Sleep for a specified number of milliseconds
   * @param {number} ms - Milliseconds to sleep
   * @returns {Promise} Promise that resolves after the specified time
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  /**
   * Send data to OpenRouter for analysis with retry logic
   * @param {string} data - The processed Facebook data
   * @param {number} chunkIndex - The index of the current chunk
   * @param {number} totalChunks - The total number of chunks
   * @returns {Promise<string>} The generated profile
   */
  async generateProfile(data, chunkIndex = 0, totalChunks = 1) {
    if (!this.prompt) {
      await this.loadPrompt();
    }

    // Adjust prompt based on whether this is a multi-chunk request
    let promptContent = this.prompt;
    if (totalChunks > 1) {
      promptContent = `${this.prompt}\n\nNOTE: This is part ${chunkIndex + 1} of ${totalChunks} data chunks. `;
      
      if (chunkIndex === 0) {
        promptContent += "This is the first chunk. Focus on understanding the data structure.";
      } else if (chunkIndex === totalChunks - 1) {
        promptContent += "This is the last chunk. Provide a complete psychological profile based on all data you've analyzed.";
      } else {
        promptContent += "This is a middle chunk. Continue analyzing the data.";
      }
    }

    const requestBody = {
      model: this.model,
      messages: [
        {
          role: 'user',
          content: `${promptContent}\n\n---\n\nFACEBOOK DATA (CHUNK ${chunkIndex + 1}/${totalChunks}):\n${data}`
        }
      ],
      temperature: this.temperature,
      max_tokens: 8192
    };

    // Implement retry logic
    let retries = 0;
    let lastError = null;
    
    while (retries <= this.MAX_RETRIES) {
      try {
        console.log(`Sending request to ${this.model} via Google Cloud Function (chunk ${chunkIndex + 1}/${totalChunks})${retries > 0 ? ` - Retry ${retries}/${this.MAX_RETRIES}` : ''}...`);
        
        const response = await fetch(this.baseUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
          // Try to get error details if possible
          let errorMessage = `Status: ${response.status}`;
          try {
            const errorData = await response.json();
            errorMessage += ` - ${JSON.stringify(errorData)}`;
          } catch (e) {
            // If we can't parse JSON, just use status text
            errorMessage += ` - ${response.statusText}`;
          }
          throw new Error(`OpenRouter API error: ${errorMessage}`);
        }

        const responseData = await response.json();
        
        if (!responseData.choices || responseData.choices.length === 0) {
          throw new Error('No choices returned from OpenRouter API');
        }

        const generatedText = responseData.choices[0].message.content;
        
        console.log(`Chunk ${chunkIndex + 1}/${totalChunks} processed successfully`);
        console.log(`Generated text length: ${generatedText.length} characters`);
        
        return generatedText;

      } catch (error) {
        lastError = error;
        retries++;
        
        if (retries <= this.MAX_RETRIES) {
          // Calculate exponential backoff delay
          const delay = this.RETRY_DELAY * Math.pow(2, retries - 1);
          console.log(`Error processing chunk ${chunkIndex + 1}/${totalChunks}. Retrying in ${delay/1000} seconds... (${retries}/${this.MAX_RETRIES})`);
          console.error(`Error details: ${error.message}`);
          await this.sleep(delay);
        } else {
          console.error(`Failed after ${this.MAX_RETRIES} retries for chunk ${chunkIndex + 1}/${totalChunks}:`, error);
          throw error;
        }
      }
    }
    
    // This should never be reached due to the throw in the else block above
    throw lastError;
  }

  /**
   * Analyze Facebook data and generate psychological profile
   * @param {Object} jsonFiles - Object containing filename: content pairs
   * @returns {Promise<Object>} Analysis results
   */
  async analyzeProfile(jsonFiles) {
    try {
      const startTime = Date.now();
      
      // Process JSON files into chunks
      const dataChunks = this.processJsonFiles(jsonFiles);
      
      console.log(`Data split into ${dataChunks.length} chunks for processing`);
      
      // If we have multiple chunks, process them sequentially and combine results
      let combinedProfile = "";
      let failedChunks = [];
      
      if (dataChunks.length === 0) {
        throw new Error("No valid data chunks to process");
      } else if (dataChunks.length === 1) {
        // Single chunk processing - simpler case
        combinedProfile = await this.generateProfile(dataChunks[0]);
      } else {
        // Multi-chunk processing
        for (let i = 0; i < dataChunks.length; i++) {
          try {
            console.log(`Processing chunk ${i + 1} of ${dataChunks.length}...`);
            
            // Process this chunk
            const chunkProfile = await this.generateProfile(dataChunks[i], i, dataChunks.length);
            
            // For the first chunk, we take everything
            if (i === 0) {
              combinedProfile = chunkProfile;
            } 
            // For the last chunk, we take the final analysis
            else if (i === dataChunks.length - 1) {
              // For simplicity, we'll just use the last chunk's output as the final result
              combinedProfile = chunkProfile;
            }
            // We could store middle chunks for reference but we'll skip them for now
          } catch (chunkError) {
            console.error(`Failed to process chunk ${i + 1}/${dataChunks.length} after all retries:`, chunkError);
            failedChunks.push(i + 1);
            
            // If this is the last chunk and it failed, use the most recent successful chunk
            if (i === dataChunks.length - 1 && combinedProfile) {
              console.log("Last chunk failed, using most recent successful chunk as final result");
            }
            
            // Continue with next chunk instead of failing the entire process
            continue;
          }
        }
      }
      
      const endTime = Date.now();
      const duration = (endTime - startTime) / 1000;
      
      return {
        success: failedChunks.length === 0 || combinedProfile.length > 0,
        profile: combinedProfile,
        stats: {
          filesProcessed: Object.keys(jsonFiles).length,
          chunksProcessed: dataChunks.length,
          chunksSuccessful: dataChunks.length - failedChunks.length,
          chunksFailed: failedChunks,
          duration,
          profileLength: combinedProfile.length,
          wordCount: combinedProfile.split(/\s+/).length
        }
      };
      
    } catch (error) {
      console.error('Profile analysis failed:', error);
      return {
        success: false,
        error: error.message,
        profile: null
      };
    }
  }
}

export default ProfileAnalyzer;
