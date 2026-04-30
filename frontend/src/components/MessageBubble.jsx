import React from 'react';
import { AlertTriangle, Ban, CheckCircle2, ShieldAlert, UserRound } from 'lucide-react';

const Badge = ({ decision }) => {
  if (decision === "ALLOW") {
    return <div className="mt-2 flex items-center gap-1.5 text-xs text-allow"><CheckCircle2 size={13} />ALLOW</div>;
  }
  if (decision === "WARN") {
    return <div className="mt-2 flex items-center gap-1.5 text-xs text-warn"><AlertTriangle size={13} />WARN - flagged as suspicious</div>;
  }
  if (decision === "BLOCK") {
    return <div className="mt-2 flex items-center gap-1.5 text-xs text-block"><Ban size={13} />BLOCK - message intercepted</div>;
  }
  return null;
};

export default function MessageBubble({ role, text, result }) {
  if (role === "user") {
    return (
      <div className="my-3 flex flex-col items-end">
        <div className="mb-1 flex items-center gap-1.5 text-xs text-text-muted">
          <span>User</span>
          <UserRound size={13} />
        </div>
        <div className="max-w-[58%] rounded-2xl rounded-tr-md border border-accent/20 bg-user-bubble px-4 py-3 text-sm leading-6 text-text-primary shadow-lg shadow-black/10 whitespace-pre-wrap">
          {text}
        </div>
        {result && <Badge decision={result.decision} />}
      </div>
    );
  }

  if (result?.decision === "BLOCK") {
    return (
      <div className="my-3 flex flex-col items-start">
        <div className="max-w-[78%] rounded-2xl rounded-tl-md border border-block/35 bg-block/10 px-4 py-3 text-sm leading-6 text-block shadow-lg shadow-black/10">
          <div className="flex items-center gap-2 font-semibold">
            <Ban size={16} />
            Message blocked
          </div>
          <div className="mt-1 text-block/85">This message was intercepted by the detection system.</div>
        </div>
      </div>
    );
  }

  return (
    <div className="my-3 flex flex-col items-start">
      <div className="max-w-[78%] rounded-2xl rounded-tl-md border border-panel-border bg-bot-bubble px-4 py-3 text-sm leading-6 text-text-primary shadow-lg shadow-black/10 whitespace-pre-wrap">
        {result?.decision === "WARN" && (
          <div className="mb-2 flex items-center gap-1.5 rounded-md border border-warn/20 bg-warn/10 px-2 py-1 text-xs text-warn">
            <ShieldAlert size={13} />
            Suspicious content detected
          </div>
        )}
        <div>{result?.llm_response || text}</div>
      </div>
    </div>
  );
}
