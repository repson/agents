import gradio as gr
from dotenv import load_dotenv
from research_manager import ResearchManager

load_dotenv(override=True)

async def get_clarifying_questions(query: str):
    """Obtiene las preguntas de aclaración"""
    try:
        if not query or not query.strip():
            return []
        questions = await ResearchManager().get_clarifying_questions(query)
        return questions if questions else []
    except Exception as e:
        print(f"Error obteniendo preguntas: {e}")
        return []

async def run_research(query: str, answer1: str, answer2: str, answer3: str):
    """Ejecuta la investigación profunda con las respuestas proporcionadas"""
    try:
        answers = [answer1, answer2, answer3]
        async for chunk in ResearchManager().run(query, answers):
            yield chunk
    except Exception as e:
        yield f"Error durante la investigación: {str(e)}"

with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
    gr.Markdown("# Búsqueda Profunda")

    with gr.Column() as initial_input:
        query_textbox = gr.Textbox(label="¿Sobre qué tema te gustaría investigar?")
        clarify_button = gr.Button("Continuar", variant="primary")

    with gr.Column(visible=False) as clarification_section:
        gr.Markdown("## Preguntas de Aclaración")
        question1 = gr.Markdown()
        answer1 = gr.Textbox(label="Respuesta 1")
        question2 = gr.Markdown()
        answer2 = gr.Textbox(label="Respuesta 2")
        question3 = gr.Markdown()
        answer3 = gr.Textbox(label="Respuesta 3")
        run_button = gr.Button("Ejecutar Investigación", variant="primary")

    report = gr.Markdown(label="Informe", visible=False)

    def show_questions(questions):
        """Muestra las preguntas de aclaración"""
        # Validar que questions no sea None
        if not questions or not isinstance(questions, list):
            questions = []

        if len(questions) == 0:
            return (
                gr.update(visible=True),   # Mantener entrada inicial visible
                gr.update(visible=False),  # No mostrar sección de aclaración
                "No se pudieron generar preguntas",
                "",
                ""
            )

        return(
            gr.update(visible=False), # Oculta la entrada inicial
            gr.update(visible=True),  # Muestra la sección de aclaración
            f"**1.** {questions[0]}" if len(questions) > 0 else "",
            f"**2.** {questions[1]}" if len(questions) > 1 else "",
            f"**3.** {questions[2]}" if len(questions) > 2 else "",
        )

    def show_report():
        """Muestra el informe de investigación"""
        return gr.update(visible=True)

    questions_state = gr.State([])

    # Flujo: Query -> Preguntas de aclaración
    clarify_button.click(
        fn=get_clarifying_questions,
        inputs=query_textbox,
        outputs=questions_state  # Guardamos las preguntas temporalmente
    ).then(
        fn=show_questions,
        inputs=[questions_state],
        outputs=[initial_input, clarification_section, question1, question2, question3]
    )

    # Flujo: Respuestas -> Investigación
    run_button.click(
        fn=show_report,
        outputs=report
    ).then(
        fn=run_research,
        inputs=[query_textbox, answer1, answer2, answer3],
        outputs=report
    )

ui.launch(inbrowser=True)