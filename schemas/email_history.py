from asyncpg import Connection
from pydantic import Field, field_validator
from pydantic_snowflake import SnowflakeId

from datetime import datetime
try:
    from datetime import UTC
except ImportError:
    from datetime import timezone
    UTC = timezone.utc
from typing import Optional

from type import UidType

from .base import UidTableModel


class EmailHistory(UidTableModel):
    __table__ = "email_history"

    user_uid: SnowflakeId
    last_sent: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    @field_validator("last_sent", mode="after")
    def ensure_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=UTC)
        return v.astimezone(UTC)

    @classmethod
    async def get_email_if_can_resend(
        cls,
        conn: Connection,
        user_uid: UidType,
        cooldown_seconds: int = 300
    ) -> Optional[str]:
        new_uid = cls._generate_uid()
        row = await conn.fetchrow(f"""
            INSERT INTO email_history (uid, user_uid, last_sent)
            VALUES ($1, $2, CURRENT_TIMESTAMP)
            ON CONFLICT (user_uid) DO UPDATE SET last_sent = EXCLUDED.last_sent
            WHERE email_history.user_uid = EXCLUDED.user_uid
                AND email_history.last_sent < (CURRENT_TIMESTAMP - INTERVAL '{cooldown_seconds} seconds')
                AND EXISTS (
                    SELECT 1 FROM users u
                    WHERE u.uid = EXCLUDED.user_uid
                        AND u.email_verified = FALSE
                )
            RETURNING (SELECT email FROM users WHERE uid = $2) AS email
        """, int(new_uid), int(user_uid))

        return row["email"] if row else None
