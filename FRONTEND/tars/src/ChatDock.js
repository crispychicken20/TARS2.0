import React from "react";
import ChatPanel from "./ChatPanel";

const ChatDock = ({ open, onClose }) => {
  return (
    <div className={`chat-dock ${open ? "open" : ""}`} aria-hidden={!open}>
      <div className="chat-dock__titlebar">
        <span>  </span>
        <button className="chat-dock__close" onClick={onClose} aria-label="Close chat">×</button>
      </div>

      <div className="chat-dock__body">
        <ChatPanel
          containerStyle={{
            marginTop: 0,
            maxWidth: "100%",
            borderRadius: 16,
            height: "5%",
          }}
        />
      </div>
    </div>
  );
};

export default ChatDock;