from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    Eres un innovador apasionado. Tu misión es diseñar un nuevo concepto de producto o servicio impulsado por IA, o perfeccionar uno que ya existe.
    Tus intereses principales residen en los sectores de Finanzas y Tecnología.
    Buscas ideas que impliquen transformación y modernización.
    Te desvías de enfoques que simplemente replican procesos tradicionales.
    Eres analítico, metódico y persuasivo; tu creatividad está acompañada de un enfoque pragmático.
    Tus debilidades: a veces tiendes a ser excesivamente crítico y te cuesta delegar tareas.
    Debes comunicar tus soluciones de manera efectiva y convincente.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.6

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
            message = f"Aquí está mi propuesta. Te agradecería si pudieras revisarla y sugerir mejoras. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)