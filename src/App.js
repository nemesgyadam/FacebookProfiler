import React, { useState, useEffect } from 'react';
import LandingPage from './components/LandingPage';
import AnalysisPage from './components/AnalysisPage';
import ProfileAnalysisPage from './components/ProfileAnalysisPage';
import OpenRouterTestPage from './components/OpenRouterTestPage';
import langfuseManager from './utils/langfuseClient';
import './App.css';

function App() {
  const [currentStep, setCurrentStep] = useState('landing');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [selectedData, setSelectedData] = useState({});
  const [prompts, setPrompts] = useState([]);

  // Initialize Langfuse and load prompts on app startup
  useEffect(() => {
    const initializeLangfuse = async () => {
      try {
        console.log('🚀 Initializing Facebook Profile Analyzer with Langfuse...');
        
        // Initialize Langfuse client
        const initialized = langfuseManager.initialize();
        if (!initialized) {
          console.error('Failed to initialize Langfuse client');
          return;
        }

        // Load all prompts from Langfuse
        const loadedPrompts = await langfuseManager.loadPrompts();
        setPrompts(loadedPrompts);

        console.log(`✅ App initialized with ${loadedPrompts.length} prompts from Langfuse`);
        
        // Log available prompts for debugging
        console.log('\n🔍 Prompt Summary:');
        loadedPrompts.forEach((prompt, index) => {
          console.log(`${index + 1}. ${prompt.name} (v${prompt.version})`);
        });

      } catch (error) {
        console.error('❌ Failed to initialize Langfuse:', error);
      }
    };
    
    initializeLangfuse();
  }, []);

  // Handle files uploaded from landing page - go directly to AI analysis
  const handleFilesUploaded = (extractedData) => {
    console.log('📁 Files uploaded to App.js:', Object.keys(extractedData).length, 'files');
    setUploadedFiles(extractedData);
    setSelectedData(extractedData);
    setCurrentStep('ai-analysis');
  };

  // Handle start over
  const handleStartOver = () => {
    setUploadedFiles({});
    setSelectedData({});
    setCurrentStep('landing');
  };

  return (
    <div className="App min-h-screen">
      {currentStep === 'test' && (
        <OpenRouterTestPage onBack={() => setCurrentStep('landing')} />
      )}
      
      {currentStep === 'landing' && (
        <LandingPage 
          onFilesUploaded={handleFilesUploaded} 
          onTestClick={() => setCurrentStep('test')}
        />
      )}
      
      {currentStep === 'analysis' && (
        <AnalysisPage
          extractedData={Object.keys(selectedData).length > 0 ? selectedData : uploadedFiles}
          onStartOver={handleStartOver}
          onAIAnalysis={() => setCurrentStep('ai-analysis')}
        />
      )}

      {currentStep === 'ai-analysis' && (
        <ProfileAnalysisPage
          jsonData={Object.keys(selectedData).length > 0 ? selectedData : uploadedFiles}
          prompts={prompts}
          onBack={() => setCurrentStep('analysis')}
          onStartOver={handleStartOver}
        />
      )}
    </div>
  );
}

export default App;
