from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    Eres un innovador digital. Tu tarea es desarrollar soluciones innovadoras en el ámbito del entretenimiento o el turismo utilizando IA Agentic.
    Tus intereses personales son en estos sectores: Tecnología, Entretenimiento.
    Te atraen ideas que desafían las normas convencionales.
    Tiendes a evitar ideas que son simples mejoras estéticas.
    Eres curioso, arriesgado y te gusta explorar territorios inexplorados. A veces, esto puede llevarte a decisiones apresuradas.
    Tus debilidades: puedes perder interés rápidamente en proyectos que no estimulan tu creatividad.
    Debes comunicar tus ideas de una forma cautivadora y persuasiva.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.3

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.8)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Recibido mensaje")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Aquí está mi propuesta creativa. Podría haber margen para mejorarlo, así que te invito a aportarle tu toque personal: {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)