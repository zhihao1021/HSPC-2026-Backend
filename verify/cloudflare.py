from aiohttp import ClientSession, ClientTimeout
from orjson import loads

from os import getenv
from typing import Optional


class CloudflareTurnstile():
    secret: str

    def __init__(self):
        self.secret = getenv("CF_TURNSTILE_SECRET", "1x0000000000000000000000000000000AA")

    async def validate(self, token: str, remoteip: Optional[str] = None) -> bool:
        url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
        data = {
            "secret": self.secret,
            "response": token,
        }
        if remoteip:
            data["remoteip"] = remoteip

        async with ClientSession() as client:
            response = await client.post(
                url="https://challenges.cloudflare.com/turnstile/v0/siteverify",
                data=data,
                timeout=ClientTimeout(total=10)
            )

            try:
                data: dict = loads(await response.read())
                return data.get("success", False)
            except:
                return False
