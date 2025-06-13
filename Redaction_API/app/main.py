from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import ReportGenerationRequest, ReportOutput
from .report_service import generate_latex_report_content
from fastapi.responses import FileResponse
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from .report_service import compile_latex_to_pdf
from .report_service import generate_latex_pdf
import tempfile
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
    allow_origins=["*"],  # o especifica dominios como ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # o ["GET", "POST", "PUT", "DELETE"]
    allow_headers=["*"],  # o ["Authorization", "Content-Type"]
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

@app.post("/generate-report-pdf/", response_class=FileResponse)
async def create_report_pdf(request_data: ReportGenerationRequest):
    """
    Recibe los datos para un informe, genera el contenido LaTeX, lo compila
    y devuelve el archivo PDF resultante.
    """
    # Paso A: Generar el contenido del informe (título, abstract, cuerpo)
    report_content = generate_latex_pdf(request_data)

    # Paso B: Cargar la plantilla Jinja2
    template = jinja_env.get_template("report_template.tex.j2")

    # Paso C: Renderizar la plantilla con el contenido generado
    full_latex_string = template.render(
        title=report_content.titulo,
        abstract_content=report_content.abstract_content,
        report_body=report_content.cuerpo_texto
    )
    
    # Paso D: Usar un directorio temporal para la compilación
    # Esto es crucial para manejar múltiples peticiones a la vez sin conflictos de archivos
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        
        # Paso E: Compilar el LaTeX a PDF
        try:
            pdf_path = await compile_latex_to_pdf(full_latex_string, temp_dir_path)
            
            # Paso F: Devolver el PDF como una respuesta de archivo.
            # FastAPI se encargará de limpiar el FileResponse. El directorio temporal se limpia automáticamente al salir del `with`.
            return FileResponse(
                path=pdf_path,
                filename="scientific_report.pdf",
                media_type="application/pdf"
            )
        except HTTPException as e:
            # Re-lanzar la excepción para que FastAPI la maneje
            raise e
        except Exception as e:
            # Capturar cualquier otro error inesperado
            raise HTTPException(status_code=500, detail=f"Un error inesperado ocurrió: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Para desarrollo, puedes correrlo directamente.
    # Para producción, usa un servidor ASGI como Uvicorn o Hypercorn con Gunicorn.
    uvicorn.run(app, host="0.0.0.0", port=8000)