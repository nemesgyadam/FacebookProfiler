import React, { useState, useCallback, useEffect, useMemo } from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Brain, Download, AlertCircle, CheckCircle, File, Info } from 'lucide-react';
import MarkdownPreview from '@uiw/react-markdown-preview';
import ProfileAnalyzer from '../utils/profileAnalyzer';
import { requiredFilePaths } from '../data/requiredFiles';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

// ... [rest of the component code remains the same until the return statement]

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-2xl w-full text-center">
        {/* ... [previous JSX] ... */}

        {/* Required Files Section - Updated to show only required files */}
        <div className="glass rounded-xl p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-white font-semibold flex items-center gap-2">
              <File className="w-5 h-5" />
              Required Data Files
            </h3>
            <div className="text-white/60 text-sm flex items-center gap-1">
              <Info className="w-4 h-4" />
              {Object.keys(extractedData).length} files available
            </div>
          </div>
          
          <div className="space-y-2">
            {requiredFilePaths.map((requiredPath, index) => {
              const hasFile = Object.keys(extractedData).some(file => file.includes(requiredPath));
              const fileKey = Object.keys(extractedData).find(file => file.includes(requiredPath));
              const fileSize = fileKey ? new Blob([extractedData[fileKey]]).size : 0;
              
              // Format file size helper function
              const formatSize = (bytes) => {
                if (bytes === 0) return '0 B';
                const k = 1024;
                const sizes = ['B', 'KB', 'MB'];
                const i = Math.floor(Math.log(bytes) / Math.log(k));
                return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
              };
              
              return (
                <div 
                  key={index} 
                  className={`p-3 rounded-lg ${hasFile ? 'bg-green-900/20 border border-green-800/50' : 'bg-white/5 border border-white/10'}`}
                >
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                      {hasFile ? (
                        <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                      ) : (
                        <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0" />
                      )}
                      <span className={`text-sm ${hasFile ? 'text-white' : 'text-white/70'}`}>
                        {requiredPath.split('/').pop()}
                      </span>
                    </div>
                    <span className={`text-xs ${hasFile ? 'text-white/60' : 'text-white/40'}`}>
                      {hasFile ? formatSize(fileSize) : 'missing'}
                    </span>
                  </div>
                  {!hasFile && (
                    <p className="text-xs text-amber-300/80 mt-1 ml-6">
                      This file wasn't found in your download. Some insights may be limited.
                    </p>
                  )}
                </div>
              );
            })}
          </div>
          
          <div className="mt-4 text-xs text-white/60">
            <p>ℹ️ Only showing required files. Your data contains {Object.keys(extractedData).length} files in total.</p>
          </div>
        </div>

        {/* ... [rest of the JSX] ... */}
      </div>
    </div>
  );
};

export default AnalysisPage;
