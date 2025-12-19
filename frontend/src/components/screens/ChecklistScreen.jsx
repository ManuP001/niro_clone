import React, { useState, useEffect } from 'react';
import { ArrowLeft, Loader, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import { BACKEND_URL } from '../../config';

const ChecklistScreen = ({ requestId, onBack }) => {
  const [checklist, setChecklist] = useState(null);
  const [checklistData, setChecklistData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchChecklist = async () => {
      if (!requestId) {
        setError('No request ID provided');
        setLoading(false);
        return;
      }

      try {
        // Fetch pipeline trace from the new debug endpoint
        const traceUrl = `${BACKEND_URL}/api/debug/pipeline-trace/latest?user_id=${requestId}`;
        console.log('[ChecklistScreen] Fetching pipeline trace from:', traceUrl);
        
        const traceResponse = await fetch(traceUrl, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          }
        });
        
        console.log('[ChecklistScreen] Trace response status:', traceResponse.status);

        if (!traceResponse.ok) {
          throw new Error(`Failed to fetch pipeline trace: ${traceResponse.status}`);
        }

        const traceData = await traceResponse.json();
        console.log('[ChecklistScreen] Got trace data:', traceData);
        
        // Store the trace data
        setChecklistData(traceData);
        
        // Try to fetch HTML rendering as well
        const htmlUrl = `${BACKEND_URL}/api/debug/pipeline-trace/render-html?user_id=${requestId}`;
        try {
          const htmlResponse = await fetch(htmlUrl, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
            }
          });
          
          if (htmlResponse.ok) {
            const html = await htmlResponse.text();
            console.log('[ChecklistScreen] Got HTML render, length:', html.length);
            setChecklist(html);
          }
        } catch (e) {
          console.warn('[ChecklistScreen] Could not fetch HTML render:', e);
          // Generate our own HTML from JSON data
          if (traceData && traceData.trace) {
            const generatedHtml = generateChecklistHTML(traceData.trace);
            setChecklist(generatedHtml);
          }
        }
      } catch (err) {
        console.error('[ChecklistScreen] Error:', err);
        setError(err.message || 'Failed to load checklist');
      } finally {
        setLoading(false);
      }
    };

    fetchChecklist();
  }, [requestId]);

  // Generate HTML from pipeline trace JSON
  const generateChecklistHTML = (trace) => {
    if (!trace) return '';
    
    const steps = trace.steps || [];
    const stepsHtml = steps.map((step, idx) => {
      const statusColor = step.status === 'success' ? '#10b981' : '#ef4444';
      const statusIcon = step.status === 'success' ? '✓' : '✗';
      
      return `
        <div style="margin-bottom: 16px; padding: 12px; border-left: 4px solid ${statusColor}; background: #f9fafb; border-radius: 4px;">
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <span style="color: ${statusColor}; font-weight: bold; font-size: 16px;">${statusIcon}</span>
            <span style="font-weight: 600; color: #111827;">${step.step_id}</span>
            <span style="color: #6b7280; font-size: 12px;">(${step.duration_ms || 0}ms)</span>
          </div>
          ${step.inputs ? `<div style="color: #4b5563; font-size: 12px; margin-bottom: 4px;"><strong>Input:</strong> ${JSON.stringify(step.inputs).substring(0, 100)}</div>` : ''}
          ${step.outputs ? `<div style="color: #4b5563; font-size: 12px;"><strong>Output:</strong> ${JSON.stringify(step.outputs).substring(0, 100)}</div>` : ''}
          ${step.error ? `<div style="color: #dc2626; font-size: 12px;"><strong>Error:</strong> ${step.error}</div>` : ''}
        </div>
      `;
    }).join('');
    
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; padding: 16px; background: #ffffff; }
          .header { margin-bottom: 24px; border-bottom: 1px solid #e5e7eb; padding-bottom: 16px; }
          .title { font-size: 20px; font-weight: 700; color: #111827; margin: 0; }
          .subtitle { font-size: 14px; color: #6b7280; margin: 4px 0 0 0; }
          .summary { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 24px; }
          .summary-item { padding: 12px; background: #f3f4f6; border-radius: 6px; }
          .summary-label { font-size: 12px; color: #6b7280; margin-bottom: 4px; }
          .summary-value { font-size: 14px; font-weight: 600; color: #111827; }
        </style>
      </head>
      <body>
        <div class="header">
          <h1 class="title">Pipeline Execution Trace</h1>
          <p class="subtitle">User: ${trace.user_id || 'Unknown'} | Run ID: ${trace.run_id || 'Unknown'}</p>
        </div>
        
        <div class="summary">
          <div class="summary-item">
            <div class="summary-label">Total Duration</div>
            <div class="summary-value">${trace.total_duration_ms || 0}ms</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">Status</div>
            <div class="summary-value" style="color: ${trace.success ? '#10b981' : '#ef4444'};">
              ${trace.success ? 'SUCCESS' : 'FAILED'}
            </div>
          </div>
        </div>
        
        <h2 style="font-size: 16px; font-weight: 600; color: #111827; margin: 24px 0 12px 0;">Steps</h2>
        ${stepsHtml}
      </body>
      </html>
    `;
  };

  if (loading) {
    return (
      <div className="h-full bg-white flex flex-col">
        <div className="px-4 pt-2 pb-4 bg-gradient-to-b from-blue-50 to-white border-b">
          <div className="flex items-center gap-3">
            <button 
              onClick={onBack}
              className="text-gray-600 hover:text-gray-800"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <h1 className="text-lg font-semibold text-gray-800">Processing Report</h1>
          </div>
        </div>
        
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <Loader className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-3" />
            <p className="text-gray-600">Loading your report...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full bg-white flex flex-col">
        <div className="px-4 pt-2 pb-4 bg-gradient-to-b from-red-50 to-white border-b">
          <div className="flex items-center gap-3">
            <button 
              onClick={onBack}
              className="text-gray-600 hover:text-gray-800"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <h1 className="text-lg font-semibold text-gray-800">Processing Report</h1>
          </div>
        </div>
        
        <div className="flex-1 flex items-center justify-center p-4">
          <div className="text-center">
            <AlertCircle className="w-8 h-8 text-red-500 mx-auto mb-3" />
            <p className="text-gray-600 mb-2">Unable to load report</p>
            <p className="text-sm text-gray-500">{error}</p>
            <button 
              onClick={onBack}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm"
            >
              Go Back
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full bg-white flex flex-col overflow-hidden">
      <div className="px-4 pt-2 pb-4 bg-gradient-to-b from-blue-50 to-white border-b flex-shrink-0">
        <div className="flex items-center gap-3 mb-2">
          <button 
            onClick={onBack}
            className="text-gray-600 hover:text-gray-800"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="text-lg font-semibold text-gray-800">Processing Report</h1>
        </div>
        <p className="text-xs text-gray-500 px-8">Request ID: {requestId}</p>
      </div>

      {/* Display structured JSON data summary if available */}
      {checklistData && checklistData.trace && (
        <div className="bg-white border-b p-4 flex-shrink-0 overflow-y-auto max-h-[250px]">
          <h2 className="font-semibold text-gray-900 mb-3">Pipeline Execution</h2>
          
          <div className="grid grid-cols-2 gap-3 text-sm mb-4">
            {/* Run ID */}
            <div className="bg-blue-50 p-2 rounded">
              <p className="text-gray-600 font-medium text-xs">Run ID</p>
              <p className="text-gray-900 text-xs font-mono truncate">{checklistData.trace.run_id?.substring(0, 12) || 'N/A'}...</p>
            </div>
            
            {/* User */}
            <div className="bg-blue-50 p-2 rounded">
              <p className="text-gray-600 font-medium text-xs">User</p>
              <p className="text-gray-900 text-xs">{checklistData.trace.user_id || 'N/A'}</p>
            </div>
            
            {/* Duration */}
            <div className="bg-green-50 p-2 rounded">
              <p className="text-gray-600 font-medium text-xs">Duration</p>
              <p className="text-gray-900 text-xs">{checklistData.trace.total_duration_ms || 0}ms</p>
            </div>
            
            {/* Status */}
            <div className="bg-purple-50 p-2 rounded">
              <p className="text-gray-600 font-medium text-xs">Status</p>
              <p className={`text-xs font-medium ${checklistData.trace.success ? 'text-green-700' : 'text-red-700'}`}>
                {checklistData.trace.success ? '✓ SUCCESS' : '✗ FAILED'}
              </p>
            </div>
          </div>
          
          {/* Steps Summary */}
          <div>
            <p className="text-xs font-semibold text-gray-700 mb-2">Steps ({checklistData.trace.steps?.length || 0})</p>
            <div className="space-y-1">
              {checklistData.trace.steps?.map((step, idx) => (
                <div key={idx} className="flex items-center gap-2 text-xs p-1 bg-gray-50 rounded">
                  <span className={step.status === 'success' ? 'text-green-600' : 'text-red-600'}>
                    {step.status === 'success' ? '✓' : '✗'}
                  </span>
                  <span className="font-mono flex-1">{step.step_id}</span>
                  <span className="text-gray-500">{step.duration_ms || 0}ms</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Display the HTML report in an iframe if available */}
      {checklist ? (
        <div className="flex-1 overflow-hidden">
          <iframe
            srcDoc={checklist}
            className="w-full h-full border-none"
            title="Checklist Report HTML"
            sandbox="allow-same-origin allow-forms"
          />
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center p-4">
          <div className="text-center">
            <AlertCircle className="w-8 h-8 text-amber-500 mx-auto mb-3" />
            <p className="text-gray-600">HTML report not available</p>
            <p className="text-sm text-gray-500 mt-1">JSON data loaded: {checklistData ? 'Yes' : 'No'}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChecklistScreen;
