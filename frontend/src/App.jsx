import React from 'react';
import ChatPanel from './components/ChatPanel';
import RiskPanel from './components/RiskPanel';
import StatsPanel from './components/StatsPanel';
import { useSession } from './hooks/useSession';
import { Activity, ShieldCheck } from 'lucide-react';

function App() {
  const { messages, currentResult, stats, isLoading, error, sendMessage, resetSession } = useSession();

  return (
    <div className="h-screen w-full overflow-hidden bg-terminal-bg text-text-primary">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_0%,rgba(56,216,198,0.13),transparent_30%),radial-gradient(circle_at_82%_12%,rgba(247,185,85,0.09),transparent_26%)]" />
      <div className="relative flex h-full w-full flex-col">
        <div className="flex h-16 shrink-0 items-center justify-between border-b border-panel-border bg-panel-bg/90 px-5 backdrop-blur">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-accent/35 bg-accent-soft text-accent">
              <ShieldCheck size={21} />
            </div>
            <div>
              <h1 className="text-base font-semibold tracking-wide text-text-primary sm:text-lg">
                Sentinel Prompt Injection Middleware
              </h1>
              <div className="mt-0.5 flex items-center gap-2 text-xs text-text-muted">
                <Activity size={13} className="text-accent" />
                Live detection engine
              </div>
            </div>
          </div>
          <div className="hidden items-center gap-2 rounded-full border border-panel-border bg-panel-soft px-3 py-1.5 text-xs text-text-muted md:flex">
            <span className="h-2 w-2 rounded-full bg-allow shadow-[0_0_12px_rgba(66,232,159,0.75)]" />
            Research demo
          </div>
        </div>

        <div className="grid min-h-0 flex-1 grid-cols-1 lg:grid-cols-[minmax(0,1fr)_340px] xl:grid-cols-[minmax(0,1fr)_340px_260px]">
          <ChatPanel
            messages={messages}
            isLoading={isLoading}
            error={error}
            onSendMessage={sendMessage}
          />
          <RiskPanel result={currentResult} />
          <StatsPanel stats={stats} onReset={resetSession} />
        </div>
      </div>
    </div>
  );
}

export default App;
