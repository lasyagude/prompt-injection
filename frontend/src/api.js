const BASE_URL = "http://localhost:8000"

export async function sendMessage(sessionId, message) {
  const res = await fetch(`${BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message })
  });
  return res.json();
}

export async function getStats(sessionId) {
  const res = await fetch(`${BASE_URL}/api/stats?session_id=${sessionId}`);
  return res.json();
}

export async function resetSession(sessionId) {
  const res = await fetch(`${BASE_URL}/api/session?session_id=${sessionId}`, {
    method: "DELETE"
  });
  return res.json();
}
