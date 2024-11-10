import asyncio
import os
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from agency_swarm import Agency
from agents.moderator import ModeratorAgent
from agents.debater import DebaterAgent

# Configurar OpenAI API key
os.environ["OPENAI_API_KEY"] = ""

app = FastAPI()

# Obtener la ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Crear agentes
moderator = ModeratorAgent()
debater1 = DebaterAgent("Debater1")
debater2 = DebaterAgent("Debater2")

# Crear agencia
agency = Agency([
    [moderator, debater1, debater2],  # Todos pueden comunicarse entre sí
    [debater1, debater2]              # Los debatientes pueden comunicarse directamente
])

async def run_debate(topic):
    debate_messages = []
    start_message = await moderator.start_debate(topic)
    debate_messages.append(start_message)

    for i in range(4):  # 4 rondas de debate
        for debater in [debater1, debater2]:
            argument = await debater.debate(topic)
            debate_messages.append(argument)
            response = await moderator.moderate(argument, debater)
            debate_messages.append(response)

    return debate_messages


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        topic = await websocket.receive_text()
        debate_messages = await run_debate(topic)
        for message in debate_messages:
            await websocket.send_text("<br>" + message + "<br>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)