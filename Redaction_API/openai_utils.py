# scientific_report_api/openai_utils.py
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
from .models import ScientificInput, ReportSection # Corrección aquí

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("No se encontró la API Key de OpenAI. Asegúrate de configurarla en el archivo .env")

client = OpenAI(api_key=API_KEY)

def generate_scientific_text_from_openai(data: ScientificInput) -> ReportSection:
    """
    Genera el contenido del informe científico usando la API de OpenAI.
    """
    prompt_template = f"""
    Eres un asistente experto en redacción científica. A partir de la siguiente información,
    genera un borrador de informe científico con las secciones: Introducción, Metodología,
    Resultados y Conclusión. Asegúrate de que el lenguaje sea formal y adecuado para
    una publicación científica.

    Información proporcionada:
    1. Hipótesis: {data.hipotesis}
    2. Fuentes relevantes/Antecedentes: {", ".join(data.fuentes) if data.fuentes else "No proporcionadas"}
    3. Descripción de la Experimentación: {data.experimentacion}
    4. Resultados Observados/Clave: {data.resultados_observados}

    Por favor, estructura tu respuesta estrictamente en formato JSON con las siguientes claves:
    "introduccion", "metodologia", "resultados_generados", "conclusion".

    Ejemplo de estructura de respuesta JSON esperada:
    {{
        "introduccion": "Texto de la introducción...",
        "metodologia": "Texto de la metodología...",
        "resultados_generados": "Texto elaborado de los resultados...",
        "conclusion": "Texto de la conclusión..."
    }}

    Genera el contenido:
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106", # o gpt-4-1106-preview si tienes acceso y prefieres mejor calidad
            messages=[
                {"role": "system", "content": "Eres un asistente de redacción científica que genera contenido en formato JSON."},
                {"role": "user", "content": prompt_template}
            ],
            temperature=0.7, # Un poco de creatividad, pero no demasiada
            max_tokens=3000, # Ajustar según necesidad
            # Importante para asegurar que la salida sea JSON parseable
            response_format={"type": "json_object"}
        )
        
        content_json_str = response.choices[0].message.content
        
        # Parsear el string JSON a un diccionario Python
        report_data = json.loads(content_json_str)

        # Validar y crear el objeto ReportSection
        return ReportSection(**report_data)

    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON de OpenAI: {e}")
        print(f"Respuesta recibida de OpenAI: {content_json_str}")
        raise ValueError("La respuesta de OpenAI no pudo ser decodificada como JSON válido.")
    except Exception as e:
        print(f"Error al interactuar con OpenAI: {e}")
        raise