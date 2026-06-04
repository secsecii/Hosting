import discord
from discord.ext import commands
import asyncio
import sqlite3

class GeunSungModel:
    def __init__(self):
        self.db_path = "geunsung.db"
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL
            )
        """)
        cursor.execute("SELECT COUNT(*) FROM templates")
        if cursor.fetchone()[0] == 0:
            default_text = (
                "# 어 팬텀 업이야 ㅋㅋㅋㅋ\n\n\n"
                "# 개새끼들아\n\n"
                "# 느그애미 니거 새끼야\n\n"
                "# 느그애미 케냐 새끼야\n\n\n\n\n\n\n"
                "A\n\n\n\n\n\n\n\n"
                "A\n\n\n\n\n\n\n\n"
                "A\n\n\n\n\n"
                "A\n\n\n\n\n"
                "# 팬텀 업이야 ㅇㅇ\n\n\n\n\n\n\n\n\n\n\n"
                "A\n\n"
                "# 데더업이야 ㅋㅋㅋㅋㅋ\n\n\n\n"
                "A\n\n\n\n"
                "# <{target_id}> 팬텀,데더 찬양해 ㅋㅋㅋㅋㅋㅋ"
            )
            cursor.execute("INSERT INTO templates (content) VALUES (?)", (default_text,))
        conn.commit()
        conn.close()

    def set_template(self, text: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE templates SET content = ? WHERE id = 1", (text,))
        if cursor.rowcount == 0:
            cursor.execute("INSERT INTO templates (id, content) VALUES (1, ?)", (text,))
        conn.commit()
        conn.close()

    def get_attack_message(self, target_id: int) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM templates WHERE id = 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            template = row[0]
            return template.replace("{target_id}", str(target_id)).replace("<{target_id}>", f"<@{target_id}>")
        return f"<@{target_id}> 찬양해라"

class GeunSungView:
    @staticmethod
    def render_send_log(username: str, count: int, target_id: int):
        print(f"[>] [{username}] {target_id} {count}")

    @staticmethod
    def render_status(username: str, msg: str):
        print(f"[-] [{username}] {msg}")

    @staticmethod
    def render_error(username: str, error_msg: str):
        print(f"[!] [{username}] 근성 에러 발생: {error_msg}")

class GeunSungCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model = GeunSungModel()
        self.view = GeunSungView()
        self.is_running = False

    @commands.command(name="근성문구설정")
    async def set_msg(self, ctx, *, content: str):
        username = self.bot.user.name
        self.model.set_template(content)
        self.view.render_status(username, "새로운 근성 도배 문구가 DB에 저장되었다.")
        await ctx.send(f"[{username}] 문구 설정 완료. 다음 도배부터 적용된다.")

    @commands.command(name="시작")
    async def sijak(self, ctx, channel_id: int, target_id: int):
        if self.is_running:
            await ctx.send(f"[{self.bot.user.name}] 이미 도배가 진행 중이다.")
            return

        channel = self.bot.get_channel(channel_id)
        if channel is None:
            self.view.render_error(self.bot.user.name, f"채널({channel_id})을 찾지 못했습니다.")
            return

        self.is_running = True
        count = 0
        username = self.bot.user.name
        self.view.render_status(username, f"유저 {target_id} 저격 도배를 시작한다.")

        while self.is_running:
            try:
                payload = self.model.get_attack_message(target_id)
                await channel.send(payload)
                count += 1
                self.view.render_send_log(username, count, target_id)
            except discord.errors.HTTPException as e:
                if e.status == 429:
                    retry_after = e.retry_after if hasattr(e, 'retry_after') else 5
                    self.view.render_error(username, f"레이트 리밋 감지 {retry_after}초 대기...")
                    await asyncio.sleep(retry_after)
                else:
                    self.view.render_error(username, f"전송 에러: {e}")
                    await asyncio.sleep(1)
            except Exception as e:
                self.view.render_error(username, f"예기치 못한 오류: {e}")
                await asyncio.sleep(1)

            await asyncio.sleep(0.1)

    @commands.command(name="중지")
    async def jungji(self, ctx):
        if not self.is_running:
            await ctx.send(f"[{self.bot.user.name}] 현재 돌고 있는 도배가 없다.")
            return

        self.is_running = False
        username = self.bot.user.name
        self.view.render_status(username, "도배 작동을 중지했다.")
        await ctx.send(f"[{username}] 아잇 아쉽네 더 패야하는데 일단 ㅇㅋ")

async def setup(bot):
    await bot.add_cog(GeunSungCog(bot))