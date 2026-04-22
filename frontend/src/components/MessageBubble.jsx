import React from 'react';

const Badge = ({ decision }) => {
  if (decision === "ALLOW") {
    return <div className="text-xs text-text-muted mt-1 flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-allow"></span>ALLOW</div>;
  }
  if (decision === "WARN") {
    return <div className="text-xs text-text-muted mt-1 flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-warn"></span>WARN — flagged as suspicious</div>;
  }
  if (decision === "BLOCK") {
    return <div className="text-xs text-text-muted mt-1 flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-block"></span>BLOCK — message intercepted</div>;
  }
  return null;
};

export default function MessageBubble({ role, text, result }) {
  if (role === "user") {
    return (
      <div className="flex flex-col items-end my-2">
        <div className="bg-user-bubble px-4 py-2 rounded max-w-[80%] border border-panel-border whitespace-pre-wrap">
          {text}
        </div>
        {result && <Badge decision={result.decision} />}
      </div>
    );
  }

  if (result?.decision === "BLOCK") {
    return (
      <div className="flex flex-col items-start my-2">
        <div className="bg-bot-bubble px-4 py-2 rounded max-w-[80%] border border-block text-block flex items-center gap-2">
          <span>🚫</span> Message Blocked — This message was intercepted by the detection system.
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-start my-2">
      <div className="bg-bot-bubble px-4 py-2 rounded max-w-[80%] border border-panel-border whitespace-pre-wrap flex flex-col gap-2">
        {result?.decision === "WARN" && (
          <div className="text-xs text-warn flex items-center gap-1 bg-warn/10 p-1 rounded">
            <span>⚠</span> Warning: suspicious content detected
          </div>
        )}
        <div>{result?.llm_response || text}</div>
      </div>
    </div>
  );
}
