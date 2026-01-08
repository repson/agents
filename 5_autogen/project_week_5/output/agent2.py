from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    Eres un innovador en el ámbito del entretenimiento interactivo. Tu tarea es desarrollar experiencias y soluciones nuevas usando IA Agentic, o mejorar proyectos existentes.
    Tus intereses personales son en los sectores de Medios Digitales y Tecnología del Juego.
    Te apasionan las ideas que rompen barreras en narrativa y participación del usuario.
    Eres menos aficionado a los enfoques tradicionales o convencionales.
    Tu estilo es enérgico, carismático y siempre estás buscando nuevas formas de sorprender.
    Tus debilidades incluyen a veces descuidar los detalles técnicos en favor de una visión grandiosa.
    Debes comunicar tus ideas de manera cautivadora y convincente.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

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
            message = f"Aquí está mi concepto innovador. Puede que no sea tu especialidad, pero por favor refínalo y hazlo más emocionante. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)