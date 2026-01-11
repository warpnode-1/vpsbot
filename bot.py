import discord
from discord.ext import commands
import subprocess
import os
import random
import datetime

from config import TOKEN, PREFIX

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

DATA_DIR = "vps_data"
os.makedirs(DATA_DIR, exist_ok=True)


# ---------- HELPERS ----------

def user_file(user_id):
    return f"{DATA_DIR}/{user_id}.txt"


def has_vps(user_id):
    return os.path.exists(user_file(user_id))


def read_vps(user_id):
    with open(user_file(user_id), "r") as f:
        return f.read().splitlines()


def write_vps(user_id, data):
    with open(user_file(user_id), "w") as f:
        f.write("\n".join(data))


# ---------- EVENTS ----------

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


# ---------- MANAGE COMMAND ----------

@bot.command(name="mange")
async def manage(ctx):
    user_id = ctx.author.id

    if not has_vps(user_id):
        embed = discord.Embed(
            title="⭐ LazyCloud - No VPS Found",
            description="You don't have any active VPS.\nContact an admin to create one.",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Quick Actions",
            value="• `!mange` - Manage VPS\n• Contact admin for VPS creation",
            inline=False
        )
        await ctx.send(embed=embed)
        return

    data = read_vps(user_id)

    container = data[0]
    created = data[1]

    embed = discord.Embed(
        title="⚙️ VPS Management Panel",
        color=discord.Color.green()
    )
    embed.add_field(name="Container", value=container, inline=False)
    embed.add_field(name="Status", value="Running", inline=False)
    embed.add_field(name="Created On", value=created, inline=False)
    embed.add_field(
        name="Commands",
        value="`!start`\n`!stop`\n`!reinstall`",
        inline=False
    )

    await ctx.send(embed=embed)


# ---------- START ----------

@bot.command()
async def start(ctx):
    user_id = ctx.author.id

    if not has_vps(user_id):
        await ctx.send("❌ You don't have a VPS.")
        return

    container = read_vps(user_id)[0]
    subprocess.run(["docker", "start", container])
    await ctx.send("✅ VPS started successfully.")


# ---------- STOP ----------

@bot.command()
async def stop(ctx):
    user_id = ctx.author.id

    if not has_vps(user_id):
        await ctx.send("❌ You don't have a VPS.")
        return

    container = read_vps(user_id)[0]
    subprocess.run(["docker", "stop", container])
    await ctx.send("⛔ VPS stopped successfully.")


# ---------- REINSTALL ----------

@bot.command()
async def reinstall(ctx):
    user_id = ctx.author.id

    if not has_vps(user_id):
        await ctx.send("❌ You don't have a VPS.")
        return

    container = read_vps(user_id)[0]

    subprocess.run(["docker", "rm", "-f", container])

    subprocess.run([
        "docker", "run", "-dit",
        "--name", container,
        "--hostname", container,
        "ubuntu:22.04",
        "sleep", "infinity"
    ])

    await ctx.send("♻️ VPS reinstalled successfully.")


# ---------- ADMIN CREATE VPS ----------

@bot.command()
async def create_vps(ctx, member: discord.Member):
    container = f"vps-{member.id}-{random.randint(1000,9999)}"

    subprocess.run([
        "docker", "run", "-dit",
        "--name", container,
        "--hostname", container,
        "ubuntu:22.04",
        "sleep", "infinity"
    ])

    created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    write_vps(member.id, [container, created])

    embed = discord.Embed(
        title="⭐ LazyCloud - VPS Created!",
        color=discord.Color.green()
    )
    embed.add_field(name="Container", value=container, inline=False)
    embed.add_field(name="OS", value="Ubuntu 22.04", inline=False)
    embed.add_field(name="Status", value="Running", inline=False)
    embed.add_field(name="Manage", value="Use `!mange`", inline=False)

    await member.send(embed=embed)
    await ctx.send("✅ VPS created successfully.")


# ---------- RUN ----------

bot.run(TOKEN)
