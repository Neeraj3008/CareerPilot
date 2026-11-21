import React, { useEffect, useState } from 'react';
import { 
  Sparkles, Check, Bookmark, ChevronDown, ChevronUp, 
  MapPin, DollarSign, Building, AlertCircle, RefreshCw 
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { Recommendation } from '../types';

export const RecommendationsView: React.FC = () => {
  const { user } = useAuth();
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [savedJobIds, setSavedJobIds] = useState<Set<string>>(new Set());
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const recs = await api.recommendations.list(15);
      setRecommendations(recs);

      // Fetch saved jobs to mark button state
      const saved = await api.savedJobs.list();
      setSavedJobIds(new Set(saved.map(s => s.job_id)));
    } catch (err) {
      console.error('Failed to load recommendations', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, [user]);

  const handleSaveJob = async (jobId: string, title: string) => {
    try {
      await api.savedJobs.save(jobId);
      setSavedJobIds(prev => new Set(prev).add(jobId));
      setSaveSuccessMsg(`Saved "${title}" to your job tracker.`);
      setTimeout(() => setSaveSuccessMsg(null), 3000);
    } catch (err) {
      console.error('Failed to save job', err);
    }
  };

  const toggleExpand = (id: string) => {
    setExpandedId(prev => prev === id ? null : id);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Title & Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-extrabold text-slate-900">Deterministic Job Recommendations</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-brand-100 text-brand-800">
              Verified Math
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Scores are deterministically ranked based on skill overlap, vector cosine similarity, role alignment, and location.
          </p>
        </div>

        <button
          onClick={fetchRecommendations}
          disabled={loading}
          className="inline-flex items-center space-x-2 px-3.5 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-300 rounded-xl hover:bg-slate-50 transition-colors shadow-sm"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Recalculate Matches</span>
        </button>
      </div>

      {saveSuccessMsg && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold rounded-xl flex items-center space-x-2 animate-fade-in">
          <Check className="w-4 h-4 text-emerald-600" />
          <span>{saveSuccessMsg}</span>
        </div>
      )}

      {loading ? (
        <div className="py-20 text-center">
          <div className="w-10 h-10 border-4 border-brand-200 border-t-brand-600 rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-sm font-semibold text-slate-600">Calculating deterministic matches across vector embeddings...</p>
        </div>
      ) : recommendations.length === 0 ? (
        <div className="py-16 text-center bg-white rounded-2xl border border-slate-200 p-8">
          <AlertCircle className="w-10 h-10 text-slate-400 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-800">No Recommendations Available Yet</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            Upload your resume or add your technical skills in the profile tab to generate personalized job matches.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {recommendations.map((rec) => {
            const isExpanded = expandedId === rec.id;
            const isSaved = savedJobIds.has(rec.job.id);
            const scoreColor = rec.match_score >= 80 
              ? 'bg-emerald-50 text-emerald-700 border-emerald-300' 
              : rec.match_score >= 60 
              ? 'bg-brand-50 text-brand-700 border-brand-300' 
              : 'bg-amber-50 text-amber-700 border-amber-300';

            return (
              <div 
                key={rec.id}
                className="bg-white rounded-2xl border border-slate-200 shadow-sm hover:border-slate-300 transition-all overflow-hidden"
              >
                {/* Main Card Header */}
                <div className="p-5 sm:p-6">
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                    <div className="space-y-1.5 flex-1">
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-bold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700">
                          {rec.job.remote_policy}
                        </span>
                        <span className="text-xs font-semibold text-slate-500">
                          {rec.job.experience_level} LEVEL
                        </span>
                      </div>
                      <h2 className="text-lg font-bold text-slate-900">{rec.job.title}</h2>
                      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-600 pt-0.5">
                        <span className="flex items-center space-x-1 font-medium">
                          <Building className="w-3.5 h-3.5 text-slate-400" />
                          <span>{rec.job.company}</span>
                        </span>
                        <span className="flex items-center space-x-1">
                          <MapPin className="w-3.5 h-3.5 text-slate-400" />
                          <span>{rec.job.location}</span>
                        </span>
                        <span className="flex items-center space-x-1 font-bold text-slate-800">
                          <DollarSign className="w-3.5 h-3.5 text-slate-400" />
                          <span>
                            {rec.job.min_salary 
                              ? `$${(rec.job.min_salary/1000).toFixed(0)}k - $${(rec.job.max_salary!/1000).toFixed(0)}k` 
                              : 'Competitive'}
                          </span>
                        </span>
                      </div>
                    </div>

                    {/* Match Score Badge */}
                    <div className="flex items-center space-x-3 self-start sm:self-auto">
                      <div className={`px-4 py-2 rounded-xl border text-center ${scoreColor}`}>
                        <div className="text-2xl font-black leading-none">{rec.match_score}%</div>
                        <div className="text-[10px] font-bold uppercase tracking-wider mt-0.5">Match Caliber</div>
                      </div>

                      <button
                        onClick={() => handleSaveJob(rec.job.id, rec.job.title)}
                        disabled={isSaved}
                        className={`p-3 rounded-xl border transition-all ${
                          isSaved 
                            ? 'bg-emerald-50 text-emerald-600 border-emerald-200' 
                            : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50 hover:text-brand-600'
                        }`}
                        title={isSaved ? "Saved" : "Save to Tracker"}
                      >
                        <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-emerald-600' : ''}`} />
                      </button>
                    </div>
                  </div>

                  {/* Skills Matching Strip */}
                  <div className="mt-4 pt-4 border-t border-slate-100 flex flex-wrap items-center gap-1.5">
                    <span className="text-xs font-semibold text-slate-500 mr-1">Matched Skills:</span>
                    {rec.matching_skills.length > 0 ? (
                      rec.matching_skills.map((s, idx) => (
                        <span key={idx} className="px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                          ✓ {s}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-slate-400">None explicitly matched</span>
                    )}

                    {rec.missing_skills.length > 0 && (
                      <>
                        <span className="text-xs font-semibold text-slate-400 ml-2 mr-1">To Acquire:</span>
                        {rec.missing_skills.slice(0, 3).map((s, idx) => (
                          <span key={idx} className="px-2 py-0.5 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">
                            + {s}
                          </span>
                        ))}
                      </>
                    )}
                  </div>
                </div>

                {/* Score Breakdown Toggle */}
                <div 
                  onClick={() => toggleExpand(rec.id)}
                  className="bg-slate-50 px-6 py-2.5 border-t border-slate-100 flex items-center justify-between cursor-pointer hover:bg-slate-100 transition-colors"
                >
                  <span className="text-xs font-semibold text-slate-700 flex items-center space-x-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-brand-600" />
                    <span>Explainable Match Breakdown & Details</span>
                  </span>
                  {isExpanded ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
                </div>

                {/* Expanded Detailed Breakdown */}
                {isExpanded && (
                  <div className="p-6 bg-slate-50/70 border-t border-slate-100 space-y-4 animate-fade-in">
                    <div>
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">Role Description</h4>
                      <p className="text-xs text-slate-700 leading-relaxed whitespace-pre-line bg-white p-4 rounded-xl border border-slate-200">
                        {rec.job.description}
                      </p>
                    </div>

                    <div>
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">Mathematical Scoring Matrix</h4>
                      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                        <div className="bg-white p-3 rounded-xl border border-slate-200 text-center">
                          <p className="text-[11px] font-semibold text-slate-500">Skill Overlap (35%)</p>
                          <p className="text-lg font-bold text-slate-900 mt-1">{rec.score_breakdown.skill_overlap_score}%</p>
                        </div>
                        <div className="bg-white p-3 rounded-xl border border-slate-200 text-center">
                          <p className="text-[11px] font-semibold text-slate-500">Semantic Cosine (30%)</p>
                          <p className="text-lg font-bold text-slate-900 mt-1">{rec.score_breakdown.semantic_score}%</p>
                        </div>
                        <div className="bg-white p-3 rounded-xl border border-slate-200 text-center">
                          <p className="text-[11px] font-semibold text-slate-500">Role Alignment (15%)</p>
                          <p className="text-lg font-bold text-slate-900 mt-1">{rec.score_breakdown.role_score}%</p>
                        </div>
                        <div className="bg-white p-3 rounded-xl border border-slate-200 text-center">
                          <p className="text-[11px] font-semibold text-slate-500">Location (10%)</p>
                          <p className="text-lg font-bold text-slate-900 mt-1">{rec.score_breakdown.location_score}%</p>
                        </div>
                        <div className="bg-white p-3 rounded-xl border border-slate-200 text-center">
                          <p className="text-[11px] font-semibold text-slate-500">Compensation (10%)</p>
                          <p className="text-lg font-bold text-slate-900 mt-1">{rec.score_breakdown.preference_score}%</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
