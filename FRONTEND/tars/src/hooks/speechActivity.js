// src/hooks/speechActivity.js
import { useState, useEffect } from "react";

export default function useSpeechActivity() {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isThinking, setIsThinking] = useState(false);

  useEffect(() => {
    let evtSource = new EventSource("http://localhost:8081/voice/activity", {
      withCredentials: false,
    });

    evtSource.onmessage = (e) => {
      const data = JSON.parse(e.data);
      setIsSpeaking(data.speaking);
      setIsThinking(data.thinking);
    };

    // IMPORTANT: reconnect if SSE drops
    evtSource.onerror = () => {
      console.warn("SSE connection lost — reconnecting...");
      evtSource.close();
      evtSource = new EventSource("http://localhost:8081/voice/activity");
    };

    return () => evtSource.close();
  }, []);

  const tarsState =
    isThinking ? "thinking" :
    isSpeaking ? "speaking" :
    "idle";

  return { isSpeaking, isThinking, tarsState };
}
