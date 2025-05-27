# scientific_report_api/models.py
from pydantic import BaseModel
from typing import List, Dict, Any

class ScientificInput(BaseModel):
    hipotesis: str
    fuentes: List[str]  # Lista de strings, podrían ser URLs o descripciones de fuentes
    experimentacion: str # Descripción del diseño experimental
    resultados_observados: str # Descripción de los resultados crudos o principales hallazgos

class ReportSection(BaseModel):
    introduccion: str
    metodologia: str
    resultados_generados: str # Resultados elaborados por la IA
    conclusion: str

class ScientificReportOutput(ReportSection):
    # Podríamos añadir metadatos adicionales si es necesario
    pass

class LatexReadyOutput(BaseModel):
    report_content: ReportSection
    # Aquí podríamos añadir campos específicos para LaTeX si es necesario,
    # como comandos LaTeX pre-generados, pero por ahora mantenemos la estructura del informe.