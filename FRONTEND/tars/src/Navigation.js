import React from "react";
import { Link } from "react-router-dom";
import "./styles/Navigation.css";

/**
 * Navigation Component
 * --------------------
 * Fixed top bar with:
 * - TARS brand on the left
 * - Voice hint in the center
 * - Chat toggle + About on the right
 */
const Navigation = ({ onChatToggle, isChatOpen = false, wakeWordDetected = false }) => {
  return (
    <nav className="nav-bar">
      {/* LEFT: Brand */}
      <Link to="/" className="nav-brand">
        <span>T.A.R.S</span>
      </Link>

      {/* CENTER: Voice Activation Hint */}
      <div className={`voice-hint ${wakeWordDetected ? "active" : ""}`}>
        <svg
          className="mic-icon"
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
          <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
          <line x1="12" y1="19" x2="12" y2="23" />
          <line x1="8" y1="23" x2="16" y2="23" />
        </svg>
        <span>{wakeWordDetected ? " Listening..." : 'Say "Hey TARS"'}</span>
      </div>

      {/* RIGHT: About + Chat Toggle */}
      <div className="nav-right">
        <Link to="/about" className="nav-link">
          About
        </Link>

        <button
          onClick={onChatToggle}
          className={`chat-toggle ${isChatOpen ? "active" : ""}`}
          aria-label={isChatOpen ? "Close chat panel" : "Open chat panel"}
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
          <span>{isChatOpen ? "Close Chat" : "Chat"}</span>
        </button>
      </div>
    </nav>
  );
};

export default Navigation;
