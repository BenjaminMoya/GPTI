from .models import ReportGenerationRequest, ReportOutput, PaperInfo
from .llm_service import get_llm_completion
import json
import os
import subprocess
import tempfile
import shutil

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

def generate_report_title(pregunta_investigacion: str, experimentacion: dict, analisis_datos: dict, lenguage: str) -> str:
    prompt = f"""
    Basado en la siguiente pregunta de investigación, detalles experimentales y resultados, genera un título conciso y académico para un informe científico en {lenguage}.
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
    report_title = generate_report_title(data.pregunta_investigacion, data.experimentacion, data.analisis_datos, data.lenguage)


    # 2. Resumen (Abstract)
    prompt_abstract = f"""
    Tarea: Escribe el RESUMEN (Abstract) para un informe científico en formato LaTeX en {data.lenguage}.
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
    - Incluye "\\documentclass", "\\begin{{document}}" o comandos similares, considerando que es el inicio del documento.
    - El idioma es {data.lenguage}.
    """
    abstract_content = get_llm_completion(prompt_abstract)
    cuerpo_texto_parts.append(abstract_content)

    # 3. Introducción
    prompt_intro = f"""
    Tarea: Escribe la sección de INTRODUCCIÓN para un informe científico en formato LaTeX en {data.lenguage}.
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
    - El idioma es {data.lenguage}.
    """
    intro_content = get_llm_completion(prompt_intro)
    cuerpo_texto_parts.append(intro_content)

    # 4. Metodología
    prompt_methods = f"""
    Tarea: Escribe la sección de METODOLOGÍA (o Materiales y Métodos) para un informe científico en formato LaTeX en {data.lenguage}.
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
    - El idioma es {data.lenguage}.
    """
    methods_content = get_llm_completion(prompt_methods)
    cuerpo_texto_parts.append(methods_content)

    # 5. Resultados
    prompt_results = f"""
    Tarea: Escribe la sección de RESULTADOS para un informe científico en formato Latex en {data.lenguage}.
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
    - El idioma es {data.lenguage}.
    """
    results_content = get_llm_completion(prompt_results)
    cuerpo_texto_parts.append(results_content)

    # 6. Discusión
    prompt_discussion = f"""
    Tarea: Escribe la sección de DISCUSIÓN para un informe científico en formato LaTeX en {data.lenguage}.
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
    - El idioma es {data.lenguage}.
    """
    discussion_content = get_llm_completion(prompt_discussion)
    cuerpo_texto_parts.append(discussion_content)

    # 7. Conclusión
    prompt_conclusion = f"""
    Tarea: Escribe la sección de CONCLUSIÓN para un informe científico en formato LaTeX en {data.lenguage}.
    Basado en la pregunta "{data.pregunta_investigacion}" y los resultados principales resumidos en: "{data.analisis_datos.resumen}".
    Las hipótesis eran:
    {hypotheses_str}

    Instrucciones para LaTeX:
    - Comienza con "\\section{{Conclusión}}".
    - Resume las principales conclusiones del estudio de forma clara y concisa.
    - Responde directamente a la pregunta de investigación.
    - Evita introducir nueva información o interpretación no presente en la discusión.
    - No incluyas "\\documentclass", "\\begin{{document}}" o comandos similares. Solo el contenido de la sección.
    - El idioma es {data.lenguage}.
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
    references_section += "\n\\end{document}"
    cuerpo_texto_parts.append(references_section)


    full_cuerpo_texto = "\n\n".join(cuerpo_texto_parts)

    return ReportOutput(
        titulo=report_title,
        referencias=referencias_list,
        cuerpo_texto=full_cuerpo_texto
    )


def clean_and_format_latex(cuerpo_texto: str) -> str:
    """
    Verifica si un string LaTeX es un documento completo y, si no lo es,
    lo arregla añadiendo la estructura necesaria para que sea compilable.

    Usa un LLM con instrucciones específicas para:
    1. Identificar si el texto es un fragmento o un documento completo.
    2. Si es un fragmento, lo envuelve en un preámbulo estándar y el entorno document.
    3. Si ya es un documento completo, lo devuelve sin cambios o con correcciones sintácticas menores.
    4. Asegura que la salida sea solo código LaTeX puro.

    Args:
        cuerpo_texto: El string con el contenido LaTeX a verificar y arreglar.

    Returns:
        Un string con el documento LaTeX completo y listo para compilar.
    """
    
    print(">>> Verificando y arreglando estructura LaTeX con IA...")

    # Instrucciones detalladas para la IA.
    system_message = (
        "Eres un asistente experto en LaTeX. Tu tarea es analizar el texto LaTeX proporcionado "
        "y asegurarte de que tenga la estructura de un documento completo y compilable. "
        "Reglas a seguir:\n"
        "1. Si el texto de entrada ya es un documento completo (tiene \\documentclass, \\begin{document}, "
        "y \\end{document}), devuélvelo tal cual. No lo modifiques a menos que encuentres un error de sintaxis obvio.\n"
        "2. Si el texto es solo un fragmento (por ejemplo, una sección, una tabla, o simple texto), "
        "DEBES envolverlo en la estructura mínima para que sea compilable. Usa \\documentclass{article} y los paquetes "
        "básicos como 'amsmath', 'graphicx', y 'babel'.\n"
        "3. Es crucial que NO alteres, elimines ni agregues contenido sustancial al texto original del usuario. "
        "Tu única misión es añadir la 'plantilla' o 'envoltura' estructural si falta.\n"
        "4. Tu respuesta DEBE contener ÚNICAMENTE el código LaTeX final. No incluyas explicaciones, "
        "comentarios, saludos, ni frases como 'Aquí está el código corregido:'."
    )

    # El prompt que le pasamos al modelo.
    user_prompt = (
        "Por favor, verifica y, si es necesario, arregla la estructura del siguiente texto LaTeX "
        "para que sea un documento compilable, siguiendo estrictamente las reglas que te he dado.\n\n"
        f"Texto LaTeX a procesar:\n---\n{cuerpo_texto}\n---"
    )

    # Llamada a la función LLM que ya teníamos.
    fixed_latex = get_llm_completion(user_prompt, system_message)

    # Post-procesamiento para eliminar los 'code fences' de Markdown si el LLM los añade.
    if fixed_latex.startswith("```latex"):
        fixed_latex = fixed_latex.removeprefix("```latex").strip()
    if fixed_latex.endswith("```"):
        fixed_latex = fixed_latex.removesuffix("```").strip()

    print(">>> Estructura LaTeX verificada y corregida.")
    ended = fixed_latex + "\n\\end{document}"
    print(ended)
    return ended

def compile_latex_to_pdf(latex_content: str, output_filename: str = "reporte") -> str:
    """
    Compila un string de LaTeX a un archivo PDF usando pdflatex.

    Crea un directorio temporal para manejar los archivos de compilación (.aux, .log).
    Guarda el PDF final en un directorio 'generated_pdfs'.

    Args:
        latex_content: El string del documento LaTeX completo.
        output_filename: El nombre del archivo PDF sin la extensión.

    Returns:
        La ruta al archivo PDF generado.
    
    Raises:
        FileNotFoundError: Si el comando 'pdflatex' no se encuentra en el sistema.
        RuntimeError: Si la compilación de LaTeX falla.
    """
    if not shutil.which("pdflatex"):
        raise FileNotFoundError(
            "El comando 'pdflatex' no se encuentra. "
            "Asegúrate de tener una distribución de LaTeX instalada (MiKTeX, TeX Live, MacTeX)."
        )

    # Crear un directorio para los PDFs generados si no existe
    output_dir = "generated_pdfs"
    os.makedirs(output_dir, exist_ok=True)
    
    # Usar un directorio temporal para los archivos de compilación sucios (.tex, .aux, .log)
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = os.path.join(temp_dir, "source.tex")
        
        # Escribir el contenido LaTeX al archivo .tex
        with open(source_path, "w", encoding="utf-8") as f:
            f.write(latex_content)
        
        print(f">>> Compilando {source_path}...")
        
        # Comando para compilar. Usamos -output-directory para mantener limpio el CWD.
        command = [
            "pdflatex",
            "-interaction=nonstopmode",  # No pedir input en caso de error
            "-output-directory", temp_dir,
            source_path
        ]
        
        try:
            # Se recomienda ejecutar pdflatex dos veces para resolver referencias cruzadas
            subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
            print(">>> Primera pasada de compilación completa.")
            subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
            print(">>> Segunda pasada de compilación completa.")
        
        except subprocess.CalledProcessError as e:
            print("!!! ERROR DE COMPILACIÓN DE LATEX !!!")
            # El log de error es crucial para depurar
            log_path = os.path.join(temp_dir, "source.log")
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8") as log_file:
                    log_content = log_file.read()
                print(f"--- Contenido del log ({log_path}) ---\n{log_content[-2000:]}") # Últimos 2000 caracteres
            
            raise RuntimeError(f"Falló la compilación de LaTeX. Revisa el log para más detalles. Error: {e.stderr}")

        # Mover el PDF generado del directorio temporal al directorio de salida final
        generated_pdf_temp_path = os.path.join(temp_dir, "source.pdf")
        final_pdf_path = os.path.join(output_dir, f"{output_filename}.pdf")
        
        if not os.path.exists(generated_pdf_temp_path):
             raise RuntimeError("La compilación de LaTeX no produjo un archivo PDF.")
             
        shutil.move(generated_pdf_temp_path, final_pdf_path)
        print(f">>> PDF generado y guardado en: {final_pdf_path}")
        
        return final_pdf_path