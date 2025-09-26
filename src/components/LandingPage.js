import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Brain, Download, Upload, File, X, CheckCircle, AlertCircle } from 'lucide-react';
import { ZipReader, BlobReader, TextWriter } from '@zip.js/zip.js';

const LandingPage = ({ onFilesUploaded }) => {
  const [files, setFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [showDownloadInstructions, setShowDownloadInstructions] = useState(false);

  
  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    // Filter for zip files only
    const zipFiles = acceptedFiles.filter(file => 
      file.type === 'application/zip' || 
      file.type === 'application/x-zip-compressed' ||
      file.name.toLowerCase().endsWith('.zip')
    );

    if (zipFiles.length > 0) {
      setFiles(prev => [...prev, ...zipFiles.map(file => ({
        file,
        id: Math.random().toString(36).substr(2, 9),
        status: 'ready',
        size: file.size
      }))]);
    }

    // Show error for rejected files
    if (rejectedFiles.length > 0 || zipFiles.length !== acceptedFiles.length) {
      // Handle rejected files (non-zip files)
      console.warn('Some files were rejected. Only ZIP files are accepted.');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/zip': ['.zip'],
      'application/x-zip-compressed': ['.zip']
    },
    multiple: true
  });

  const removeFile = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
    if (files.length <= 1) {
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    
    setIsUploading(true);
    let allFilesExtractedData = {};

    try {
      for (const fileObj of files) {
        setFiles(prev => prev.map(f => f.id === fileObj.id ? { ...f, status: 'unzipping' } : f));
        const reader = new ZipReader(new BlobReader(fileObj.file));
        const entries = await reader.getEntries();

        for (const entry of entries) {
          if (!entry.directory && entry.filename.toLowerCase().endsWith('.json')) {
            const writer = new TextWriter();
            const content = await entry.getData(writer);
            allFilesExtractedData[entry.filename] = content;
          }
        }
        await reader.close();
        setFiles(prev => prev.map(f => f.id === fileObj.id ? { ...f, status: 'unzipped' } : f));
      }
      console.log('All files extracted:', allFilesExtractedData);
      onFilesUploaded(allFilesExtractedData); // Pass extracted data to App.js
    } catch (error) {
      console.error('Error during unzipping:', error);
      setFiles(prev => prev.map(f => ({ ...f, status: 'error' })));
    } finally {
      setIsUploading(false);
    }
  };

  const totalSize = files.reduce((sum, f) => sum + f.size, 0);
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-2xl w-full mx-auto">
        {/* Minimal Hero */}
        <div className="text-center mb-8">
          <div className="flex flex-col items-center">
            <div className="flex items-center gap-4 mb-2">
              <Brain className="w-10 h-10 text-white" />
              <h1 className="text-3xl font-bold text-white">
                Facebook Psychology Analysis
              </h1>
            </div>
            <p className="text-white/80">
              Get AI-powered psychological insights from your Facebook data
            </p>
          </div>
          <div className="mt-6 p-4 bg-white/5 rounded-lg text-left max-w-2xl mx-auto">
            <p className="text-white/80 text-sm mb-3">
              Did you know? Social media platforms like Facebook track your every move - from what you like and share to how long you look at each post. 
              They know your interests, fears, political views, and even predict your future behavior.
            </p>
            <p className="text-white/80 text-sm">
              This tool helps you understand what your data reveals about you. Simply upload your Facebook data to get a comprehensive psychological profile, 
              including personality traits, emotional patterns, and behavioral insights - all processed securely on your device.
            </p>
          </div>
        </div>

        {/* Simple Instructions */}
        <div className="glass rounded-xl p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <p className="text-white">Need your Facebook data first?</p>
            <a
              href="https://accountscenter.facebook.com/info_and_permissions/dyi"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors text-sm"
            >
              <Download className="w-4 h-4" />
              Navigate to Facebook Data Download page
            </a>
          </div>
          
          <button 
            onClick={() => setShowDownloadInstructions(!showDownloadInstructions)}
            className="text-blue-400 hover:text-blue-300 text-sm flex items-center gap-1"
          >
            {showDownloadInstructions ? 'Hide' : 'Show'} detailed instructions
            <svg 
              className={`w-4 h-4 transition-transform ${showDownloadInstructions ? 'rotate-180' : ''}`} 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24" 
              xmlns="http://www.w3.org/2000/svg"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          {showDownloadInstructions && (
            <div className="mt-4 pt-4 border-t border-white/10">
              <div className="flex flex-col md:flex-row gap-6">
                <div className="flex-1">
                  <h3 className="text-white font-medium mb-3">How to download your Facebook data:</h3>
                  <ol className="list-decimal list-inside space-y-2 text-white/80 text-sm">
                    <li>Click the "Download Your Data" button above</li>
                    <li>Log in to your Facebook account if prompted</li>
                    <li>Select "Download your information"</li>
                    <li>Choose <span className="font-medium text-white">JSON</span> format (required for analysis)</li>
                    <li>Select "Low" media quality (we don't need your photos/videos)</li>
                    <li>Set the date range to "All of my data"</li>
                    <li>Click "Create File" and wait for the download link</li>
                    <li>Once ready, click the download link and save the ZIP file</li>
                    <li>Upload the ZIP file above to analyze your data</li>
                  </ol>
                  <div className="mt-4 p-3 bg-amber-900/30 border border-amber-800/50 rounded-lg">
                    <p className="text-amber-200 text-sm font-medium">⚠️ Important Note:</p>
                    <p className="text-amber-100 text-xs mt-1">
                      Facebook may take <span className="font-semibold">several hours</span> to prepare your data if you select "All of my data". 
                      For faster results, choose a <span className="font-semibold">smaller date range</span> (like 3 months).
                    </p>
                  </div>
                  <p className="mt-4 text-white/60 text-xs">
                    Your data is processed locally in your browser and never sent to any server.
                  </p>
                </div>
                <div className="md:w-1/3 flex-shrink-0">
                  <img 
                    src="/download.png" 
                    alt="Facebook download instructions" 
                    className="rounded-lg border border-white/10 shadow-lg w-full h-auto"
                  />
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Upload Section */}
        <div className="glass rounded-xl p-6">
          <div className="text-center mb-4">
            <h2 className="text-xl font-bold text-white mb-2">Upload Your Data</h2>
            <p className="text-white/70 text-sm">Drag and drop your Facebook ZIP file here</p>
          </div>
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-300 ${
              isDragActive
                ? 'border-white bg-white/10'
                : 'border-white/30 hover:border-white/50 hover:bg-white/5'
            }`}
          >
            <input {...getInputProps()} />
            
            <div className="flex flex-col items-center">
              <Upload className="w-12 h-12 text-white/70 mb-4" />
              
              {isDragActive ? (
                <p className="text-white text-lg">Drop your ZIP files here...</p>
              ) : (
                <p className="text-white text-lg">
                  Drag & drop your ZIP files here, or <span className="underline">click to select files</span>
                </p>
              )}
            </div>
          </div>
          
          {files.length > 0 && (
            <div className="mt-6">
              <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                <File className="w-5 h-5" />
                Uploaded Files ({files.length})
              </h3>
              
              <div className="space-y-3 max-h-60 overflow-y-auto">
                {files.map((fileItem) => (
                  <div
                    key={fileItem.id}
                    className="flex items-center justify-between bg-white/10 rounded-lg p-3"
                  >
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <div className="flex-shrink-0">
                        {fileItem.status === 'ready' && (
                          <File className="w-5 h-5 text-white/70" />
                        )}
                        {fileItem.status === 'uploading' && (
                          <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        )}
                        {fileItem.status === 'completed' && (
                          <CheckCircle className="w-5 h-5 text-green-400" />
                        )}
                        {fileItem.status === 'error' && (
                          <AlertCircle className="w-5 h-5 text-red-400" />
                        )}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <p className="text-white text-sm font-medium truncate">
                          {fileItem.file.name}
                        </p>
                        <p className="text-white/60 text-xs">
                          {formatFileSize(fileItem.size)}
                        </p>
                      </div>
                    </div>
                    
                    {fileItem.status === 'ready' && (
                      <button
                        onClick={() => removeFile(fileItem.id)}
                        className="text-white/60 hover:text-white p-1 transition-colors"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
              
              <div className="mt-4 pt-4 border-t border-white/20">
                <div className="flex justify-between items-center text-white/80 text-sm mb-4">
                  <span>Total size: {formatFileSize(totalSize)}</span>
                  <span>{files.length} file{files.length !== 1 ? 's' : ''}</span>
                </div>
                
                <button
                  onClick={handleUpload}
                  disabled={isUploading || files.length === 0}
                  className="w-full bg-primary-500 text-white py-3 rounded-lg font-semibold hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
                >
                  {isUploading ? (
                    <div className="flex items-center justify-center gap-2">
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Processing Files...
                    </div>
                  ) : (
                    'Start Analysis'
                  )}
                </button>
              </div>
            </div>
          )}
        </div>
        
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

export default LandingPage;
