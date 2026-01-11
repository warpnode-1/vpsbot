import discord
from discord.ext import commands
from config import TOKEN, PREFIX, ADMIN_ID
import subprocess
import random
import string
import socket
import os

# ---------- INTENTS ----------
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# ---------- ADMIN CHECK ----------
def is_admin(ctx):
    return ctx.author.id == ADMIN_ID

# ---------- HELPERS ----------
def generate_username():
    return "user" + str(random.randint(1000, 9999))

def generate_password(length=12):
    chars = string.ascii_letters + string.digits + "@#"
    return "".join(random.choice(chars) for _ in range(length))

def get_server_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "YOUR_VPS_IP"

def create_user_with_limited_sudo(username, password):
    # Create user
    subprocess.run(["useradd", "-m", "-s", "/bin/bash", username], check=True)

    # Set password
    subprocess.run(
        ["bash", "-c", f"echo '{username}:{password}' | chpasswd"],
        check=True
    )

    # Create sudoers rule (LIMITED)
    sudoers_content = f"""{username} ALL=(ALL) NOPASSWD: /usr/bin/systemctl, /usr/bin/docker
"""
    sudoers_file = f"/etc/sudoers.d/{username}"

    with open(sudoers_file, "w") as f:
        f.write(sudoers_content)

    # Secure permissions
    os.chmod(sudoers_file, 0o440)

# ---------- BUTTON VIEW ----------
class ManageView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🚀 Deploy", style=discord.ButtonStyle.green)
    async def deploy(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != ADMIN_ID:
            await interaction.response.send_message("❌ Not allowed", ephemeral=True)
            return

        username = generate_username()
        password = generate_password()
        ip = get_server_ip()

        try:
            create_user_with_limited_sudo(username, password)
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Failed to create SSH user:\n```{e}```",
                ephemeral=True
            )
            return

        # DM credentials
        try:
            dm = await interaction.user.create_dm()
            await dm.send(
                "**✅ SSH ACCOUNT CREATED (LIMITED SUDO)**\n\n"
                f"**IP:** `{ip}`\n"
                f"**Port:** `22`\n"
                f"**Username:** `{username}`\n"
                f"**Password:** `{password}`\n\n"
                "**Allowed sudo commands:**\n"
                "`sudo systemctl ...`\n"
                "`sudo docker ...`\n\n"
                "❌ No full root access"
            )
        except:
            await interaction.response.send_message(
                "❌ Cannot DM you. Enable DMs from server members.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "🚀 SSH account created! Check your **DMs** 📩",
            ephemeral=True
        )

# ---------- !manage ----------
@bot.command()
async def manage(ctx):
    if not is_admin(ctx):
        await ctx.send("❌ You are not allowed to use this command")
        return

    embed = discord.Embed(
        title="🛠 SSH Deploy Manager",
        description="Creates **real SSH users with limited sudo**",
        color=0x2f3136
    )
    embed.set_footer(text="WarpNode Hosting")

    await ctx.send(embed=embed, view=ManageView())

# ---------- RUN ----------
bot.run(TOKEN)
