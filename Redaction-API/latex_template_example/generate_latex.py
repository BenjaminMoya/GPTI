# scientific_report_api/latex_template_example/generate_latex.py
import json
from jinja2 import Environment, FileSystemLoader
import subprocess
import os
import re

# Función para escapar caracteres especiales de LaTeX
def escape_latex_chars(value):
    if not isinstance(value, str):
        value = str(value)
    # Mapeo de caracteres especiales y sus reemplazos LaTeX
    # Esta lista puede necesitar ser extendida
    mapping = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
    }
    # Reemplazar caracteres
    for char, replacement in mapping.items():
        value = value.replace(char, replacement)
    
    # Manejar saltos de línea (convertir a \par o \\)
    value = value.replace('\n\n', '\n\\par\n') # Doble salto de línea a nuevo párrafo
    value = value.replace('\n', '\\\\\n')       # Salto de línea simple a salto de línea LaTeX
    
    return value

# Configurar Jinja2
env = Environment(loader=FileSystemLoader('.')) # Busca plantillas en el directorio actual
env.filters['escape_latex'] = escape_latex_chars # Registrar el filtro personalizado
template = env.get_template('report_template.tex.jinja')

# Datos JSON de ejemplo (esto vendría de la API)
# Puedes pegar aquí la salida JSON de tu API
example_api_output = {
  "report_content": {
    "introduccion": "La inteligencia artificial (IA) ha emergido como una fuerza transformadora en numerosas disciplinas. Su aplicación en la redacción científica automatizada representa un área de creciente interés, con el potencial de acelerar la diseminación del conocimiento. Esta sección introduce el problema de la generación de texto científico y la hipótesis de que modelos de lenguaje avanzados pueden producir borradores coherentes y relevantes.",
    "metodologia": "Para evaluar la capacidad de la IA en la generación de informes, se utilizó un modelo de lenguaje grande (LLM), específicamente GPT-3.5-turbo. Se diseñó un prompt estructurado que solicitaba la generación de secciones clave de un informe (introducción, metodología, resultados, conclusión) a partir de una entrada JSON que contenía la hipótesis, fuentes, descripción experimental y resultados observados. El prompt incluía la instrucción de devolver la salida en formato JSON.",
    "resultados_generados": "El modelo LLM generó con éxito el contenido para cada sección solicitada. La 'introducción' contextualizó adecuadamente el tema. La 'metodología' describió de forma plausible el enfoque, aunque de manera general. Los 'resultados generados' expandieron los 'resultados observados' proporcionados, añadiendo un nivel de elaboración discursiva. La 'conclusión' resumió los hallazgos teóricos y propuso implicaciones. Se observó que la calidad del texto dependía fuertemente de la claridad y detalle de la información de entrada y de la especificidad del prompt.",
    "conclusion": "Este experimento preliminar demuestra la viabilidad de utilizar modelos de lenguaje como GPT-3.5-turbo para generar borradores de informes científicos estructurados. Si bien los resultados son prometedores, la supervisión humana sigue siendo crucial para garantizar la precisión factual, la profundidad analítica y la originalidad. Futuras investigaciones podrían enfocarse en refinar los prompts, integrar bases de datos de conocimiento especializado y desarrollar métricas de evaluación más robustas para la calidad del texto científico generado por IA."
  }
}


# Cargar datos desde un archivo JSON (si lo prefieres)
# with open('api_response_example.json', 'r', encoding='utf-8') as f:
#     data_from_api = json.load(f)

data_from_api = example_api_output # Usamos el ejemplo directamente

# Renderizar la plantilla con los datos
output_tex_content = template.render(data_from_api)

# Guardar el archivo .tex
output_tex_filename = 'informe_generado.tex'
with open(output_tex_filename, 'w', encoding='utf-8') as f:
    f.write(output_tex_content)

print(f"Archivo '{output_tex_filename}' generado con éxito.")

# (Opcional) Compilar a PDF usando pdflatex
# Asegúrate de tener una distribución de LaTeX instalada (MiKTeX, TeX Live, etc.)
# y que pdflatex esté en tu PATH.
try:
    # Compilar dos veces para referencias cruzadas y tabla de contenidos si las hubiera
    subprocess.run(['pdflatex', '-interaction=nonstopmode', output_tex_filename], check=True)
    subprocess.run(['pdflatex', '-interaction=nonstopmode', output_tex_filename], check=True)
    print(f"PDF '{output_tex_filename.replace('.tex', '.pdf')}' generado con éxito.")
    # Limpiar archivos auxiliares
    for ext in ['.aux', '.log', '.out', '.toc']: # Agrega más extensiones si es necesario
        if os.path.exists(output_tex_filename.replace('.tex', ext)):
            os.remove(output_tex_filename.replace('.tex', ext))
except FileNotFoundError:
    print("Error: pdflatex no encontrado. Asegúrate de que LaTeX esté instalado y en el PATH.")
except subprocess.CalledProcessError as e:
    print(f"Error durante la compilación de LaTeX: {e}")
    print("Revisa el archivo .log para más detalles.")