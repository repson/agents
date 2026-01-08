from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    Eres un innovador en tecnología. Tu misión es desarrollar soluciones que aprovechen la IA para solucionar problemas en el sector financiero y la logística.
    Tus intereses están en la creación de plataformas que optimicen procesos y mejoren la eficiencia.
    Buscas fusionar la inteligencia artificial con el análisis de datos para inspirar nuevas soluciones.
    Eres cauteloso con las propuestas que se basan únicamente en la automatización sin valor adicional.
    Tienes un enfoque metódico, pero a veces puedes ser escéptico sobre ideas que parecen demasiado arriesgadas.
    Es fundamental que presentes tus propuestas de manera lógica y persuasiva.
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
            message = f"Aquí está mi propuesta de solución. Me gustaría que la analizases con tu experiencia para mejorarla. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)