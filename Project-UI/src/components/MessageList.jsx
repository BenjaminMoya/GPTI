import React, { useEffect, useRef } from 'react';
import Message from './Message';

function MessageList({ messages, isLoading }) {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]); // También cuando isLoading cambia para el "typing"

  return (
    <div className="message-list">
      {messages.map((msg) => (
        <Message key={msg.id} sender={msg.sender} text={msg.text} />
      ))}
      {isLoading && (
        <Message sender="ai" text="Escribiendo..." isTyping={true} />
      )}
      <div ref={messagesEndRef} />
    </div>
  );
}

export default MessageList;