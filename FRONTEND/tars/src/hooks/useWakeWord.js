import { useEffect, useState } from "react";

export default function useWakeWord() {
  const [isListening, setIsListening] = useState(false);
  const [detected, setDetected] = useState(false);

  useEffect(() => {
    // Start backend listening once UI loads
    const startListening = async () => {
      try {
        await fetch("http://localhost:8081/wakeword/start", { method: "POST" });
        setIsListening(true);
      } catch (e) {
        console.error("Failed to start wake-word:", e);
      }
    };

    startListening();

    // Poll every 1.5 s
    const poll = setInterval(async () => {
      try {
        const res = await fetch("http://localhost:8081/wakeword/status");
        const data = await res.json();
        if (data.detected) {
          setDetected(true);
          // reset after few seconds
          setTimeout(() => setDetected(false), 4000);
        }
      } catch (e) {
        console.error("Polling error:", e);
      }
    }, 1500);

    return () => clearInterval(poll);
  }, []);

  return { isListening, detected };
}
