// src/CameraPanel.js
import React from "react";
import "../styles/CameraPanel.css";

const CameraPanel = ({
  isOpen,
  isMinimized,
  isAnalyzing,
  lastResult,
  error,
  videoRef,
  openCamera,
  closeCamera,
  toggleMinimize,
  captureAndAnalyze,
}) => {
  if (!isOpen) return null;

  return (
    <div className={`camera-panel ${isMinimized ? "camera-panel--minimized" : ""}`}>
      <div className="camera-panel__header">
        <span className="camera-panel__title">TARS VISION</span>
        <div className="camera-panel__actions">
          <button onClick={toggleMinimize}> {isMinimized ? "▢" : "–"} </button>
          <button onClick={closeCamera}>✕</button>
        </div>
      </div>

      {!isMinimized && (
        <div className="camera-panel__body">
          <video
            ref={videoRef}
            className="camera-panel__video"
            autoPlay
            muted
            playsInline
          />


          <div className="camera-panel__controls">
            <button onClick={captureAndAnalyze} disabled={isAnalyzing}>
              {isAnalyzing ? "Analyzing…" : "Analyze Frame"}
            </button>
          </div>

          <div className="camera-panel__info">
            {error && <div className="camera-panel__error">{error}</div>}
            {lastResult && !error && (
              <div className="camera-panel__result">
                <span className="label">TARS sees:</span> {lastResult}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default React.memo(CameraPanel); 
