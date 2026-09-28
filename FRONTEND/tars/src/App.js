// src/App.js
import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useLocation
} from "react-router-dom";

import Navigation from "./Navigation";
import HolographicDots from "./Design/HolographicDots";
import About from "./About";
import ChatDock from "./ChatDock";

import useWakeWord from "./hooks/useWakeWord";
import useSpeechActivity from "./hooks/speechActivity";
import useVision from "./hooks/useVision";
import CameraPanel from "./hooks/CameraPanel";

import "./App.css";


// =====================================================
// App Component (Router Wrapper)
// =====================================================
function App() {
  const [showChat, setShowChat] = useState(false);
  const toggleChat = () => setShowChat((prev) => !prev);

  // Vision state mirrors backend SSE stream
  const [visionState, setVisionState] = useState({
    active: false,
    source: null
  });

  // Subscribe to /vision/state SSE stream
  useEffect(() => {
    const evt = new EventSource("http://localhost:8081/vision/state");

    evt.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        setVisionState(data);
      } catch (err) {
        console.error("Vision SSE decode error:", err);
      }
    };

    return () => evt.close();
  }, []);

  return (
    <Router>
      <AppContent
        showChat={showChat}
        toggleChat={toggleChat}
        visionState={visionState}
      />
    </Router>
  );
}


// =====================================================
// Inner App Content (Uses hooks + routes)
// =====================================================
function AppContent({ showChat, toggleChat, visionState }) {
  const location = useLocation();

  const { detected } = useWakeWord();
  const { tarsState } = useSpeechActivity();
  const vision = useVision();

  // Disable scroll on home page
  useEffect(() => {
    document.body.style.overflow = location.pathname === "/" ? "hidden" : "auto";
  }, [location.pathname]);

  useEffect(() => {
    if (visionState.active && visionState.source === "mac") {
      vision.openCamera();  // safe guarded
    }

    if (!visionState.active) {
      vision.closeCamera();
    }
  }, [visionState.active, visionState.source]);


  return (
    <>
      <Navigation
        onChatToggle={toggleChat}
        isChatOpen={showChat}
        wakeWordDetected={detected}
      />

      <Routes>
        {/* ================================== */}
        {/* HOME PAGE */}
        {/* ================================== */}
        <Route
          path="/"
          element={
            <>
              <HolographicDots tarsState={tarsState} />
              <ChatDock open={showChat} onClose={toggleChat} />

              {/* Vision Control Panel (UI inside corner) */}
              <CameraPanel {...vision} />

            </>
          }
        />

        {/* ================================== */}
        {/* ABOUT PAGE */}
        {/* ================================== */}
        <Route path="/about" element={<About />} />
      </Routes>
    </>
  );
}

export default App;
