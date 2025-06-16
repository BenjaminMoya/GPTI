from pydantic import BaseModel, Field
from typing import List, Dict, Any

class PaperInfo(BaseModel):
    titulo: str
    autores: List[str]
    resumen: str
    año: int
    doi: str
    fuente: str

class HypothesisItem(BaseModel):
    hipotesis: str
    justificacion: str
    formato: str

class ExperimentationConditions(BaseModel):
    regularizacion: str
    epochs: int
    metricas: List[str]

class ExperimentationDetails(BaseModel):
    modelo: str
    dataset: str
    condiciones: ExperimentationConditions
    repeticiones: int
    formato: str 

class DataAnalysisStatistics(BaseModel):
    loss_promedio_con_L2: float
    loss_promedio_sin_L2: float
    p_valor: float

class DataAnalysisResults(BaseModel):
    resumen: str
    graficos_generados: List[str] = Field(default_factory=list)
    estadisticas: DataAnalysisStatistics

class ReportGenerationRequest(BaseModel):
    pregunta_investigacion: str = Field(..., example="¿Cómo afecta la regularización L2 al rendimiento de redes neuronales?")
    info_papers: List[PaperInfo]
    formulacion_hipotesis: List[HypothesisItem]
    experimentacion: ExperimentationDetails
    analisis_datos: DataAnalysisResults

class ReportOutput(BaseModel):
    titulo: str
    formato: str = "Latex"
    referencias: List[str]
    cuerpo_texto: str 


class ReportBody(BaseModel):
    cuerpo_texto: str = Field(..., example="\\section{Introducción} Este es un texto de prueba.")

class LatexRequest(BaseModel):
    latex_content: str = Field(..., description="Un string que contiene un documento LaTeX completo y válido.")