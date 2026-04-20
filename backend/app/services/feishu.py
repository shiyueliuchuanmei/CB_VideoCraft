"""
飞书 OAuth2.0 服务
"""
import httpx
from urllib.parse import urlencode
from app.config import settings


class FeishuService:
    """飞书 API 服务"""

    FEISHU_OAUTH_URL = "https://open.feishu.cn/open-apis/authen/v1/authorize"
    FEISHU_TOKEN_URL = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"
    FEISHU_USER_INFO_URL = "https://open.feishu.cn/open-apis/authen/v1/user_info"

    def get_authorization_url(self, state: str = "") -> str:
        """生成飞书授权 URL"""
        params = {
            "app_id": settings.FEISHU_APP_ID,
            "redirect_uri": settings.FEISHU_REDIRECT_URI,
            "state": state,
            "response_type": "code",
        }
        return f"{self.FEISHU_OAUTH_URL}?{urlencode(params)}"

    async def get_access_token(self, code: str) -> dict:
        """用 code 换取 access_token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.FEISHU_TOKEN_URL,
                json={
                    "grant_type": "authorization_code",
                    "code": code,
                    "app_id": settings.FEISHU_APP_ID,
                    "app_secret": settings.FEISHU_APP_SECRET,
                },
                headers={
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            data = response.json()

            if data.get("code") != 0:
                raise Exception(f"飞书 API 错误: code={data.get('code')}, msg={data.get('msg')}")

            return data.get("data", {})

    async def get_user_info(self, access_token: str) -> dict:
        """获取飞书用户信息"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.FEISHU_USER_INFO_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
            )
            response.raise_for_status()
            data = response.json()

            if data.get("code") != 0:
                raise Exception(f"飞书 API 错误: {data.get('msg')}")

            return data.get("data", {})


feishu_service = FeishuService()
