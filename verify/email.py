from asyncpg import Connection
from pydantic_snowflake import SnowflakeId

from asyncio import get_running_loop
from datetime import timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from os import getenv
from smtplib import SMTP
from urllib.parse import unquote_plus, urlencode

from auth.exceptions import INVALID_TOKEN
from auth.type import JWTPayload
from auth.utils import sign_token, verify_token
from schemas.user import User
from type import ScopeType


class VerifyManager():
    username: str
    password: str
    host: str
    port: int
    sender: str
    use_tls: bool = True
    external_url: str
    discord_link: str
    template: str

    def __init__(self) -> None:
        self.username = getenv("SMTP_USERNAME", "")
        self.password = getenv("SMTP_PASSWORD", "")
        self.host = getenv("SMTP_HOST", "")
        self.port = int(getenv("SMTP_PORT", "587"))
        self.sender = getenv("SMTP_SENDER", "")
        self.use_tls = getenv("SMTP_USE_TLS", "true").lower() in (
            "true", "1", "yes")
        self.external_url = getenv("VERIFY_URL", "http://localhost:8000")
        self.discord_link = getenv("DISCORD_LINK", "")
        self.verify_code_map = {}

        with open("email_template.html", "r", encoding="utf-8") as f:
            self.template = f.read()

    def _send_email(self, email: str, message: str) -> None:
        if getenv("DEBUG", "false").lower() in ("true", "1", "yes"):
            print(f"DEBUG MODE: Email to {email} with content:\n{message}")
            return

        with SMTP(self.host, self.port) as smtp:
            if self.use_tls:
                smtp.starttls()
            smtp.login(self.username, self.password)
            smtp.sendmail(self.sender, email, message)
            smtp.close()

    async def send_email(self, uid: str, email: str) -> None:
        token_payload = JWTPayload(
            uid=uid,
            scopes=set([ScopeType.USE_EMAIL])
        )
        token_payload.exp = token_payload.iat + timedelta(minutes=30)
        jwt = sign_token(token_payload).access_token

        encode_string = urlencode({"code": jwt})
        verify_url = f"{self.external_url}?{encode_string}"

        message = MIMEMultipart("related")
        message["Subject"] = "HSPC 2026 Email 驗證"
        message["From"] = f"HSPC <{self.sender}>"
        message["To"] = email

        context = self.template \
            .replace("$LINK", verify_url) \
            .replace("$EMAIL", self.sender) \
            .replace("$DISCORD_LINK", self.discord_link)

        message.attach(MIMEText(context, "html", "utf-8"))

        loop = get_running_loop()
        await loop.run_in_executor(None, self._send_email, email, message.as_string())

    async def verify_code(self, conn: Connection, code: str) -> SnowflakeId:
        jwt = unquote_plus(code)
        payload = verify_token(jwt)

        if ScopeType.USE_EMAIL not in payload.scopes:
            raise INVALID_TOKEN

        await User.update_by_uid(
            conn=conn,
            uid=payload.uid,
            data={"email_verified": True}
        )

        return SnowflakeId(payload.uid)


VERIFY_MANAGER = VerifyManager()
