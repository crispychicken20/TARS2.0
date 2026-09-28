// src/hooks/useVision.js
import { useState, useRef, useCallback } from "react";

export default function useVision() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [lastResult, setLastResult] = useState("");
  const [error, setError] = useState("");

  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const openingRef = useRef(false);

  // -----------------------------------------------------
  // SAFE CAMERA OPEN (no “operation was aborted” errors)
  // -----------------------------------------------------
  const openCamera = useCallback(async () => {
    try {
      console.log("Opening camera (simple mode)…");

      // Request MacBook front camera
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user" },
        audio: false
      });

      const video = videoRef.current;
      if (!video) return;

      video.srcObject = stream;
      video.muted = true;
      video.playsInline = true; // iOS + macOS fix
      video.autoplay = true;

      await video.play();

      streamRef.current = stream;
      setIsOpen(true);
    } catch (err) {
      console.error("Simple camera open FAILED:", err);
      setError("Cannot access camera.");
    }
  }, []);


  // -----------------------------------------------------
  // STOP STREAM SAFELY
  // -----------------------------------------------------
  const stopStream = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
  }, []);

  // -----------------------------------------------------
  // CLOSE CAMERA
  // -----------------------------------------------------
  const closeCamera = useCallback(() => {
    stopStream();
    setIsOpen(false);
    setIsMinimized(false);
    setIsAnalyzing(false);
    setLastResult("");
    setError("");
  }, [stopStream]);

  // -----------------------------------------------------
  // MINIMIZE
  // -----------------------------------------------------
  const toggleMinimize = useCallback(() => {
    setIsMinimized((prev) => !prev);
  }, []);

  // -----------------------------------------------------
  // CAPTURE + ANALYZE (unchanged logic)
  // -----------------------------------------------------
  const captureAndAnalyze = useCallback(async () => {
    if (!videoRef.current) return;
    try {
      setIsAnalyzing(true);
      setError("");

      const video = videoRef.current;
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 480;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      const blob = await new Promise((resolve) =>
        canvas.toBlob(resolve, "image/jpeg", 0.9)
      );

      const formData = new FormData();
      formData.append("file", blob, "frame.jpg");

      const visionRes = await fetch("http://localhost:8081/vision/analyze", {
        method: "POST",
        body: formData,
      });
      const json = await visionRes.json();

      if (json.error) {
        setError(json.error);
        setIsAnalyzing(false);
        return;
      }

      const desc = json.vision_result || "I see something but it's unclear.";
      setLastResult(desc);

      await fetch("http://localhost:8081/voice/tts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: `From the camera, I see: ${desc}` }),
      });

      setIsAnalyzing(false);
    } catch (err) {
      console.error("Vision error:", err);
      setError("Vision analysis failed.");
      setIsAnalyzing(false);
    }
  }, []);

  return {
    isOpen,
    isMinimized,
    isAnalyzing,
    lastResult,
    error,
    visionActive: isOpen && !isMinimized,
    videoRef,

    openCamera,
    closeCamera,
    toggleMinimize,
    captureAndAnalyze,
  };
}
