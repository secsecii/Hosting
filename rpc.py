import discord
from discord.ext import commands
import json
import os

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = "status.json"
        self.all_data = {}

        self.bot.loop.create_task(self.init())

    async def init(self):
        await self.bot.wait_until_ready()

        self.all_data = self.load_data()

        self.bot_id = str(self.bot.user.id)

        self.data = self.all_data.get(self.bot_id, {})

        await self.apply_status()

    def load_data(self):
        if os.path.exists(self.file):
            with open(self.file, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except:
                    return {}
        return {}

    def save_data(self):
        self.all_data[self.bot_id] = self.data
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(self.all_data, f, indent=4)

    async def apply_status(self):
        await self.bot.wait_until_ready()

        status = self.data.get("status")
        activity = self.data.get("activity")

        if not status and not activity:
            return

        kwargs = {}

        if status:
            kwargs["status"] = getattr(discord.Status, status)

        if activity:
            kwargs["activity"] = self.build_activity(activity)

        await self.bot.change_presence(**kwargs)

    def build_activity(self, data):
        if not data:
            return None

        return discord.Activity(
            type=getattr(discord.ActivityType, data["type"]),
            name=data["name"],
            url=data.get("url")
        )

    @commands.command(name="방해금지")
    async def dnd(self, ctx):
        self.data = {"status": "dnd", "activity": None}
        self.save_data()

        await self.bot.change_presence(status=discord.Status.dnd)
        await ctx.send("```방해금지 상태로 변경되었습니다.```")

    @commands.command(name="자리비움")
    async def idle(self, ctx):
        self.data = {"status": "idle", "activity": None}
        self.save_data()

        await self.bot.change_presence(status=discord.Status.idle)
        await ctx.send("```자리비움 상태로 변경되었습니다.```")

    @commands.command(name="온라인")
    async def online(self, ctx):
        self.data = {"status": "online", "activity": None}
        self.save_data()

        await self.bot.change_presence(status=discord.Status.online)
        await ctx.send("```온라인 상태로 변경되었습니다.```")

    @commands.command(name="오프라인")
    async def offline(self, ctx):
        self.data = {"status": "invisible", "activity": None}
        self.save_data()

        await self.bot.change_presence(status=discord.Status.invisible)
        await ctx.send("```오프라인 상태로 변경되었습니다.```")

    @commands.command(name="게임중")
    async def playing(self, ctx, *, msg: str):
        self.data = {
            "status": None,
            "activity": {"type": "playing", "name": msg}
        }
        self.save_data()

        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name=msg
            )
        )
        await ctx.send(f"```게임중 상태로 변경되었습니다.```**```{msg}```**")

    @commands.command(name="방송중")
    async def streaming(self, ctx, *, msg: str):
        self.data = {
            "status": None,
            "activity": {
                "type": "streaming",
                "name": msg,
                "url": "https://twitch.tv/rpc"
            }
        }
        self.save_data()

        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.streaming,
                name=msg,
                url="https://twitch.tv/rpc"
            )
        )
        await ctx.send(f"```방송중 상태로 변경되었습니다.```**```{msg}```**")

    @commands.command(name="상태초기화")
    async def reset_status(self, ctx):
        self.data = {}
        self.save_data()

        await self.bot.change_presence()
        await ctx.send("```상태가 초기화 되었습니다.```")

async def setup(bot):
    await bot.add_cog(Status(bot))