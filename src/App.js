import React, { useState, useEffect } from 'react';
import LandingPage from './components/LandingPage';
import ProcessingPage from './components/ProcessingPage';
import AnalysisPage from './components/AnalysisPage';
import ProfileAnalysisPage from './components/ProfileAnalysisPage';
import langfuseManager from './utils/langfuseClient';
import './App.css';

function App() {
  const [currentStep, setCurrentStep] = useState('landing');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [processingStatus, setProcessingStatus] = useState('initializing');
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

  // Handle files uploaded from landing page
  const handleFilesUploaded = (extractedData) => {
    setUploadedFiles(extractedData); // Store extracted data
    setProcessingStatus('completed');
    
    // Skip processing page and go directly to analysis
    setCurrentStep('analysis');
  };

  const handleStartOver = () => {
    setCurrentStep('landing');
    setUploadedFiles([]);
    setProcessingStatus('initializing');
  };

  return (
    <div className="App min-h-screen">
      {currentStep === 'landing' && (
        <LandingPage onFilesUploaded={handleFilesUploaded} />
      )}
      
      {currentStep === 'processing' && (
        <ProcessingPage 
          extractedData={uploadedFiles}
          status={processingStatus}
          onStartOver={handleStartOver}
          onContinueToAnalysis={() => setCurrentStep('analysis')}
        />
      )}

      {currentStep === 'analysis' && (
        <AnalysisPage
          extractedData={uploadedFiles}
          onStartOver={handleStartOver}
          onAIAnalysis={() => setCurrentStep('ai-analysis')}
        />
      )}

      {currentStep === 'ai-analysis' && (
        <ProfileAnalysisPage
          jsonData={uploadedFiles}
          prompts={prompts}
          onBack={() => setCurrentStep('analysis')}
          onStartOver={handleStartOver}
        />
      )}
    </div>
  );
}

export default App;
