from flask import Flask, render_template
from bot.bot import bot # T_T
import time

app = Flask(__name__)

start_time = time.time()

@app.route("/")
def index():
    uptime = round(time.time() - start_time)
    servers = len(bot.guilds)
    users = sum(g.member_count for g in bot.guilds)
    return render_template("index.html", uptime=uptime, servers=servers, users=users)

@app.route("/commands")
def commands():
    commands_list = [
        {
            "name": cmd.name,
            "help": cmd.help or "No description",
            "aliases": cmd.aliases
        }
        for cmd in bot.commands if not cmd.hidden
    ]
    return render_template("commands.html", commands=commands_list)