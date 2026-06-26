import React, { useState, useEffect } from 'react';

const ReviewModal = ({ jobId, onClose, onSuccess }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/jobs/${jobId}/review`);
        if (!response.ok) throw new Error("Failed to fetch review details");
        const json = await response.json();
        setData(json);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchDetails();
  }, [jobId]);

  const handleAction = async (action) => {
    setActionLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/jobs/${jobId}/${action}`, {
        method: 'POST'
      });
      if (!response.ok) throw new Error(`Failed to ${action} job`);
      onSuccess();
    } catch (err) {
      alert(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
    </div>
  );

  if (error) return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-slate-800 p-6 rounded-lg max-w-md w-full border border-slate-700 text-center">
        <h3 className="text-xl text-red-400 mb-4">Error Loading Review</h3>
        <p className="text-slate-300 mb-6">{error}</p>
        <button onClick={onClose} className="px-4 py-2 bg-slate-700 rounded text-white">Close</button>
      </div>
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-6">
      <div className="bg-slate-900 rounded-2xl w-full h-full max-w-7xl border border-slate-700 flex flex-col overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-800/50">
          <div>
            <h2 className="text-2xl font-bold text-slate-100">Review Application: {data.job.company_name}</h2>
            <a href={data.job.url} target="_blank" rel="noreferrer" className="text-blue-400 hover:underline text-sm">{data.job.url}</a>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors p-2">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left Pane - Job Description */}
          <div className="w-1/2 border-r border-slate-800 flex flex-col">
            <div className="p-3 bg-slate-800/80 font-medium text-slate-300 border-b border-slate-700">Original Job Description</div>
            <div className="flex-1 overflow-y-auto p-6 bg-slate-900/50">
              <pre className="whitespace-pre-wrap text-sm text-slate-300 font-mono leading-relaxed">
                {data.job_description}
              </pre>
            </div>
          </div>

          {/* Right Pane - Email Draft & Resume */}
          <div className="w-1/2 flex flex-col h-full overflow-hidden">
            <div className="p-3 bg-slate-800/80 font-medium text-slate-300 border-b border-slate-700">Synthesized Email Draft</div>
            <div className="h-1/3 overflow-y-auto p-6 bg-slate-900/50 border-b border-slate-800">
               <pre className="whitespace-pre-wrap text-sm text-green-400 font-mono">
                {data.email_draft}
              </pre>
            </div>
            
            <div className="p-3 bg-slate-800/80 font-medium text-slate-300 border-b border-slate-700 flex justify-between">
              <span>Tailored Resume (PDF)</span>
            </div>
            <div className="flex-1 bg-slate-800/20 p-4">
              {data.resume_pdf_base64 ? (
                <iframe 
                  src={`data:application/pdf;base64,${data.resume_pdf_base64}`} 
                  className="w-full h-full rounded border border-slate-700"
                  title="Tailored Resume"
                />
              ) : (
                <div className="flex h-full items-center justify-center text-slate-500">Resume PDF not generated</div>
              )}
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-6 border-t border-slate-800 bg-slate-900 flex justify-end gap-4">
          <button 
            disabled={actionLoading}
            onClick={() => handleAction('reject')}
            className="px-6 py-2.5 rounded-lg border border-red-500/50 text-red-400 hover:bg-red-500 hover:text-white transition-colors disabled:opacity-50"
          >
            Reject Application
          </button>
          <button 
            disabled={actionLoading}
            onClick={() => handleAction('approve')}
            className="px-8 py-2.5 rounded-lg bg-green-500 hover:bg-green-600 text-white font-semibold transition-colors shadow-lg shadow-green-500/20 disabled:opacity-50 flex items-center gap-2"
          >
            {actionLoading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white/20 border-t-white"></div>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
            )}
            Approve & Send Email
          </button>
        </div>
      </div>
    </div>
  );
};

export default ReviewModal;
