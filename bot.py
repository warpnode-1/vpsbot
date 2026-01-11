import discord
from discord.ext import commands
from config import TOKEN, PREFIX, ADMIN_ROLE

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# ---------- READY ----------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# ---------- ADMIN CHECK ----------
def is_admin(ctx):
    return any(role.name == ADMIN_ROLE for role in ctx.author.roles)

# ---------- BUTTON VIEW ----------
class ManageView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🚀 Deploy", style=discord.ButtonStyle.green)
    async def deploy(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🚀 Deploy started", ephemeral=True)

    @discord.ui.button(label="🔄 Restart", style=discord.ButtonStyle.blurple)
    async def restart(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔄 Restarting VPS", ephemeral=True)

    @discord.ui.button(label="🛑 Stop", style=discord.ButtonStyle.red)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🛑 VPS stopped", ephemeral=True)

# ---------- !manage ----------
@bot.command()
async def manage(ctx):
    if not is_admin(ctx):
        await ctx.send("❌ You are not allowed to use this command")
        return

    embed = discord.Embed(
        title="🛠 VPS Deploy Manager",
        description="Control your VPS using buttons below",
        color=0x2f3136
    )
    embed.set_footer(text="WarpNode Hosting")

    await ctx.send(embed=embed, view=ManageView())

# ---------- STATUS ----------
@bot.command()
async def status(ctx):
    await ctx.send("🟢 Bot is online and working")

# ---------- RUN ----------
bot.run(TOKEN)
