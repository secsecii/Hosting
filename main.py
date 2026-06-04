import asyncio
import os
import discord
from discord.ext import commands
from config import Config

class SelfBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=Config.PREFIX, self_bot=True, help_command=None)

    async def setup_hook(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")

    async def on_ready(self):
        print(f"Logged in as: {self.user.name} ({self.user.id})")

async def main():
    bot = SelfBot()
    try:
        await bot.start(Config.TOKEN)
    except discord.LoginFailure:
        print("Invalid Token")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())