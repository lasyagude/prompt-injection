import { useState } from 'react';
import * as api from '../api';

export function useSession() {
  const [sessionId, setSessionId] = useState(() => crypto.randomUUID());
  const [messages, setMessages] = useState([]);
  const [currentResult, setCurrentResult] = useState(null);
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const sendMessage = async (text) => {
    setIsLoading(true);
    setError("");
    setMessages((prev) => [...prev, { role: "user", text }]);
    
    try {
      const result = await api.sendMessage(sessionId, text);
      if (!result || result.detail) {
        throw new Error(result?.detail || "The detector API returned an unexpected response.");
      }
      
      setMessages((prev) => {
        const newMsgs = [...prev];
        if (newMsgs.length > 0 && newMsgs[newMsgs.length - 1].role === "user") {
          newMsgs[newMsgs.length - 1].result = result;
        }
        return [...newMsgs, { role: "assistant", result }];
      });
      
      setCurrentResult(result);
      
      const newStats = await api.getStats(sessionId);
      setStats(newStats);
    } catch (error) {
      console.error("Failed to send message:", error);
      setError(error.message || "Unable to reach the detection API.");
    } finally {
      setIsLoading(false);
    }
  };

  const resetSession = async () => {
    try {
      await api.resetSession(sessionId);
    } catch (e) {
      console.error("Reset failed", e);
    }
    setSessionId(crypto.randomUUID());
    setMessages([]);
    setCurrentResult(null);
    setStats(null);
    setError("");
  };

  return { messages, currentResult, stats, isLoading, error, sendMessage, resetSession };
}
