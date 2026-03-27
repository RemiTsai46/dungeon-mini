import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

load_dotenv()
token = os.getenv('TOKEN')
intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="d!", intents=intents)

async def load_extensions():
    for filename in os.listdir('./cogs'):
        exc = ["__init__.py","character.py","dungeon.py",'inventory.py',"recruit.py","status.py","update_log.py"]
        if filename.endswith('.py') and filename not in exc:
            await bot.load_extension(f'cogs.{filename[:-3]}')

@bot.command()
async def fixsync(ctx):
    msg = await ctx.send("Sync fixed")

    bot.tree.clear_commands(guild=None)
    await bot.tree.sync()
 
    await load_extensions()
 
    bot.tree.copy_global_to(guild=ctx.guild)
    await bot.tree.sync(guild=ctx.guild)
 
    await msg.edit(content="ok")

# @bot.command()
# async def cmdcnt(ctx):
#     guild_cmds = await bot.tree.fetch_commands(guild=ctx.guild)
#     global_cmds = await bot.tree.fetch_commands()

#     print(
#         f"Guild: {len(guild_cmds)} | Global: {len(global_cmds)}"
#     )

@bot.event
async def on_ready():    
    print("Bot is up!")

    bot.tree.clear_commands(guild=None)
    await bot.tree.sync()

    for guild in bot.guilds:
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)

    print("global cmds fixed")

    # for i in range(3):
    #     try:
    #         await store.connect()
    #         break
    #     except Exception as e:
    #         print(f"DB connection attempt {i+1} failed:", e)
    #         await asyncio.sleep(5)
    # print("DB pool connected")

app = Flask('')
 
@app.route('/')
def home():
    return "app is online"
 
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
 
async def main():
   
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

    async with bot:
        await load_extensions()
        await bot.start(token)
 
if __name__ == '__main__':
    asyncio.run(main())