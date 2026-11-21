import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { DashboardView } from './components/DashboardView';
import { RecommendationsView } from './components/RecommendationsView';
import { SearchView } from './components/SearchView';
import { ChatView } from './components/ChatView';
import { ResumeProfileView } from './components/ResumeProfileView';
import { SavedTrackerView } from './components/SavedTrackerView';
import { AuthModal } from './components/AuthModal';

const MainContent: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const { user } = useAuth();

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
      <Navbar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        onOpenAuth={() => setIsAuthOpen(true)} 
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {activeTab === 'dashboard' && (
          <DashboardView 
            setActiveTab={setActiveTab} 
            onOpenAuth={() => setIsAuthOpen(true)} 
          />
        )}
        {activeTab === 'recommendations' && <RecommendationsView />}
        {activeTab === 'search' && <SearchView />}
        {activeTab === 'chat' && <ChatView />}
        {activeTab === 'resume' && <ResumeProfileView />}
        {activeTab === 'tracker' && <SavedTrackerView />}
      </main>

      <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500">
        <p className="font-semibold text-slate-700">CareerPilot — Production-Oriented AI Job Search & Career Agent</p>
        <p className="mt-1">
          FastAPI • PostgreSQL • pgvector • Gemini LLM Tools • React • TypeScript • Tailwind CSS
        </p>
      </footer>

      <AuthModal isOpen={isAuthOpen} onClose={() => setIsAuthOpen(false)} />
    </div>
  );
};

export function App() {
  return (
    <AuthProvider>
      <MainContent />
    </AuthProvider>
  );
}

export default App;
