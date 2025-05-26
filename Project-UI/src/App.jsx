import React, { useState, useEffect, useRef } from 'react';
import MessageList from './components/MessageList';
import InputArea from './components/InputArea';
import './App.css';

// Icono simple de "Enviar" (puedes usar una librería de iconos como react-icons)
const SendIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path>
  </svg>
);

function App() {
  const [messages, setMessages] = useState([
    { id: 1, text: 'Hola, ¿en qué puedo ayudarte hoy?', sender: 'ai' },
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (inputText) => {
    if (!inputText.trim()) return;

    const newUserMessage = {
      id: Date.now(),
      text: inputText,
      sender: 'user',
    };
    setMessages((prevMessages) => [...prevMessages, newUserMessage]);
    setIsLoading(true);

    // Simular respuesta de la IA
    setTimeout(() => {
      const aiResponse = `Esta es una respuesta simulada para: "${inputText}".`;
      const newAiMessage = {
        id: Date.now() + 1, // Asegurar ID único
        text: aiResponse,
        sender: 'ai',
      };
      setMessages((prevMessages) => [...prevMessages, newAiMessage]);
      setIsLoading(false);
    }, 1500 + Math.random() * 1000); // Retraso aleatorio para simular procesamiento
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Cientifico IA</h1>
        {/* Aquí podrías añadir un botón de "Nuevo Chat" etc. */}
      </header>
      <div className="chat-area">
        <MessageList messages={messages} isLoading={isLoading} />
      </div>
      <InputArea onSendMessage={handleSendMessage} isLoading={isLoading} SendIcon={SendIcon} />
    </div>
  );
}

export default App;
