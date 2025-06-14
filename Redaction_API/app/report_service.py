from .models import ReportGenerationRequest, ReportOutput, PaperInfo
from .llm_service import get_llm_completion
import json
from pathlib import Path
import asyncio
import os
from fastapi import HTTPException

def format_papers_for_prompt(papers: list[PaperInfo]) -> str:
    formatted_papers = []
    for p in papers:
        autores_str = ", ".join(p.autores)
        formatted_papers.append(
            f"- Título: {p.titulo}\n  Autores: {autores_str}\n  Año: {p.año}\n  Resumen: {p.resumen}\n  DOI: {p.doi}"
        )
    return "\n".join(formatted_papers)

def format_hypotheses_for_prompt(hypotheses: list[dict]) -> str:
    formatted = []
    for h in hypotheses:
        formatted.append(f"- Hipótesis: {h['hipotesis']}\n  Justificación: {h['justificacion']}")
    return "\n".join(formatted)

def generate_report_title(pregunta_investigacion: str, experimentacion: dict, analisis_datos: dict) -> str:
    prompt = f"""
    Basado en la siguiente pregunta de investigación, detalles experimentales y resultados, genera un título conciso y académico para un informe científico.
    Pregunta de Investigación: {pregunta_investigacion}
    Modelo experimental: {experimentacion.modelo}
    Resultados clave: {analisis_datos.resumen}

    Ejemplo de título: "Evaluación del Efecto de la Regularización L2 en Redes Neuronales Convolucionales para la Clasificación de Imágenes en CIFAR-10"
    Responde ÚNICAMENTE con el título.
    """
    return get_llm_completion(prompt, system_message="Eres un asistente que genera títulos académicos concisos.")


def generate_latex_report_content(data: ReportGenerationRequest) -> ReportOutput:
    """
    Genera el contenido del informe científico en LaTeX utilizando el LLM.
    """
    cuerpo_texto_parts = []
    
    # Convertir objetos Pydantic a dicts para pasarlos como strings a los prompts
    info_papers_str = format_papers_for_prompt(data.info_papers)
    hypotheses_str = format_hypotheses_for_prompt([h.model_dump() for h in data.formulacion_hipotesis])
    experimentacion_str = json.dumps(data.experimentacion.model_dump(), indent=2, ensure_ascii=False)
    analisis_datos_str = json.dumps(data.analisis_datos.model_dump(), indent=2, ensure_ascii=False)

    # 1. Título (generado por LLM o basado en la pregunta)
    # report_title = f"Evaluación de: {data.pregunta_investigacion}" # Simple
    report_title = generate_report_title(data.pregunta_investigacion, data.experimentacion, data.analisis_datos)


    # 2. Resumen (Abstract)
    prompt_abstract = f"""
    Tarea: Escribe el RESUMEN (Abstract) para un informe científico en formato LaTeX.
    El informe trata sobre: "{data.pregunta_investigacion}".
    Información clave del estudio:
    Hipótesis principales:
    {hypotheses_str}
    Metodología usada:
    {experimentacion_str}
    Resultados principales y conclusiones:
    {analisis_datos_str}

    Instrucciones para LaTeX:
    - Comienza con "\\section*{{Resumen}}" (o Abstract).
    - Sé conciso y cubre los puntos clave: introducción breve, objetivos, métodos, resultados principales y conclusión principal.
    - No incluyas "\\documentclass", "\\begin{{document}}" o comandos similares. Solo el contenido de la sección.
    - El idioma es español.
    """
    abstract_content = get_llm_completion(prompt_abstract)
    cuerpo_texto_parts.append(abstract_content)

    # 3. Introducción
    prompt_intro = f"""
    Tarea: Escribe la sección de INTRODUCCIÓN para un informe científico en formato LaTeX.
    Pregunta de investigación central: "{data.pregunta_investigacion}"
    Información de artículos de referencia para contextualizar (menciónalos si es relevante, ej. Smith et al., 2021):
    {info_papers_str}
    Hipótesis a investigar:
    {hypotheses_str}

    Instrucciones para LaTeX:
    - Comienza con "\\section{{Introducción}}".
    - Estructura:
        1. Contexto general del problema y su importancia.
        2. Breve revisión de literatura relevante (puedes citar los papers proporcionados).
        3. Declaración del problema específico o pregunta de investigación.
        4. Objetivos del estudio y presentación de las hipótesis.
    - No incluyas "\\documentclass", "\\begin{{document}}" o comandos similares. Solo el contenido de la sección.
    - El idioma es español.
    """
    intro_content = get_llm_completion(prompt_intro)
    cuerpo_texto_parts.append(intro_content)

    # 4. Metodología
    prompt_methods = f"""
    Tarea: Escribe la sección de METODOLOGÍA (o Materiales y Métodos) para un informe científico en formato LaTeX.
    Detalles de la experimentación:
    {experimentacion_str}
    La pregunta de investigación que guía estos métodos es: "{data.pregunta_investigacion}"

    Instrucciones para LaTeX:
    - Comienza con "\\section{{Metodología}}".
    - Describe con suficiente detalle para que el experimento pueda ser replicado:
        - Modelo utilizado ({data.experimentacion.modelo}).
        - Dataset ({data.experimentacion.dataset}).
        - Condiciones experimentales (regularización: {data.experimentacion.condiciones.regularizacion}, epochs: {data.experimentacion.condiciones.epochs}, métricas: {', '.join(data.experimentacion.condiciones.metricas)}).
        - Número de repeticiones ({data.experimentacion.repeticiones}).
    - No incluyas "\\documentclass", "\\begin{{document}}" o comandos similares. Solo el contenido de la sección.
    - El idioma es español.
    """
    methods_content = get_llm_completion(prompt_methods)
    cuerpo_texto_parts.append(methods_content)

    # 5. Resultados
    prompt_results = f"""
    Tarea: Escribe la sección de RESULTADOS para un informe científico en formato LaTeX.
    Análisis de datos y hallazgos:
    {analisis_datos_str}
    Los gráficos generados son: {', '.join(data.analisis_datos.graficos_generados)}. Debes mencionarlos e incluir placeholders para ellos.

    Instrucciones para LaTeX:
    - Comienza con "\\section{{Resultados}}".
    - Presenta los hallazgos de forma objetiva, sin interpretación.
    - Menciona las estadísticas clave (ej. loss promedio, p-valor).
    - Incluye placeholders para los gráficos. Ejemplo para un gráfico llamado 'grafico.png':
      \\begin{{figure}}[htbp]
      \\centering
      \\includegraphics[width=0.8\\textwidth]{{grafico.png}}
      \\caption{{Descripción del gráfico.}}
      \\label{{fig:nombre_descriptivo}}
      \\end{{figure}}
    - Adapta los nombres de archivo y captions para '{', '.join(data.analisis_datos.graficos_generados)}'.
    - No incluyas "\\documentclass", "\\begin{{document}}" o comandos similares. Solo el contenido de la sección.
    - El idioma es español.
    """
    results_content = get_llm_completion(prompt_results)
    cuerpo_texto_parts.append(results_content)

    # 6. Discusión
    prompt_discussion = f"""
    Tarea: Escribe la sección de DISCUSIÓN para un informe científico en formato LaTeX.
    Pregunta de investigación: "{data.pregunta_investigacion}"
    Hipótesis planteadas:
    {hypotheses_str}
    Resultados obtenidos (resumen):
    {data.analisis_datos.resumen}
    Estadísticas clave: {data.analisis_datos.estadisticas.model_dump_json(indent=2)}
    Información de artículos de referencia para comparar (menciónalos si es relevante):
    {info_papers_str}

    Instrucciones para LaTeX:
    - Comienza con "\\section{{Discusión}}".
    - Estructura:
        1. Interpreta los resultados en el contexto de las hipótesis y la pregunta de investigación. ¿Se confirmaron las hipótesis?
        2. Compara los hallazgos con estudios previos (usando la info de papers).
        3. Menciona las limitaciones del estudio.
        4. Sugiere implicaciones y posibles trabajos futuros.
    - No incluyas "\\documentclass", "\\begin{{document}}" o comandos similares. Solo el contenido de la sección.
    - El idioma es español.
    """
    discussion_content = get_llm_completion(prompt_discussion)
    cuerpo_texto_parts.append(discussion_content)

    # 7. Conclusión
    prompt_conclusion = f"""
    Tarea: Escribe la sección de CONCLUSIÓN para un informe científico en formato LaTeX.
    Basado en la pregunta "{data.pregunta_investigacion}" y los resultados principales resumidos en: "{data.analisis_datos.resumen}".
    Las hipótesis eran:
    {hypotheses_str}

    Instrucciones para LaTeX:
    - Comienza con "\\section{{Conclusión}}".
    - Resume las principales conclusiones del estudio de forma clara y concisa.
    - Responde directamente a la pregunta de investigación.
    - Evita introducir nueva información o interpretación no presente en la discusión.
    - No incluyas "\\documentclass", "\\begin{{document}}" o comandos similares. Solo el contenido de la sección.
    - El idioma es español.
    """
    conclusion_content = get_llm_completion(prompt_conclusion)
    cuerpo_texto_parts.append(conclusion_content)

    # 8. Referencias (simplificado)
    # Para un sistema completo, usarías BibTeX y \cite{} en el texto.
    # Aquí, creamos una lista simple. El LLM debería haber sido instruido para citar como (Autor, Año) en el texto.
    referencias_list = []
    bib_items = []
    for i, paper in enumerate(data.info_papers):
        # Crear una etiqueta simple para la bibliografía, ej. smith2021
        try:
            last_name_autor_principal = paper.autores[0].split('.')[0].split(' ')[-1].lower()
            ref_key = f"{last_name_autor_principal}{paper.año}"
        except:
            ref_key = f"ref{i+1}{paper.año}"

        autores_str = " & ".join(paper.autores) # Formato más tipo BibTeX para autores
        
        # Formato para la lista de referencias "Smith & Lee, 2021"
        if len(paper.autores) > 1:
            ref_display = f"{paper.autores[0].split('.')[0]} & {paper.autores[1].split('.')[0]}, {paper.año}"
        elif paper.autores:
            ref_display = f"{paper.autores[0].split('.')[0]}, {paper.año}"
        else:
            ref_display = f"Anónimo, {paper.año}"
        referencias_list.append(ref_display)

        # Formato para \bibitem en LaTeX
        bib_item_str = f"\\bibitem{{{ref_key}}} {autores_str} ({paper.año}). \\textit{{{paper.titulo}}}. {paper.fuente}."
        if paper.doi:
            bib_item_str += f" DOI: \\url{{{paper.doi}}}"
        bib_items.append(bib_item_str)

    references_section = "\\section*{Referencias}\n" # O \section{Referencias} si quieres numerada
    references_section += "\\begin{thebibliography}{99}\n" # El 99 es un placeholder para el item más largo
    references_section += "\n".join(bib_items)
    references_section += "\n\\end{thebibliography}\n"
    cuerpo_texto_parts.append(references_section)


    full_cuerpo_texto = "\n\n".join(cuerpo_texto_parts)

    return ReportOutput(
        titulo=report_title,
        referencias=referencias_list,
        cuerpo_texto=full_cuerpo_texto
    )

async def compile_latex_to_pdf(latex_content: str, working_dir: Path) -> Path:
    """
    Compila una cadena de texto LaTeX a un archivo PDF.
    
    Args:
        latex_content: El contenido completo del archivo .tex.
        working_dir: El directorio temporal donde se realizarán las operaciones.

    Returns:
        La ruta al archivo PDF generado.
        
    Raises:
        HTTPException: Si la compilación de LaTeX falla.
    """
    tex_filename = "report.tex"
    pdf_filename = "report.pdf"
    log_filename = "report.log"
    
    tex_filepath = working_dir / tex_filename
    pdf_filepath = working_dir / pdf_filename
    log_filepath = working_dir / log_filename

    # Escribir el contenido LaTeX al archivo .tex
    with open(tex_filepath, "w", encoding="utf-8") as f:
        f.write(latex_content)

    # Comando para compilar con pdflatex
    # -interaction=nonstopmode: Evita que el proceso se detenga si hay errores menores.
    # -output-directory: Asegura que todos los archivos de salida vayan al directorio de trabajo.
    command = [
        "pdflatex",
        "-interaction=nonstopmode",
        f"-output-directory={working_dir}",
        str(tex_filepath),
    ]

    # Ejecutar pdflatex. Se recomienda ejecutarlo dos veces para resolver referencias cruzadas (índices, etc.)
    for i in range(2):
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            # Si falla la compilación, lee el log para dar un error útil
            log_content = ""
            if os.path.exists(log_filepath):
                with open(log_filepath, "r", encoding="utf-8") as log_file:
                    log_content = log_file.read()
            
            error_detail = {
                "message": "Falló la compilación de LaTeX.",
                "return_code": process.returncode,
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
                "log": log_content[-2000:] # Devuelve los últimos 2000 caracteres del log
            }
            raise HTTPException(status_code=500, detail=error_detail)

    if not os.path.exists(pdf_filepath):
        raise HTTPException(status_code=500, detail="El PDF no fue generado, revisa el log de LaTeX.")

    return pdf_filepath


# --- 4. Lógica de Generación de Contenido (tu función, ahora simulada) ---
def generate_latex_pdf(data: ReportGenerationRequest) -> ReportOutput:
    """
    Esta es una versión MOCK de tu función. 
    En un caso real, aquí irían tus llamadas al LLM.
    """
    # Simulamos la salida que tu función original produciría
    titulo = f"Informe sobre: {data.pregunta_investigacion}"
    
    abstract = "Este es el resumen (abstract) del informe. Describe brevemente los objetivos, métodos, resultados y conclusiones principales del estudio."
    
    # Unimos las secciones en un solo string de cuerpo
    cuerpo_partes = [
        "\\section{Introducción}\nAquí se presenta el contexto del problema, la literatura relevante y las hipótesis.",
        "\\section{Metodología}\nSe describe el diseño experimental, los materiales y los métodos utilizados.",
        "\\section{Resultados}\nPresentación objetiva de los hallazgos, a menudo con tablas y figuras.\n\\begin{figure}[h!]\n\\centering\n% \\includegraphics[width=0.8\\textwidth]{placeholder.png}\n\\caption{Ejemplo de figura.}\n\\label{fig:ejemplo}\n\\end{figure}",
        "\\section{Discusión}\nInterpretación de los resultados, limitaciones y comparación con otros estudios.",
        "\\section{Conclusión}\nResumen de las conclusiones clave del informe.",
        "\\section*{Referencias}\n\\begin{thebibliography}{9}\n\\bibitem{knuth1984}\nDonald E. Knuth. \\textit{The TeXbook}. Addison-Wesley Professional, 1984.\n\\end{thebibliography}"
    ]
    cuerpo_completo = "\n\n".join(cuerpo_partes)

    return ReportOutput(
        titulo=titulo,
        abstract_content=abstract,
        cuerpo_texto=cuerpo_completo
    )