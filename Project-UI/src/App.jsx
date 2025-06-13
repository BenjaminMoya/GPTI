import React, { useState, useEffect, useRef } from 'react';
import MessageList from './components/MessageList';
import InputArea from './components/InputArea';
import generateReport from "./services/CientificAPI"; // Asegúrate de que esta ruta sea correcta
import latexReport from "./services/CientificAPI";
import './App.css';

// Icono simple de "Enviar" 
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
  
  const newJson = {
  "pregunta_investigacion": "¿Cómo afecta la regularización L2 al rendimiento de redes neuronales?",
  "info_papers": [
    {
      "titulo": "L2 Regularization in Deep Learning",
      "autores": ["Smith J.", "Lee A."],
      "resumen": "This paper explores the role of L2",
      "año": 2021,
      "doi": "10.1234/arxiv.2301.00001",
      "fuente": "ArXiv"
    }
  ],
  "formulacion_hipotesis": [
    {
      "hipotesis": "Si se aplica regularización L2 en redes CNN con datasets pequeños, entonces se reduce el sobreajuste del modelo",
      "justificacion": "Basado en estudios previos que muestran correlación entre L2 y estabilidad del entrenamiento",
      "formato": "IF-THEN"
    }
  ],
  "experimentacion": {
    "modelo": "CNN",
    "dataset": "CIFAR-10",
    "condiciones": {
      "regularizacion": "L2",
      "epochs": 20,
      "metricas": ["accuracy", "val_loss"]
    },
    "repeticiones": 3,
    "formato": "python script o notebook"
  },
  "analisis_datos": {
    "resumen": "Los modelos con L2 regularization mostraron menor varianza y menor pérdida promedio que los modelos sin regularización",
    "graficos_generados": ["grafico_comparacion_loss.png", "boxplot_accuracy.png"],
    "estadisticas": {
      "loss_promedio_con_L2": 0.21,
      "loss_promedio_sin_L2": 0.34,
      "p_valor": 0.02
    }
  }
  }

  const newUserMessage = {
    id: Date.now(),
    text: inputText,
    sender: 'user',
  };
  setMessages((prevMessages) => [...prevMessages, newUserMessage]);
  setIsLoading(true);

  try {
    // Llamada real a la API
    const response = await generateReport(newJson);

    const newAiMessage = {
      id: Date.now() + 1,
      text: "Respuesta en consola"|| "No se recibió respuesta válida de la IA.",
      sender: 'ai',
    };
    console.log("Respuesta de la IA:", response.data); // Para depuración
    setMessages((prevMessages) => [...prevMessages, newAiMessage]);

    try{
      const response2 = await latexReport(response.data.cuerpo_texto);

      const newAiMessage = {
        id: Date.now() + 1,
        text: "Generado el pdf"|| "No se recibió respuesta válida de la IA.",
        sender: 'ai',
      };
      console.log("Respuesta de la IA:", response2.data); // Para depuración
      setMessages((prevMessages) => [...prevMessages, newAiMessage]);

      
    }catch (error) {
      const errorMessage = {
      id: Date.now() + 1,
      text: `Error al generar respuesta: ${error.message}`,
      sender: 'ai',
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  } catch (error) {
    const errorMessage = {
      id: Date.now() + 1,
      text: `Error al generar respuesta: ${error.message}`,
      sender: 'ai',
    };
    setMessages((prevMessages) => [...prevMessages, errorMessage]);
  } finally {
    setIsLoading(false);
  }
};

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Cientifico IA</h1>
        {/* Aquí iran nuevos botones o cuadros de dialogo */}
      </header>
      <div className="chat-area">
        <MessageList messages={messages} isLoading={isLoading} />
      </div>
      <InputArea onSendMessage={handleSendMessage} isLoading={isLoading} SendIcon={SendIcon} />
    </div>
  );
}

export default App;
