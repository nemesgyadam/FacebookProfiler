import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { ArrowLeft, Brain, Clock, AlertCircle, Download, CheckCircle } from 'lucide-react';
import ProfileAnalyzer from '../utils/profileAnalyzer';
import { selectDataForPrompt } from '../utils/promptDataSelector';

// Function to format analysis text from markdown-like format to HTML
const formatAnalysisText = (text) => {
  if (!text) return '';
  
  return text
    // Convert markdown headers to HTML
    .replace(/^### (.*$)/gim, '<h3 style="font-size: 1.1em; font-weight: 600; margin: 1.5em 0 0.5em 0; color: #374151;">$1</h3>')
    .replace(/^## (.*$)/gim, '<h2 style="font-size: 1.25em; font-weight: 700; margin: 2em 0 1em 0; color: #1f2937;">$1</h2>')
    .replace(/^# (.*$)/gim, '<h1 style="font-size: 1.5em; font-weight: 800; margin: 2em 0 1em 0; color: #111827;">$1</h1>')
    
    // Convert bold text
    .replace(/\*\*(.*?)\*\*/g, '<strong style="font-weight: 600; color: #1f2937;">$1</strong>')
    
    // Convert bullet points
    .replace(/^- (.*$)/gim, '<div style="margin: 0.5em 0; padding-left: 1em;">• $1</div>')
    
    // Convert numbered lists
    .replace(/^\d+\. (.*$)/gim, '<div style="margin: 0.5em 0; padding-left: 1em;">$1</div>')
    
    // Convert line breaks to proper spacing
    .replace(/\n\n/g, '<div style="margin: 1em 0;"></div>')
    .replace(/\n/g, '<br>')
    
    // Convert sections with === or --- separators
    .replace(/^={3,}$/gim, '<hr style="margin: 2em 0; border: none; border-top: 2px solid #e5e7eb;">')
    .replace(/^-{3,}$/gim, '<hr style="margin: 1.5em 0; border: none; border-top: 1px solid #e5e7eb;">');
};

const ProfileAnalysisPage = ({ jsonData, prompts, onBack, onStartOver }) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState([]);
  const [error, setError] = useState(null);
  const [currentPrompt, setCurrentPrompt] = useState('');
  const [progress, setProgress] = useState(0);
  const [completedPrompts, setCompletedPrompts] = useState(0);

  const analyzer = useMemo(() => new ProfileAnalyzer(), []);

  const runAllPrompts = useCallback(async () => {
    if (!jsonData || Object.keys(jsonData).length === 0) {
      setError('No data available for analysis');
      return;
    }

    if (!prompts || prompts.length === 0) {
      setError('No prompts available');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setAnalysisResults([]);
    setProgress(0);
    setCompletedPrompts(0);

    const results = [];

    try {
      for (let i = 0; i < prompts.length; i++) {
        const prompt = prompts[i];
        setCurrentPrompt(prompt.name);
        
        console.log(`🔄 Running prompt ${i + 1}/${prompts.length}: ${prompt.name}`);
        
        // Select data based on prompt configuration
        const selectionResult = await selectDataForPrompt(prompt.name, jsonData);
        const selectedData = selectionResult.selectedData || selectionResult;
        console.log(`📊 Selected ${Object.keys(selectedData).length} files for prompt: ${prompt.name}`);
        
        // Load the prompt from Langfuse
        await analyzer.loadPrompt(prompt.name);
        
        // Run analysis
        const result = await analyzer.analyzeProfile(selectedData);
        
        if (result.success) {
          results.push({
            promptName: prompt.name,
            profile: result.profile,
            stats: result.stats,
            dataCount: Object.keys(selectedData).length
          });
          console.log(`✅ Completed prompt: ${prompt.name}`);
        } else {
          console.error(`❌ Failed prompt: ${prompt.name}`, result.error);
          results.push({
            promptName: prompt.name,
            error: result.error,
            dataCount: Object.keys(selectedData).length
          });
        }
        
        setCompletedPrompts(i + 1);
        setProgress(((i + 1) / prompts.length) * 100);
      }
      
      setAnalysisResults(results);
      console.log(`🎉 Completed all ${prompts.length} prompts!`);
      
    } catch (err) {
      setError(err.message);
      console.error('❌ Error running prompts:', err);
    } finally {
      setIsAnalyzing(false);
      setCurrentPrompt('');
    }
  }, [jsonData, prompts, analyzer]);

  // Auto-start analysis when component mounts
  useEffect(() => {
    if (prompts && prompts.length > 0 && jsonData && Object.keys(jsonData).length > 0) {
      runAllPrompts();
    }
  }, [prompts, jsonData, runAllPrompts]);

  const downloadAllProfiles = () => {
    if (!analysisResults || analysisResults.length === 0) return;
    
    const combinedProfile = analysisResults
      .filter(result => result.profile)
      .map(result => `# ${result.promptName} Analysis\n\n${result.profile}\n\n---\n`)
      .join('\n');
    
    const blob = new Blob([combinedProfile], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `facebook_analysis_${new Date().toISOString().split('T')[0]}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-6xl w-full mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          {onBack && (
            <button
              onClick={onBack}
              className="absolute top-4 left-4 text-white/60 hover:text-white transition-colors p-2 rounded-lg hover:bg-white/10"
              title="Back"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          )}
          
          <div className="flex justify-center mb-4">
            <div className="p-4 bg-white/20 rounded-full backdrop-blur-sm">
              <Brain className="w-12 h-12 text-white" />
            </div>
          </div>
          {isAnalyzing ? (
            <>
              <h1 className="text-4xl font-bold text-white mb-4">
                AI Analysis in Progress
              </h1>
              <p className="text-lg text-white/80 max-w-2xl mx-auto">
                Running all prompts automatically and generating comprehensive psychological insights.
              </p>
            </>
          ) : (
            <>
              <h1 className="text-4xl font-bold text-white mb-4">
                Analysis Complete
              </h1>
              <p className="text-lg text-white/80 max-w-2xl mx-auto">
                Your psychological profile has been generated based on your Facebook data.
              </p>
            </>
          )}
        </div>

        {/* Progress Section */}
        {isAnalyzing && (
          <div className="glass rounded-xl p-6 mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-white">Analysis Progress</h2>
              <div className="text-white/70 text-sm">
                {completedPrompts}/{prompts?.length || 0} prompts completed
              </div>
            </div>

            {/* Progress Bar */}
            <div className="mb-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-white/80 text-sm">Overall Progress</span>
                <span className="text-white/80 text-sm">{Math.round(progress)}%</span>
              </div>
              <div className="w-full bg-white/20 rounded-full h-3">
                <div 
                  className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>

            {/* Current Prompt */}
            {currentPrompt && (
              <div className="flex items-center gap-3 p-4 bg-white/10 rounded-lg">
                <Clock className="w-5 h-5 text-blue-300 animate-spin" />
                <span className="text-white">Running: <strong>{currentPrompt}</strong></span>
              </div>
            )}
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="glass rounded-xl p-6 mb-8 border border-red-500/30">
            <div className="flex items-center gap-3 mb-4">
              <AlertCircle className="w-6 h-6 text-red-400" />
              <h2 className="text-xl font-semibold text-red-400">Analysis Error</h2>
            </div>
            <p className="text-red-300 mb-4">{error}</p>
            <button
              onClick={runAllPrompts}
              className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors"
            >
              Retry Analysis
            </button>
          </div>
        )}

        {/* Results Display */}
        {!isAnalyzing && analysisResults.length > 0 && (
          <>
            {/* Results Header */}
            <div className="glass rounded-xl p-6 mb-8">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-white">Analysis Complete</h2>
                <button
                  onClick={downloadAllProfiles}
                  className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  Download All
                </button>
              </div>
              
              <div className="flex items-center gap-3 p-4 bg-green-500/20 rounded-lg border border-green-500/30">
                <CheckCircle className="w-6 h-6 text-green-400" />
                <span className="text-green-300">
                  Successfully completed {analysisResults.filter(r => r.profile).length} out of {analysisResults.length} analyses
                </span>
              </div>
            </div>

            {/* Individual Results */}
            {analysisResults.map((result, index) => (
              <div key={index} className="glass rounded-xl p-6 mb-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold text-white">{result.promptName} Analysis</h3>
                  <div className="text-white/60 text-sm">
                    {result.dataCount} files processed
                  </div>
                </div>
                
                {result.error ? (
                  <div className="p-4 bg-red-500/20 rounded-lg border border-red-500/30">
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                      <div className="flex justify-between items-start mb-4">
                        <h3 className="text-lg font-semibold text-gray-900">{result.promptName} Analysis</h3>
                        <span className="text-sm text-gray-500">{result.dataCount} files processed</span>
                      </div>
                      <div className="prose prose-gray max-w-none">
                        <div 
                          className="formatted-analysis text-sm text-gray-700 leading-relaxed"
                          dangerouslySetInnerHTML={{
                            __html: formatAnalysisText(result.profile)
                          }}
                        />
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="text-lg font-semibold text-gray-900">{result.promptName} Analysis</h3>
                      <span className="text-sm text-gray-500">{result.dataCount} files processed</span>
                    </div>
                    <div className="prose prose-gray max-w-none">
                      <div 
                        className="formatted-analysis text-sm text-gray-700 leading-relaxed"
                        style={{
                          lineHeight: '1.6',
                          fontFamily: 'system-ui, -apple-system, sans-serif'
                        }}
                        dangerouslySetInnerHTML={{
                          __html: formatAnalysisText(result.profile)
                        }}
                      />
                    </div>
                  </div>
                )}
              </div>
            ))}
          </>
        )}
        <div className="flex justify-between items-center mt-8">
          <button
            onClick={onStartOver}
            className="text-white/60 hover:text-white transition-colors"
          >
            ← Start Over
          </button>
          
          {!isAnalyzing && analysisResults.length === 0 && !error && (
            <div className="text-white/60 text-center flex-1">
              <Clock className="w-6 h-6 mx-auto mb-2 animate-pulse" />
              <p>Initializing analysis...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfileAnalysisPage;
