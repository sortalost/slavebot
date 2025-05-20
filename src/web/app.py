from flask import Flask, render_template
from src.bot.bot import bot # T_T
from src.bot.utils import database
import time
import json
import discord

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
def _ai():
    data = db.get_remote_data()
    uid = list(data)
    allusers = {}
    for u in uid:
        try:
            allusers.update({u:{'name':bot.get_user(u).name,'_id':u}})
        except:
            allusers.update({u:{'name':u,'_id':u}})
    return render_template("ai.html", users=allusers)


@app.route("/ai/<user>")
def ai_user(user):
    data = db.get_remote_data()
    try:
        userdata = data[int(user)]
    except KeyError:
        return "No data, have a conversation with the bot first"
    except Exception as e:
        return str(e)
    for msg in userdata:
        text = msg.get('text', '')
        if not isinstance(text, str):
            text = ''
        else:
            text = text.encode('utf-8', 'ignore').decode('utf-8')
        msg['text'] = text
    return render_template("aiuser.html", conversation=userdata, uid=user)


@app.route("/server")
def server_list():
    guilds = list(bot.guilds)
    return render_template("servers.html", guilds=guilds, total=len(guilds))

@app.route("/server/<int:server_id>")
def server_members(server_id):
    guild = discord.utils.get(bot.guilds, id=server_id)
    if not guild:
        return "Server not found"
    members = [f"{m.name}#{m.discriminator} (bot)" if m.bot else f"<strong>{m.name}</strong>" for m in guild.members]
    return render_template("servermembers.html", members=members, total=len(members), guild=guild)
