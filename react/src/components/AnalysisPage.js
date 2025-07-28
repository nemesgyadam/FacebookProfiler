import React, { useState, useCallback, useEffect, useMemo } from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Brain, Download, AlertCircle, CheckCircle } from 'lucide-react';
import MarkdownPreview from '@uiw/react-markdown-preview';
import ProfileAnalyzer from '../utils/profileAnalyzer';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);


const AnalysisPage = ({ sessionId, extractedData, onStartOver }) => {
  const [isAnalyzing, setIsAnalyzing] = useState(true); // Start as analyzing
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);

  // Create analyzer instance with useMemo to prevent recreation on each render
  const analyzer = useMemo(() => new ProfileAnalyzer(), []);
  
  // Define handleAIAnalysis with useCallback to use it in useEffect
  const handleAIAnalysis = useCallback(async () => {
    if (!extractedData || Object.keys(extractedData).length === 0) {
      setError('No data available for analysis');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setAnalysisResult(null);

    try {
      console.log('Starting direct Gemini analysis...');
      // Skip intermediate steps and process directly
      const result = await analyzer.analyzeProfile(extractedData);
      
      if (result.success) {
        // Directly set the result and show the analysis
        setAnalysisResult(result.profile);
        setStats(result.stats);
        setError(null);
        
        // Scroll to the analysis results
        setTimeout(() => {
          document.querySelector('.analysis-results')?.scrollIntoView({ behavior: 'smooth' });
        }, 100);
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
  }, [extractedData, analyzer]);
  
  // Auto-start analysis when component loads
  useEffect(() => {
    if (extractedData && Object.keys(extractedData).length > 0) {
      handleAIAnalysis();
    }
  }, [extractedData, handleAIAnalysis]); // Include all dependencies



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
  const adPreferencesData = extractedData['data/ads_information/ad_preferences.json'];
  const advertisersInteractedData = extractedData['data/ads_information/advertisers_who_interacted_with_you.json'];
  const adInterestsData = extractedData['data/ads_information/ad_interests.json'];
  let parsedAdPreferences = null;
  if (adPreferencesData) {
    try {
      parsedAdPreferences = JSON.parse(adPreferencesData);
    } catch (error) {
      console.error('Error parsing ad_preferences.json:', error);
    }
  }

  // This preserves the structure for future use if needed
  if (advertisersInteractedData) {
    try {
      JSON.parse(advertisersInteractedData); // Parse to validate but don't store
    } catch (error) {
      console.error('Error parsing advertisers_you_interacted_with.json:', error);
    }
  }

  // Similarly for ad interests
  if (adInterestsData) {
    try {
      JSON.parse(adInterestsData); // Parse to validate but don't store
    } catch (error) {
      console.error('Error parsing ad_interests.json:', error);
    }
  }

  // Statistics are calculated but used in the UI via direct references to the parsed data

  const adTopicsData = parsedAdPreferences?.preferences_v2_ad_topics || [];
  const topicNames = adTopicsData.map(topic => topic.name);
  const topicCounts = topicNames.reduce((acc, topic) => {
    acc[topic] = (acc[topic] || 0) + 1;
    return acc;
  }, {});

  const adTopicsChartData = {
    labels: Object.keys(topicCounts),
    datasets: [
      {
        label: 'Number of Occurrences',
        data: Object.values(topicCounts),
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
        labels: { color: 'white' },
      },
      title: {
        display: true,
        text: 'Frequency of Ad Topics',
        color: 'white',
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== null) {
              label += context.parsed.y;
            }
            return label;
          }
        }
      }
    },
    scales: {
      x: {
        ticks: { color: 'white' },
        grid: { color: 'rgba(255, 255, 255, 0.1)' }
      },
      y: {
        ticks: { color: 'white' },
        grid: { color: 'rgba(255, 255, 255, 0.1)' }
      },
    },
  };
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-2xl w-full text-center">
        <h1 className="text-4xl font-bold text-white mb-4">Who are you?</h1>
        <p className="text-lg text-white/90 mb-8">
          Here's a summary of your Facebook data.
        </p>



        {parsedAdPreferences?.preferences_v2_ad_topics?.length > 0 && (
          <div className="glass rounded-xl p-6 mb-6 text-left">
            <h3 className="text-white font-semibold mb-4">🎯 Your Ad Topics</h3>
            <div className="space-y-2 text-white/80 text-sm">
              {parsedAdPreferences.preferences_v2_ad_topics.map((topic, index) => (
                <div key={index} className="flex justify-between items-center">
                  <span>{topic.name}</span>
                </div>
              ))}
            </div>
          </div>
        )}
        {parsedAdPreferences?.preferences_v2_ad_topics?.length > 0 && (
          <div className="glass rounded-xl p-6 mb-6 text-left">
            <h3 className="text-white font-semibold mb-4">📊 Ad Topics Distribution</h3>
            <div className="space-y-2 text-white/80 text-sm">
              <Bar data={adTopicsChartData} options={chartOptions} />
            </div>
          </div>
        )}

        {/* JSON Files Section */}
        <div className="glass rounded-xl p-6 mb-6">
          <h3 className="text-white font-semibold mb-4">📁 Extracted JSON Files</h3>
          <p className="text-white/70 text-sm mb-4">
            {Object.keys(extractedData).length} JSON files ready for analysis:
          </p>
          <div className="max-h-40 overflow-y-auto space-y-1">
            {Object.keys(extractedData).map((filename, index) => {
              const content = extractedData[filename];
              const size = new Blob([content]).size;
              const formatSize = (bytes) => {
                if (bytes === 0) return '0 B';
                const k = 1024;
                const sizes = ['B', 'KB', 'MB'];
                const i = Math.floor(Math.log(bytes) / Math.log(k));
                return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
              };
              
              return (
                <div key={index} className="flex justify-between items-center bg-white/5 p-2 rounded text-sm">
                  <span className="text-white/90 truncate flex-1">{filename}</span>
                  <span className="text-white/60 text-xs ml-2">{formatSize(size)}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* AI Analysis Section */}
        <div className="glass rounded-xl p-6 mb-6">
          <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
            <Brain className="w-5 h-5" />
            AI Psychological Analysis
          </h3>
          {/* Loading Indicator - Replaced button with status indicator */}
          {isAnalyzing && (
            <div className="flex items-center justify-center gap-2 text-white/80 py-3 mb-4">
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Analyzing your data with AI...</span>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="mb-4 p-3 bg-red-500/20 rounded-lg border border-red-500/30">
              <div className="flex items-center gap-2 text-red-300 text-sm">
                <AlertCircle className="w-4 h-4" />
                {error}
              </div>
            </div>
          )}

          {/* Results Display */}
          {analysisResult && (
            <div className="space-y-4 analysis-results">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-green-300">
                  <CheckCircle className="w-5 h-5" />
                  <span className="font-medium">Analysis Complete</span>
                </div>
                <button
                  onClick={downloadProfile}
                  className="flex items-center gap-2 bg-primary-500 hover:bg-primary-600 text-white px-3 py-1 rounded-lg text-sm transition-colors"
                >
                  <Download className="w-4 h-4" />
                  Download
                </button>
              </div>

              {/* Stats */}
              {stats && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-4">
                  <div className="bg-white/10 p-2 rounded text-center">
                    <div className="text-lg font-bold text-white">{stats.filesProcessed}</div>
                    <div className="text-white/60 text-xs">Files</div>
                  </div>
                  <div className="bg-white/10 p-2 rounded text-center">
                    <div className="text-lg font-bold text-white">{stats.duration.toFixed(1)}s</div>
                    <div className="text-white/60 text-xs">Time</div>
                  </div>
                  <div className="bg-white/10 p-2 rounded text-center">
                    <div className="text-lg font-bold text-white">{Math.floor(stats.profileLength / 1000)}k</div>
                    <div className="text-white/60 text-xs">Chars</div>
                  </div>
                  <div className="bg-white/10 p-2 rounded text-center">
                    <div className="text-lg font-bold text-white">{stats.wordCount.toLocaleString()}</div>
                    <div className="text-white/60 text-xs">Words</div>
                  </div>
                </div>
              )}

              {/* Analysis Display */}
              <div className="w-full max-w-[1800px] mx-auto">
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                  {/* Summary Box */}
                  <div className="bg-white/5 rounded-lg p-6 border border-white/10 hover:border-white/20 transition-colors flex flex-col h-[70vh]">
                    <h3 className="text-white font-semibold mb-4 flex items-center gap-2 text-lg">
                      <CheckCircle className="w-5 h-5 text-green-400" />
                      Summary
                    </h3>
                    <div className="flex-1 overflow-y-auto custom-scrollbar pr-2">
                      <MarkdownPreview
                        source={analysisResult.split('\n').slice(0, 20).join('\n') + '\n\n*View complete analysis in the right panel*'}
                        style={{ 
                          backgroundColor: 'transparent', 
                          color: '#f1f5f9',
                          fontSize: '1rem',
                          lineHeight: '1.7',
                          maxWidth: '100%',
                          padding: '0.5rem 0'
                        }}
                        data-color-mode="dark"
                      />
                    </div>
                  </div>

                  {/* Complete Analysis Box */}
                  <div className="bg-white/5 rounded-lg p-6 border border-white/10 hover:border-white/20 transition-colors flex flex-col h-[70vh]">
                    <h3 className="text-white font-semibold mb-4 flex items-center gap-2 text-lg">
                      <Brain className="w-5 h-5 text-blue-400" />
                      Complete Analysis
                    </h3>
                    <div className="flex-1 overflow-y-auto custom-scrollbar pr-2">
                      <MarkdownPreview
                        source={analysisResult}
                        style={{ 
                          backgroundColor: 'transparent', 
                          color: '#f1f5f9',
                          fontSize: '1rem',
                          lineHeight: '1.7',
                          maxWidth: '100%',
                          padding: '0.5rem 0'
                        }}
                        data-color-mode="dark"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <button
          onClick={onStartOver}
          className="w-full bg-white/20 text-white py-3 rounded-lg font-semibold hover:bg-white/30 transition-colors mb-6"
        >
          Start Over
        </button>
        
        {/* Footer */}
        <footer className="mt-12 pt-4 border-t border-white/10">
          <div className="text-center text-sm text-white/60">
            <p>Created by <a 
              href="https://adamnemes.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300 transition-colors font-medium"
            >
              Nemes
            </a></p>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default AnalysisPage;
