from agency_swarm import Agent, set_openai_key
import os
from openai import OpenAI

class ModeratorAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Moderator",
            instructions="./instructions/moderator_instructions.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools=[],
            tools_folder="./tools",
            model="gpt-4o-mini"
        )
        # Configurar la clave de OpenAI
        set_openai_key(os.getenv("OPENAI_API_KEY"))
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def response_validator(self, message):
        if isinstance(message, str) and len(message) > 0:
            return message
        else:
            return "Mensaje inválido"

    async def start_debate(self, topic):
        intro = self.generate_text(f"Generar una breve introducción para un debate sobre el tema.: {topic}")
        return f"Moderador: {intro} Comencemos con el primer participante."

    async def moderate(self, message, sender):
        if sender.name.startswith("Debater"):
            comment = self.generate_text(f"Generar un breve comentario del moderador sobre el argumento.: '{message}'")
            return f"Moderador: {comment} Ahora pasemos al otro participante."
        else:
            return f"Moderador: Por favor, mantengamos el orden en el debate."

    def generate_text(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"Instrucciones del moderador: {self.instructions}"},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error al generar texto: {e}")
            return "Lo siento, no pude generar una respuesta en este momento."