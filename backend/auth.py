"""Authentication, JWT session tokens, OTP verification, and 1-vs-2 system limit enforcement."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import Depends, HTTPException, Header

from backend.database import db_session
from backend.seed_data import hash_password

JWT_SECRET = os.environ.get("ASTRO_JWT_SECRET", "astro-unified-local-dev-secret-2026")
JWT_ALG = "HS256"
TOKEN_EXPIRE_HOURS = 72


def issue_token_for_account(
    account_id: int,
    role: str,
    max_sessions: int,
    portal: str = "consumer",
    device_label: str = "Web Browser",
    force_replace: bool = True,
) -> tuple[str, str]:
    """Create a session row & JWT; enforces max_sessions (Gold=1, Platinum=2)."""
    jti = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    exp = now + timedelta(hours=TOKEN_EXPIRE_HOURS)

    with db_session() as conn:
        active_rows = conn.execute(
            "SELECT jti, device_label, created_at FROM sessions WHERE account_id=? AND active=1 ORDER BY created_at ASC",
            (account_id,),
        ).fetchall()

        if len(active_rows) >= max_sessions:
            if not force_replace:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "SESSION_LIMIT_REACHED",
                        "message": (
                            f"Active system limit reached ({max_sessions} allowed on your plan). "
                            "Upgrade to Platinum for 2 simultaneous systems or confirm session takeover."
                        ),
                        "max_sessions": max_sessions,
                        "active_sessions": [dict(r) for r in active_rows],
                    },
                )
            excess = len(active_rows) - max_sessions + 1
            for row in active_rows[:excess]:
                conn.execute("UPDATE sessions SET active=0 WHERE jti=?", (row["jti"],))

        conn.execute(
            "INSERT INTO sessions(jti, account_id, portal, device_label, created_at, expires_at, active) VALUES (?,?,?,?,?,?,1)",
            (jti, account_id, portal, device_label[:64], now.isoformat(), exp.isoformat()),
        )

    payload = {
        "sub": str(account_id),
        "role": role,
        "jti": jti,
        "exp": int(exp.timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
    return token, jti


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {exc}") from exc


def get_optional_account(authorization: str | None = Header(default=None)) -> dict[str, Any] | None:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        return None
    payload = decode_token(token)
    jti = payload.get("jti")
    account_id = int(payload["sub"])
    with db_session() as conn:
        sess = conn.execute(
            "SELECT * FROM sessions WHERE jti=? AND account_id=? AND active=1",
            (jti, account_id),
        ).fetchone()
        if not sess:
            raise HTTPException(
                status_code=401,
                detail="Session logged out or replaced by another active system login.",
            )
        acc = conn.execute("SELECT * FROM accounts WHERE id=?", (account_id,)).fetchone()
        if not acc:
            raise HTTPException(status_code=401, detail="Account not found.")
        res = dict(acc)
        res["jti"] = jti
        res.pop("password_hash", None)
        return res


def get_current_account(account: dict[str, Any] | None = Depends(get_optional_account)) -> dict[str, Any]:
    if not account:
        raise HTTPException(status_code=401, detail="Authentication required.")
    return account


def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed
