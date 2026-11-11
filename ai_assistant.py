
import json
import time
import streamlit as st

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

    Presenta el análisis en español con estas secciones:

    1. HALLAZGOS:
       Identifica materiales requeridos, existencias y faltantes.

    2. IMPACTO EN PRODUCCIÓN:
       Explica cómo afectan los faltantes a la fabricación.

    3. RECOMENDACIONES:
       Sugiere acciones concretas para resolver los faltantes.

    Reglas:
    - Utiliza únicamente los datos proporcionados.
    - No inventes cantidades, costos ni existencias.
    - No supongas compras o reservas no informadas.
    - No modifiques inventarios ni órdenes.
    - Utiliza lenguaje claro y profesional.
    """

    client = genai.Client(api_key=api_key)

    response = None

    # Intentar hasta tres veces ante errores temporales
    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=1200
                )
            )

            break

        except Exception as error:

            error_message = str(error).lower()

            temporary_error = any(
                term in error_message
                for term in [
                    "503",
                    "unavailable",
                    "high demand",
                    "429",
                    "resource_exhausted"
                ]
            )

            if temporary_error and attempt < 2:

                time.sleep(2 ** (attempt + 1))
                continue

            raise RuntimeError(
                f"No fue posible generar el análisis: {error}"
            ) from error

    if response is None or not response.text:
        raise RuntimeError(
            "Gemini no devolvió una respuesta. Intenta nuevamente."
        )

    return response.text.strip()

