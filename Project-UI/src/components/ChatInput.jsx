import React, { useState, useEffect } from 'react';
import styles from '../styles/ChatInput.module.css';
import { FiSend } from 'react-icons/fi';

function ChatInput({ input, setInput, onSend }) {
  const [placeholderIndex, setPlaceholderIndex] = useState(0);

  const prompts = [
    "Enter a prompt here",
    "¿How does the use of machine learning algorithms impact the efficiency of analyzing large volumes of data?",
    "¿What are the effects of using functional programming languages on error detection in critical systems?",
    "¿How quantum computing could transform modern cryptography?",
    "¿What impact does algorithm optimization have on data center energy consumption?"
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setPlaceholderIndex((prev) => (prev + 1) % prompts.length);
    }, 7500); // cambia cada 5 segundos

    return () => clearInterval(interval);
  }, []);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
    }
  };

  return (
    <div className={styles.chatInputContainer}>
      <div className={styles.inputWrapper}>
        <textarea
          placeholder={prompts[placeholderIndex]}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows="1"
        />
        <button onClick={onSend} className={styles.sendButton}>
          <FiSend size={20} />
        </button>
      </div>
      <p className={styles.disclaimer}>
        Cientific AI may display inaccurate info, including about people, so double-check its responses.
      </p>
    </div>
  );
}

export default ChatInput;
