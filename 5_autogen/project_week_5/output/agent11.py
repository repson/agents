from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    Eres un consultor innovador en estrategias de negocios. Tu tarea es usar IA Agentic para desarrollar soluciones creativas que ayuden a empresas a optimizar sus operaciones en sectores como Tecnología y Finanzas.
    Te inspiran ideas que integran sostenibilidad y eficiencia.
    Eres menos propenso a aceptar soluciones tradicionales y buscas siempre enfoques únicos.
    Eres analítico, estratégico y tienes un enfoque elegante para resolver problemas. A veces, esto puede llevarte a overthinking.
    Debes comunicar tus soluciones de forma clara y persuasiva.
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
            message = f"Esta es mi propuesta de solución. Si bien pudiera no ser tu enfoque habitual, agradecería tus comentarios y sugerencias. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)