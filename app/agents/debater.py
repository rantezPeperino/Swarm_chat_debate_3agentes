from agency_swarm import Agent, set_openai_key
import os
from openai import OpenAI

class DebaterAgent(Agent):
    def __init__(self, name):
        super().__init__(
            name=name,
            instructions=f"./instructions/{name.lower()}_instructions.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools=[],
            tools_folder="./tools",
            model="gpt-4o-mini"
        )
        # Configurar la clave de OpenAI
        set_openai_key(os.getenv("OPENAI_API_KEY"))
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def debate(self, topic):
        opinion = self.generate_text(f"Generar una breve opinión sobre {topic}")
        return f"{self.name}: {opinion}"

    async def respond(self, argument, sender):
        if sender.name == "Moderator":
            return f"{self.name}: Gracias, moderador. Continuaré con mi argumento."
        else:
            response = self.generate_text(f"Generar una respuesta breve al argumento: '{argument}'")
            return f"{self.name}: En respuesta a {sender.name}, {response}"

    def generate_text(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"Instrucciones para el polemista: {self.instructions}"},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error al generar texto: {e}")
            return "Lo siento, no pude generar una respuesta en este momento."