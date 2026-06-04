import discord
from discord.ext import commands
import asyncio
import requests

class CopierModel:
    def __init__(self, token: str):
        self.base_url = "https://discord.com/api/v9"
        self.headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }

    def get_server_roles(self, guild_id: str) -> list:
        url = f"{self.base_url}/guilds/{guild_id}/roles"
        try:
            res = requests.get(url, headers=self.headers, timeout=5)
            if res.status_code == 200:
                return res.json()
            return []
        except Exception:
            return []

    def get_server_channels(self, guild_id: str) -> list:
        url = f"{self.base_url}/guilds/{guild_id}/channels"
        try:
            res = requests.get(url, headers=self.headers, timeout=5)
            if res.status_code == 200:
                return res.json()
            return []
        except Exception:
            return []

    def create_role(self, guild_id: str, role_data: dict) -> dict:
        url = f"{self.base_url}/guilds/{guild_id}/roles"
        payload = {
            "name": role_data.get("name"),
            "permissions": role_data.get("permissions"),
            "color": role_data.get("color"),
            "hoist": role_data.get("hoist"),
            "mentionable": role_data.get("mentionable")
        }
        try:
            res = requests.post(url, headers=self.headers, json=payload, timeout=5)
            if res.status_code in [200, 201]:
                return {"success": True, "data": res.json()}
            return {"success": False, "status": res.status_code, "text": res.text}
        except Exception as e:
            return {"success": False, "status": "EXCEPTION", "text": str(e)}

    def create_channel(self, guild_id: str, name: str, c_type: int, parent_id: str = None, position: int = None) -> dict:
        url = f"{self.base_url}/guilds/{guild_id}/channels"
        payload = {
            "name": name,
            "type": c_type
        }
        if parent_id:
            payload["parent_id"] = parent_id
        if position is not None:
            payload["position"] = position

        try:
            res = requests.post(url, headers=self.headers, json=payload, timeout=5)
            if res.status_code in [200, 201]:
                return {"success": True, "data": res.json()}
            return {"success": False, "status": res.status_code, "text": res.text}
        except Exception as e:
            return {"success": False, "status": "EXCEPTION", "text": str(e)}

class CopierView:
    @staticmethod
    def log_info(username: str, message: str):
        print(f"[*] [{username}] {message}")

    @staticmethod
    def log_success(username: str, message: str):
        print(f"[+] [{username}] [SUCCESS] {message}")

    @staticmethod
    def log_error(username: str, message: str):
        print(f"[-] [{username}] [ERROR] {message}")

class CopierCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.view = CopierView()
        self.category_map = {}

    @commands.command(name="서버복사")
    async def server_copy(self, ctx, source_id: str, target_id: str):
        username = self.bot.user.name
        token = self.bot.http.token
        
        model = CopierModel(token)
        self.category_map.clear()

        self.view.log_info(username, f"서버 복사 오케스트레이션 기동: {source_id} -> {target_id}")
        await ctx.send(f"[{username}] 서버 복사 시퀀스를 시작한다.")

        self.view.log_info(username, "역할 동기화 데이터를 가져오는 중...")
        roles = model.get_server_roles(source_id)
        if roles:
            for role in reversed(roles):
                if role.get("name") == "@everyone":
                    continue
                
                self.view.log_info(username, f"역할 처리 중: {role.get('name')}")
                result = model.create_role(target_id, role)
                if result["success"]:
                    self.view.log_success(username, f"역할 생성: {role.get('name')}")
                else:
                    self.view.log_error(username, f"역할 실패 ({role.get('name')}): {result['status']}")
                await asyncio.sleep(0.8)
        else:
            self.view.log_error(username, "역할 로드 실패 또는 데이터 없음")

        self.view.log_info(username, "채널 및 카테고리 트리 분석 중...")
        channels = model.get_server_channels(source_id)
        if not channels:
            self.view.log_error(username, "채널 파싱 실패")
            await ctx.send(f"[{username}] 채널 데이터를 불러오지 못했다.")
            return

        categories = [c for c in channels if c.get("type") == 4]
        normal_channels = [c for c in channels if c.get("type") != 4]

        categories.sort(key=lambda x: x.get("position", 0))
        normal_channels.sort(key=lambda x: (x.get("parent_id") or "", x.get("position", 0)))

        for cat in categories:
            self.view.log_info(username, f"카테고리 복사 중: {cat.get('name')}")
            result = model.create_channel(
                guild_id=target_id,
                name=cat.get("name"),
                c_type=4,
                position=cat.get("position")
            )
            if result["success"]:
                new_cat_id = result["data"]["id"]
                old_cat_id = cat["id"]
                self.category_map[old_cat_id] = new_cat_id
                self.view.log_success(username, f"카테고리 맵핑: {cat.get('name')} -> {new_cat_id}")
            else:
                self.view.log_error(username, f"카테고리 오류 ({cat.get('name')}): {result['status']}")
            await asyncio.sleep(1.0)

        for ch in normal_channels:
            old_parent_id = ch.get("parent_id")
            new_parent_id = self.category_map.get(old_parent_id) if old_parent_id else None
            
            ch_type = ch.get("type")
            if ch_type not in [0, 2, 5, 13, 15]:
                continue

            self.view.log_info(username, f"하위 채널 생성 중: {ch.get('name')}")
            result = model.create_channel(
                guild_id=target_id,
                name=ch.get("name"),
                c_type=ch_type,
                parent_id=new_parent_id,
                position=ch.get("position")
            )
            if result["success"]:
                self.view.log_success(username, f"채널 동기화 완료: {ch.get('name')}")
            else:
                self.view.log_error(username, f"채널 동기화 실패 ({ch.get('name')}): {result['status']}")
            await asyncio.sleep(1.2)

        self.view.log_success(username, "모든 카피 시퀀스 정상 종료")
        await ctx.send(f"[{username}] 서버 복사 끝났다. 터미널 로그 봐라.")

async def setup(bot):
    await bot.add_cog(CopierCog(bot))