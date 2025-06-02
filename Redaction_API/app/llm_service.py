import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv() # Carga variables de entorno desde .env

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
YOUR_SITE_URL = os.getenv("YOUR_SITE_URL", "http://localhost:8000") # Default si no está en .env
YOUR_SITE_NAME = os.getenv("YOUR_SITE_NAME", "AcademicReportGenerator") # Default

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY no encontrada en las variables de entorno.")

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=OPENROUTER_API_KEY,
)

def get_llm_completion(prompt_content: str, system_message: str = "Eres un asistente experto en redacción científica en LaTeX.") -> str:
    """
    Obtiene una completación del modelo LLM de OpenRouter.
    """
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": YOUR_SITE_URL,
                "X-Title": YOUR_SITE_NAME,
            },
            model="deepseek/deepseek-r1-0528-qwen3-8b:free", # Modelo especificado
            # model="mistralai/mistral-7b-instruct:free", # Alternativa si deepseek no funciona bien para español o LaTeX
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": prompt_content
                }
            ],
            temperature=0.7, # Ajustar para creatividad vs factualidad
            max_tokens=2000 # Ajustar según la longitud esperada de la sección
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error al llamar a la API de OpenRouter: {e}")
        # Podrías retornar un texto de error o re-intentar
        return f"% Error al generar contenido: {e}"

    