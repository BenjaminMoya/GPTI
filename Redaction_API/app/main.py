from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import ReportGenerationRequest, ReportOutput, ReportBody
from .report_service import generate_latex_report_content, clean_and_format_latex,compile_latex_to_pdf
from fastapi.responses import FileResponse
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import os

app = FastAPI(
    title="API Generadora de Informes Científicos en LaTeX",
    version="1.0.0",
    description="Genera un informe científico automatizado (IMRyD) usando DeepSeek y datos estructurados."
)

templates_dir = Path(__file__).parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(templates_dir))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Verifica si la API key está cargada al inicio

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
    
@app.post("/generate-and-download-pdf", response_class=FileResponse)
async def generate_and_download_pdf(report_body: ReportBody):
    """
    Endpoint principal que recibe LaTeX, lo limpia, lo compila y devuelve el PDF.
    """
    try:
        # 1. Limpiar y formatear el LaTeX usando la IA
        full_latex_code = clean_and_format_latex(report_body.cuerpo_texto)
        
        # 2. Compilar el LaTeX a PDF
        pdf_path = compile_latex_to_pdf(full_latex_code, "reporte_generado")

        # 3. Devolver el archivo PDF para su descarga
        return FileResponse(
            path=pdf_path,
            media_type='application/pdf',
            filename='reporte_final.pdf' # Nombre que verá el usuario al descargar
        )
    except (FileNotFoundError, RuntimeError, HTTPException) as e:
        # Manejar errores específicos y devolver una respuesta clara
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # Captura de cualquier otro error inesperado
        print(f"Error inesperado: {e}")
        raise HTTPException(status_code=500, detail="Ocurrió un error interno inesperado.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)