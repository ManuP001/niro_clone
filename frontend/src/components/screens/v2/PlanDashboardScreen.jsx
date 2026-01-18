import React, { useState, useEffect } from 'react';
import { apiV2, formatPrice, getRemedyCategoryIcon } from './utils';

/**
 * PlanDashboardScreen - Active plan management
 * 
 * Shows:
 * - Plan progress
 * - Today's tasks
 * - Consultation booking
 * - Remedy add-ons
 */
export default function PlanDashboardScreen({ 
  token,
  planId,
  onBack,
  onNavigate
}) {
  const [loading, setLoading] = useState(true);
  const [planData, setPlanData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadPlan();
  }, [planId]);

  const loadPlan = async () => {
    try {
      const response = await apiV2.get(`/plans/${planId}`, token);
      if (response.ok) {
        setPlanData(response);
      } else {
        setError('Plan not found');
      }
    } catch (err) {
      setError('Failed to load plan');
    } finally {
      setLoading(false);
    }
  };

  const completeTask = async (taskId) => {
    try {
      await apiV2.post(`/plans/${planId}/tasks/${taskId}/complete`, {}, token);
      loadPlan(); // Reload to update progress
    } catch (err) {
      console.error('Failed to complete task:', err);
    }
  };

  // Loading
  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-emerald-200 border-t-emerald-500 rounded-full animate-spin" />
      </div>
    );
  }

  // Error
  if (error || !planData) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-6">
        <div className="text-center">
          <p className="text-slate-600">{error || 'Plan not found'}</p>
          <button onClick={onBack} className="text-emerald-600 mt-4">Go Back</button>
        </div>
      </div>
    );
  }

  const { plan, today_tasks, progress, consult_status, remedy_addons } = planData;

  return (
    <div className="min-h-screen bg-slate-50 pb-24">
      {/* Header */}
      <div className="bg-gradient-to-br from-emerald-500 to-teal-600 text-white">
        <div className="px-6 pt-12 pb-6">
          <div className="flex items-center justify-between mb-4">
            <button 
              onClick={onBack}
              className="text-emerald-100 flex items-center"
            >
              <span className="mr-2">←</span> Back
            </button>
            <button className="text-emerald-100">
              ⚙️
            </button>
          </div>
          
          <h1 className="text-xl font-bold">{plan.package?.name || 'Your Plan'}</h1>
          <p className="text-emerald-100 text-sm mt-1">Week {progress.current_week} of {progress.total_weeks}</p>
          
          {/* Progress Bar */}
          <div className="mt-4">
            <div className="h-3 bg-emerald-400/30 rounded-full overflow-hidden">
              <div 
                className="h-full bg-white rounded-full transition-all"
                style={{ width: `${progress.percent}%` }}
              />
            </div>
            <div className="flex justify-between mt-2 text-emerald-100 text-sm">
              <span>{progress.percent}% complete</span>
              <span>{progress.tasks_completed}/{progress.tasks_total} tasks</span>
            </div>
          </div>
        </div>
      </div>

      <div className="px-6 -mt-4 space-y-4">
        
        {/* Today's Tasks */}
        <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-slate-800">Today's Tasks</h3>
            <span className="text-sm text-slate-500">
              {today_tasks.filter(t => t.status === 'completed').length}/{today_tasks.length} done
            </span>
          </div>
          
          {today_tasks.length === 0 ? (
            <div className="text-center py-6">
              <span className="text-4xl mb-2 block">🎉</span>
              <p className="text-slate-600">All done for today!</p>
              <p className="text-slate-400 text-sm">Great work. See you tomorrow.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {today_tasks.map(task => (
                <div 
                  key={task.task_id}
                  className={`flex items-start p-3 rounded-xl transition-all ${
                    task.status === 'completed' 
                      ? 'bg-emerald-50' 
                      : 'bg-slate-50 hover:bg-slate-100'
                  }`}
                >
                  <button
                    onClick={() => task.status !== 'completed' && completeTask(task.task_id)}
                    className={`w-6 h-6 rounded-full border-2 mr-3 flex-shrink-0 flex items-center justify-center transition-all ${
                      task.status === 'completed'
                        ? 'bg-emerald-500 border-emerald-500'
                        : 'border-slate-300 hover:border-emerald-400'
                    }`}
                  >
                    {task.status === 'completed' && (
                      <span className="text-white text-xs">✓</span>
                    )}
                  </button>
                  <div className="flex-1">
                    <p className={`font-medium ${
                      task.status === 'completed' ? 'text-slate-500 line-through' : 'text-slate-800'
                    }`}>
                      {task.name}
                    </p>
                    <p className="text-slate-500 text-sm">{task.description}</p>
                    <div className="flex items-center mt-2 text-xs text-slate-400">
                      <span>{task.duration_minutes} min</span>
                      <span className="mx-2">•</span>
                      <span className="capitalize">{task.content_type.replace('_', ' ')}</span>
                    </div>
                  </div>
                  {task.status !== 'completed' && (
                    <button className="text-emerald-600 text-lg">
                      ▶️
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Consultation */}
        {plan.package?.includes_consultation && (
          <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm">
            <h3 className="font-semibold text-slate-800 mb-4">Consultation</h3>
            
            <div className="grid grid-cols-2 gap-3">
              <a 
                href={consult_status.booking_url || plan.consultation_booking_url || 'https://calendar.app.google/GJMg3Btky7cwdaYf9'}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-blue-50 border border-blue-100 rounded-xl p-4 text-left hover:bg-blue-100 transition-all block"
              >
                <span className="text-2xl mb-2 block">📹</span>
                <p className="font-medium text-slate-800">Book Session</p>
                <p className="text-slate-500 text-xs mt-1">
                  {consult_status.sessions_remaining}/{consult_status.sessions_total} remaining
                </p>
              </a>
              
              <button 
                className="bg-purple-50 border border-purple-100 rounded-xl p-4 text-left hover:bg-purple-100 transition-all"
                onClick={() => onNavigate('chat')}
              >
                <span className="text-2xl mb-2 block">💬</span>
                <p className="font-medium text-slate-800">Chat Support</p>
                <p className="text-slate-500 text-xs mt-1">
                  Reply within {consult_status.chat_sla_hours || 12}hrs
                </p>
              </button>
            </div>
          </div>
        )}

        {/* Remedy Add-Ons */}
        <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-slate-800">Remedy Add-Ons</h3>
            <button 
              onClick={() => onNavigate('remedies', { planId })}
              className="text-emerald-600 text-sm font-medium"
            >
              + Add More
            </button>
          </div>
          
          {remedy_addons.length === 0 ? (
            <div className="text-center py-4">
              <p className="text-slate-500 text-sm">No remedy add-ons yet</p>
              <button 
                onClick={() => onNavigate('remedies', { planId })}
                className="text-emerald-600 text-sm mt-2"
              >
                Browse available remedies
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {remedy_addons.map(addon => (
                <div key={addon.addon_id} className="flex items-center p-3 bg-amber-50 rounded-xl">
                  <span className="text-xl mr-3">{getRemedyCategoryIcon(addon.remedy?.category)}</span>
                  <div className="flex-1">
                    <p className="font-medium text-slate-800">{addon.remedy?.name}</p>
                    <p className="text-slate-500 text-xs capitalize">
                      Status: {addon.status.replace('_', ' ')}
                    </p>
                  </div>
                  <button className="text-slate-400">→</button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Weekly Streak */}
        <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm">
          <h3 className="font-semibold text-slate-800 mb-4">This Week</h3>
          <div className="flex justify-between">
            {['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((day, idx) => {
              const isCompleted = idx < (progress.current_week <= 1 ? today_tasks.filter(t => t.status === 'completed').length : 3);
              const isToday = idx === new Date().getDay() - 1 || (new Date().getDay() === 0 && idx === 6);
              return (
                <div key={idx} className="text-center">
                  <p className="text-xs text-slate-500 mb-2">{day}</p>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    isCompleted 
                      ? 'bg-emerald-500 text-white' 
                      : isToday 
                        ? 'bg-emerald-100 text-emerald-600 border-2 border-emerald-500'
                        : 'bg-slate-100 text-slate-400'
                  }`}>
                    {isCompleted ? '✓' : '○'}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Bottom CTA */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-100 p-4">
        <button
          onClick={() => onNavigate('chat')}
          className="w-full bg-slate-100 text-slate-700 font-medium py-3 rounded-xl flex items-center justify-center hover:bg-slate-200 transition-all"
        >
          <span className="mr-2">💬</span>
          Questions? Chat with me
        </button>
      </div>
    </div>
  );
}
