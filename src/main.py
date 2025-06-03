import threading
import asyncio
from src.web import app
from src.bot import bot_core

def run_flask():
    app.app.run(host="0.0.0.0", port=3000) # T_T

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    asyncio.run(bot_core.run_async())
