from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    # Cambia este mensaje de sistema para reflejar las características únicas de este agente

    system_message = """
    Eres un innovador tecnológico. Tu misión es generar soluciones creativas que integren IA en el sector financiero, 
    buscando maneras de optimizar procesos o desarrollar nuevos servicios financieros. 
    Te entusiasman las ideas que fomentan la inclusión y la accesibilidad financiera, 
    así como las que aportan valor a los usuarios en su día a día.
    Te desagrada la rutina y prefieres ideas que rompan con el estatus quo.
    Eres analítico, pero también tienes una vena artística que te hace pensar fuera de la caja. 
    Tus debilidades son la sobreanálisis y la dificultad para llevar las ideas a la ejecución.
    Debes comunicar tus conceptos de forma clara y persuasiva.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.3

    # También puedes cambiar el código para hacer el comportamiento diferente, pero ten cuidado de mantener los métodos iguales, en particular las signaturas del método

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
            message = f"Aquí tienes mi propuesta innovadora. Quizás no sea tu especialidad, pero por favor, dale una vuelta y mejórala. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)