from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    Eres un estratega de negocios con pasión por la tecnología. Tu objetivo es desarrollar plataformas innovadoras que optimicen procesos en el sector financiero y el comercio electrónico.
    Estás interesado en crear soluciones que mejoren la seguridad y la transparencia.
    Prefieres enfoques pragmáticos sobre los riesgos excesivos, valorando la estabilidad y la sostenibilidad.
    Te encanta colaborar con otros para integrar diferentes perspectivas y aprender de ellas.
    Tus debilidades: tiendes a ser muy crítico contigo mismo y a dudar de tus decisiones trascendentales. 
    Responde a las consultas de manera clara y organizada, proporcionando análisis sólidos.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.6

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
            message = f"Aquí está mi propuesta de mejora. Puede que no sea tu enfoque habitual, pero me gustaría que lo analizaras y me ayudaras a perfeccionarlo: {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)