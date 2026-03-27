import discord
import json
import os
import time
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="-", intents=intents)

DATA_FILE = "scores.json"
COOLDOWN_SECONDS = 600
cooldowns = {}

def load_scores():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_scores(scores):
    with open(DATA_FILE, "w") as f:
        json.dump(scores, f, indent=2)

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")

@bot.command()
async def mooc(ctx, member: discord.Member):
    if member.id == ctx.author.id:
        await ctx.send("Tu peux pas te mooc toi-même")
        return

    key = f"{ctx.author.id}-{member.id}"
    now = time.time()

    if key in cooldowns and now - cooldowns[key] < COOLDOWN_SECONDS:
        remaining = int(COOLDOWN_SECONDS - (now - cooldowns[key]))
        minutes = remaining // 60
        seconds = remaining % 60
        await ctx.send(f"Cooldown actif, encore {minutes}m{seconds}s avant de re-mooc {member.display_name}.")
        return

    cooldowns[key] = now
    scores = load_scores()
    uid = str(member.id)
    scores[uid] = scores.get(uid, 0) + 1
    save_scores(scores)

    await ctx.send(f"{member.mention} s'est fait mooc par {ctx.author.display_name} ! Total : **{scores[uid]} mooc** 📚")

@bot.command()
async def leaderboard(ctx):
    scores = load_scores()
    if not scores:
        await ctx.send("Aucun mooc enregistré pour l'instant.")
        return

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    lines = []
    medals = ["🥇", "🥈", "🥉"]

    for i, (uid, count) in enumerate(sorted_scores):
        member = ctx.guild.get_member(int(uid))
        name = member.display_name if member else f"Utilisateur inconnu ({uid})"
        prefix = medals[i] if i < 3 else f"`{i+1}.`"
        lines.append(f"{prefix} **{name}** — {count} mooc")

    embed = discord.Embed(title="🏆 Classement des moocs", description="\n".join(lines), color=0xFF4444)
    await ctx.send(embed=embed)

bot.run(os.getenv("TOKEN"))