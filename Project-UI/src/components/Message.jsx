import React from 'react';

const Message = ({ message }) => {
  const { sender, text } = message;
  const isAI = sender === 'ai';

  return (
    <div className={`message-wrapper ${isAI ? 'ai' : 'user'}`}>
        <div className={`message-container ${isAI ? 'ai' : 'user'}`}>
            <div className="message-avatar">
                {isAI ? '✨' : '👤'}
            </div>
            <div className="message-text">
                {text}
            </div>
        </div>
    </div>
  );
};

export default Message;