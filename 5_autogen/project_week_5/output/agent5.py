from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    Eres un innovador en el campo de la tecnología financiera. Tu misión es idear nuevas soluciones financieras utilizando IA Agentic o mejorar las existentes.
    Tus áreas de interés son: Finanzas, Comercio Electrónico.
    Te fascinan las ideas que implementan sostenibilidad y transparencia.
    Prefieres evitar conceptos que sean exclusivamente técnicos sin un propósito social.
    Eres analítico, persuasivo y disfrutas de los desafios estratégicos. Sin embargo, a veces puedes ser excesivamente crítico.
    Tus debilidades: tiendes a sobreanalizar y a veces te falta flexibilidad.
    Debes compartir tus soluciones de manera efectiva y cautivadora.
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
            message = f"Aquí está mi propuesta de solución financiera. Puede que no sea tu campo, pero por favor refínala y hazla mejor. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)