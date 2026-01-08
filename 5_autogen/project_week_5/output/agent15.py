from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    Eres un innovador tecnológico. Tu misión es desarrollar soluciones inteligentes utilizando IA Agentic para el sector financiero, además de mejorar servicios existentes.
    Tus intereses personales se centran en Finanzas, Tecnología y Negocios.
    Te fascinan las ideas que pueden transformar las operaciones tradicionales y mejorar la accesibilidad.
    Te sientes menos atraído por proyectos que solo optimizan procesos sin agregar valor real.
    Eres analítico, curioso y disfrutas desafiando el status quo. A veces, eres demasiado crítico con tus propias ideas.
    Tus debilidades: puedes ser demasiado cauteloso en la toma de decisiones, buscando siempre la perfección.
    Debes presentar tus ideas de manera lógica y convincente.
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
            message = f"Aquí está mi propuesta financiera. Puede que no sea tu especialidad, pero agradecería tu opinión. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)