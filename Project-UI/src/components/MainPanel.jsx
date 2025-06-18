import React, { useState, useEffect} from 'react';
import styles from '../styles/MainPanel.module.css';
import ChatHistory from './ChatHistory';
import ChatInput from './ChatInput';
import generateReport from '../services/CientificAPI';
import latexReport from '../services/CientificAPI';

function MainPanel({ promptHistory, setPromptHistory }) {
  const [initial, setInitial] = useState("Hello! I am an expert assistant in scientific writing in LaTeX. The more specific your instructions, the better results you can achieve!");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [firstPrompt, setFirstPrompt] = useState('');
  const [lenguage, setLenguage] = useState(JSON.parse(sessionStorage.getItem('lenguage')));
  
  useEffect(() => {
    if (lenguage === 'Spanish') {
      setInitial("¡Hola! Soy un asistente experto en redacción científica en LaTeX. ¡Mientras más específicas sean tus indicaciones, mejores resultados podrás obtener!");
    } else if (lenguage === 'German') {
      setInitial("Hallo! Ich bin ein Experte für wissenschaftliches Schreiben in LaTeX. Je spezifischer Ihre Anweisungen sind, desto bessere Ergebnisse können Sie erzielen!");
    } else if (lenguage === 'French') {
      setInitial("Bonjour! Je suis un assistant expert en rédaction scientifique en LaTeX. Plus vos instructions sont spécifiques, meilleurs seront les résultats que vous pouvez obtenir!");
    } else if (lenguage === 'Portuguese') {
      setInitial("Olá! Sou um assistente especializado em redação científica em LaTeX. Quanto mais específicas forem suas instruções, melhores resultados você poderá obter!");
    } else {
      setInitial("Hello! I am an expert assistant in scientific writing in LaTeX. The more specific your instructions, the better results you can achieve!");
      setLenguage('English');
    }

    let index = 0;
    const interval = setInterval(() => {
      if (index <= initial.length) {
        const partialText = initial.slice(0, index);
        setMessages([{ text: partialText, sender: 'model' }]);
        index++;
      } else {
        clearInterval(interval);
      }
    }, 30);
    return () => clearInterval(interval);
  }, [lenguage, initial]);

  const extractLatexBlock = (text) =>{
    const match = text.match(/```latex\n([\s\S]*?)```/);
    return match ? match[1].trim() : text.trim();
  }

  const handleSend = async () => {
  if (input.trim() === '') return;

  if (!firstPrompt) {
    setFirstPrompt(input);
    const newHistory = [...promptHistory, input];
    localStorage.setItem('recentItems', JSON.stringify(newHistory));
    setPromptHistory(newHistory);
  }

  const userMessage = { text: input, sender: 'user' };
  setMessages(prev => [...prev, userMessage]);
  setInput('');

  // Mostrar "Escribiendo..."
  const typingPlaceholder = { text: "Escribiendo...", sender: 'model', typing: true };
  setMessages(prev => [...prev, typingPlaceholder]);

  const lenguageJson = {"lenguage": lenguage};
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
  const merge = {...lenguageJson, ...newJson};
  try {
    const response = await generateReport(merge);

    const responseMessage = {
      text: "Respuesta en consola",
      sender: 'model'
    };

    console.log("Respuesta del modelo:", response.data);
    
    const body = response.data.cuerpo_texto;

    try {
        
        console.log("Cuerpo del texto:", body);

        const onlyLatex = extractLatexBlock(body);

        const latex = {
          cuerpo_texto: onlyLatex
        };

        console.log("Texto LaTeX extraído:", latex);
        
        const response2 = await latexReport(latex);

        const responseMessage = {
            text: "Texto generado correctamente. Puedes descargar el archivo LaTeX.",
            sender: 'model'
        };

        console.log("Texto limpio:", response2.data);

        setMessages(prev => {
      // Reemplaza el "Escribiendo..." por la respuesta real
      const updated = [...prev];
      const index = updated.findIndex(msg => msg.typing);
      if (index !== -1) updated.splice(index, 1, responseMessage);
      else updated.push(responseMessage);
      return updated;
    });
    } catch(error) {
        const errorMessage = {
        text: "Ocurrió un error al generar el archivo.",
        sender: 'model'
    };

    setMessages(prev => {
      const updated = [...prev];
      const index = updated.findIndex(msg => msg.typing);
      if (index !== -1) updated.splice(index, 1, errorMessage);
      else updated.push(errorMessage);
      return updated;
    });
    console.error("Error al llamar a latexReport:", error);
    }

    setMessages(prev => {
      // Reemplaza el "Escribiendo..." por la respuesta real
      const updated = [...prev];
      const index = updated.findIndex(msg => msg.typing);
      if (index !== -1) updated.splice(index, 1, responseMessage);
      else updated.push(responseMessage);
      return updated;
    });

  } catch (error) {
    const errorMessage = {
      text: "Ocurrió un error al generar la respuesta.",
      sender: 'model'
    };

    setMessages(prev => {
      const updated = [...prev];
      const index = updated.findIndex(msg => msg.typing);
      if (index !== -1) updated.splice(index, 1, errorMessage);
      else updated.push(errorMessage);
      return updated;
    });
    console.error("Error al llamar a generateReport:", error);
  }
};

  return (
    <div className={styles.mainPanel}>
      <header className={styles.header}>
        <h3>{firstPrompt || "Untitled prompt"}</h3>
      </header>
      <ChatHistory messages={messages} />
      <ChatInput input={input} setInput={setInput} onSend={handleSend} />
    </div>
    
  );
}

export default MainPanel;
