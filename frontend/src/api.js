const BASE_URL = "http://localhost:8000"

export async function sendMessage(sessionId, message) {
  const res = await fetch(`${BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message })
  });
  if (!res.ok) {
    throw new Error(`Detection API error (${res.status})`);
  }
  return res.json();
}

export async function getStats(sessionId) {
  const res = await fetch(`${BASE_URL}/api/stats?session_id=${sessionId}`);
  if (!res.ok) {
    throw new Error(`Stats API error (${res.status})`);
  }
  return res.json();
}

export async function resetSession(sessionId) {
  const res = await fetch(`${BASE_URL}/api/session?session_id=${sessionId}`, {
    method: "DELETE"
  });
  if (!res.ok) {
    throw new Error(`Reset API error (${res.status})`);
  }
  return res.json();
}
