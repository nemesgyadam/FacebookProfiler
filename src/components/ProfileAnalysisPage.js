import React, { useState } from 'react';
import { Brain, Clock, FileText, AlertCircle, CheckCircle, Download } from 'lucide-react';
import ProfileAnalyzer from '../utils/profileAnalyzer';

const ProfileAnalysisPage = ({ jsonData, prompts, onBack, onStartOver }) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [selectedPrompt, setSelectedPrompt] = useState('facebook-profiler');

  const analyzer = new ProfileAnalyzer();

  const handleAnalyze = async () => {
    if (!jsonData || Object.keys(jsonData).length === 0) {
      setError('No JSON data available for analysis');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setAnalysisResult(null);

    try {
      console.log(`Starting profile analysis with prompt: ${selectedPrompt}...`);
      
      // Load the selected prompt from Langfuse
      await analyzer.loadPrompt(selectedPrompt);
      
      const result = await analyzer.analyzeProfile(jsonData);
      
      if (result.success) {
        setAnalysisResult(result.profile);
        setStats(result.stats);
        setError(null);
      } else {
        setError(result.error);
        setAnalysisResult(null);
      }
    } catch (err) {
      setError(err.message);
      setAnalysisResult(null);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const downloadProfile = () => {
    if (!analysisResult) return;
    
    const blob = new Blob([analysisResult], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `psychological_profile_${new Date().toISOString().split('T')[0]}.md`;
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
          <div className="flex justify-center mb-4">
            <div className="p-4 bg-white/20 rounded-full backdrop-blur-sm">
              <Brain className="w-12 h-12 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-white mb-4">
            AI Psychological Profile Analysis
          </h1>
          <p className="text-lg text-white/80 max-w-2xl mx-auto">
            Generate comprehensive psychological insights using Gemini 2.5 Pro AI analysis of your Facebook data.
          </p>
        </div>

        {/* Analysis Controls */}
        <div className="glass rounded-xl p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white">Analysis Controls</h2>
            {stats && (
              <div className="text-white/70 text-sm">
                {stats.filesProcessed} files • {stats.duration.toFixed(1)}s
              </div>
            )}
          </div>

          {/* Data Status */}
          <div className="mb-6 p-4 bg-white/10 rounded-lg">
            <div className="flex items-center gap-3 mb-2">
              <FileText className="w-5 h-5 text-blue-300" />
              <span className="font-medium text-white">Data Status</span>
            </div>
            {jsonData && Object.keys(jsonData).length > 0 ? (
              <div className="text-green-300 text-sm">
                ✅ {Object.keys(jsonData).length} JSON files loaded and ready for analysis
              </div>
            ) : (
              <div className="text-orange-300 text-sm">
                ⚠️ No JSON data loaded. Please upload your Facebook data first.
              </div>
            )}
          </div>

          {/* Prompt Selection */}
          <div className="mb-6 p-4 bg-white/10 rounded-lg">
            <div className="flex items-center gap-3 mb-3">
              <Brain className="w-5 h-5 text-green-300" />
              <span className="font-medium text-white">Analysis Prompt</span>
            </div>
            <select
              value={selectedPrompt}
              onChange={(e) => setSelectedPrompt(e.target.value)}
              className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="facebook-profiler">Default Facebook Profiler</option>
              {prompts && prompts.map((prompt) => (
                <option key={prompt.name} value={prompt.name}>
                  {prompt.name} (v{prompt.version})
                </option>
              ))}
            </select>
            <div className="text-white/60 text-xs mt-2">
              {prompts ? `${prompts.length} prompts loaded from Langfuse` : 'Loading prompts...'}
            </div>
          </div>

          {/* API Key Status */}
          <div className="mb-6 p-4 bg-white/10 rounded-lg">
            <div className="flex items-center gap-3 mb-2">
              <Brain className="w-5 h-5 text-purple-300" />
              <span className="font-medium text-white">Gemini API Status</span>
            </div>
            {process.env.REACT_APP_OPENROUTER_API_KEY ? (
              <div className="text-green-300 text-sm">
                ✅ API Key configured
              </div>
            ) : (
              <div className="text-red-300 text-sm">
                ❌ API Key not found. Please set REACT_APP_GEMINI_API_KEY environment variable.
              </div>
            )}
          </div>

          {/* Analyze Button */}
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing || !jsonData || Object.keys(jsonData).length === 0 || !process.env.REACT_APP_GEMINI_API_KEY}
            className="w-full bg-primary-500 text-white py-3 rounded-lg font-semibold hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center gap-2"
          >
            {isAnalyzing ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Analyzing with Gemini 2.5 Pro...
              </>
            ) : (
              <>
                <Brain className="w-5 h-5" />
                Generate Psychological Profile
              </>
            )}
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="glass rounded-xl p-6 mb-8 border border-red-500/30">
            <div className="flex items-center gap-3 mb-3">
              <AlertCircle className="w-6 h-6 text-red-400" />
              <h3 className="text-lg font-semibold text-white">Analysis Error</h3>
            </div>
            <div className="text-red-300 text-sm bg-red-500/10 p-3 rounded-lg">
              {error}
            </div>
          </div>
        )}

        {/* Results Display */}
        {analysisResult && (
          <div className="glass rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-6 h-6 text-green-400" />
                <h3 className="text-lg font-semibold text-white">Psychological Profile Generated</h3>
              </div>
              <button
                onClick={downloadProfile}
                className="flex items-center gap-2 bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                <Download className="w-4 h-4" />
                Download Profile
              </button>
            </div>

            {/* Stats */}
            {stats && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-white/10 p-3 rounded-lg text-center">
                  <div className="text-2xl font-bold text-white">{stats.filesProcessed}</div>
                  <div className="text-white/60 text-sm">Files Analyzed</div>
                </div>
                <div className="bg-white/10 p-3 rounded-lg text-center">
                  <div className="text-2xl font-bold text-white">{stats.duration.toFixed(1)}s</div>
                  <div className="text-white/60 text-sm">Generation Time</div>
                </div>
                <div className="bg-white/10 p-3 rounded-lg text-center">
                  <div className="text-2xl font-bold text-white">{stats.profileLength.toLocaleString()}</div>
                  <div className="text-white/60 text-sm">Characters</div>
                </div>
                <div className="bg-white/10 p-3 rounded-lg text-center">
                  <div className="text-2xl font-bold text-white">{stats.wordCount.toLocaleString()}</div>
                  <div className="text-white/60 text-sm">Words</div>
                </div>
              </div>
            )}

            {/* Profile Content */}
            <div className="bg-white/5 rounded-lg p-6 max-h-96 overflow-y-auto">
              <div className="text-white/90 whitespace-pre-wrap font-mono text-sm leading-relaxed">
                {analysisResult}
              </div>
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="glass rounded-xl p-6 mt-8">
          <h3 className="text-lg font-semibold text-white mb-4">How It Works</h3>
          <div className="space-y-3 text-white/80 text-sm">
            <div className="flex items-start gap-3">
              <div className="bg-primary-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">1</div>
              <div>Your uploaded Facebook JSON files are processed and formatted for analysis</div>
            </div>
            <div className="flex items-start gap-3">
              <div className="bg-primary-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">2</div>
              <div>Data is sent to Google's Gemini 2.5 Pro AI model with specialized psychological analysis prompts</div>
            </div>
            <div className="flex items-start gap-3">
              <div className="bg-primary-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">3</div>
              <div>AI generates comprehensive psychological insights based on Big Five personality model and other psychological frameworks</div>
            </div>
            <div className="flex items-start gap-3">
              <div className="bg-primary-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">4</div>
              <div>Results include personality traits, mental health indicators, behavioral patterns, and personalized recommendations</div>
            </div>
          </div>
          
          <div className="mt-4 p-4 bg-blue-500/20 rounded-lg border border-blue-500/30">
            <div className="flex items-center gap-2 text-blue-200 mb-2">
              <Clock className="w-5 h-5" />
              <span className="font-medium">Setup Required</span>
            </div>
            <p className="text-blue-100 text-sm">
              To use this feature, you need to set up an OpenRouter API key. Add <code className="bg-blue-500/30 px-1 rounded">REACT_APP_OPENROUTER_API_KEY</code> to your environment variables.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileAnalysisPage;
