/**
 * Utility for selecting data points based on prompt configuration
 */

/**
 * Load prompt configuration from prompt_config.json
 */
async function loadPromptConfig() {
  try {
    const response = await fetch('/prompt_config.json');
    if (!response.ok) {
      throw new Error(`Failed to load prompt config: ${response.statusText}`);
    }
    const config = await response.json();
    return config;
  } catch (error) {
    console.error('❌ Error loading prompt config:', error);
    return null;
  }
}

/**
 * Normalize file path for comparison (handle both / and \ separators)
 */
function normalizePath(path) {
  return path.replace(/\\/g, '/').toLowerCase();
}

/**
 * Check if a file path matches a pattern (exact file or folder)
 */
function matchesPattern(filePath, pattern) {
  const normalizedFile = normalizePath(filePath);
  const normalizedPattern = normalizePath(pattern);
  
  // If pattern ends with .json, look for both .json and .html versions
  if (normalizedPattern.endsWith('.json')) {
    const basePattern = normalizedPattern.replace('.json', '');
    const jsonMatch = normalizedFile === normalizedPattern || normalizedFile.endsWith('/' + normalizedPattern);
    const htmlMatch = normalizedFile === basePattern + '.html' || normalizedFile.endsWith('/' + basePattern + '.html');
    return jsonMatch || htmlMatch;
  }
  
  // Otherwise, it's a folder pattern - check if file is inside this folder
  return normalizedFile.startsWith(normalizedPattern + '/') || normalizedFile.includes('/' + normalizedPattern + '/');
}

/**
 * Select data points based on prompt configuration
 * @param {string} promptName - Name of the selected prompt
 * @param {Object} extractedData - All extracted data files
 * @returns {Object} - Selected data files and metadata
 */
export async function selectDataForPrompt(promptName, extractedData) {
  console.log(`🔍 Selecting data for prompt: "${promptName}"`);
  
  // Load prompt configuration
  const promptConfig = await loadPromptConfig();
  
  if (!promptConfig || !promptConfig.prompts) {
    console.warn('⚠️ No prompt config found, using all data points');
    return {
      selectedData: extractedData,
      usedFiles: Object.keys(extractedData),
      configFound: false,
      totalFiles: Object.keys(extractedData).length
    };
  }
  
  // Find the specific prompt configuration
  const promptSettings = promptConfig.prompts.find(p => p.name === promptName);
  
  if (!promptSettings || !promptSettings.data) {
    console.warn(`⚠️ No config found for prompt "${promptName}", using all data points`);
    return {
      selectedData: extractedData,
      usedFiles: Object.keys(extractedData),
      configFound: false,
      totalFiles: Object.keys(extractedData).length
    };
  }
  
  console.log(`✅ Found config for prompt "${promptName}" with ${promptSettings.data.length} patterns`);
  
  // Select files based on the configuration
  const selectedData = {};
  const usedFiles = [];
  const availableFiles = Object.keys(extractedData);
  
  // Process each pattern in the prompt configuration
  for (const pattern of promptSettings.data) {
    console.log(`🔍 Processing pattern: "${pattern}"`);
    
    // Find all files that match this pattern
    const matchingFiles = availableFiles.filter(filePath => matchesPattern(filePath, pattern));
    
    if (matchingFiles.length > 0) {
      console.log(`  ✅ Found ${matchingFiles.length} files matching pattern "${pattern}"`);
      matchingFiles.forEach(file => {
        if (!selectedData[file]) { // Avoid duplicates
          selectedData[file] = extractedData[file];
          usedFiles.push(file);
        }
      });
    } else {
      console.log(`  ⚠️ No files found matching pattern "${pattern}"`);
    }
  }
  
  console.log(`📊 Selected ${usedFiles.length} files out of ${availableFiles.length} total files`);
  console.log('📋 Used files:', usedFiles);
  
  return {
    selectedData,
    usedFiles,
    configFound: true,
    totalFiles: availableFiles.length,
    selectedCount: usedFiles.length,
    patterns: promptSettings.data
  };
}

/**
 * Get all available prompt names from configuration
 */
export async function getAvailablePrompts() {
  const promptConfig = await loadPromptConfig();
  
  if (!promptConfig || !promptConfig.prompts) {
    return [];
  }
  
  return promptConfig.prompts.map(p => p.name);
}
