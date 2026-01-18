import React, { useState, useEffect } from 'react';
import { Filter, ChevronDown, ChevronUp, CheckCircle, XCircle, RefreshCw } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';

const CandidateSignalsScreen = ({ userId }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState('score_final');
  const [sortDir, setSortDir] = useState('desc');
  const [filterPlanet, setFilterPlanet] = useState('all');
  const [filterType, setFilterType] = useState('all');
  const [filterKept, setFilterKept] = useState('all');
  const [showFilters, setShowFilters] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Always fetch the latest candidate signals (no user filter for debug)
      // This ensures we see the most recent data regardless of which user generated it
      const url = `${BACKEND_URL}/api/debug/candidate-signals/latest`;
      const response = await fetch(url);
      
      if (!response.ok) {
        if (response.status === 404) {
          setError('No candidate signals data found. Ask a question in chat first.');
        } else {
          throw new Error(`HTTP ${response.status}`);
        }
        setData(null);
        return;
      }
      
      const result = await response.json();
      setData(result.data);
    } catch (err) {
      setError(`Failed to load candidate signals: ${err.message}`);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [userId]);

  // Get unique planets and types for filters
  const planets = data?.candidates ? [...new Set(data.candidates.map(c => c.planet))].sort() : [];
  const types = data?.candidates ? [...new Set(data.candidates.map(c => c.signal_type))].sort() : [];

  // Filter and sort candidates
  const filteredCandidates = data?.candidates?.filter(c => {
    if (filterPlanet !== 'all' && c.planet !== filterPlanet) return false;
    if (filterType !== 'all' && c.signal_type !== filterType) return false;
    if (filterKept === 'kept' && !c.kept) return false;
    if (filterKept === 'dropped' && c.kept) return false;
    return true;
  }).sort((a, b) => {
    const aVal = a[sortBy] || 0;
    const bVal = b[sortBy] || 0;
    if (sortDir === 'desc') return bVal - aVal;
    return aVal - bVal;
  }) || [];

  const toggleSort = (field) => {
    if (sortBy === field) {
      setSortDir(sortDir === 'desc' ? 'asc' : 'desc');
    } else {
      setSortBy(field);
      setSortDir('desc');
    }
  };

  const SortHeader = ({ field, label }) => (
    <th 
      className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
      onClick={() => toggleSort(field)}
    >
      <div className="flex items-center gap-1">
        {label}
        {sortBy === field && (
          sortDir === 'desc' ? <ChevronDown className="w-3 h-3" /> : <ChevronUp className="w-3 h-3" />
        )}
      </div>
    </th>
  );

  return (
    <div className="h-full bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b px-4 py-3 flex items-center gap-3">
        <div className="flex-1">
          <h1 className="text-lg font-semibold text-gray-800">Signal Matching</h1>
          <p className="text-xs text-gray-500">View all candidate signals from your last query</p>
        </div>
        <button 
          onClick={fetchData} 
          className="p-2 hover:bg-gray-100 rounded"
          title="Refresh"
        >
          <RefreshCw className={`w-4 h-4 text-gray-600 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="text-gray-500">Loading...</div>
          </div>
        )}

        {error && !loading && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
            <p className="text-red-600">{error}</p>
            <button 
              onClick={fetchData}
              className="mt-2 text-sm text-red-600 underline"
            >
              Try again
            </button>
          </div>
        )}

        {data && !loading && (
          <>
            {/* Summary Card */}
            <div className="bg-white rounded-lg shadow-sm border p-4 mb-4">
              <h2 className="text-sm font-semibold text-gray-700 mb-3">Summary</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div className="bg-blue-50 rounded-lg p-3">
                  <p className="text-2xl font-bold text-blue-600">{data.summary?.total_candidates || 0}</p>
                  <p className="text-xs text-blue-700">Total Candidates</p>
                </div>
                <div className="bg-green-50 rounded-lg p-3">
                  <p className="text-2xl font-bold text-green-600">{data.summary?.kept_count || 0}</p>
                  <p className="text-xs text-green-700">Kept</p>
                </div>
                <div className="bg-red-50 rounded-lg p-3">
                  <p className="text-2xl font-bold text-red-600">{data.summary?.dropped_count || 0}</p>
                  <p className="text-xs text-red-700">Dropped</p>
                </div>
                <div className="bg-purple-50 rounded-lg p-3">
                  <p className="text-2xl font-bold text-purple-600">{Object.keys(data.summary?.counts_by_planet || {}).length}</p>
                  <p className="text-xs text-purple-700">Planets</p>
                </div>
              </div>

              {/* Context */}
              <div className="mt-4 pt-3 border-t text-xs text-gray-600">
                <p><strong>Question:</strong> {data.user_question || 'N/A'}</p>
                <p><strong>Topic:</strong> {data.topic || 'N/A'} | <strong>Time Context:</strong> {data.time_context || 'N/A'} | <strong>Intent:</strong> {data.intent || 'N/A'}</p>
              </div>

              {/* Planet Distribution */}
              {data.summary?.counts_by_planet && (
                <div className="mt-4 pt-3 border-t">
                  <p className="text-xs font-medium text-gray-600 mb-2">Signals by Planet:</p>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(data.summary.counts_by_planet).map(([planet, count]) => (
                      <span key={planet} className="text-xs px-2 py-1 bg-gray-100 rounded-full">
                        {planet}: {count}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Filters */}
            <div className="bg-white rounded-lg shadow-sm border mb-4">
              <button 
                onClick={() => setShowFilters(!showFilters)}
                className="w-full px-4 py-3 flex items-center justify-between text-sm font-medium text-gray-700"
              >
                <div className="flex items-center gap-2">
                  <Filter className="w-4 h-4" />
                  Filters
                </div>
                {showFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
              
              {showFilters && (
                <div className="px-4 pb-4 grid grid-cols-3 gap-3">
                  <div>
                    <label className="text-xs text-gray-500">Planet</label>
                    <select 
                      value={filterPlanet} 
                      onChange={(e) => setFilterPlanet(e.target.value)}
                      className="w-full text-sm border rounded p-1.5"
                    >
                      <option value="all">All</option>
                      {planets.map(p => <option key={p} value={p}>{p}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="text-xs text-gray-500">Type</label>
                    <select 
                      value={filterType} 
                      onChange={(e) => setFilterType(e.target.value)}
                      className="w-full text-sm border rounded p-1.5"
                    >
                      <option value="all">All</option>
                      {types.map(t => <option key={t} value={t}>{t}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="text-xs text-gray-500">Status</label>
                    <select 
                      value={filterKept} 
                      onChange={(e) => setFilterKept(e.target.value)}
                      className="w-full text-sm border rounded p-1.5"
                    >
                      <option value="all">All</option>
                      <option value="kept">Kept</option>
                      <option value="dropped">Dropped</option>
                    </select>
                  </div>
                </div>
              )}
            </div>

            {/* Signals Table */}
            <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <SortHeader field="planet" label="Planet" />
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">House</th>
                      <SortHeader field="score_final" label="Score" />
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredCandidates.map((candidate, idx) => (
                      <tr key={idx} className={candidate.kept ? 'bg-green-50' : 'bg-white hover:bg-gray-50'}>
                        <td className="px-3 py-2 whitespace-nowrap">
                          {candidate.kept ? (
                            <span className="flex items-center gap-1 text-green-600">
                              <CheckCircle className="w-4 h-4" />
                              <span className="text-xs">{candidate.final_id}</span>
                            </span>
                          ) : (
                            <span className="text-red-400">
                              <XCircle className="w-4 h-4" />
                            </span>
                          )}
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap text-sm font-medium text-gray-900">
                          {candidate.planet}
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-500">
                          <span className="px-2 py-0.5 bg-gray-100 rounded">{candidate.signal_type}</span>
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-500">
                          {candidate.house ? `${candidate.house}H` : '-'}
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap">
                          <span className={`text-sm font-medium ${
                            candidate.score_final >= 0.65 ? 'text-green-600' :
                            candidate.score_final >= 0.50 ? 'text-amber-600' : 'text-red-500'
                          }`}>
                            {candidate.score_final?.toFixed(2)}
                          </span>
                        </td>
                        <td className="px-3 py-2 text-xs text-gray-600 max-w-xs truncate">
                          {candidate.text_human}
                        </td>
                      </tr>
                    ))}
                    {filteredCandidates.length === 0 && (
                      <tr>
                        <td colSpan={6} className="px-3 py-8 text-center text-gray-500">
                          No signals match the current filters
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Top 10 by Score */}
            {data.summary?.top_10_by_score && (
              <div className="bg-white rounded-lg shadow-sm border p-4 mt-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Top 10 by Score</h3>
                <div className="space-y-2">
                  {data.summary.top_10_by_score.map((item, idx) => (
                    <div key={idx} className="flex items-center gap-3 text-xs">
                      <span className="w-6 text-gray-400">{idx + 1}.</span>
                      <span className={`w-4 h-4 rounded-full ${item.kept ? 'bg-green-500' : 'bg-red-300'}`}></span>
                      <span className="flex-1 font-medium">{item.planet}</span>
                      <span className={`font-mono ${item.kept ? 'text-green-600' : 'text-gray-400'}`}>
                        {item.score?.toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default CandidateSignalsScreen;
