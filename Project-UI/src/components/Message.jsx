import React from 'react';

// Iconos simples para usuario y AI (puedes usar imágenes o SVGs más elaborados)
const UserIcon = () => <div className="avatar user-avatar">U</div>;
const AiIcon = () => <div className="avatar ai-avatar">R</div>; // R de Robot

function Message({ sender, text, isTyping }) {
  const isUser = sender === 'user';

  return (
    <div className={`message-wrapper ${isUser ? 'user' : 'ai'}`}>
      {!isUser && <AiIcon />}
      <div className={`message-bubble ${isUser ? 'user-bubble' : 'ai-bubble'} ${isTyping ? 'typing-bubble' : ''}`}>
        {isTyping ? (
          <div className="typing-indicator">
            <span></span><span></span><span></span>
          </div>
        ) : (
          text
        )}
      </div>
      {isUser && <UserIcon />}
    </div>
  );
}

export default Message;