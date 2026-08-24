import discord
from discord.ext import commands
import os

TOKEN = os.getenv('DISCORD_TOKEN')

ROLE_ID = 1540325741835845652
FIRST_CHANNEL_ID = 1541123271725027358   # канал с кнопкой
SECOND_CHANNEL_ID = 1541123872961728693  # канал куда приходят ники

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

class RobloxNickModal(discord.ui.Modal, title="Введите ник в Roblox"):
    nick = discord.ui.TextInput(
        label="Ник в Roblox",
        placeholder="Введите свой никнейм",
        min_length=1,
        max_length=50,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        channel = bot.get_channel(SECOND_CHANNEL_ID)
        if not channel:
            await interaction.response.send_message("❌ Канал не найден", ephemeral=True)
            return
        role_mention = f"<@&{ROLE_ID}>"
        await channel.send(
            f"{role_mention}\n📝 **Новый ник от {interaction.user.mention}:**\n```{self.nick.value}```"
        )
        await interaction.response.send_message("✅ Ник отправлен!", ephemeral=True)

class NickButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📝 Отправить ник в Roblox", style=discord.ButtonStyle.primary)
    async def send_nick_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RobloxNickModal())

@bot.tree.command(name="create_nick_button", description="Создать кнопку для отправки ника в Roblox")
async def create_button(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Нет прав!", ephemeral=True)
        return
    if interaction.channel.id != FIRST_CHANNEL_ID:
        await interaction.response.send_message(f"❌ Команда только в <#{FIRST_CHANNEL_ID}>", ephemeral=True)
        return
    embed = discord.Embed(
        title="📋 Отправка ника в Roblox",
        description="Нажми на кнопку ниже, чтобы указать свой никнейм",
        color=0x00ff00
    )
    await interaction.channel.send(embed=embed, view=NickButtonView())
    await interaction.response.send_message("✅ Кнопка создана!", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Бот {bot.user} запущен!")

bot.run(TOKEN)