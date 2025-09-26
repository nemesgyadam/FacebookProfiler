import React, { useState } from 'react';
import { Play, CheckCircle, XCircle, Clock, AlertTriangle, ArrowLeft } from 'lucide-react';
import OpenRouterTester from '../utils/openRouterTest';

const OpenRouterTestPage = ({ onBack }) => {
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState(null);
  const [logs, setLogs] = useState([]);

  // Capture console logs
  const captureConsole = () => {
    const originalLog = console.log;
    const originalError = console.error;
    const originalWarn = console.warn;
    
    const logCapture = [];
    
    console.log = (...args) => {
      logCapture.push({ type: 'log', message: args.join(' '), timestamp: new Date().toLocaleTimeString() });
      originalLog(...args);
    };
    
    console.error = (...args) => {
      logCapture.push({ type: 'error', message: args.join(' '), timestamp: new Date().toLocaleTimeString() });
      originalError(...args);
    };
    
    console.warn = (...args) => {
      logCapture.push({ type: 'warn', message: args.join(' '), timestamp: new Date().toLocaleTimeString() });
      originalWarn(...args);
    };
    
    return () => {
      console.log = originalLog;
      console.error = originalError;
      console.warn = originalWarn;
      return logCapture;
    };
  };

  const runTests = async () => {
    setIsRunning(true);
    setResults(null);
    setLogs([]);
    
    const restoreConsole = captureConsole();
    
    try {
      const tester = new OpenRouterTester();
      const testResults = await tester.runAllTests();
      setResults(testResults);
    } catch (error) {
      console.error('Test execution failed:', error);
    } finally {
      const capturedLogs = restoreConsole();
      setLogs(capturedLogs);
      setIsRunning(false);
    }
  };

  const getStatusIcon = (status) => {
    if (status === true) return <CheckCircle className="w-5 h-5 text-green-400" />;
    if (status === false) return <XCircle className="w-5 h-5 text-red-400" />;
    return <Clock className="w-5 h-5 text-gray-400" />;
  };

  const getLogIcon = (type) => {
    switch (type) {
      case 'error': return <XCircle className="w-4 h-4 text-red-400" />;
      case 'warn': return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
      default: return <CheckCircle className="w-4 h-4 text-blue-400" />;
    }
  };

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          {onBack && (
            <button
              onClick={onBack}
              className="absolute top-4 left-4 text-white/60 hover:text-white transition-colors p-2 rounded-lg hover:bg-white/10"
              title="Back to Landing Page"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          )}
          
          <h1 className="text-4xl font-bold text-white mb-4">
            OpenRouter Proxy Test
          </h1>
          <p className="text-lg text-white/80">
            Test your Google Cloud Function proxy to ensure LLM predictions work correctly
          </p>
        </div>

        {/* Test Controls */}
        <div className="glass rounded-xl p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white">Test Controls</h2>
            <div className="text-white/60 text-sm">
              Endpoint: https://openrouter-proxy-456775528821.europe-west1.run.app/
            </div>
          </div>
          
          <button
            onClick={runTests}
            disabled={isRunning}
            className="w-full bg-blue-500 text-white py-3 rounded-lg font-semibold hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center gap-2"
          >
            {isRunning ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Running Tests...
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                Run All Tests
              </>
            )}
          </button>
        </div>

        {/* Test Results */}
        {results && (
          <div className="glass rounded-xl p-6 mb-6">
            <h2 className="text-xl font-semibold text-white mb-4">Test Results</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div className="bg-white/5 rounded-lg p-4">
                <div className="flex items-center gap-3 mb-2">
                  {getStatusIcon(results.connectivity)}
                  <span className="font-medium text-white">Connectivity Test</span>
                </div>
                <p className="text-white/70 text-sm">
                  Tests if the proxy endpoint is reachable
                </p>
              </div>

              <div className="bg-white/5 rounded-lg p-4">
                <div className="flex items-center gap-3 mb-2">
                  {getStatusIcon(results.simplePrompt)}
                  <span className="font-medium text-white">Simple Prompt Test</span>
                </div>
                <p className="text-white/70 text-sm">
                  Tests basic LLM response generation
                </p>
              </div>

              <div className="bg-white/5 rounded-lg p-4">
                <div className="flex items-center gap-3 mb-2">
                  {getStatusIcon(results.facebookData)}
                  <span className="font-medium text-white">Facebook Data Test</span>
                </div>
                <p className="text-white/70 text-sm">
                  Tests analysis with mock Facebook data
                </p>
              </div>

              <div className="bg-white/5 rounded-lg p-4">
                <div className="flex items-center gap-3 mb-2">
                  {getStatusIcon(results.errorHandling)}
                  <span className="font-medium text-white">Error Handling Test</span>
                </div>
                <p className="text-white/70 text-sm">
                  Tests proper error response handling
                </p>
              </div>
            </div>

            {/* Overall Status */}
            <div className="bg-white/10 rounded-lg p-4">
              <div className="flex items-center gap-3">
                {Object.values(results).every(Boolean) ? (
                  <>
                    <CheckCircle className="w-6 h-6 text-green-400" />
                    <div>
                      <div className="font-semibold text-green-400">All Tests Passed!</div>
                      <div className="text-white/70 text-sm">OpenRouter proxy is working correctly</div>
                    </div>
                  </>
                ) : (
                  <>
                    <XCircle className="w-6 h-6 text-red-400" />
                    <div>
                      <div className="font-semibold text-red-400">Some Tests Failed</div>
                      <div className="text-white/70 text-sm">Check the logs below for details</div>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Logs */}
        {logs.length > 0 && (
          <div className="glass rounded-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Test Logs</h2>
            
            <div className="bg-black/50 rounded-lg p-4 max-h-96 overflow-y-auto">
              {logs.map((log, index) => (
                <div key={index} className="flex items-start gap-3 mb-2 text-sm">
                  <span className="text-white/40 text-xs mt-1 min-w-[60px]">
                    {log.timestamp}
                  </span>
                  {getLogIcon(log.type)}
                  <span className={`flex-1 ${
                    log.type === 'error' ? 'text-red-300' :
                    log.type === 'warn' ? 'text-yellow-300' :
                    'text-white/80'
                  }`}>
                    {log.message}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OpenRouterTestPage;
