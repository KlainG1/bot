import disnake
import random
import time
import aiohttp
import os
import json
import sqlite3
import itertools
import asyncio
import datetime
from disnake import ui
from disnake.ext import commands
from disnake.ui import View, Button, Select, Item
import asyncio
import subprocess

bot = commands.Bot(command_prefix="!", help_command=None, intents=disnake.Intents.all())

CENSORED_WORDS = ["fook", "fooking", "cooking", "hacking", "penis", "хуй", "хуеcос", "suck"]

@bot.event
async def on_ready():
    print(f"{bot.user} готов!")

@bot.event
async def on_member_join(member):
    role = disnake.utils.get(member.guild.roles, id=1218969266163024022)
    
    # Указываем ID канала, в который будет отправлено приветственное сообщение
    welcome_channel_id = 1219644951067885568

    # Получаем объект канала по его ID
    welcome_channel = member.guild.get_channel(welcome_channel_id)
    
    embed = disnake.Embed(
        title="Поприветствуем нового участника!",
        description=f"{member.name}",
        color=0xf12345
    )

    await member.add_roles(role)
    await welcome_channel.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Игнорировать сообщения от других ботов
    if any(word in message.content.lower() for word in CENSORED_WORDS):
        await message.delete()
        await message.channel.send(f"{message.author.mention} такие слова запрещены!", delete_after=5)
        return  # Игнорировать сообщения с запрещенными словами

    muted_role = disnake.utils.get(message.guild.roles, name="Muted")
    if muted_role in message.author.roles:
        await message.delete()
        await message.author.send("Вы замучены и не можете писать в этом чате.", delete_after=5)
        return

    await bot.process_commands(message)

@bot.command()
async def avatar(ctx, member: disnake.Member = None):
    if member is None:
        member = ctx.author

    avatar_url = member.avatar.url
    embed = disnake.Embed(title=f"Ава {member.display_name}", color=member.color)
    embed.set_image(url=avatar_url)

    await ctx.send(embed=embed)

@bot.command()
async def banner(ctx, user: disnake.Member = None):
    target = user or ctx.author

    if target.banner:
        banner_image = await target.banner.read()
        await ctx.send(f"Баннер пользователя {target.display_name}:", file=disnake.File(banner_image, filename="banner.png"))
    else:
        await ctx.send(f"У пользователя {target.display_name} нет баннера.")

@bot.command()
async def botping(ctx):
    latency = round(ctx.bot.latency * 1000)  # Получаем пинг в миллисекундах
    await ctx.send(f"Мой текущий пинг составляет {latency} мс.")

@bot.command()
async def myping(ctx):
    latency = round(ctx.bot.latency * 1000)  # Получаем пинг в миллисекундах
    await ctx.send(f"Ваш текущий пинг составляет {latency} мс.")

@bot.command()
async def clear(ctx, amount: int):
    if ctx.author.guild_permissions.manage_messages:  
        await ctx.channel.purge(limit=amount + 1)  
        await ctx.send(f'Удалено {amount} сообщений.', delete_after=5)  
    else:
        await ctx.send("У вас нет разрешения на управление сообщениями.")

@bot.command()
async def slowmode(ctx, time: int):
    if ctx.author.guild_permissions.manage_channels:
        await ctx.channel.edit(slowmode_delay=time)
        await ctx.send(f"Медленный режим установлен на {time} секунд.")
    else:
        await ctx.send("У вас нет разрешения на управление каналами.")

@bot.command()
async def random_holiday(ctx):
    holidays = [
        "Новый год",
        "День Рождения",
        "День Святого Валентина",
        "Международный женский день",
        "День Победы",
        "День рождения моего кота",
        "День рождения моей собаки",
        "День дружбы",
        "День рождения друга",
        "День рождения подруги",
        "День программиста",
        "День смеха",
        "День рождения великой тети Марты"
    ]

    random_holiday = random.choice(holidays)
    await ctx.send(f"Сегодня отмечается: {random_holiday}!")

@bot.command()
async def say(ctx, *, message):
    # Отправляем сообщение в тот же канал, откуда пришла команда
    await ctx.send(message)

@bot.command()
async def random_meme(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://www.reddit.com/r/memes/random.json", headers={"User-Agent": "Mozilla/5.0"}) as response:
            data = await response.json()
            meme = data[0]["data"]["children"][0]["data"]
            meme_title = meme["title"]
            meme_url = meme["url"]

            embed = disnake.Embed(title=meme_title, color=disnake.Color.random())
            embed.set_image(url=meme_url)

            await ctx.send(embed=embed)

@bot.command()
async def help(ctx):
    embed = disnake.Embed(title="Справка по командам", color=disnake.Color.blurple())
    embed.add_field(name="!avatar [пользователь]", value="Показывает аватар пользователя.", inline=False)
    embed.add_field(name="!banner [пользователь]", value="Показывает баннер пользователя.", inline=False)
    embed.add_field(name="!botping", value="Показывает пинг бота.", inline=False)
    embed.add_field(name="!myping", value="Показывает ваш пинг.", inline=False)
    embed.add_field(name="!clear [количество]", value="Удаляет сообщения в чате.", inline=False)
    embed.add_field(name="!slowmode [время]", value="Устанавливает режим замедления на канале.", inline=False)
    embed.add_field(name="!random_holiday", value="Показывает случайный праздник.", inline=False)
    embed.add_field(name="!random_meme", value="Показывает случайный мем.", inline=False)
    embed.add_field(name="!warn [пользователь] [причина]", value="Выдает предупреждение пользователю.", inline=False)
    embed.add_field(name="!warnings [пользователь]", value="Показывает предупреждения пользователя.", inline=False)
    embed.add_field(name="!kick [пользователь] [причина]", value="Кикает пользователя с сервера.", inline=False)
    embed.add_field(name="!ban [пользователь] [причина]", value="Банит пользователя на сервере.", inline=False)
    embed.add_field(name="!mute [пользователь] [время] [причина]", value="Выдает мут пользователю.", inline=False)
    embed.add_field(name="!unmute [пользователь]", value="Снимает мут с пользователя.", inline=False)
    embed.add_field(name="!unban [пользователь]", value="Разбанивает пользователя.", inline=False)
    embed.add_field(name="!dog", value="Показывает случайное изображение собаки.", inline=False)
    embed.add_field(name="!giveaway [время] [приз]", value="Запускает розыгрыш с указанным временем и призом.", inline=False)
    embed.add_field(name="!random_number [начало] [конец]", value="Генерирует случайное число в заданном диапазоне.", inline=False)
    embed.add_field(name="!magicball [вопрос]", value="Шар говорит 'Да' или 'Нет' на ваш вопрос.", inline=False)
    embed.add_field(name="!help", value="Показывает эту справку.", inline=False)

    await ctx.send(embed=embed)



@bot.command()
async def userinfo(ctx, member: disnake.Member = None):
    member = member or ctx.author
    embed = disnake.Embed(title=f"Информация о {member}", color=member.color)
    embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="Имя пользователя", value=member.name)
    embed.add_field(name="Тэг пользователя", value=member.discriminator)
    embed.add_field(name="ID пользователя", value=member.id)
    embed.add_field(name="Присоединился", value=member.joined_at.strftime("%d.%m.%Y %H:%M:%S"))
    embed.add_field(name="Аккаунт создан", value=member.created_at.strftime("%d.%m.%Y %H:%M:%S"))
    embed.add_field(name="Статус", value=member.status)
    embed.add_field(name="Активность", value=member.activity if member.activity else "Нет активности")
    await ctx.send(embed=embed)

@bot.command()
async def activity(ctx, member: disnake.Member = None):
    member = member or ctx.author
    if member.activity:
        await ctx.send(f"{member} активен {member.activity}")
    else:
        await ctx.send(f"{member} не имеет активности в данный момент.")

@bot.command()
async def poll(ctx, question, *options):
    if len(options) > 10:
        await ctx.send("Максимальное количество вариантов ответа - 10.")
        return

    if len(options) < 2:
        await ctx.send("Должно быть как минимум два варианта ответа.")
        return

    # Создание встроенного сообщения для голосования
    embed = disnake.Embed(title="Голосование", description=question, color=disnake.Color.green())

    # Добавление вариантов ответа в описание сообщения
    for index, option in enumerate(options):
        embed.add_field(name=f"Вариант {index+1}", value=option, inline=False)

    # Отправка сообщения с голосованием и добавление реакций
    message = await ctx.send(embed=embed)
    for i in range(len(options)):
        await message.add_reaction(chr(0x1F1E6 + i))

    await ctx.message.delete()  # Удаление сообщения-команды

@bot.command()
async def magicball(ctx, question):
    responses = ["Да", "Нет", "Возможно", "Неуверен", "Однозначно да", "Однозначно нет"]
    response = random.choice(responses)
    await ctx.send(f"Шар говорит: {response}")

@bot.command()
async def random_number(ctx, start: int, end: int):
    if start > end:
        await ctx.send("Начальное значение должно быть меньше конечного значения.")
        return
    random_num = random.randint(start, end)
    await ctx.send(f"Случайное число между {start} и {end}: {random_num}")

@bot.command()
async def dog(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://random.dog/woof.json") as response:
            data = await response.json()
            dog_url = data["url"]
            await ctx.send(dog_url)

@bot.command()
async def giveaway(ctx, duration: int, prize: str):
    await ctx.send(f"🎉 Розыгрыш на сервере! 🎉\n\nПриз: {prize}\n\nРозыгрыш продлится {duration} минут.\nЧтобы принять участие, нажмите на реакцию ниже!")
    message = await ctx.send("🎉 Реагируйте на это сообщение, чтобы участвовать в розыгрыше! 🎉")
    await message.add_reaction("🎉")
    await asyncio.sleep(duration * 60)
    message = await ctx.channel.fetch_message(message.id)
    reactions = message.reactions
    participants = []
    for reaction in reactions:
        if reaction.emoji == "🎉":
            async for user in reaction.users():
                if user != bot.user:
                    participants.append(user)
    if len(participants) > 0:
        winner = random.choice(participants)
        await ctx.send(f"🎉 Поздравляем {winner.mention} с победой в розыгрыше! Приз: {prize}! 🎉")
    else:
        await ctx.send("🎉 Розыгрыш завершился, но никто не принял в нем участие. Следующий раз повезет! 🎉")

@bot.command()
async def uptime(ctx):
    uptime_seconds = int(time.time() - bot.start_time)
    uptime_str = str(datetime.timedelta(seconds=uptime_seconds))
    await ctx.send(f"Время работы бота: {uptime_str}")

# Словарь для хранения предупреждений
warnings = {}

class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def warn(self, ctx, member: disnake.Member, *, reason="Не указана"):
        if member.bot:
            return await ctx.send("Нельзя выдавать предупреждения ботам.")
        
        if ctx.author.top_role <= member.top_role:
            return await ctx.send("Вы не можете давать предупреждения этому пользователю, так как у него или у вас одинаковая или более высокая роль.")
        
        user_id = str(member.id)
        if user_id not in warnings:
            warnings[user_id] = {"count": 0, "expiry": None}

        warnings[user_id]["count"] += 1
        warnings[user_id]["expiry"] = datetime.datetime.utcnow() + datetime.timedelta(days=1)

        await ctx.send(f"{member.mention} получил предупреждение за {reason}. Это его {warnings[user_id]['count']}-е предупреждение.")

        if warnings[user_id]["count"] >= 3:
            await member.kick(reason="Достигнут лимит предупреждений (3).")

    @commands.command()
    async def warnings(self, ctx, member: disnake.Member):
        user_id = str(member.id)
        if user_id not in warnings:
            return await ctx.send("У этого пользователя нет предупреждений.")

        await ctx.send(f"У пользователя {member.display_name} {warnings[user_id]['count']} предупреждений. Следующее предупреждение будет истекать {warnings[user_id]['expiry']}.")
bot.add_cog(Warn(bot))

@bot.command()
@commands.has_permissions(kick_members=True, administrator=True)
async def kick(ctx, member: disnake.Member, *, reason=None):
    await ctx.send(f"Пользователь {member.mention} будет исключен по причине: **{reason}**.", delete_after=5)
    await asyncio.sleep(1)
    await member.kick(reason=reason)

@bot.command(name="бан", aliases=["баня", "банан", "ban"])
@commands.has_permissions(ban_members=True, administrator=True)
async def ban(ctx, member: disnake.Member, duration: int=None, *, reason=None):
    if duration:
        hours, minutes = divmod(duration, 60)
        time_str = f"{hours} часов {minutes} минут" if hours else f"{minutes} минут"
        await ctx.send(f"Пользователь {member.mention} будет забанен на **{time_str}** по причине: **{reason}**.", delete_after=5)
        await asyncio.sleep(1)
        await member.ban(reason=reason)
        await asyncio.sleep(duration * 60)
        await member.unban()
    else:
        await ctx.send(f"Пользователь {member.mention} будет забанен навсегда по причине: **{reason}**.", delete_after=5)
        await asyncio.sleep(1)
        await member.ban(reason=reason)

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Пожалуйста, укажите пользователя для бана.")

@bot.command()
@commands.has_permissions(kick_members=True, administrator=True)
async def mute(ctx, member: disnake.Member, duration: int=None, *, reason=None):
    mute_role = disnake.utils.get(ctx.guild.roles, name="Muted")

    if not mute_role:
        await ctx.send("Роль для мута не найдена. Создайте роль с названием 'Muted' и настройте ее права.")
        return

    if duration:
        hours, minutes = divmod(duration, 60)
        time_str = f"{hours} часов {minutes} минут" if hours else f"{minutes} минут"
        await ctx.send(f"Пользователь {member.mention} будет замучен на **{time_str}** по причине: **{reason}**.", delete_after=5)
        await asyncio.sleep(1)
        await member.add_roles(mute_role, reason=reason)
        await asyncio.sleep(duration * 60)
        await member.remove_roles(mute_role)
    else:
        await ctx.send(f"Пользователь {member.mention} будет замучен навсегда по причине: **{reason}**.", delete_after=5)
        await asyncio.sleep(1)
        await member.add_roles(mute_role, reason=reason)

@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Пожалуйста, укажите пользователя для мута.")

@bot.command()
@commands.has_permissions(kick_members=True, administrator=True)
async def unmute(ctx, member: disnake.Member):
    mute_role = disnake.utils.get(ctx.guild.roles, name="Muted")

    if not mute_role:
        await ctx.send("Роль для мута не найдена.")
        return

    await member.remove_roles(mute_role)
    await ctx.send(f"{member.mention} был размучен.", delete_after=5)

@unmute.error
async def unmute_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Пожалуйста, укажите пользователя для размута.") 

@bot.command()
@commands.has_permissions(ban_members=True, administrator=True)
async def unban(ctx, member_id: int):
    banned_users = await ctx.guild.bans()

    for ban_entry in banned_users:
        user = ban_entry.user

        if user.id == member_id:
            await ctx.guild.unban(user)
            await ctx.send(f"Пользователь {user.mention} был разбанен.", delete_after=5)
            await ctx.message.delete()
            return

    await ctx.send("Пользователь не найден в списке забаненных.")

@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Пожалуйста, укажите ID пользователя для разбана.")

bot.run("MTIwNjY4ODg0MTY2Mjk5NjU1MQ.Gnve_J.4YUKIcVSrX0kDNauDG0KKFL8f1FkuHX-57rg54")