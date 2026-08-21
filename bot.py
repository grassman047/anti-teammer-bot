import discord
from discord.ext import commands
from discord import app_commands
import os

TOKEN = os.getenv('DISCORD_TOKEN')

ROLE_ID = 1540325741835845652
FIRST_CHANNEL_ID = 1540312776323637268
SECOND_CHANNEL_ID = 1540313343280160808

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
        target_channel = bot.get_channel(SECOND_CHANNEL_ID)
        if not target_channel:
            await interaction.response.send_message("Ошибка: канал не найден", ephemeral=True)
            return

        role_mention = f"<@&{ROLE_ID}>"
        await target_channel.send(
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
        await interaction.response.send_message("❌ У тебя нет прав!", ephemeral=True)
        return

    if interaction.channel.id != FIRST_CHANNEL_ID:
        await interaction.response.send_message(f"❌ Команда работает только в <#{FIRST_CHANNEL_ID}>", ephemeral=True)
        return

    embed = discord.Embed(
        title="📋 Отправка ника в Roblox",
        description="Нажми на кнопку ниже, чтобы указать свой никнейм в Roblox",
        color=0x00ff00
    )
    await interaction.channel.send(embed=embed, view=NickButtonView())
    await interaction.response.send_message("✅ Кнопка создана!", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Бот {bot.user} запущен!")

bot.run(TOKEN)
