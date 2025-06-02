from fastapi import FastAPI, HTTPException
from .models import ReportGenerationRequest, ReportOutput
from .report_service import generate_latex_report_content
import os

app = FastAPI(
    title="API Generadora de Informes Científicos en LaTeX",
    version="1.0.0",
    description="Genera un informe científico automatizado (IMRyD) usando DeepSeek y datos estructurados."
)

# Verifica si la API key está cargada al inicio
# (llm_service ya lo hace, pero una verificación aquí puede ser útil)
if not os.getenv("OPENROUTER_API_KEY"):
    print("ADVERTENCIA: OPENROUTER_API_KEY no está configurada. La API fallará.")

@app.post("/generate-report/", response_model=ReportOutput, tags=["Informes"])
async def create_report(request_data: ReportGenerationRequest):
    """
    Genera un informe científico en formato LaTeX.

    Proporciona los siguientes datos:
    - **pregunta_investigacion**: La pregunta central del estudio.
    - **info_papers**: Lista de papers relevantes (título, autores, resumen, año, doi, fuente).
    - **formulacion_hipotesis**: Lista de hipótesis (hipótesis, justificación, formato).
    - **experimentacion**: Detalles del experimento (modelo, dataset, condiciones, repeticiones).
    - **analisis_datos**: Resultados del análisis (resumen, gráficos, estadísticas).

    Retorna un JSON con:
    - **titulo**: Título sugerido para el informe.
    - **formato**: "Latex".
    - **referencias**: Lista de referencias formateadas (simplificado).
    - **cuerpo_texto**: Contenido completo del informe en LaTeX (secciones IMRyD + Referencias).
    """
    try:
        report = generate_latex_report_content(request_data)
        return report
    except Exception as e:
        # Loggear el error en un sistema real
        print(f"Error durante la generación del informe: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# Ejemplo de cómo añadir datos de ejemplo para la documentación de FastAPI (Swagger UI)
# Esto se puede hacer directamente en los Pydantic models con `Field(example=...)`
# o aquí para el request body completo.
# Lo he puesto en los modelos Pydantic para mejor organización.

if __name__ == "__main__":
    import uvicorn
    # Para desarrollo, puedes correrlo directamente.
    # Para producción, usa un servidor ASGI como Uvicorn o Hypercorn con Gunicorn.
    uvicorn.run(app, host="0.0.0.0", port=8000)