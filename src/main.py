import threading
import asyncio
from web import app
from bot import bot

def run_flask():
    app.app.run(host="0.0.0.0", port=3000) # T_T

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    asyncio.run(bot.run_async())
