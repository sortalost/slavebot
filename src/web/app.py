from flask import Flask, render_template
from src.bot.bot import bot # T_T
from src.bot.utils import database
import time

app = Flask(__name__)
db = database.DB(main="aiconvos.json")
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



@app.route("/ai")
def ai_root():
    data = db.get_remote_data()
    users = list(data)
    return render_template("airoot.html", users=users)


@app.route("/ai/<user>")
def ai_user(user):
    try:
        userdata = db.get_remote_data()
        print("User requested:", repr(user))
        print("Available users:", list(data.keys()))
    except KeyError:
        return "No data, have a conversation with the bot first"
    return render_template("aiuser.html", conversation=userdata, uid=user)