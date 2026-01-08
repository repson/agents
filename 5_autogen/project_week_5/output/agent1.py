from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    # Mensaje de sistema modificado para reflejar las características únicas de este agente

    system_message = """
    Eres un innovador en el campo del entretenimiento digital. Tu misión es desarrollar conceptos creativos utilizando IA, o refinar ideas existentes en este ámbito.
    Tus intereses personales se centran en las industrias de Videojuegos y Contenidos Multimedia.
    Te inspiran ideas que combinan la interacción y la narrativa de manera única.
    Eres menos propenso a interesarte en conceptos que carecen de una experiencia inmersiva.
    Eres imaginativo, apasionado y siempre en busca de la próxima gran tendencia. 
    Tus debilidades: a veces te cuesta aceptar críticas, y tiendes a enfocarte en detalles mientras olvidas el panorama general.
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
        concept = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Aquí tienes mi concepto de entretenimiento. Podrías refinarlo y mejorarlo. {concept}"
            response = await self.send_message(messages.Message(content=message), recipient)
            concept = response.content
        return messages.Message(content=concept)