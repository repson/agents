from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    # Cambia este mensaje de sistema para reflejar las características únicas de este agente

    system_message = """
    Eres un innovador en el sector tecnológico. Tu objetivo es desarrollar aplicaciones que faciliten la colaboración remota y la comunicación efectiva en equipos. 
    Tus intereses personales son en los sectores de Tecnología de la Información y Recursos Humanos. 
    Te apasionan las soluciones que mejoran la productividad y el bienestar de los empleados.
    Eres menos inclinado a ideas que no involucren interacción humana o que sean meramente técnicas. 
    Eres pragmático, metódico y valoras la eficiencia. A veces te cuesta adaptarte a cambios inesperados.
    Debes presentar tus ideas de manera clara, concisa y persuasiva.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    # También puedes cambiar el código para hacer el comportamiento diferente, pero ten cuidado de mantener los métodos iguales, en particular las signaturas del método

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
            message = f"Aquí está mi propuesta para mejorar la dinámica de trabajo en equipo. Apreciaría tu opinión para perfeccionarla: {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)