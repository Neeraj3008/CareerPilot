import React, { useState, useEffect } from 'react';
import { 
  Search, MapPin, DollarSign, Building, Bookmark, 
  Filter, Check, Sparkles, AlertCircle 
} from 'lucide-react';
import { api } from '../services/api';
import { Job } from '../types';

export const SearchView: React.FC = () => {
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState('');
  const [remotePolicy, setRemotePolicy] = useState('');
  const [minSalary, setMinSalary] = useState<number | undefined>(undefined);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [savedJobIds, setSavedJobIds] = useState<Set<string>>(new Set());
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);

  const performSearch = async () => {
    setLoading(true);
    try {
      const results = await api.search.semantic({
        query: query.trim() || undefined,
        location: location.trim() || undefined,
        remote_policy: remotePolicy || undefined,
        min_salary: minSalary,
        limit: 20
      });
      setJobs(results);

      const saved = await api.savedJobs.list();
      setSavedJobIds(new Set(saved.map(s => s.job_id)));
    } catch (err) {
      console.error('Search failed', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    performSearch();
  }, []);

  const handleSaveJob = async (jobId: string, title: string) => {
    try {
      await api.savedJobs.save(jobId);
      setSavedJobIds(prev => new Set(prev).add(jobId));
      setSaveSuccessMsg(`Saved "${title}" to your tracker.`);
      setTimeout(() => setSaveSuccessMsg(null), 3000);
    } catch (err) {
      console.error('Failed to save job', err);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Search Header */}
      <div>
        <div className="flex items-center space-x-2">
          <h1 className="text-2xl font-extrabold text-slate-900">Semantic Vector Job Search</h1>
          <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-purple-100 text-purple-800 flex items-center space-x-1">
            <Sparkles className="w-3 h-3" />
            <span>pgvector 768-D</span>
          </span>
        </div>
        <p className="text-xs text-slate-500 mt-1">
          Search using natural language or concepts (e.g., "Build RAG pipelines with PyTorch", "Modern React Tailwind UI").
        </p>
      </div>

      {saveSuccessMsg && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold rounded-xl flex items-center space-x-2 animate-fade-in">
          <Check className="w-4 h-4 text-emerald-600" />
          <span>{saveSuccessMsg}</span>
        </div>
      )}

      {/* Filter Bar */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && performSearch()}
              placeholder="Search by keywords, architecture concepts, or roles..."
              className="w-full pl-10 pr-4 py-2.5 text-sm rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
            />
          </div>

          <button
            onClick={performSearch}
            disabled={loading}
            className="px-6 py-2.5 rounded-xl text-sm font-semibold text-white bg-brand-600 hover:bg-brand-700 shadow-sm transition-all whitespace-nowrap"
          >
            {loading ? 'Searching...' : 'Search Roles'}
          </button>
        </div>

        {/* Filter Selectors */}
        <div className="flex flex-wrap items-center gap-3 pt-2 border-t border-slate-100 text-xs">
          <div className="flex items-center space-x-1 text-slate-500 font-semibold">
            <Filter className="w-3.5 h-3.5" />
            <span>Filters:</span>
          </div>

          <select
            value={remotePolicy}
            onChange={(e) => setRemotePolicy(e.target.value)}
            className="px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="">All Work Policies</option>
            <option value="REMOTE">Remote Only</option>
            <option value="HYBRID">Hybrid</option>
            <option value="ONSITE">Onsite</option>
          </select>

          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Location (e.g. San Francisco)"
            className="px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 text-xs focus:outline-none focus:ring-2 focus:ring-brand-500"
          />

          <select
            value={minSalary ? String(minSalary) : ''}
            onChange={(e) => setMinSalary(e.target.value ? Number(e.target.value) : undefined)}
            className="px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="">Any Salary</option>
            <option value="100000">$100k+ / year</option>
            <option value="140000">$140k+ / year</option>
            <option value="180000">$180k+ / year</option>
          </select>

          {(query || remotePolicy || location || minSalary) && (
            <button
              onClick={() => {
                setQuery('');
                setLocation('');
                setRemotePolicy('');
                setMinSalary(undefined);
              }}
              className="text-xs text-brand-600 hover:text-brand-800 font-semibold underline ml-auto"
            >
              Reset Filters
            </button>
          )}
        </div>
      </div>

      {/* Results List */}
      {loading ? (
        <div className="py-20 text-center">
          <div className="w-8 h-8 border-4 border-brand-200 border-t-brand-600 rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-xs font-semibold text-slate-500">Searching dense vector indices and keyword filters...</p>
        </div>
      ) : jobs.length === 0 ? (
        <div className="py-16 text-center bg-white rounded-2xl border border-slate-200 p-8">
          <AlertCircle className="w-10 h-10 text-slate-400 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-800">No Jobs Found Matching Criteria</h3>
          <p className="text-xs text-slate-500 mt-1">Try broadening your search query or clearing policy filters.</p>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="text-xs font-semibold text-slate-500 px-1">
            Displaying {jobs.length} roles ranked by semantic relevance
          </div>

          <div className="grid grid-cols-1 gap-4">
            {jobs.map((job) => {
              const isSaved = savedJobIds.has(job.id);
              return (
                <div
                  key={job.id}
                  className="bg-white rounded-2xl border border-slate-200 p-5 sm:p-6 shadow-sm hover:border-slate-300 transition-all flex flex-col sm:flex-row justify-between gap-4"
                >
                  <div className="space-y-2 flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700">
                        {job.remote_policy}
                      </span>
                      <span className="text-xs font-semibold text-slate-500">
                        {job.experience_level}
                      </span>
                    </div>

                    <h2 className="text-lg font-bold text-slate-900">{job.title}</h2>
                    
                    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-600">
                      <span className="flex items-center space-x-1 font-medium">
                        <Building className="w-3.5 h-3.5 text-slate-400" />
                        <span>{job.company}</span>
                      </span>
                      <span className="flex items-center space-x-1">
                        <MapPin className="w-3.5 h-3.5 text-slate-400" />
                        <span>{job.location}</span>
                      </span>
                      <span className="flex items-center space-x-1 font-bold text-slate-800">
                        <DollarSign className="w-3.5 h-3.5 text-slate-400" />
                        <span>
                          {job.min_salary ? `$${(job.min_salary/1000).toFixed(0)}k - $${(job.max_salary!/1000).toFixed(0)}k` : 'Competitive'}
                        </span>
                      </span>
                    </div>

                    <p className="text-xs text-slate-600 leading-relaxed mt-2 line-clamp-3">
                      {job.description}
                    </p>

                    <div className="flex flex-wrap gap-1.5 pt-2">
                      {(job.skills || []).map((s) => (
                        <span key={s.id} className="px-2 py-0.5 rounded-md text-[11px] font-medium bg-slate-100 text-slate-700">
                          {s.skill_name}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="self-end sm:self-start">
                    <button
                      onClick={() => handleSaveJob(job.id, job.title)}
                      disabled={isSaved}
                      className={`flex items-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-semibold border transition-all ${
                        isSaved
                          ? 'bg-emerald-50 text-emerald-600 border-emerald-200'
                          : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
                      }`}
                    >
                      <Bookmark className={`w-3.5 h-3.5 ${isSaved ? 'fill-emerald-600' : ''}`} />
                      <span>{isSaved ? 'Saved' : 'Save'}</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
