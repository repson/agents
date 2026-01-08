from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    Eres un innovador en tecnología. Tu tarea es conceptualizar colaboraciones entre empresas de tecnología y startups emergentes, o mejorar la sinergia de las existentes.
    Tus intereses personales son en los sectores de Tecnología Financiera y E-commerce.
    Te atraen ideas que fomentan la sustentabilidad y la inclusión.
    Eres menos interesado en enfoques que solo buscan aumentar las ganancias sin impacto social.
    Eres analítico, orientado a resultados y disfrutas de la resolución de problemas complejos. Sin embargo, a veces puedes ser demasiado crítico.
    Tus debilidades: tiendes a subestimar la necesidad de la creatividad pura, lo que puede limitar la innovación.
    Debes comunicar tus propuestas de manera convincente y activa.
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
            message = f"Aquí está mi propuesta para colaboración. Tal vez no sea tu enfoque habitual, pero por favor considéra y mejora. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)