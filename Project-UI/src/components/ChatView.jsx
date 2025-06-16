import React, { useState, useRef, useEffect } from 'react';
import Message from './Message';

const ChatView = ({ messages, onSendMessage }) => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim()) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };

  return (
    <div className="chat-view">
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="empty-chat-container">
            <h1>ChatGPT Clone</h1>
            <p>Envía un mensaje para comenzar.</p>
          </div>
        ) : (
          messages.map((msg) => <Message key={msg.id} message={msg} />)
        )}
        <div ref={messagesEndRef} />
      </div>
      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Escribe un mensaje..."
        />
        <button type="submit">➢</button>
      </form>
    </div>
  );
};

export default ChatView;