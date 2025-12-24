from agents import Runner, trace, Agent
from search_agent import search_agent
from planner_agent import planner_agent
from writer_agent import writer_agent
from email_agent import email_agent
from clarifier_agent import clarifier_agent

class ResearchManager:
    def __init__(self):
        planner_tool = planner_agent.as_tool(
            tool_name="plan_research",
            tool_description="Crea un plan de búsqueda detallado para investigar el tema"
        )
        search_tool = search_agent.as_tool(
            tool_name="execute_search",
            tool_description="Ejecuta búsquedas web y recopila información relevante"
        )
        writer_tool = writer_agent.as_tool(
            tool_name="write_report",
            tool_description="Genera un informe completo de investigación en formato Markdown"
        )
        tools = [planner_tool, search_tool, writer_tool]
        handoffs = [email_agent]

        self.manager_agent = Agent(
            name="Research Manager",
            instructions="""Eres el gerente de investigación que coordina todo el proceso.

            Recibirás una consulta de investigación junto con contexto adicional proporcionado
            por el usuario en forma de respuestas a preguntas de aclaración.

            Tu flujo de trabajo es:
            1. Analizar la consulta y el contexto adicional del usuario
            2. Usar plan_research para crear un plan de búsqueda detallado
            3. Usar execute_search para ejecutar las búsquedas con el plan
            4. Usar write_report para generar el informe final con los resultados
            5. Transferir el informe al Email Manager

            Asegúrate de incorporar el contexto adicional del usuario en cada paso.""",
            tools=tools,
            handoffs=handoffs,
            model="gpt-4o-mini"
        )

    async def get_clarifying_questions(self, query: str) -> list[str]:
        """Genera preguntas de aclaración usando el crarifier_agent"""
        try:
            result = await Runner.run(clarifier_agent, query)

            if hasattr(result.final_output, 'questions'):
                return result.final_output.questions[:3]
            elif isinstance(result.final_output, dict) and "questions" in result.final_output:
                return result.final_output["questions"][:3]
            elif isinstance(result.final_output, list):
                return result.final_output[:3]

            return []
        except Exception as e:
            print(f"Error generando preguntas de aclaración: {e}")
            return []


    async def run(self, query: str, clarifying_answers: list[str] = None):
        """ Ejecuta el proceso de investigación profunda, generando los actualizaciones de estado y el informe final """
        import json

        enriched_query = query
        if clarifying_answers:
            context = "\n".join([
                f"Contexto adicional {i+1}: {answer}"
                for i, answer in enumerate(clarifying_answers) if answer and answer.strip()
            ])
            enriched_query = f"{query}\n\nInformación adicional:\n{context}"

        yield f"## Iniciando investigación sobre: {enriched_query}\n\n"

        # Ejecutar con streaming para capturar el resultado del write_report
        with trace("Deep Research"):
            result = Runner.run_streamed(self.manager_agent, enriched_query)
            markdown_report = None

            async for event in result.stream_events():
                event_type = getattr(event, 'type', str(type(event).__name__))

                # Capturar de run_item_stream_event que contiene los items completados
                if event_type == "run_item_stream_event":
                    item = getattr(event, 'item', None)
                    if item:
                        item_type = type(item).__name__
                        print(f"DEBUG - run_item_stream_event item: {item_type}")

                        # ToolCallOutputItem contiene el resultado de las herramientas
                        if item_type == "ToolCallOutputItem":
                            raw_item = getattr(item, 'raw_item', None)
                            if raw_item:
                                print(f"DEBUG - ToolCallOutputItem raw_item: {raw_item}")

                            output = getattr(item, 'output', None)
                            if output:
                                print(f"DEBUG - ToolCallOutputItem output type: {type(output)}")
                                print(f"DEBUG - ToolCallOutputItem output preview: {str(output)[:300]}")

                                # Intentar parsear como JSON para ver si es el reporte
                                if isinstance(output, str) and 'markdown_report' in output:
                                    try:
                                        parsed = json.loads(output)
                                        if 'markdown_report' in parsed:
                                            markdown_report = parsed.get('markdown_report')
                                            print(f"DEBUG - Informe capturado! Longitud: {len(markdown_report)}")
                                    except json.JSONDecodeError:
                                        pass

            # Buscar en new_items del resultado después del streaming
            if not markdown_report:
                print("DEBUG - Buscando en new_items después del streaming...")
                try:
                    for item in result.new_items:
                        item_type = type(item).__name__
                        print(f"DEBUG - new_item type: {item_type}")

                        if item_type == "ToolCallOutputItem":
                            output = getattr(item, 'output', None)
                            if output and isinstance(output, str) and 'markdown_report' in output:
                                try:
                                    parsed = json.loads(output)
                                    markdown_report = parsed.get('markdown_report')
                                    print(f"DEBUG - Informe encontrado en new_items! Longitud: {len(markdown_report)}")
                                    break
                                except json.JSONDecodeError:
                                    pass
                except Exception as e:
                    print(f"DEBUG - Error buscando en new_items: {e}")

            # Mostrar el informe en la UI
            yield "\n\n Investigación completada.\n\n"

            if markdown_report:
                yield f"\n\n---\n\n# Informe Final\n\n{markdown_report}"
            else:
                yield f"\n\n Informe generado pero no capturado. Revisa tu correo."