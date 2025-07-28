import React, { useState } from 'react';

// Reliable JSON viewer that works with all Facebook data
const JsonViewer = ({ jsonData, fileName }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  if (!jsonData) {
    return <div className="text-white/70">No JSON data available.</div>;
  }

  let parsedData;
  try {
    parsedData = JSON.parse(jsonData);
  } catch (error) {
    return (
      <div className="glass rounded-xl p-6 mb-6">
        <h3 className="text-white font-semibold mb-4">📄 {fileName} (Error)</h3>
        <div className="text-red-400">Error parsing JSON: {error.message}</div>
        <pre className="text-white/70 whitespace-pre-wrap break-all mt-4">{jsonData}</pre>
      </div>
    );
  }
  
  const jsonString = JSON.stringify(parsedData, null, 2);
  const preview = jsonString.length > 1000 ? jsonString.substring(0, 1000) + '...' : jsonString;
  
  return (
    <div className="glass rounded-xl p-6 mb-6">
      <h3 className="text-white font-semibold mb-4">📄 {fileName}</h3>
      <div className="mb-4 flex gap-2">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
        >
          {isExpanded ? 'Show Preview' : 'Show Full JSON'}
        </button>
        <span className="text-green-400 text-sm flex items-center">
          ✓ Stable viewer
        </span>
      </div>
      <div className="overflow-auto max-h-96">
        <pre className="text-white/80 whitespace-pre-wrap break-all text-sm bg-black/20 p-4 rounded">
          {isExpanded ? jsonString : preview}
        </pre>
      </div>
    </div>
  );
};

export default JsonViewer;
