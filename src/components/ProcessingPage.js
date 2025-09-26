import React, { useState, useEffect } from 'react';
import { CheckCircle, Clock, AlertCircle, Home, Brain, Filter } from 'lucide-react';
import JsonViewer from './JsonViewer';
import { selectDataForPrompt, getAvailablePrompts } from '../utils/promptDataSelector';

const ProcessingPage = ({ extractedData, status, sessionId, onStartOver, onContinueToAnalysis, selectedPrompt = null }) => {
  const [selectedJsonFile, setSelectedJsonFile] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [dataSelection, setDataSelection] = useState(null);
  const [availablePrompts, setAvailablePrompts] = useState([]);
  const [currentPrompt, setCurrentPrompt] = useState(selectedPrompt || 'all');

  // Debug logging
  console.log('🔍 ProcessingPage received extractedData:', extractedData);
  console.log('🔍 ProcessingPage extractedData keys:', Object.keys(extractedData || {}));

  // Load available prompts on component mount
  useEffect(() => {
    const loadPrompts = async () => {
      try {
        const prompts = await getAvailablePrompts();
        setAvailablePrompts(prompts);
        console.log('📋 Available prompts for data selection:', prompts);
      } catch (error) {
        console.error('❌ Failed to load available prompts:', error);
      }
    };
    loadPrompts();
  }, []);

  // Select data based on current prompt
  useEffect(() => {
    const selectData = async () => {
      console.log(`🎯 Selecting data for prompt: "${currentPrompt}"`);
      console.log('🎯 Available extractedData:', extractedData);
      console.log('🎯 ExtractedData keys count:', Object.keys(extractedData || {}).length);
      
      if (currentPrompt === 'all') {
        // Use all data
        const allDataSelection = {
          selectedData: extractedData,
          usedFiles: Object.keys(extractedData || {}),
          configFound: false,
          totalFiles: Object.keys(extractedData || {}).length,
          selectedCount: Object.keys(extractedData || {}).length
        };
        setDataSelection(allDataSelection);
        console.log('📊 Using all data points:', Object.keys(extractedData || {}).length, 'files');
        console.log('📊 All data selection result:', allDataSelection);
      } else {
        // Use prompt-specific data selection
        console.log(`🔍 Calling selectDataForPrompt with prompt: "${currentPrompt}"`);
        const selection = await selectDataForPrompt(currentPrompt, extractedData);
        console.log('📊 Prompt-specific selection result:', selection);
        setDataSelection(selection);
      }
    };

    console.log('🔄 Data selection effect triggered');
    console.log('🔄 Current prompt:', currentPrompt);
    console.log('🔄 ExtractedData exists:', !!extractedData);
    console.log('🔄 ExtractedData keys:', Object.keys(extractedData || {}));

    if (extractedData && Object.keys(extractedData).length > 0) {
      console.log('✅ Proceeding with data selection');
      selectData();
    } else {
      console.log('⚠️ No extractedData available, skipping data selection');
    }
  }, [currentPrompt, extractedData]);

  // Filter files based on current data selection and search term
  const filteredFiles = dataSelection ? 
    dataSelection.usedFiles.filter(fileName => 
      fileName.toLowerCase().includes(searchTerm.toLowerCase())
    ) : [];
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

        {/* Prompt Selection */}
        <div className="glass rounded-xl p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <Brain className="w-5 h-5 text-blue-400" />
            <h3 className="text-white font-semibold">Data Selection by Prompt</h3>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-white/80 text-sm mb-2">Select Prompt Configuration:</label>
              <select
                value={currentPrompt}
                onChange={(e) => setCurrentPrompt(e.target.value)}
                className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Data Points (Default)</option>
                {availablePrompts.map((prompt) => (
                  <option key={prompt} value={prompt}>
                    {prompt} Configuration
                  </option>
                ))}
              </select>
            </div>

            {dataSelection && (
              <div className="bg-white/5 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Filter className="w-4 h-4 text-green-400" />
                  <span className="text-white font-medium">Selection Summary</span>
                </div>
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="space-y-2">
                    <div className="flex justify-between text-white/80">
                      <span>Total Files:</span>
                      <span>{dataSelection.totalFiles}</span>
                    </div>
                    <div className="flex justify-between text-white/80">
                      <span>Selected Files:</span>
                      <span className="text-green-400">{dataSelection.selectedCount}</span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-white/80">
                      <span>Config Found:</span>
                      <span className={dataSelection.configFound ? 'text-green-400' : 'text-yellow-400'}>
                        {dataSelection.configFound ? 'Yes' : 'No'}
                      </span>
                    </div>
                    <div className="flex justify-between text-white/80">
                      <span>Coverage:</span>
                      <span className="text-blue-400">
                        {Math.round((dataSelection.selectedCount / dataSelection.totalFiles) * 100)}%
                      </span>
                    </div>
                  </div>
                </div>

                {dataSelection.patterns && (
                  <div className="mt-3 pt-3 border-t border-white/10">
                    <div className="text-white/60 text-xs">
                      <strong>Patterns:</strong> {dataSelection.patterns.length} configured
                    </div>
                  </div>
                )}
              </div>
            )}
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
              <span>Files for analysis:</span>
              <span className="text-green-400">{dataSelection?.selectedCount || 0}</span>
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

        {/* Selected JSON Files List */}
        {status === 'completed' && dataSelection && (
          <div className="glass rounded-xl p-6 mb-6">
            <h3 className="text-white font-semibold mb-4">
              Selected Files ({filteredFiles.length} of {dataSelection.selectedCount} selected, {dataSelection.totalFiles} total)
            </h3>
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
                onClick={() => {
                  console.log('🚀 Continue to Analysis clicked!');
                  console.log('🚀 Current prompt:', currentPrompt);
                  console.log('🚀 Data selection:', dataSelection);
                  console.log('🚀 Selected data keys:', Object.keys(dataSelection?.selectedData || {}));
                  console.log('🚀 Used files:', dataSelection?.usedFiles);
                  onContinueToAnalysis(dataSelection?.selectedData);
                }}
                className="w-full bg-green-500 text-white py-3 rounded-lg font-semibold hover:bg-green-600 transition-colors"
              >
                Continue to Analysis ({dataSelection?.selectedCount || 0} files)
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
