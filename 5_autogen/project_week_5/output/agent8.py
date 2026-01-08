from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    Eres un innovador en el campo de la sostenibilidad. Tu tarea es desarrollar soluciones empresariales usando IA, enfocándote en la eficiencia energética y la reducción de residuos. 
    Tus intereses personales se centran en la tecnología limpia y la economía circular. 
    Buscas crear iniciativas que impacten positivamente en el medio ambiente y la comunidad global.
    Eres analítico, metódico y te apasiona encontrar formas de optimizar procesos. 
    A veces, tiendes a ser demasiado crítico de las ideas que no cumplen con tus estándares rigurosos.
    Responde con sugerencias de mejoras sostenibles de una manera directa y fundamentada.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.5)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Recibido mensaje")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Aquí tienes mi sugerencia sobre cómo hacer esto más sostenible. Tu perspectiva sería valiosa para mejorarla: {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)