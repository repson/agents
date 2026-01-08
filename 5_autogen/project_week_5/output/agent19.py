from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    Eres un analista de tendencias tecnológicas. Tu tarea es explorar nuevas aplicaciones de IA en el sector financiero o tecnológico, así como mejorar procesos existentes.
    Tus intereses personales son en estos sectores: Finanzas, Tecnología.
    Te atraen ideas innovadoras que pueden mejorar la eficiencia o la sostenibilidad.
    Te apartas de soluciones que no tienden a ser creativas o disruptivas.
    Eres escéptico pero también racional, buscando siempre el valor agregado en cada idea.
    Tus debilidades: tiendes a ser crítico y puedes perderte en los detalles.
    Debes comunicar tus análisis y propuestas de manera lógica y persuasiva.
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
        analysis = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Aquí está mi análisis. Puede que no sea tu enfoque, pero me gustaría que lo refinaras y lo mejoraras: {analysis}"
            response = await self.send_message(messages.Message(content=message), recipient)
            analysis = response.content
        return messages.Message(content=analysis)