import React, { useState } from 'react';
import ReviewModal from './ReviewModal';

const KanbanBoard = ({ jobs, refreshJobs, loading }) => {
  const [selectedJobId, setSelectedJobId] = useState(null);

  // Derive columns
  const leads = jobs.evaluation.filter(j => j.status === 'pending');
  const evaluating = jobs.evaluation.filter(j => j.status === 'processing');
  
  const needsReview = jobs.review.filter(j => j.status === 'pending');
  const applied = jobs.review.filter(j => j.status === 'sent');
  const rejected = jobs.review.filter(j => j.status === 'rejected').concat(
    jobs.evaluation.filter(j => j.status === 'failed' || j.status === 'rejected')
  );

  const columns = [
    { id: 'leads', title: 'New Leads', items: leads, color: 'border-blue-500' },
    { id: 'evaluating', title: 'Scraping / Evaluating', items: evaluating, color: 'border-purple-500' },
    { id: 'review', title: 'Needs Review', items: needsReview, color: 'border-yellow-500', isReviewable: true },
    { id: 'applied', title: 'Applied', items: applied, color: 'border-green-500' },
    { id: 'rejected', title: 'Rejected / Failed', items: rejected, color: 'border-red-500' },
  ];

  return (
    <div className="flex gap-6 overflow-x-auto pb-4 h-[calc(100vh-140px)]">
      {columns.map(col => (
        <div key={col.id} className="min-w-[320px] w-[320px] flex flex-col bg-slate-800/50 rounded-xl border border-slate-700 overflow-hidden">
          <div className={`p-4 border-t-4 ${col.color} bg-slate-800 flex justify-between items-center`}>
            <h2 className="font-semibold text-slate-200">{col.title}</h2>
            <span className="bg-slate-700 text-slate-300 text-xs px-2 py-1 rounded-full">{col.items.length}</span>
          </div>
          
          <div className="p-4 flex-1 overflow-y-auto space-y-4">
            {col.items.map(item => (
              <div 
                key={item.id + (item.url || item.company_name)} 
                className={`p-4 rounded-lg bg-slate-800 border border-slate-700 shadow-lg ${col.isReviewable ? 'cursor-pointer hover:border-yellow-500 transition-colors' : ''}`}
                onClick={() => col.isReviewable && setSelectedJobId(item.id)}
              >
                <div className="text-sm font-medium text-slate-200 mb-2 truncate">
                  {item.company_name || 'Evaluating URL...'}
                </div>
                <div className="text-xs text-slate-400 truncate" title={item.url}>
                  {item.url}
                </div>
                {col.isReviewable && (
                  <div className="mt-3">
                    <span className="text-xs font-medium text-yellow-500 bg-yellow-500/10 px-2 py-1 rounded">Action Required</span>
                  </div>
                )}
              </div>
            ))}
            
            {col.items.length === 0 && !loading && (
              <div className="text-center text-slate-500 text-sm mt-8">
                No jobs in this column
              </div>
            )}
          </div>
        </div>
      ))}
      
      {selectedJobId && (
        <ReviewModal 
          jobId={selectedJobId} 
          onClose={() => setSelectedJobId(null)} 
          onSuccess={() => {
            setSelectedJobId(null);
            refreshJobs();
          }}
        />
      )}
    </div>
  );
};

export default KanbanBoard;
