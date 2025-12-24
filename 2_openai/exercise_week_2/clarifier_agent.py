from pydantic import BaseModel, Field
from agents import Agent

class ClarificationRequests(BaseModel):
    questions: list[str] = Field(description="Una lista de preguntas de aclaración para hacer al usuario.")

INSTRUCTIONS = """Eres un experto en hacer preguntas de aclaración para investigaciones.
    Cuando recibes una consulta de investigación, generas exactamente 3 preguntas específicas
    que ayudarán a entender mejor:
    - El contexto y motivación del usuario
    - El nivel de profundidad deseado
    - Aspectos específicos de interés
    Las preguntas deben ser claras, concisas y relevantes para mejorar la investigación.
    IMPORTANTE: Devuelve SOLO las 3 preguntas, sin explicaciones adicionales."""

clarifier_agent = Agent(
    name="Agente de clarificación",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=ClarificationRequests
)