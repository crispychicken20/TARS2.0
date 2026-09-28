// src/ChatPanel.js
import React, { useState, useEffect, useRef } from "react";
import "./styles/ChatPanel.css";

function ChatPanel({ containerStyle = {} }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  const sendMessage = () => {
    if (!input.trim()) return;

    const newMessage = {
      sender: "You",
      text: input,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };
    setMessages([...messages, newMessage]);
    setInput("");

    // Simulated TARS response
    setTimeout(() => {
      const tarsResponse = {
        sender: "TARS",
        text: "I'm TARS, your AI assistant. How can I help you today?",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, tarsResponse]);
    }, 1000);
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="chat-container" style={containerStyle}>
      {/* Header */}
      <div className="chat-header">
        <div className="chat-logo">T</div>
        <h2 className="chat-title">TARS Chat</h2>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`chat-message ${msg.sender === "You" ? "user" : "tars"}`}
          >
            <div className="chat-bubble">{msg.text}</div>
            <div className="chat-meta">
              {msg.sender} • {msg.timestamp}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="chat-input-section">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Type your message..."
          className="chat-input"
        />
        <button onClick={sendMessage} className="chat-send">
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatPanel;
