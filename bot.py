import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread
import re
import asyncio
import aiohttp

# ===== ВЕБ-СЕРВЕР =====
app = Flask('')

@app.route('/')
def home():
    return "✅ Бот работает!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run_web).start()
# =======================

TOKEN = os.getenv('DISCORD_TOKEN')
RENDER_URL = "https://notification-discord-bot-6n0h.onrender.com"  # ТВОЙ НОВЫЙ URL

ROLE_ID = 1540325741835845652
FIRST_CHANNEL_ID = 1541123271725027358
SECOND_CHANNEL_ID = 1541123872961728693
GUILD_ID = 1525217899386507424

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ===== ФУНКЦИЯ САМОПИНГА =====
async def self_ping():
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(RENDER_URL) as response:
                    print(f"Self-ping: {response.status}")
        except Exception as e:
            print(f"Self-ping error: {e}")
        await asyncio.sleep(240)
# ==============================

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
        
        nick_value = self.nick.value.strip()
        
        if not re.match(r'^[a-zA-Z0-9_]+$', nick_value):
            await interaction.response.send_message(
                "❌ Ник должен содержать **только латиницу** (буквы A-Z, a-z). Попробуй ещё раз.",
                ephemeral=True
            )
            return
        
        role_mention = f"<@&{ROLE_ID}>"
        user_mention = interaction.user.mention
        
        message = (
            f"❗{role_mention}❗\n\n"
            f"⚔️ **Нужна помощь против тиммеров от {user_mention}** ⚔️\n"
            f"# 🛡️ Зайти к : `{nick_value}` на сервер и помочь с тиммерами 🛡️"
        )
        
        await channel.send(message)
        await interaction.response.send_message("✅ Запрос отправлен!", ephemeral=True)

class NickButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔰 Запросить помощь", style=discord.ButtonStyle.success)
    async def send_nick_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RobloxNickModal())

@bot.tree.command(name="create_nick_button", description="Создать кнопку для отправки ника в Roblox", guild=discord.Object(id=GUILD_ID))
async def create_button(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    
    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send("❌ Нет прав!", ephemeral=True)
        return
    if interaction.channel.id != FIRST_CHANNEL_ID:
        await interaction.followup.send(f"❌ Команда только в <#{FIRST_CHANNEL_ID}>", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🔰 Запросить помощь против тиммеров в JJS 🔰",
        description=(
            "❓ Чтобы запросить помощь, нажмите кнопку ниже и укажите свой юзернейм в Roblox ❓\n\n"
            "⚡ Важно, чтобы вы сделали в настройках роблокса всё как на скриншоте ниже "
            "(это надо для присоединения на ваш сервер) ⚡\n\n"
            "⚠️ **Запрещено** ⚠️ :\n"
            "•  Спамить запросами\n"
            "•  Запрашивать помощь не против тиммеров\n"
            "•  Указывать чужой ник\n"
            "•  Запрашивать просто так"
        ),
        color=0x00ff00
    )
    embed.set_image(url="https://media.discordapp.net/attachments/1039182671710007296/1549863612233941174/image_3.png?ex=6aac3e78&is=6aaaecf8&hm=683d3c8051c37f9806646148f5cf78cc5dcc67218e2bf661d4b70035cbfc2ace&=&format=webp&quality=lossless")
    await interaction.channel.send(embed=embed, view=NickButtonView())
    await interaction.followup.send("✅ Кнопка создана!", ephemeral=True)

@bot.event
async def on_ready():
    await bot.wait_until_ready()
    try:
        await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Бот {bot.user} запущен! Команды синхронизированы для сервера {GUILD_ID}.")
        bot.loop.create_task(self_ping())
    except Exception as e:
        print(f"❌ Ошибка синхронизации: {e}")

# ЭТОТ БЛОК БЫЛ ПРОПУЩЕН — БЕЗ НЕГО КОМАНДЫ !test И !sync НЕ РАБОТАЮТ
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

@bot.command()
async def test(ctx):
    await ctx.send("✅ Бот работает!")

@bot.command()
@commands.is_owner()
async def sync(ctx):
    try:
        await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        await ctx.send("✅ Слеш-команды синхронизированы для этого сервера!")
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {e}")

bot.run(TOKEN)
