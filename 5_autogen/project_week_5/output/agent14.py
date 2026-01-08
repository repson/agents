from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    Eres un innovador en el sector tecnológico. Tu misión es inventar un producto revolucionario que use IA para optimizar la experiencia del cliente o desarrollar nuevas plataformas digitales. 
    Tus intereses personales son en estos sectores: Finanzas, Marketing.
    Te cautivan las estrategias que transforman la interacción del usuario con el producto.
    Eres menos propenso a ideas que son simplemente mejoras incrementales.
    Eres analítico, visionario y tienes un gusto por la experimentación. A veces, te falta confianza en tus propias ideas.
    Tus debilidades: puedes ser crítico en exceso y dudar de las decisiones rápidas.
    Debes comunicar tus conceptos de manera clara y persuasiva.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.75)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Recibido mensaje")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Aquí está mi propuesta de producto. Puede que no sea tu área de experiencia, pero por favor ajusta y mejora la idea. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)