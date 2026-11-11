
import json
import streamlit as st
import time
from google import genai
from google.genai import types


MODEL_NAME = "gemini-3.8-flash"


def analyze_material_shortages(analysis_context):
    """
    Analiza faltantes de materiales y genera recomendaciones
    para apoyar las decisiones de producción.
    """

    api_key = st.secrets.get("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "No se encuentra la clave GEMINI_API_KEY en Streamlit."
        )

    context = json.dumps(
        analysis_context,
        ensure_ascii=False,
        indent=2,
        default=str
    )

    prompt = f"""
    Analiza la siguiente información de inventario y producción
    de SYNTHEX:

    {context}

    Tu tarea es:

    1. Identificar los materiales que presentan faltantes.
    2. Explicar cómo afectan la capacidad de producción.
    3. Identificar qué materiales requieren atención prioritaria.
    4. Recomendar acciones concretas para continuar la producción.
    5. Explicar los resultados en lenguaje sencillo y profesional.

    Reglas importantes:

    - Utiliza únicamente los datos proporcionados.
    - No inventes cantidades, costos ni existencias.
    - Diferencia los requerimientos de materiales de las existencias.
    - Si falta información, indícalo expresamente.
    - No modifiques inventarios ni órdenes.
    - Presenta el resultado en español.
    - Organiza la respuesta con títulos y recomendaciones.
    """

    try:
        client = genai.Client(api_key=api_key)

               response = None

        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        max_output_tokens=1200,
                        thinking_config=types.ThinkingConfig(
                            thinking_level="low"
                        )
                    )
                )
                break

            except Exception as error:
                error_message = str(error).lower()

                temporary_error = (
                    "503" in error_message
                    or "unavailable" in error_message
                    or "high demand" in error_message
                )

                if temporary_error and attempt < 2:
                    time.sleep(2 ** (attempt + 1))
                    continue

                raise

        if not response.text:
            raise RuntimeError(
                "El modelo no devolvió una respuesta."
            )

        return response.text.strip()

    except Exception as error:
        raise RuntimeError(
            f"No fue posible generar el análisis: {error}"
        ) from error
