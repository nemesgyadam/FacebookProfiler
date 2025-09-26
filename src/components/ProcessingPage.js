import React, { useState } from 'react';
import { CheckCircle, Clock, AlertCircle, Home } from 'lucide-react';
import JsonViewer from './JsonViewer';
import { requiredFilePathsSet } from '../data/requiredFiles';

const ProcessingPage = ({ extractedData, status, sessionId, onStartOver, onContinueToAnalysis }) => {
  const [selectedJsonFile, setSelectedJsonFile] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Filter extracted files to only show required ones
  const filteredFiles = Object.keys(extractedData).filter(fileName => {
    // Check if this file is in our required files list
    const isRequired = requiredFilePathsSet.has(fileName);
    return isRequired && fileName.toLowerCase().includes(searchTerm.toLowerCase());
  });
  const getStatusInfo = () => {
    switch (status) {
      case 'completed':
        return {
          icon: <CheckCircle className="w-8 h-8 text-green-400" />,
          title: 'Processing Complete',
          description: 'Your Facebook data has been successfully processed!',
          color: 'green'
        };
      case 'error':
        return {
          icon: <AlertCircle className="w-8 h-8 text-red-400" />,
          title: 'Processing Error',
          description: 'There was an error processing your files. Please try again.',
          color: 'red'
        };
      default:
        return {
          icon: <Clock className="w-8 h-8 text-gray-400" />,
          title: 'Preparing',
          description: 'Getting ready to process your data...',
          color: 'gray'
        };
    }
  };

  const statusInfo = getStatusInfo();

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        <div className="text-center mb-8 animate-fade-in">
          <h1 className="text-4xl font-bold text-white mb-4">
            Processing Your Data
          </h1>
          <p className="text-lg text-white/90">
            Please wait while we analyze your Facebook data
          </p>
        </div>

        {/* Status Card */}
        <div className="glass rounded-xl p-8 mb-6 animate-slide-up">
          <div className="text-center mb-6">
            <div className="flex justify-center mb-4">
              {statusInfo.icon}
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">
              {statusInfo.title}
            </h2>
            <p className="text-white/80">
              {statusInfo.description}
            </p>
          </div>

          {/* Progress Steps */}
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                status === 'completed' 
                  ? 'bg-green-500' 
                  : 'bg-white/20'
              }`}>
                {status === 'completed' ? (
                  <CheckCircle className="w-4 h-4 text-white" />
                ) : (
                  <div className="w-2 h-2 bg-white/50 rounded-full" />
                )}
              </div>
              <span className={`${
                status === 'completed' 
                  ? 'text-white' 
                  : 'text-white/60'
              }`}>
                Data Processing
              </span>
            </div>

            <div className="flex items-center gap-3">
              <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                status === 'completed' 
                  ? 'bg-green-500' 
                  : 'bg-white/20'
              }`}>
                {status === 'completed' ? (
                  <CheckCircle className="w-4 h-4 text-white" />
                ) : (
                  <div className="w-2 h-2 bg-white/50 rounded-full" />
                )}
              </div>
              <span className={`${
                status === 'completed' 
                  ? 'text-white' 
                  : 'text-white/60'
              }`}>
                Prepare for analysis
              </span>
            </div>
          </div>
        </div>

        {/* File Information */}
        <div className="glass rounded-xl p-6 mb-6">
          <h3 className="text-white font-semibold mb-4">📁 Processing Details</h3>
          <div className="space-y-2 text-white/80 text-sm">
            <div className="flex justify-between">
              <span>Files extracted:</span>
              <span>{Object.keys(extractedData).length}</span>
            </div>
            <div className="flex justify-between">
              <span>Session ID:</span>
              <span className="font-mono text-xs">{sessionId?.slice(0, 8)}...</span>
            </div>
            <div className="flex justify-between">
              <span>Status:</span>
              <span className={`capitalize ${
                status === 'completed' ? 'text-green-400' :
                status === 'error' ? 'text-red-400' :
                'text-yellow-400'
              }`}>
                {status || 'Initializing'}
              </span>
            </div>
          </div>
        </div>

        {/* Extracted JSON Files List */}
        {status === 'completed' && (Object.keys(extractedData).length > 0) && (
          <div className="glass rounded-xl p-6 mb-6">
            <h3 className="text-white font-semibold mb-4">Extracted Files ({filteredFiles.length} of {Object.keys(extractedData).length})</h3>
            <input
              type="text"
              placeholder="Search files..."
              className="w-full p-2 mb-4 rounded-lg bg-white/10 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <div className="grid grid-cols-1 gap-3 max-h-60 overflow-y-auto custom-scrollbar">
              {filteredFiles.map((fileName) => (
                <button
                  key={fileName}
                  onClick={() => setSelectedJsonFile(fileName)}
                  className={`text-left p-2 rounded-lg transition-colors duration-200 ${
                    selectedJsonFile === fileName ? 'bg-blue-600 text-white' : 'bg-white/10 hover:bg-white/20 text-white/80'
                  }`}
                >
                  {fileName}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Selected File Viewer */}
        {status === 'completed' && selectedJsonFile && (
          selectedJsonFile.endsWith('.json') ? (
            <JsonViewer 
              jsonData={extractedData[selectedJsonFile]}
              fileName={selectedJsonFile}
            />
          ) : (
            <div className="glass rounded-xl p-6 mb-6">
              <h3 className="text-white font-semibold mb-4">📄 {selectedJsonFile}</h3>
              <div className="overflow-auto max-h-96">
                <pre className="text-white/70 whitespace-pre-wrap break-all text-sm">{extractedData[selectedJsonFile]}</pre>
              </div>
            </div>
          )
        )}

        {/* Action Buttons */}
        <div className="text-center">
          {status === 'completed' && (
            <div className="space-y-4">
              <button
                onClick={onContinueToAnalysis}
                className="w-full bg-green-500 text-white py-3 rounded-lg font-semibold hover:bg-green-600 transition-colors"
              >
                Continue to Analysis
              </button>
              <button
                onClick={onStartOver}
                className="w-full bg-white/20 text-white py-3 rounded-lg font-semibold hover:bg-white/30 transition-colors flex items-center justify-center gap-2"
              >
                <Home className="w-4 h-4" />
                Start Over
              </button>
            </div>
          )}

          {status === 'error' && (
            <div className="space-y-4">
              <button className="w-full bg-red-500 text-white py-3 rounded-lg font-semibold hover:bg-red-600 transition-colors">
                Try Again
              </button>
              <button
                onClick={onStartOver}
                className="w-full bg-white/20 text-white py-3 rounded-lg font-semibold hover:bg-white/30 transition-colors flex items-center justify-center gap-2"
              >
                <Home className="w-4 h-4" />
                Start Over
              </button>
            </div>
          )}

          {status !== 'completed' && status !== 'error' && (
            <div className="glass rounded-lg p-4">
              <p className="text-white/70 text-sm">
                This may take a few moments. 
                Please don't close this window.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProcessingPage;
