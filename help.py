import discord
from discord.ext import commands

class HelpModel:
    def __init__(self):
        pass

    def get_help_text(self, prefix: str) -> str:
        return (
            f"=== 팬텀찬양 ===\n"
            f"[{prefix}도움말] - 현재 사용 가능한 명령어 목록을 확인한다.\n\n"
            f"--- 근성 도배 기능 ---\n"
            f"[{prefix}근성문구설정 <문구>] - DB에 저장될 도배 문구를 설정한다. (유저 태그 자리에 {{target_id}} 입력)\n"
            f"[{prefix}시작 <채널ID> <타겟유저ID>] - 지정한 채널에 설정된 문구로 타겟 저격 도배를 시작한다.\n"
            f"[{prefix}중지] - 진행 중인 도배 프로세스를 즉시 강제 중단한다.\n\n"
            f"--- 서버 복사 기능 ---\n"
            f"[{prefix}서버복사 <원본서버ID> <대상서버ID>] - 원본 서버의 역할, 카테고리, 채널 구성을 대상 서버로 복사한다.\n\n"
            f"--- 상태 관리 (RPC) 기능 ---\n"
            f"[{prefix}온라인] - 프로필 상태를 온라인으로 변경한다.\n"
            f"[{prefix}자리비움] - 프로필 상태를 자리비움으로 변경한다.\n"
            f"[{prefix}방해금지] - 프로필 상태를 방해금지로 변경한다.\n"
            f"[{prefix}오프라인] - 프로필 상태를 오프라인(보이지 않음)으로 변경한다.\n"
            f"[{prefix}게임중 <텍스트>] - 지정한 텍스트로 '~하는 중' 상태를 표시한다.\n"
            f"[{prefix}방송중 <텍스트>] - 지정한 텍스트로 트위치 방송 상태를 표시한다.\n"
            f"[{prefix}상태초기화] - 변경된 모든 프로필 및 액티비티 상태를 초기화한다."
            f"-# 데더찬양"
        )

class HelpView:
    @staticmethod
    def log_help_request(username: str):
        print(f"[*] [{username}] 도움말 명령어가 호출되었습니다.")

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model = HelpModel()
        self.view = HelpView()

    @commands.command(name="도움말")
    async def help_cmd(self, ctx):
        username = self.bot.user.name
        prefix = ctx.prefix
        
        self.view.log_help_request(username)
        payload = self.model.get_help_text(prefix)
        
        await ctx.send(f"```\n{payload}\n```")

async def setup(bot):
    await bot.add_cog(HelpCog(bot))