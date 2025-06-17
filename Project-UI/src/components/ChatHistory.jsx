import React, { useRef, useEffect } from 'react';
import styles from '../styles/ChatHistory.module.css';
import { FaUserCircle } from 'react-icons/fa';
import { DiGoogleCloudPlatform } from 'react-icons/di';

function ChatHistory({ messages }) {
  const endOfMessagesRef = useRef(null);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className={styles.chatHistory}>
      {messages.map((msg, index) => (
        <div key={index} className={`${styles.message} ${styles[msg.sender]}`}>
          <div className={styles.avatar}>
            {msg.sender === 'user' ? <FaUserCircle size={28} /> : <DiGoogleCloudPlatform size={28} color="#8ab4f8" />}
          </div>
          <div className={styles.content}>
            <p>{msg.text}</p>
          </div>
        </div>
      ))}
      <div ref={endOfMessagesRef} />
    </div>
  );
}

export default ChatHistory;