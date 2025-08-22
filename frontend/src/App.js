import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [backendStatus, setBackendStatus] = useState('Checking...');
  const [loading, setLoading] = useState(true);

  // Test backend connection when app loads
  useEffect(() => {
    const testBackend = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/test');
        setBackendStatus(`✅ ${response.data.message}`);
      } catch (error) {
        setBackendStatus('❌ Backend not connected');
        console.error('Backend connection failed:', error);
      } finally {
        setLoading(false);
      }
    };

    testBackend();
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-blue-600 mb-2">
            🌊 WaveMail
          </h1>
          <p className="text-gray-600 mb-6">
            AI-Powered Email Assistant
          </p>
          
          <div className="bg-gray-50 p-4 rounded-lg">
            <h2 className="font-semibold mb-2">System Status:</h2>
            <p className={`${loading ? 'text-gray-500' : 'text-green-600'}`}>
              Frontend: ✅ Running
            </p>
            <p className={loading ? 'text-gray-500' : backendStatus.includes('✅') ? 'text-green-600' : 'text-red-600'}>
              Backend: {backendStatus}
            </p>
          </div>
          
          <div className="mt-6 text-sm text-gray-500">
            Day 1 Setup Complete! 🎉
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;