import React, { useState } from 'react';
import LandingPage from './components/LandingPage';
import ProcessingPage from './components/ProcessingPage';
import AnalysisPage from './components/AnalysisPage';
import ProfileAnalysisPage from './components/ProfileAnalysisPage';
import './App.css';

function App() {
  const [currentStep, setCurrentStep] = useState('landing');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [processingStatus, setProcessingStatus] = useState('initializing');

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
          onBack={() => setCurrentStep('analysis')}
          onStartOver={handleStartOver}
        />
      )}
    </div>
  );
}

export default App;
