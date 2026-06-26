import React, { useState, useEffect } from 'react';
import KanbanBoard from './components/KanbanBoard';

function App() {
  const [jobs, setJobs] = useState({ evaluation: [], review: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/jobs');
      if (!response.ok) {
        throw new Error('Failed to fetch jobs');
      }
      const data = await response.json();
      setJobs(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-8 font-sans">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
            Enterprise Swarm Dashboard
          </h1>
          <p className="text-slate-400 mt-2">Multi-Agent Job Application Tracker</p>
        </div>
        <button 
          onClick={fetchJobs}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-md transition-colors border border-slate-700"
        >
          Refresh
        </button>
      </header>

      {error ? (
        <div className="p-4 bg-red-900/50 border border-red-500 rounded-lg text-red-200">
          Error: {error}
        </div>
      ) : (
        <KanbanBoard jobs={jobs} refreshJobs={fetchJobs} loading={loading} />
      )}
    </div>
  );
}

export default App;
