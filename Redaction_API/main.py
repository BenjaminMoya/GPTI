# scientific_report_api/main.py
from fastapi import FastAPI, HTTPException
from Redaction_API.models import ScientificInput, ScientificReportOutput, LatexReadyOutput, ReportSection
from Redaction_API.openai_utils import generate_scientific_text_from_openai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="API de Generación de Informes Científicos",
    description="Genera secciones de un informe científico usando OpenAI, listo para exportar a LaTeX.",
    version="0.1.0"
)

@app.post("/generate-report/", response_model=LatexReadyOutput)
async def create_scientific_report(input_data: ScientificInput):
    """
    Recibe datos científicos y genera el contenido del informe.

    - **hipotesis**: La hipótesis principal del estudio.
    - **fuentes**: Lista de fuentes o antecedentes relevantes.
    - **experimentacion**: Descripción detallada de la metodología y experimentación.
    - **resultados_observados**: Resumen de los resultados clave obtenidos.
    """
    try:
        print("Datos recibidos:", input_data.model_dump_json(indent=2)) # Para debug
        report_sections: ReportSection = generate_scientific_text_from_openai(input_data)
        
        # El objeto report_sections ya cumple con la estructura de ReportSection
        # Lo envolvemos en LatexReadyOutput para la respuesta final de la API
        latex_ready_json = LatexReadyOutput(report_content=report_sections)
        
        print("Respuesta generada:", latex_ready_json.model_dump_json(indent=2)) # Para debug
        return latex_ready_json
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Considerar loggear el error real aquí para debug interno
        print(f"Error inesperado: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor al generar el informe.")

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Generación de Informes Científicos. Usa el endpoint /docs para ver la documentación."}

# Para ejecutar la API: uvicorn main:app --reload --app-dir scientific_report_api