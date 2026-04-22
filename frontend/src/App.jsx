import React from 'react';
import ChatPanel from './components/ChatPanel';
import RiskPanel from './components/RiskPanel';
import StatsPanel from './components/StatsPanel';
import { useSession } from './hooks/useSession';

function App() {
  const { messages, currentResult, stats, isLoading, sendMessage, resetSession } = useSession();

  return (
    <div className="flex w-full h-screen font-mono text-text-primary bg-terminal-bg">
      <div className="flex-grow flex flex-col h-full bg-terminal-bg relative">
        <div className="absolute top-0 left-0 right-0 h-16 border-b border-panel-border bg-panel-bg flex items-center px-6 z-10 w-full">
          <h1 className="text-xl font-bold uppercase tracking-widest text-[#cccccc] flex items-center gap-3">
            <span className="w-3 h-3 bg-block rounded inline-block animate-pulse"></span>
            Injection Detector
          </h1>
        </div>
        <ChatPanel 
          messages={messages} 
          isLoading={isLoading} 
          onSendMessage={sendMessage} 
        />
      </div>
      <RiskPanel result={currentResult} />
      <StatsPanel stats={stats} onReset={resetSession} />
    </div>
  );
}

export default App;
