import React, { useState, useRef, useEffect } from 'react';

function InputArea({ onSendMessage, isLoading, SendIcon }) {
  const [inputText, setInputText] = useState('');
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputText.trim() && !isLoading) {
      onSendMessage(inputText);
      setInputText('');
      textareaRef.current.style.height = 'auto'; // Reset height
    }
  };

  const handleInputChange = (e) => {
    setInputText(e.target.value);
    // Auto-ajustar altura del textarea
    textareaRef.current.style.height = 'auto';
    textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
  };
  
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  useEffect(() => {
    if (textareaRef.current) {
        textareaRef.current.style.height = '24px'; // Altura inicial
    }
  }, []);


  return (
    <div className="input-area-container">
      <form onSubmit={handleSubmit} className="input-form">
        <textarea
          ref={textareaRef}
          value={inputText}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder="Envía un mensaje..."
          rows="1"
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !inputText.trim()} className="send-button">
          {isLoading ? (
            <div className="spinner"></div>
          ) : (
            <SendIcon />
          )}
        </button>
      </form>
      <p className="footer-text">
        Esta IA puede cometer errores. Considera verificar la información importante.
      </p>
    </div>
  );
}

export default InputArea;