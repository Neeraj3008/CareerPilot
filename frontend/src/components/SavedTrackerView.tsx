import React, { useEffect, useState } from 'react';
import { 
  Bookmark, Trash2, Building, MapPin, 
  DollarSign, ExternalLink, AlertCircle, Check 
} from 'lucide-react';
import { api } from '../services/api';
import { SavedJob } from '../types';

export const SavedTrackerView: React.FC = () => {
  const [savedJobs, setSavedJobs] = useState<SavedJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [updateMsg, setUpdateMsg] = useState<string | null>(null);

  const fetchSaved = async () => {
    setLoading(true);
    try {
      const data = await api.savedJobs.list();
      setSavedJobs(data);
    } catch (err) {
      console.error('Failed to load saved jobs', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSaved();
  }, []);

  const handleStatusChange = async (id: string, status: string) => {
    try {
      await api.savedJobs.update(id, status);
      setSavedJobs(prev => prev.map(j => j.id === id ? { ...j, status: status as any } : j));
      setUpdateMsg('Status updated');
      setTimeout(() => setUpdateMsg(null), 2000);
    } catch (err) {
      console.error('Failed to update status', err);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.savedJobs.delete(id);
      setSavedJobs(prev => prev.filter(j => j.id !== id));
    } catch (err) {
      console.error('Failed to delete saved job', err);
    }
  };

  const statusColors: Record<string, string> = {
    SAVED: 'bg-slate-100 text-slate-700',
    APPLIED: 'bg-blue-50 text-blue-700 border border-blue-200',
    INTERVIEWING: 'bg-purple-50 text-purple-700 border border-purple-200',
    OFFERED: 'bg-emerald-50 text-emerald-700 border border-emerald-200 font-bold',
    REJECTED: 'bg-rose-50 text-rose-700 border border-rose-200',
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <div className="flex items-center space-x-2">
          <h1 className="text-2xl font-extrabold text-slate-900">Application Pipeline Tracker</h1>
          <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-slate-100 text-slate-800">
            {savedJobs.length} Positions Tracked
          </span>
        </div>
        <p className="text-xs text-slate-500 mt-1">
          Organize your application lifecycle from saved opportunities to final offers.
        </p>
      </div>

      {updateMsg && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold rounded-xl flex items-center space-x-2 animate-fade-in">
          <Check className="w-4 h-4 text-emerald-600" />
          <span>{updateMsg}</span>
        </div>
      )}

      {loading ? (
        <div className="py-20 text-center">
          <div className="w-8 h-8 border-4 border-brand-200 border-t-brand-600 rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-xs font-semibold text-slate-500">Loading your saved positions...</p>
        </div>
      ) : savedJobs.length === 0 ? (
        <div className="py-16 text-center bg-white rounded-2xl border border-slate-200 p-8">
          <Bookmark className="w-10 h-10 text-slate-400 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-800">No Saved Jobs Yet</h3>
          <p className="text-xs text-slate-500 mt-1">
            Browse AI recommendations or search roles and click "Save" to build your pipeline.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {savedJobs.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm hover:border-slate-300 transition-all flex flex-col sm:flex-row justify-between gap-4 items-start sm:items-center"
            >
              <div className="space-y-1.5 flex-1">
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-bold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700">
                    {item.job.remote_policy}
                  </span>
                  <span className="text-xs text-slate-400">
                    Saved on {new Date(item.created_at).toLocaleDateString()}
                  </span>
                </div>
                <h3 className="text-base font-bold text-slate-900">{item.job.title}</h3>
                <div className="flex flex-wrap items-center gap-x-4 text-xs text-slate-600">
                  <span className="flex items-center space-x-1 font-medium">
                    <Building className="w-3.5 h-3.5 text-slate-400" />
                    <span>{item.job.company}</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    <span>{item.job.location}</span>
                  </span>
                  <span className="flex items-center space-x-1 font-bold text-slate-800">
                    <DollarSign className="w-3.5 h-3.5 text-slate-400" />
                    <span>
                      {item.job.min_salary 
                        ? `$${(item.job.min_salary/1000).toFixed(0)}k - $${(item.job.max_salary!/1000).toFixed(0)}k` 
                        : 'Competitive'}
                    </span>
                  </span>
                </div>
              </div>

              {/* Status Select & Delete */}
              <div className="flex items-center space-x-3 w-full sm:w-auto justify-between sm:justify-end border-t sm:border-t-0 pt-3 sm:pt-0 border-slate-100">
                <select
                  value={item.status}
                  onChange={(e) => handleStatusChange(item.id, e.target.value)}
                  className={`text-xs font-bold px-3 py-1.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 ${
                    statusColors[item.status] || 'bg-slate-100'
                  }`}
                >
                  <option value="SAVED">Saved</option>
                  <option value="APPLIED">Applied</option>
                  <option value="INTERVIEWING">Interviewing</option>
                  <option value="OFFERED">Offered 🎉</option>
                  <option value="REJECTED">Archived / Rejected</option>
                </select>

                <button
                  onClick={() => handleDelete(item.id)}
                  className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                  title="Remove from Tracker"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
