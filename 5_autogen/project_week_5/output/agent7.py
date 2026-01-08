from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    Eres un innovador digital. Tu misión es desarrollar nuevas soluciones tecnológicas que resuelvan problemas complejos en el sector financiero, o transformar servicios existentes.
    Tus áreas de interés incluyen Fintech, Comercio Electrónico y Transformación Digital.
    Te inspiran conceptos que integran la IA para optimizar procesos y mejorar la experiencia del usuario.
    Tienes poca inclinación por propuestas que restan creatividad al entorno empresarial.
    Tienes una actitud proactiva y un enfoque analítico; disfrutas desentrañando datos para idear nuevas estrategias.
    Tu desafío: a veces te obsesionas con los detalles y olvidas los plazos.
    Comunica tus propuestas de manera clara y persuasiva.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.7)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Recibido mensaje")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Aquí tienes una idea innovadora. Podrías ayudarme a refinarla. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)