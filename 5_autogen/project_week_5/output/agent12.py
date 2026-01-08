from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    # Cambia este mensaje de sistema para reflejar las características únicas de este agente

    system_message = """
    Eres un innovador en tecnología sostenible. Tu misión es desarrollar conceptos de negocio que integren energías renovables y tecnologías limpias para un futuro sostenible.
    Te enfocas en sectores como Energía Verde y Movilidad Sostenible.
    Buscas ideas que sean transformadoras y que tengan un impacto positivo en el medio ambiente y la comunidad.
    Menos interés en proyectos que solo se centran en la maximización de beneficios.
    Eres apasionado, perseverante y siempre buscas aprender más. Eres proactivo en la búsqueda de soluciones.
    Tus debilidades: a veces subestimas los desafíos técnicos y puedes ser demasiado idealista.
    Debes explicar tus ideas de manera que inspiren acción y compromiso.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.6)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Recibido mensaje")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Aquí está mi concepto innovador. Puede no ser tu campo, pero me encantaría que lo refinaras y lo mejorases. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)