// src/About.js
import React, { useEffect, useRef } from "react";
import "./styles/About.css";

/**
 * About Page Component
 * Dedicated page for T.A.R.S information and features.
 */
const About = () => {
  const containerRef = useRef(null);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, []);

  return (
    <div ref={containerRef} className="about-container">
      {/* Hero Section */}
      <div className="about-hero">
        <div className="tars-logo">T</div>
        <h1 className="tars-title">T.A.R.S</h1>
        <p className="tars-subtitle">Tactically Advanced Responsive System</p>

        <div className="about-description">
          <p>
            Welcome to T.A.R.S, your AI-powered assistant. Inspired by futuristic
            holographic systems, this project demonstrates interactive spatial
            visualization using canvas, motion physics, and React. Explore the mesh,
            feel the gravity, and enter a new era of visual AI.
          </p>
        </div>
      </div>

      {/* Core Capabilities */}
      <div className="about-section">
        <h2 className="section-title">Core Capabilities</h2>
        <div className="features-grid">
          <FeatureCard
            icon="🎤"
            title="Voice Activation"
            description="Wake word detection powered by Porcupine. Just say 'Hey TARS' to activate your assistant."
          />
          <FeatureCard
            icon="💬"
            title="Natural Language"
            description="Advanced speech-to-text and text-to-speech capabilities for seamless human-AI interaction."
          />
          <FeatureCard
            icon="🧠"
            title="Intelligent Processing"
            description="Context-aware AI brain that understands and responds to your commands intelligently."
          />
          <FeatureCard
            icon="🌐"
            title="Web Integration"
            description="Real-time weather updates, web searches, and information retrieval at your command."
          />
          <FeatureCard
            icon="📸"
            title="Object Detection"
            description="Hands-free camera operations and visual processing capabilities."
          />
          <FeatureCard
            icon="✨"
            title="Holographic UI"
            description="Beautiful interactive particle system with physics-based motion and mouse interaction."
          />
        </div>
      </div>

      {/* Technology Stack */}
      <div className="about-section">
        <h2 className="section-title">Built With</h2>
        <div className="tech-stack">
          <TechBadge name="React" />
          <TechBadge name="Google Gemini" />
          <TechBadge name="Web Audio API" />
          <TechBadge name="Porcupine Wake Word" />
          <TechBadge name="Vosk STT" />
        </div>
      </div>

      {/* Call To Action */}
      <div className="about-cta">
        <p>Experience the future of AI interaction. Start chatting with T.A.R.S today.</p>
        <button onClick={() => (window.location.href = "/")} className="cta-button">
          Return to TARS
        </button>
      </div>
    </div>
  );
};

/* Reusable FeatureCard Component */
const FeatureCard = ({ icon, title, description }) => (
  <div className="feature-card">
    <div className="feature-icon">{icon}</div>
    <h3>{title}</h3>
    <p>{description}</p>
  </div>
);

/* Tech Badge Component */
const TechBadge = ({ name }) => (
  <div className="tech-badge">{name}</div>
);

export default About;
