"""Unified FastAPI Backend for AstroScience App + GDVPanel Portal."""

from __future__ import annotations

import io
import json
import math
import struct
import uuid
import wave
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.astro_engine import (
    compute_matchmaking,
    compute_panchang,
    full_kundli_bundle,
    generate_kundli_pdf,
    generate_order_invoice_pdf,
)
from backend.auth import (
    get_current_account,
    get_optional_account,
    issue_token_for_account,
    verify_password,
)
from backend.database import db_session, init_db
from backend.seed_data import hash_password, seed_all

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    seed_all()
    yield


app = FastAPI(
    title="AstroScience & GDVPanel Unified API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------
class OtpSendReq(BaseModel):
    phone: str = Field(..., min_length=6, max_length=20)


class OtpVerifyReq(BaseModel):
    phone: str
    otp: str
    name: str | None = None
    device_label: str = "AstroScience Mobile Web"


class LoginReq(BaseModel):
    identifier: str
    password: str
    portal: str = "portal"
    device_label: str = "Web Browser"
    force_replace: bool = True


class RegisterAccountReq(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    password: str = Field(..., min_length=6)
    role: str = "user"


class MemberIn(BaseModel):
    name: str
    dob: str
    birth_time: str
    gender: str = "Male"
    place_name: str = "New Delhi"
    state_name: str = ""
    country_name: str = "India"
    latitude: float = 28.6139
    longitude: float = 77.2090
    tz_offset: float = 5.5
    confirm_plan_reset: bool = False


class KundliBundleReq(BaseModel):
    member_id: int | None = None
    name: str | None = None
    dob: str | None = None
    birth_time: str | None = None
    gender: str = "Male"
    place_name: str = "New Delhi"
    latitude: float = 28.6139
    longitude: float = 77.2090
    tz_offset: float = 5.5
    target_year: int | None = None


class CategoryConsultReq(BaseModel):
    member_id: int
    marriage_status: str | None = None
    child_status: str | None = None
    question_note: str | None = None


class MatchmakingReq(BaseModel):
    boy_name: str
    boy_dob: str
    boy_time: str
    boy_lat: float = 28.6139
    boy_lon: float = 77.2090
    boy_tz: float = 5.5
    girl_name: str
    girl_dob: str
    girl_time: str
    girl_lat: float = 28.6139
    girl_lon: float = 77.2090
    girl_tz: float = 5.5


class FolderIn(BaseModel):
    member_id: int = 0
    name: str


class SavedPredictionIn(BaseModel):
    folder_id: int
    member_id: int
    title: str
    prediction_type: str = "Kundli12GharPrediction"
    prediction_text: str
    upay_id: int = 0
    upay_text: str = ""
    sentiment: str = "Positive"


class CartAddReq(BaseModel):
    product_id: int
    quantity: int = 1
    member_id: int = 0


class CartUpdateReq(BaseModel):
    quantity: int = Field(..., ge=1, le=20)


class CouponReq(BaseModel):
    code: str


class AddressIn(BaseModel):
    address_type: str = "Home"
    full_name: str
    phone: str
    line1: str
    line2: str = ""
    city: str
    state: str
    pincode: str


class CreateOrderReq(BaseModel):
    order_type: str  # 'shop' | 'subscription' | 'course' | 'portal_registration' | 'lalkitab_file'
    member_id: int | None = None
    plan_id: int | None = None
    course_id: int | None = None
    address_id: int | None = None
    coupon_code: str | None = None
    credits_to_use: int = 0
    reg_details: dict[str, Any] | None = None


class VerifyOrderReq(BaseModel):
    order_id: int
    razorpay_payment_id: str | None = None
    simulate_status: str = "paid"


class VisitorLeadReq(BaseModel):
    name: str
    contact: str
    study_astro: str = "Yes"
    pro_astro: str = "No"
    city: str = ""


class CommentReq(BaseModel):
    comment_text: str


class FeedbackReq(BaseModel):
    message: str
    rating: int = 5


class CrmClientRegReq(BaseModel):
    client_name: str
    client_phone: str
    client_email: str | None = None
    plan_id: int
    city: str = "New Delhi"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _redact_bundle_for_plan(bundle: dict[str, Any], is_premium: bool) -> dict[str, Any]:
    """Server-side enforcement mirroring APK Free (`plan_id==0`) vs Premium (`plan_id!=0`)."""
    out = dict(bundle)
    if is_premium:
        out["access_tier"] = "premium"
        out["locked_sections"] = []
        return out

    out["access_tier"] = "free"
    out["locked_sections"] = [
        "past_future_dashas",
        "remedies_upay",
        "premium_vivaran_predictions",
        "varshphal_age_ranges",
    ]

    redacted_ghar = []
    for g in bundle["ghar_predictions"]:
        gc = dict(g)
        if gc["upay_id"] != 0:
            gc["upay"] = "LOCKED (Upgrade to AstroScience Premium to unlock personalized Upay Remedy)"
            gc["upay_locked"] = True
        else:
            gc["upay_locked"] = False
        redacted_ghar.append(gc)
    out["ghar_predictions"] = redacted_ghar

    dashas = json.loads(json.dumps(bundle["dashas"]))
    for key in ("mahadashas", "antardashas", "pratyantardashas", "lk_dashas"):
        for item in dashas[key]:
            if not item.get("is_current"):
                item["locked"] = True
                item["summary"] = "LOCKED — Past/Future Dasha interpretation requires Premium Plan."
            else:
                item["locked"] = False
    out["dashas"] = dashas

    redacted_ages = []
    for ar in bundle["age_ranges"]:
        ac = dict(ar)
        if not ac["is_current"]:
            ac["locked"] = True
            ac["summary"] = "LOCKED — Upgrade to Premium to view multi-year Varshphal predictions."
        else:
            ac["locked"] = False
        redacted_ages.append(ac)
    out["age_ranges"] = redacted_ages

    redacted_viv = []
    for v in bundle["vivaran"]:
        vc = dict(v)
        if vc.get("is_prediction") == "Yes" and vc["index_id"] not in (8, 9, 10, 20) and vc["index_id"] > 3:
            vc["locked"] = True
            vc["detail"] = "LOCKED — Activate Kundali Plan for full Astrological Vivaran analysis."
        else:
            vc["locked"] = False
            vc["kalyankari_exempt"] = vc["index_id"] in (8, 9, 10, 20)
        redacted_viv.append(vc)
    out["vivaran"] = redacted_viv
    return out


def _build_bhajan_wav(product_id: int) -> bytes:
    freqs = {9: (136.1, 272.2), 10: (144.0, 216.0), 11: (172.06, 258.09)}
    f1, f2 = freqs.get(product_id, (136.1, 204.15))
    sr = 16000
    duration = 4.0
    n_samples = int(sr * duration)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        frames = bytearray()
        for i in range(n_samples):
            t = i / sr
            env = min(1.0, t / 0.25) * min(1.0, (duration - t) / 0.5)
            chime = 0.65 * math.sin(2 * math.pi * f1 * t) + 0.35 * math.sin(2 * math.pi * f2 * t)
            sample = int(max(-1.0, min(1.0, env * 0.45 * chime)) * 32767)
            frames.extend(struct.pack("<h", sample))
        wf.writeframes(bytes(frames))
    return buf.getvalue()


def _plan_to_api(r: Any) -> dict[str, Any]:
    d = dict(r)
    d["benefits"] = json.loads(d["features_json"])
    return d


# ---------------------------------------------------------------------------
# Health & Auth Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health():
    return {"status": "ok", "service": "AstroScience + GDVPanel Unified", "ephemeris": "SwissEph Lahiri"}


@app.post("/api/auth/otp/send")
def send_otp(req: OtpSendReq):
    otp = "123456"
    exp = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
    with db_session() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO otp_challenges(phone, otp_code, expires_at) VALUES (?,?,?)",
            (req.phone.strip(), otp, exp),
        )
    return {
        "sent": True,
        "phone": req.phone.strip(),
        "demo_otp": otp,
        "message": "Local sandbox OTP generated (use 123456).",
    }


@app.post("/api/auth/otp/verify")
def verify_otp(req: OtpVerifyReq):
    phone = req.phone.strip()
    now = datetime.now(timezone.utc).isoformat()
    with db_session() as conn:
        ch = conn.execute(
            "SELECT * FROM otp_challenges WHERE phone=? AND otp_code=?",
            (phone, req.otp.strip()),
        ).fetchone()
        if not ch and req.otp.strip() != "123456":
            raise HTTPException(status_code=400, detail="Invalid OTP code. Use 123456 in sandbox mode.")

        acc = conn.execute("SELECT * FROM accounts WHERE phone=?", (phone,)).fetchone()
        if not acc:
            cur = conn.execute(
                """INSERT INTO accounts(account_type, name, phone, password_hash, role, credits_balance, max_sessions, created_at)
                   VALUES ('consumer', ?, ?, ?, 'user', 300, 5, ?)""",
                (req.name or f"Seeker {phone[-4:]}", phone, hash_password("Demo@1234"), now),
            )
            acc_id = cur.lastrowid
            conn.execute(
                """INSERT INTO family_members(account_id, name, gender, dob, birth_time, place_name, latitude, longitude, tz_offset, is_primary, plan_id, plan_name)
                   VALUES (?, ?, 'Male', '1995-08-15', '09:30', 'New Delhi', 28.6139, 77.2090, 5.5, 1, 0, 'Free Plan')""",
                (acc_id, req.name or f"Seeker {phone[-4:]}"),
            )
            acc = conn.execute("SELECT * FROM accounts WHERE id=?", (acc_id,)).fetchone()

    acc_d = dict(acc)
    token, jti = issue_token_for_account(
        acc_d["id"], acc_d["role"], acc_d["max_sessions"], portal="consumer", device_label=req.device_label
    )
    acc_d.pop("password_hash", None)
    return {"token": token, "jti": jti, "account": acc_d}


@app.post("/api/auth/login")
def login_password(req: LoginReq):
    ident = req.identifier.strip().lower()
    with db_session() as conn:
        acc = conn.execute(
            "SELECT * FROM accounts WHERE lower(email)=? OR phone=?",
            (ident, req.identifier.strip()),
        ).fetchone()
    if not acc or not verify_password(req.password, acc["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email/phone or password. (Demo password: Demo@1234)")
    acc_d = dict(acc)
    token, jti = issue_token_for_account(
        acc_d["id"],
        acc_d["role"],
        acc_d["max_sessions"],
        portal=req.portal,
        device_label=req.device_label,
        force_replace=req.force_replace,
    )
    acc_d.pop("password_hash", None)
    return {"token": token, "jti": jti, "account": acc_d}


@app.post("/api/auth/register")
def register_account(req: RegisterAccountReq):
    now = datetime.now(timezone.utc).isoformat()
    with db_session() as conn:
        existing = conn.execute(
            "SELECT id FROM accounts WHERE (email IS NOT NULL AND lower(email)=?) OR (phone IS NOT NULL AND phone=?)",
            ((req.email or "__none__").lower(), req.phone or "__none__"),
        ).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="Account with this email or phone already exists.")
        cur = conn.execute(
            """INSERT INTO accounts(account_type, role, name, email, phone, password_hash, credits_balance, max_sessions, created_at)
               VALUES ('consumer',?,?,?,?,?,300,2,?)""",
            (req.role, req.name, req.email, req.phone, hash_password(req.password), now),
        )
        acc_id = cur.lastrowid
        conn.execute(
            """INSERT INTO family_members(account_id, name, gender, dob, birth_time, place_name, latitude, longitude, tz_offset, is_primary, plan_id, plan_name)
               VALUES (?, ?, 'Male', '1996-05-12', '10:15', 'New Delhi', 28.6139, 77.2090, 5.5, 1, 0, 'Free Plan')""",
            (acc_id, req.name),
        )
        acc = dict(conn.execute("SELECT * FROM accounts WHERE id=?", (acc_id,)).fetchone())
    token, jti = issue_token_for_account(acc["id"], acc["role"], acc["max_sessions"], device_label="Initial Registration")
    acc.pop("password_hash", None)
    return {"token": token, "jti": jti, "account": acc}


@app.post("/api/auth/logout")
def logout(account: dict[str, Any] = Depends(get_current_account)):
    with db_session() as conn:
        conn.execute("UPDATE sessions SET active=0 WHERE jti=?", (account["jti"],))
    return {"logged_out": True}


@app.get("/api/auth/me")
def get_me(account: dict[str, Any] = Depends(get_current_account)):
    with db_session() as conn:
        active_sessions = [
            dict(r)
            for r in conn.execute(
                "SELECT jti, portal, device_label, created_at, expires_at FROM sessions WHERE account_id=? AND active=1 ORDER BY created_at DESC",
                (account["id"],),
            ).fetchall()
        ]
        enrollments = [
            r["course_id"]
            for r in conn.execute(
                "SELECT course_id FROM course_enrollments WHERE account_id=?", (account["id"],)
            ).fetchall()
        ]
    return {"account": account, "active_sessions": active_sessions, "enrolled_course_ids": enrollments}


@app.get("/api/auth/sessions")
def list_sessions(account: dict[str, Any] = Depends(get_current_account)):
    with db_session() as conn:
        rows = [
            dict(r)
            for r in conn.execute(
                "SELECT jti, portal, device_label, active, created_at, expires_at FROM sessions WHERE account_id=? ORDER BY created_at DESC LIMIT 10",
                (account["id"],),
            ).fetchall()
        ]
    return {"max_sessions": account["max_sessions"], "sessions": rows}


# ---------------------------------------------------------------------------
# Public Portal, Places, Pincodes, Plans & Courses
# ---------------------------------------------------------------------------
@app.get("/api/plans")
def get_plans(scope: str | None = None):
    with db_session() as conn:
        if scope:
            rows = conn.execute("SELECT * FROM registration_plans WHERE plan_scope=? ORDER BY id", (scope,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM registration_plans ORDER BY plan_scope, id").fetchall()
    return {"plans": [_plan_to_api(r) for r in rows]}


@app.get("/api/popup")
def get_popup():
    return {
        "enabled": True,
        "title": "Prarambhik Vashistha Jyotish + Platinum Software",
        "subtitle": "Enroll in Guruji GD Vashist's Lal Kitab certification course or unlock unlimited Acharya Kundali PDFs.",
        "cta_text": "Explore Plans",
        "cta_route": "/registration",
    }


@app.post("/api/visitor")
def submit_visitor_lead(req: VisitorLeadReq):
    now = datetime.now(timezone.utc).isoformat()
    with db_session() as conn:
        cur = conn.execute(
            "INSERT INTO visitor_leads(name, contact, study_astro, pro_astro, city, created_at) VALUES (?,?,?,?,?,?)",
            (req.name, req.contact, req.study_astro, req.pro_astro, req.city, now),
        )
    return {"submitted": True, "lead_id": cur.lastrowid}


@app.get("/api/places/search")
def search_places(q: str = Query(default="", min_length=0)):
    with db_session() as conn:
        if q.strip():
            rows = conn.execute(
                "SELECT * FROM places_pincodes WHERE lower(place_name) LIKE ? OR pincode LIKE ? LIMIT 12",
                (f"%{q.strip().lower()}%", f"%{q.strip()}%"),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM places_pincodes LIMIT 12").fetchall()
    return {"places": [dict(r) for r in rows]}


@app.get("/api/pincodes/{pincode}")
def lookup_pincode(pincode: str):
    with db_session() as conn:
        row = conn.execute("SELECT * FROM places_pincodes WHERE pincode=? LIMIT 1", (pincode.strip(),)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Pincode not found in local postal index.")
    return dict(row)


@app.get("/api/courses")
def list_courses(account: dict[str, Any] | None = Depends(get_optional_account)):
    with db_session() as conn:
        courses = [dict(r) for r in conn.execute("SELECT * FROM courses ORDER BY id").fetchall()]
        enrolled = set()
        if account:
            enrolled = {
                r["course_id"]
                for r in conn.execute("SELECT course_id FROM course_enrollments WHERE account_id=?", (account["id"],)).fetchall()
            }
        for c in courses:
            c["is_enrolled"] = c["id"] in enrolled
            c["learning_outcomes"] = json.loads(c["learning_outcomes_json"])
            c["requirements"] = json.loads(c["requirements_json"])
    return {"courses": courses}


@app.get("/api/courses/{course_id}")
def get_course_detail(course_id: int, account: dict[str, Any] | None = Depends(get_optional_account)):
    with db_session() as conn:
        c = conn.execute("SELECT * FROM courses WHERE id=?", (course_id,)).fetchone()
        if not c:
            raise HTTPException(status_code=404, detail="Course not found")
        course = dict(c)
        enrolled = False
        if account:
            enr = conn.execute(
                "SELECT id FROM course_enrollments WHERE account_id=? AND course_id=?",
                (account["id"], course_id),
            ).fetchone()
            enrolled = bool(enr)
        videos = [
            dict(v)
            for v in conn.execute("SELECT * FROM course_videos WHERE course_id=? ORDER BY sequence_no", (course_id,)).fetchall()
        ]
    for v in videos:
        unlocked = enrolled or bool(v["is_preview"])
        v["locked"] = not unlocked
        v["stream_url"] = "/api/audio/10.wav" if unlocked else None
    course["is_enrolled"] = enrolled
    course["learning_outcomes"] = json.loads(course["learning_outcomes_json"])
    course["requirements"] = json.loads(course["requirements_json"])
    course["videos"] = videos
    return course


# ---------------------------------------------------------------------------
# Family Profiles & Kundli / Categories / Matchmaking / Panchang
# ---------------------------------------------------------------------------
@app.get("/api/members")
def list_members(account: dict[str, Any] = Depends(get_current_account)):
    with db_session() as conn:
        rows = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM family_members WHERE account_id=? ORDER BY id ASC", (account["id"],)
            ).fetchall()
        ]
    return {"members": rows}


@app.post("/api/members")
def create_member(req: MemberIn, account: dict[str, Any] = Depends(get_current_account)):
    if not req.name.strip():
        raise HTTPException(status_code=400, detail="Member name is required.")
    with db_session() as conn:
        cur = conn.execute(
            """INSERT INTO family_members(account_id, name, gender, dob, birth_time, place_name, state_name, country_name, latitude, longitude, tz_offset, is_primary, plan_id, plan_name)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,0,0,'Free Plan')""",
            (
                account["id"],
                req.name.strip(),
                req.gender,
                req.dob,
                req.birth_time,
                req.place_name,
                req.state_name,
                req.country_name,
                req.latitude,
                req.longitude,
                req.tz_offset,
            ),
        )
        member = dict(conn.execute("SELECT * FROM family_members WHERE id=?", (cur.lastrowid,)).fetchone())
    return {"member": member}


@app.put("/api/members/{member_id}")
def update_member(member_id: int, req: MemberIn, account: dict[str, Any] = Depends(get_current_account)):
    with db_session() as conn:
        existing = conn.execute(
            "SELECT * FROM family_members WHERE id=? AND account_id=?", (member_id, account["id"])
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Member profile not found.")
        ex = dict(existing)

        birth_changed = any([
            ex["dob"] != req.dob,
            ex["birth_time"] != req.birth_time,
            ex["gender"] != req.gender,
            ex["place_name"] != req.place_name,
            abs(float(ex["latitude"]) - req.latitude) > 1e-4,
            abs(float(ex["longitude"]) - req.longitude) > 1e-4,
        ])

        plan_id = ex["plan_id"]
        plan_name = ex["plan_name"]
        plan_expired = False

        if plan_id != 0 and birth_changed:
            if not req.confirm_plan_reset:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "PLAN_EXPIRATION_CONFIRM_REQUIRED",
                        "message": "If you change the details of this profile then the activated plan will be expired. Are you sure you want to continue?",
                    },
                )
            plan_id = 0
            plan_name = "Free Plan"
            plan_expired = True

        conn.execute(
            """UPDATE family_members
               SET name=?, gender=?, dob=?, birth_time=?, place_name=?, state_name=?, country_name=?, latitude=?, longitude=?, tz_offset=?, plan_id=?, plan_name=?
               WHERE id=?""",
            (
                req.name,
                req.gender,
                req.dob,
                req.birth_time,
                req.place_name,
                req.state_name,
                req.country_name,
                req.latitude,
                req.longitude,
                req.tz_offset,
                plan_id,
                plan_name,
                member_id,
            ),
        )
        updated = dict(conn.execute("SELECT * FROM family_members WHERE id=?", (member_id,)).fetchone())
    return {"member": updated, "plan_expired": plan_expired}


@app.delete("/api/members/{member_id}")
def delete_member(member_id: int, account: dict[str, Any] = Depends(get_current_account)):
    with db_session() as conn:
        count = conn.execute(
            "SELECT count(*) as cnt FROM family_members WHERE account_id=?", (account["id"],)
        ).fetchone()["cnt"]
        if count <= 1:
            raise HTTPException(status_code=400, detail="Cannot delete the last family profile.")
        cur = conn.execute(
            "DELETE FROM family_members WHERE id=? AND account_id=?", (member_id, account["id"])
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Member profile not found.")
    return {"deleted": True}


@app.post("/api/kundli/bundle")
def get_kundli_bundle(req: KundliBundleReq, account: dict[str, Any] | None = Depends(get_optional_account)):
    is_premium = False
    if req.member_id:
        if not account:
            raise HTTPException(status_code=401, detail="Authentication required to query a saved member profile.")
        with db_session() as conn:
            row = conn.execute("SELECT * FROM family_members WHERE id=?", (req.member_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Member profile not found.")
        member = dict(row)
        if member["account_id"] != account["id"] and account.get("role") != "crm_agent":
            raise HTTPException(status_code=403, detail="Access denied for this family profile.")
        is_acharya_platinum = account.get("reg_plan_id", 0) >= 2
        is_premium = (member["plan_id"] != 0) or is_acharya_platinum
    else:
        if not (req.dob and req.birth_time):
            raise HTTPException(status_code=400, detail="Provide either member_id or dob + birth_time.")
        is_acharya_platinum = bool(account and account.get("reg_plan_id", 0) >= 2)
        member = {
            "id": 0,
            "name": req.name or "Guest Native",
            "dob": req.dob,
            "birth_time": req.birth_time,
            "gender": req.gender,
            "place_name": req.place_name,
            "latitude": req.latitude,
            "longitude": req.longitude,
            "tz_offset": req.tz_offset,
            "plan_id": 2 if is_acharya_platinum else 0,
            "plan_name": "Acharya Portal" if is_acharya_platinum else "Free Plan",
        }
        is_premium = is_acharya_platinum

    try:
        raw = full_kundli_bundle(member, target_year=req.target_year)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid date or birth time format: {exc}") from exc
    return _redact_bundle_for_plan(raw, is_premium=is_premium)


@app.post("/api/kundli/custom-pdf")
def download_custom_kundli_pdf(req: KundliBundleReq, account: dict[str, Any] | None = Depends(get_optional_account)):
    if not (req.dob and req.birth_time):
        raise HTTPException(status_code=400, detail="dob and birth_time required.")
    member = {
        "id": 0,
        "name": req.name or "Client Chart",
        "dob": req.dob,
        "birth_time": req.birth_time,
        "gender": req.gender,
        "place_name": req.place_name,
        "latitude": req.latitude,
        "longitude": req.longitude,
        "tz_offset": req.tz_offset,
        "plan_id": 2,
        "plan_name": "Full Kundali Report (Swiss Ephemeris)",
    }
    try:
        bundle = full_kundli_bundle(member, target_year=req.target_year)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid date or birth time format: {exc}") from exc
    pdf_bytes = generate_kundli_pdf(bundle)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="client_kundali.pdf"'},
    )


@app.get("/api/kundli/{member_id}/pdf")
def download_kundli_pdf(member_id: int, account: dict[str, Any] = Depends(get_current_account)):
    with db_session() as conn:
        row = conn.execute("SELECT * FROM family_members WHERE id=?", (member_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Member not found.")
    member = dict(row)
    if member["account_id"] != account["id"] and account.get("role") != "crm_agent":
        raise HTTPException(status_code=403, detail="Access denied for this family profile.")
    bundle = full_kundli_bundle(member)
    pdf_bytes = generate_kundli_pdf(bundle)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="kundali_{member_id}.pdf"'},
    )


@app.get("/api/categories")
def list_categories():
    with db_session() as conn:
        rows = [dict(r) for r in conn.execute("SELECT * FROM horoscope_categories ORDER BY id").fetchall()]
    return {"categories": rows}


@app.post("/api/kundli/category/{cat_id}")
def get_category_consultation(
    cat_id: int,
    req: CategoryConsultReq,
    account: dict[str, Any] = Depends(get_current_account),
):
    with db_session() as conn:
        cat = conn.execute("SELECT * FROM horoscope_categories WHERE id=?", (cat_id,)).fetchone()
        member = conn.execute("SELECT * FROM family_members WHERE id=?", (req.member_id,)).fetchone()
    if not cat or not member:
        raise HTTPException(status_code=404, detail="Category or Member not found.")
    m = dict(member)
    if m["account_id"] != account["id"] and account.get("role") != "crm_agent":
        raise HTTPException(status_code=403, detail="Access denied for this family profile.")
    if m["plan_id"] == 0 and account.get("reg_plan_id", 0) < 2:
        raise HTTPException(
            status_code=402,
            detail={
                "code": "PREMIUM_REQUIRED",
                "message": f"'{cat['title']}' predictions require an active Membership Plan on {m['name']}.",
            },
        )
    bundle = full_kundli_bundle(m)
    chart = bundle["chart"]
    context_note = ""
    if cat_id == 3:
        context_note = f"Marital status considered: {req.marriage_status or 'Not specified'}."
    elif cat_id == 5:
        context_note = f"Parenthood status considered: {req.child_status or 'Not specified'}."
    elif cat_id == 44:
        context_note = "7th House Ashtakoot & Venus/Jupiter balance analyzed for compatibility readiness."

    p_map = {1: 1, 2: 2, 3: 7, 4: 4, 5: 5, 7: 12, 10: 4, 44: 7}
    h_idx = p_map.get(cat_id, 1) - 1
    hp = bundle["ghar_predictions"][h_idx]
    return {
        "category": dict(cat),
        "member_name": m["name"],
        "house_focus": hp,
        "ascendant": chart["ascendant"]["rashi"],
        "context_note": context_note,
        "detailed_reading": (
            f"Based on {m['name']}'s {chart['ascendant']['rashi']} Lagna and House {hp['house']} "
            f"({hp['rashi']}, ruled by {hp['lord']}), {hp['prediction']} Recommended Remedy: {hp['upay']}"
        ),
    }


@app.post("/api/matchmaking")
def run_matchmaking(req: MatchmakingReq):
    boy = {"name": req.boy_name, "dob": req.boy_dob, "birth_time": req.boy_time, "latitude": req.boy_lat, "longitude": req.boy_lon, "tz_offset": req.boy_tz}
    girl = {"name": req.girl_name, "dob": req.girl_dob, "birth_time": req.girl_time, "latitude": req.girl_lat, "longitude": req.girl_lon, "tz_offset": req.girl_tz}
    try:
        return compute_matchmaking(boy, girl)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid date or time format: {exc}") from exc


@app.get("/api/panchang")
def get_panchang(
    target_date: str | None = None,
    latitude: float = 28.6139,
    longitude: float = 77.2090,
    tz_offset: float = 5.5,
    place_name: str = "New Delhi",
):
    today = date.today()
    dt_str = target_date or today.isoformat()
    try:
        dt = date.fromisoformat(dt_str)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid date format (YYYY-MM-DD expected).") from exc

    if abs((dt - today).days) > 35:
        raise HTTPException(
            status_code=400,
            detail="Panchang / Choghadiya range is limited to ±1 month from today (matching AstroScience calendar rule).",
        )
    return compute_panchang(dt_str, latitude, longitude, tz_offset=tz_offset, place_name=place_name)


# ---------------------------------------------------------------------------
# Saved Predictions & Folders (Free Plan redacts Upay!)
# ---------------------------------------------------------------------------
@app.get("/api/saved/folders")
def list_saved_folders(account: dict[str, Any] = Depends(get_current_account)):
    with db_session() as conn:
        folders = [
            dict(r)
            for r in conn.execute("SELECT * FROM saved_folders WHERE account_id=? ORDER BY id", (account["id"],)).fetchall()
        ]
    return {"folders": folders}


@app.post("/api/saved/folders")
def create_saved_folder(req: FolderIn, account: dict[str, Any] = Depends(get_current_account)):
    now = datetime.now(timezone.utc).isoformat()
    with db_session() as conn:
        member_id = req.member_id
        if member_id:
            owned = conn.execute("SELECT id FROM family_members WHERE id=? AND account_id=?", (member_id, account["id"])).fetchone()
            if not owned:
                raise HTTPException(status_code=403, detail="Access denied for specified family profile.")
        else:
            m = conn.execute("SELECT id FROM family_members WHERE account_id=? ORDER BY id LIMIT 1", (account["id"],)).fetchone()
            if not m:
                raise HTTPException(status_code=400, detail="Create a family profile first.")
            member_id = m["id"]
        cur = conn.execute(
            "INSERT INTO saved_folders(account_id, member_id, name, created_at) VALUES (?,?,?,?)",
            (account["id"], member_id, req.name.strip(), now),
        )
        folder = dict(conn.execute("SELECT * FROM saved_folders WHERE id=?", (cur.lastrowid,)).fetchone())
    return {"folder": folder}


@app.get("/api/saved/predictions")
def list_saved_predictions(
    folder_id: int | None = None,
    sentiment: str | None = None,
    account: dict[str, Any] = Depends(get_current_account),
):
    with db_session() as conn:
        q = """SELECT sp.*, COALESCE(fm.name, '') as member_name, COALESCE(fm.plan_id, 0) as member_plan_id
               FROM saved_predictions sp LEFT JOIN family_members fm ON sp.member_id=fm.id
               WHERE sp.account_id=?"""
        params: list[Any] = [account["id"]]
        if folder_id:
            q += " AND sp.folder_id=?"
            params.append(folder_id)
        if sentiment and sentiment != "All":
            q += " AND sp.sentiment=?"
            params.append(sentiment)
        q += " ORDER BY sp.id DESC"
        rows = [dict(r) for r in conn.execute(q, params).fetchall()]

    for r in rows:
        if r["member_plan_id"] == 0 and account.get("reg_plan_id", 0) < 2 and r["upay_id"] != 0:
            r["upay_locked"] = True
            r["upay_text"] = "LOCKED (Upgrade profile to unlock saved remedy)"
        else:
            r["upay_locked"] = False
    return {"predictions": rows}


@app.post("/api/saved/predictions")
def save_prediction(req: SavedPredictionIn, account: dict[str, Any] = Depends(get_current_account)):
    now = datetime.now(timezone.utc).isoformat()
    with db_session() as conn:
        f_ok = conn.execute("SELECT id FROM saved_folders WHERE id=? AND account_id=?", (req.folder_id, account["id"])).fetchone()
        m_ok = conn.execute("SELECT id FROM family_members WHERE id=? AND account_id=?", (req.member_id, account["id"])).fetchone()
        if not f_ok or not m_ok:
            raise HTTPException(status_code=403, detail="Invalid folder or family profile.")
        cur = conn.execute(
            """INSERT INTO saved_predictions(folder_id, account_id, member_id, title, prediction_type, sentiment, prediction_text, upay_id, upay_text, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                req.folder_id,
                account["id"],
                req.member_id,
                req.title,
                req.prediction_type,
                req.sentiment,
                req.prediction_text,
                req.upay_id,
                req.upay_text,
                now,
            ),
        )
        row = dict(conn.execute("SELECT * FROM saved_predictions WHERE id=?", (cur.lastrowid,)).fetchone())
    return {"saved": row}


@app.delete("/api/saved/predictions/{pred_id}")
def delete_saved_prediction(pred_id: int, account: dict[str, Any] = Depends(get_current_account)):
    with db_session() as conn:
        conn.execute("DELETE FROM saved_predictions WHERE id=? AND account_id=?", (pred_id, account["id"]))
    return {"deleted": True}


# ---------------------------------------------------------------------------
# Products, Audio Mantra WAVs, Cart, Addresses, Checkout & Orders
# ---------------------------------------------------------------------------
@app.get("/api/products")
def list_products(type: str | None = None, q: str | None = None):
    with db_session() as conn:
        sql = "SELECT * FROM products WHERE 1=1"
        params: list[Any] = []
        if type:
            sql += " AND category_slug=?"
            params.append(type)
        if q:
            sql += " AND (lower(title) LIKE ? OR lower(description) LIKE ?)"
            params.extend([f"%{q.lower()}%", f"%{q.lower()}%"])
        rows = [dict(r) for r in conn.execute(sql + " ORDER BY id", params).fetchall()]
    return {"products": rows}


@app.get("/api/audio/{product_id}.wav")
def stream_audio_wav(product_id: int):
    return Response(content=_build_bhajan_wav(product_id), media_type="audio/wav")


@app.get("/api/cart")
def get_cart(account: dict[str, Any] = Depends(get_current_account)):
    with db_session() as conn:
        rows = [
            dict(r)
            for r in conn.execute(
                """SELECT c.id as cart_id, c.quantity, c.member_id, p.*
                   FROM cart_items c JOIN products p ON c.product_id=p.id
                   WHERE c.account_id=? ORDER BY c.id DESC""",
                (account["id"],),
            ).fetchall()
        ]
    subtotal = sum(r["price"] * r["quantity"] for r in rows)
    return {"items": rows, "subtotal": subtotal, "reward_credits": account["credits_balance"]}


@app.post("/api/cart")
def add_to_cart(req: CartAddReq, account: dict[str, Any] = Depends(get_current_account)):
    with db_session() as conn:
        prod = conn.execute("SELECT * FROM products WHERE id=?", (req.product_id,)).fetchone()
        if not prod:
            raise HTTPException(status_code=404, detail="Product not found.")
        if prod["is_audio"]:
            raise HTTPException(status_code=400, detail="Free Mantra/Bhajan items do not require checkout.")
        existing = conn.execute(
            "SELECT * FROM cart_items WHERE account_id=? AND product_id=? AND member_id=?",
            (account["id"], req.product_id, req.member_id),
        ).fetchone()
        if existing:
            conn.execute("UPDATE cart_items SET quantity=quantity+? WHERE id=?", (req.quantity, existing["id"]))
        else:
            conn.execute(
                "INSERT INTO cart_items(account_id, product_id, member_id, quantity) VALUES (?,?,?,?)",
                (account["id"], req.product_id, req.member_id, req.quantity),
            )
    return get_cart(account)


@app.put("/api/cart/{cart_id}")
def update_cart_item(cart_id: int, req: CartUpdateReq, account: dict[str, Any] = Depends(get_current_account)):
    with db_session() as conn:
        cur = conn.execute(
            "UPDATE cart_items SET quantity=? WHERE id=? AND account_id=?",
            (req.quantity, cart_id, account["id"]),
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Cart item not found.")
    return get_cart(account)


@app.delete("/api/cart/{cart_id}")
def delete_cart_item(cart_id: int, account: dict[str, Any] = Depends(get_current_account)):
    with db_session() as conn:
        conn.execute("DELETE FROM cart_items WHERE id=? AND account_id=?", (cart_id, account["id"]))
    return get_cart(account)


@app.post("/api/cart/apply-coupon")
def apply_coupon(req: CouponReq, account: dict[str, Any] = Depends(get_current_account)):
    cart = get_cart(account)
    subtotal = cart["subtotal"]
    with db_session() as conn:
        c = conn.execute("SELECT * FROM coupons WHERE upper(code)=?", (req.code.strip().upper(),)).fetchone()
    if not c:
        raise HTTPException(status_code=404, detail="Invalid coupon code. Try ASTRO10 or GURUJI20.")
    discount = min(c["max_discount"], round(subtotal * c["discount_percent"] / 100.0))
    return {"code": c["code"], "discount_pct": c["discount_percent"], "discount_amount": discount}


@app.get("/api/addresses")
def list_addresses(account: dict[str, Any] = Depends(get_current_account)):
    with db_session() as conn:
        rows = [dict(r) for r in conn.execute("SELECT * FROM addresses WHERE account_id=?", (account["id"],)).fetchall()]
    return {"addresses": rows}


@app.post("/api/addresses")
def create_address(req: AddressIn, account: dict[str, Any] = Depends(get_current_account)):
    with db_session() as conn:
        cur = conn.execute(
            "INSERT INTO addresses(account_id, address_type, full_name, phone, line1, line2, pincode, city, state) VALUES (?,?,?,?,?,?,?,?,?)",
            (account["id"], req.address_type, req.full_name, req.phone, req.line1, req.line2, req.pincode, req.city, req.state),
        )
        row = dict(conn.execute("SELECT * FROM addresses WHERE id=?", (cur.lastrowid,)).fetchone())
    return {"address": row}


@app.delete("/api/addresses/{addr_id}")
def delete_address(addr_id: int, account: dict[str, Any] = Depends(get_current_account)):
    with db_session() as conn:
        conn.execute("DELETE FROM addresses WHERE id=? AND account_id=?", (addr_id, account["id"]))
    return {"deleted": True}


@app.post("/api/checkout/create-order")
def create_order(req: CreateOrderReq, account: dict[str, Any] = Depends(get_current_account)):
    now = datetime.now(timezone.utc).isoformat()
    with db_session() as conn:
        line_items: list[dict[str, Any]] = []
        subtotal = 0
        gst = 0
        title = ""
        order_kind = "product"

        if req.order_type == "shop":
            cart_rows = [
                dict(r)
                for r in conn.execute(
                    "SELECT c.quantity, p.* FROM cart_items c JOIN products p ON c.product_id=p.id WHERE c.account_id=?",
                    (account["id"],),
                ).fetchall()
            ]
            if not cart_rows:
                raise HTTPException(status_code=400, detail="Your cart is empty.")
            for cr in cart_rows:
                subtotal += cr["price"] * cr["quantity"]
                line_items.append({"product_id": cr["id"], "title": cr["title"], "quantity": cr["quantity"], "unit_price": cr["price"], "plan_type": cr["plan_type"]})
            title = cart_rows[0]["title"] + (f" (+{len(cart_rows)-1} more)" if len(cart_rows) > 1 else "")

        elif req.order_type == "subscription":
            order_kind = "subscription"
            if not (req.member_id and req.plan_id):
                raise HTTPException(status_code=400, detail="member_id and plan_id required.")
            m = conn.execute("SELECT * FROM family_members WHERE id=? AND account_id=?", (req.member_id, account["id"])).fetchone()
            plan = conn.execute("SELECT * FROM registration_plans WHERE id=? AND plan_scope='consumer_sub'", (req.plan_id,)).fetchone()
            if not m or not plan:
                raise HTTPException(status_code=404, detail="Member or consumer plan not found.")
            if m["plan_id"] != 0:
                raise HTTPException(status_code=409, detail="Membership Plan already Activated for this user")
            subtotal = plan["total_price"]
            title = f"{plan['name']} for {m['name']}"
            line_items.append({"product_id": plan["id"], "title": title, "quantity": 1, "unit_price": plan["total_price"], "plan_type": 2})

        elif req.order_type == "portal_registration":
            order_kind = "registration"
            if not req.plan_id:
                raise HTTPException(status_code=400, detail="plan_id required for portal registration.")
            plan = conn.execute("SELECT * FROM registration_plans WHERE id=? AND plan_scope='portal_reg'", (req.plan_id,)).fetchone()
            if not plan:
                raise HTTPException(status_code=404, detail="Portal plan not found.")
            subtotal = plan["base_fee"] + plan["recurring_fee"]
            gst = plan["gst"]
            title = f"GDVPanel {plan['name']} Registration"
            line_items.append({"product_id": plan["id"], "title": title, "quantity": 1, "unit_price": plan["total_price"], "plan_type": 2})

        elif req.order_type == "course":
            order_kind = "course"
            if not req.course_id:
                raise HTTPException(status_code=400, detail="course_id required.")
            course = conn.execute("SELECT * FROM courses WHERE id=?", (req.course_id,)).fetchone()
            if not course:
                raise HTTPException(status_code=404, detail="Course not found.")
            already = conn.execute(
                "SELECT id FROM course_enrollments WHERE account_id=? AND course_id=?", (account["id"], req.course_id)
            ).fetchone()
            if already:
                raise HTTPException(status_code=409, detail="You are already enrolled in this course.")
            subtotal = course["price"]
            title = course["title"]
            line_items.append({"product_id": course["id"], "title": title, "quantity": 1, "unit_price": course["price"], "plan_type": 2})
        else:
            raise HTTPException(status_code=400, detail="Unsupported order_type.")

        discount = 0
        if req.coupon_code:
            cp = conn.execute("SELECT * FROM coupons WHERE upper(code)=?", (req.coupon_code.strip().upper(),)).fetchone()
            if cp:
                discount = min(cp["max_discount"], round(subtotal * cp["discount_percent"] / 100.0))

        credits_used = max(0, min(req.credits_to_use, account["credits_balance"], max(0, subtotal + gst - discount)))
        total_amount = max(0, subtotal + gst - discount - credits_used)

        order_num = f"AST-{uuid.uuid4().hex[:8].upper()}"
        rzp_order_id = f"order_sandbox_{uuid.uuid4().hex[:10]}"
        cur = conn.execute(
            """INSERT INTO orders(order_number, account_id, member_id, order_kind, title, subtotal, discount, credits_used, gst, total_amount, payment_status, razorpay_order_id, address_snapshot, plan_id_granted, course_id_granted, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,'Pending',?,?,?,?,?)""",
            (
                order_num,
                account["id"],
                req.member_id or 0,
                order_kind,
                title,
                subtotal,
                discount,
                credits_used,
                gst,
                total_amount,
                rzp_order_id,
                json.dumps(req.reg_details or {}),
                req.plan_id or 0,
                req.course_id or 0,
                now,
            ),
        )
        order_id = cur.lastrowid
        for li in line_items:
            conn.execute(
                "INSERT INTO order_items(order_id, product_id, title, quantity, unit_price, plan_type) VALUES (?,?,?,?,?,?)",
                (order_id, li["product_id"], li["title"], li["quantity"], li["unit_price"], li["plan_type"]),
            )
        order = dict(conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone())
    return {"order": order, "items": line_items, "razorpay_key_sandbox": "rzp_test_astro_unified"}


@app.post("/api/checkout/verify")
def verify_order_payment(req: VerifyOrderReq, account: dict[str, Any] = Depends(get_current_account)):
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    with db_session() as conn:
        order = conn.execute("SELECT * FROM orders WHERE id=? AND account_id=?", (req.order_id, account["id"])).fetchone()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found.")
        if order["payment_status"] == "Paid":
            return {"verified": True, "order": dict(order)}

        if req.simulate_status != "paid":
            conn.execute("UPDATE orders SET payment_status='Cancelled' WHERE id=?", (order["id"],))
            raise HTTPException(status_code=402, detail="Payment failed or cancelled by user.")

        pay_id = req.razorpay_payment_id or f"pay_sandbox_{uuid.uuid4().hex[:10]}"
        conn.execute(
            "UPDATE orders SET payment_status='Paid', razorpay_payment_id=? WHERE id=?",
            (pay_id, order["id"]),
        )

        if order["credits_used"] > 0:
            conn.execute("UPDATE accounts SET credits_balance=MAX(0, credits_balance-?) WHERE id=?", (order["credits_used"], account["id"]))
            conn.execute("INSERT INTO reward_ledger(account_id, delta, reason, created_at) VALUES (?,?,?,?)", (account["id"], -order["credits_used"], f"Redeemed on {order['order_number']}", now_iso))

        cashback = max(10, round(order["total_amount"] * 0.02))
        conn.execute("UPDATE accounts SET credits_balance=credits_balance+? WHERE id=?", (cashback, account["id"]))
        conn.execute("INSERT INTO reward_ledger(account_id, delta, reason, created_at) VALUES (?,?,?,?)", (account["id"], cashback, f"2% Cosmic Reward for {order['order_number']}", now_iso))

        if order["order_kind"] == "product":
            conn.execute("DELETE FROM cart_items WHERE account_id=?", (account["id"],))
        elif order["order_kind"] == "subscription" and order["member_id"] and order["plan_id_granted"]:
            plan = conn.execute("SELECT * FROM registration_plans WHERE id=?", (order["plan_id_granted"],)).fetchone()
            exp_dt = (now + timedelta(days=plan["duration_days"])).strftime("%Y-%m-%d")
            conn.execute(
                "UPDATE family_members SET plan_id=?, plan_name=?, expiry_date=? WHERE id=? AND account_id=?",
                (plan["id"], plan["name"], exp_dt, order["member_id"], account["id"]),
            )
            conn.execute(
                "INSERT INTO notifications(account_id, title, body, is_read, created_at) VALUES (?,?,?,0,?)",
                (account["id"], "Subscription Activated", f"{plan['name']} is now active with unlocked Dashas & Remedies.", now_iso),
            )
        elif order["order_kind"] == "registration" and order["plan_id_granted"]:
            plan = conn.execute("SELECT * FROM registration_plans WHERE id=?", (order["plan_id_granted"],)).fetchone()
            conn.execute(
                "UPDATE accounts SET role='acharya', account_type='acharya', reg_plan_id=?, subs_plan_id=?, max_sessions=? WHERE id=?",
                (plan["id"], plan["mapped_subscription_plan_id"] or 3, plan["max_systems"], account["id"]),
            )
            conn.execute(
                "INSERT INTO notifications(account_id, title, body, is_read, created_at) VALUES (?,?,?,0,?)",
                (account["id"], "GDVPanel Activated", f"{plan['name']} unlocked ({plan['max_systems']} system limit).", now_iso),
            )
        elif order["order_kind"] == "course" and order["course_id_granted"]:
            exp_iso = (now + timedelta(days=90)).isoformat()
            conn.execute(
                "INSERT OR IGNORE INTO course_enrollments(account_id, course_id, enrolled_at, expires_at) VALUES (?,?,?,?)",
                (account["id"], order["course_id_granted"], now_iso, exp_iso),
            )
            conn.execute(
                "INSERT INTO notifications(account_id, title, body, is_read, created_at) VALUES (?,?,?,0,?)",
                (account["id"], "Course Unlocked", "All 14 Lal Kitab & Vashistha Jyotish video lectures are now available.", now_iso),
            )

        updated_order = dict(conn.execute("SELECT * FROM orders WHERE id=?", (order["id"],)).fetchone())
        updated_acc = dict(conn.execute("SELECT * FROM accounts WHERE id=?", (account["id"],)).fetchone())
        updated_acc.pop("password_hash", None)

    return {"verified": True, "order": updated_order, "account": updated_acc, "cashback_earned": cashback}


@app.get("/api/orders")
def list_orders(account: dict[str, Any] = Depends(get_current_account)):
    with db_session() as conn:
        orders = [dict(r) for r in conn.execute("SELECT * FROM orders WHERE account_id=? ORDER BY id DESC", (account["id"],)).fetchall()]
        for o in orders:
            o["items"] = [dict(it) for it in conn.execute("SELECT * FROM order_items WHERE order_id=?", (o["id"],)).fetchall()]
    return {"orders": orders}


@app.post("/api/orders/{order_id}/cancel")
def cancel_order(order_id: int, account: dict[str, Any] = Depends(get_current_account)):
    with db_session() as conn:
        o = conn.execute("SELECT * FROM orders WHERE id=? AND account_id=?", (order_id, account["id"])).fetchone()
        if not o:
            raise HTTPException(status_code=404, detail="Order not found.")
        if o["order_kind"] != "product":
            raise HTTPException(status_code=400, detail="Only physical shop orders can be cancelled.")
        conn.execute("UPDATE orders SET payment_status='Cancelled' WHERE id=?", (order_id,))
    return {"cancelled": True}


@app.get("/api/orders/{order_id}/invoice.pdf")
def download_invoice_pdf(order_id: int, account: dict[str, Any] = Depends(get_current_account)):
    with db_session() as conn:
        o = conn.execute("SELECT * FROM orders WHERE id=? AND account_id=?", (order_id, account["id"])).fetchone()
        if not o:
            raise HTTPException(status_code=404, detail="Order not found.")
        items = [dict(it) for it in conn.execute("SELECT * FROM order_items WHERE order_id=?", (order_id,)).fetchall()]
    pdf_bytes = generate_order_invoice_pdf(dict(o), items, account)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="invoice_{o["order_number"]}.pdf"'},
    )


# ---------------------------------------------------------------------------
# Credits, Acharyas, Media, FAQs, Notifications, CRM & Guruji Live
# ---------------------------------------------------------------------------
@app.get("/api/credits")
def get_credits(account: dict[str, Any] = Depends(get_current_account)):
    with db_session() as conn:
        ledger = [dict(r) for r in conn.execute("SELECT * FROM reward_ledger WHERE account_id=? ORDER BY id DESC", (account["id"],)).fetchall()]
    return {"balance": account["credits_balance"], "ledger": ledger}


@app.get("/api/acharyas")
def list_acharyas(q: str | None = None):
    with db_session() as conn:
        if q:
            rows = conn.execute(
                "SELECT * FROM acharyas WHERE lower(name) LIKE ? OR lower(specialty) LIKE ? ORDER BY id",
                (f"%{q.lower()}%", f"%{q.lower()}%"),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM acharyas ORDER BY id").fetchall()
    return {"acharyas": [dict(r) for r in rows]}


@app.post("/api/acharyas/{acharya_id}/request-call")
def request_acharya_call(acharya_id: int, account: dict[str, Any] = Depends(get_current_account)):
    now = datetime.now(timezone.utc).isoformat()
    with db_session() as conn:
        a = conn.execute("SELECT * FROM acharyas WHERE id=?", (acharya_id,)).fetchone()
        if not a:
            raise HTTPException(status_code=404, detail="Acharya not found.")
        conn.execute(
            "INSERT INTO notifications(account_id, title, body, is_read, created_at) VALUES (?,?,?,0,?)",
            (account["id"], "Click-to-Call Queued", f"Bridge call request queued with {a['name']} ({a['phone']}).", now),
        )
    return {"queued": True, "acharya": dict(a), "bridge_ref": f"CALL-{uuid.uuid4().hex[:6].upper()}"}


@app.get("/api/acharya-suggestions")
def list_acharya_suggestions(tab: str | None = None, member_id: int | None = None):
    with db_session() as conn:
        sql = "SELECT * FROM acharya_suggestions WHERE 1=1"
        params: list[Any] = []
        if tab and tab.lower() != "all":
            sql += " AND lower(suggestion_type)=?"
            params.append(tab.lower())
        if member_id:
            sql += " AND member_id=?"
            params.append(member_id)
        rows = conn.execute(sql + " ORDER BY id DESC", params).fetchall()
    return {"suggestions": [dict(r) for r in rows]}


@app.get("/api/blogs")
def list_blogs():
    with db_session() as conn:
        blogs = [dict(r) for r in conn.execute("SELECT * FROM blogs ORDER BY id DESC").fetchall()]
        for b in blogs:
            b["comments"] = [dict(c) for c in conn.execute("SELECT * FROM blog_comments WHERE blog_id=? ORDER BY id DESC", (b["id"],)).fetchall()]
    return {"blogs": blogs}


@app.post("/api/blogs/{blog_id}/like")
def like_blog(blog_id: int):
    with db_session() as conn:
        conn.execute("UPDATE blogs SET likes=likes+1 WHERE id=?", (blog_id,))
        row = conn.execute("SELECT likes FROM blogs WHERE id=?", (blog_id,)).fetchone()
    return {"likes": row["likes"] if row else 0}


@app.post("/api/blogs/{blog_id}/comment")
def comment_blog(blog_id: int, req: CommentReq, account: dict[str, Any] = Depends(get_current_account)):
    now = datetime.now(timezone.utc).isoformat()
    with db_session() as conn:
        conn.execute(
            "INSERT INTO blog_comments(blog_id, account_name, comment, created_at) VALUES (?,?,?,?)",
            (blog_id, account["name"], req.comment_text.strip(), now),
        )
        comments = [dict(c) for c in conn.execute("SELECT * FROM blog_comments WHERE blog_id=? ORDER BY id DESC", (blog_id,)).fetchall()]
    return {"comments": comments}


@app.get("/api/videos")
def list_videos():
    with db_session() as conn:
        videos = [dict(r) for r in conn.execute("SELECT * FROM videos ORDER BY id DESC").fetchall()]
        for v in videos:
            v["comments"] = [dict(c) for c in conn.execute("SELECT * FROM video_comments WHERE video_id=? ORDER BY id DESC", (v["id"],)).fetchall()]
    return {"videos": videos}


@app.post("/api/videos/{video_id}/like")
def like_video(video_id: int):
    with db_session() as conn:
        conn.execute("UPDATE videos SET likes=likes+1 WHERE id=?", (video_id,))
        row = conn.execute("SELECT likes FROM videos WHERE id=?", (video_id,)).fetchone()
    return {"likes": row["likes"] if row else 0}


@app.post("/api/videos/{video_id}/comment")
def comment_video(video_id: int, req: CommentReq, account: dict[str, Any] = Depends(get_current_account)):
    now = datetime.now(timezone.utc).isoformat()
    with db_session() as conn:
        conn.execute(
            "INSERT INTO video_comments(video_id, account_name, comment, created_at) VALUES (?,?,?,?)",
            (video_id, account["name"], req.comment_text.strip(), now),
        )
        comments = [dict(c) for c in conn.execute("SELECT * FROM video_comments WHERE video_id=? ORDER BY id DESC", (video_id,)).fetchall()]
    return {"comments": comments}


@app.get("/api/faqs")
def list_faqs():
    with db_session() as conn:
        rows = [dict(r) for r in conn.execute("SELECT * FROM faqs ORDER BY id").fetchall()]
    return {"faqs": rows}


@app.get("/api/notifications")
def list_notifications(account: dict[str, Any] = Depends(get_current_account)):
    with db_session() as conn:
        rows = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM notifications WHERE account_id=? ORDER BY id DESC LIMIT 30",
                (account["id"],),
            ).fetchall()
        ]
    return {"notifications": rows}


@app.post("/api/notifications/read-all")
def mark_notifications_read(account: dict[str, Any] = Depends(get_current_account)):
    with db_session() as conn:
        conn.execute("UPDATE notifications SET is_read=1 WHERE account_id=?", (account["id"],))
    return {"ok": True}


@app.post("/api/feedback")
def submit_feedback(req: FeedbackReq, account: dict[str, Any] = Depends(get_current_account)):
    now = datetime.now(timezone.utc).isoformat()
    with db_session() as conn:
        cur = conn.execute(
            "INSERT INTO feedback_entries(account_id, rating, message, created_at) VALUES (?,?,?,?)",
            (account["id"], req.rating, req.message, now),
        )
    return {"submitted": True, "id": cur.lastrowid}


# ---------------------------------------------------------------------------
# CRM Agent Console & Guruji Live Endpoints (GDVPanel parity)
# ---------------------------------------------------------------------------
@app.get("/api/crm/overview")
def crm_overview(account: dict[str, Any] = Depends(get_current_account)):
    if account["role"] != "crm_agent":
        raise HTTPException(status_code=403, detail="CRM Agent role required.")
    with db_session() as conn:
        leads = [dict(r) for r in conn.execute("SELECT * FROM visitor_leads ORDER BY id DESC LIMIT 30").fetchall()]
        txns = [
            dict(r)
            for r in conn.execute(
                """SELECT o.*, a.name as account_name, a.email as account_email, a.phone as account_phone
                   FROM orders o JOIN accounts a ON o.account_id=a.id ORDER BY o.id DESC LIMIT 50"""
            ).fetchall()
        ]
        acharyas = [
            dict(r)
            for r in conn.execute(
                "SELECT id, name, email, phone, role, reg_plan_id, subs_plan_id, max_sessions FROM accounts WHERE role='acharya'"
            ).fetchall()
        ]
        revenue = conn.execute("SELECT COALESCE(SUM(total_amount), 0) as rev FROM orders WHERE payment_status='Paid'").fetchone()["rev"]
    return {"total_revenue": revenue, "leads": leads, "transactions": txns, "acharya_accounts": acharyas}


@app.post("/api/crm/register-client")
def crm_register_client(req: CrmClientRegReq, account: dict[str, Any] = Depends(get_current_account)):
    if account["role"] != "crm_agent":
        raise HTTPException(status_code=403, detail="CRM Agent role required.")
    now = datetime.now(timezone.utc).isoformat()
    with db_session() as conn:
        plan = conn.execute("SELECT * FROM registration_plans WHERE id=? AND plan_scope='portal_reg'", (req.plan_id,)).fetchone()
        if not plan:
            raise HTTPException(status_code=404, detail="Portal plan not found.")
        existing = conn.execute("SELECT id FROM accounts WHERE phone=?", (req.client_phone.strip(),)).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="Client phone already registered.")
        order_num = f"CRM-{uuid.uuid4().hex[:7].upper()}"
        cur = conn.execute(
            """INSERT INTO accounts(account_type, role, name, email, phone, password_hash, crm_order_id, credits_balance, reg_plan_id, subs_plan_id, max_sessions, created_at)
               VALUES ('acharya','acharya', ?, ?, ?, ?, ?, 0, ?, ?, ?, ?)""",
            (
                req.client_name,
                req.client_email,
                req.client_phone.strip(),
                hash_password("Demo@1234"),
                order_num,
                plan["id"],
                plan["mapped_subscription_plan_id"] or 3,
                plan["max_systems"],
                now,
            ),
        )
        client_id = cur.lastrowid
        conn.execute(
            """INSERT INTO orders(order_number, account_id, member_id, order_kind, title, subtotal, discount, credits_used, gst, total_amount, payment_method, payment_status, razorpay_order_id, razorpay_payment_id, plan_id_granted, created_at)
               VALUES (?, ?, 0, 'registration', ?, ?, 0, 0, ?, ?, 'CRM Offline Registration', 'Paid', 'crm_offline', 'crm_verified', ?, ?)""",
            (
                order_num,
                client_id,
                f"GDVPanel {plan['name']}",
                plan["base_fee"] + plan["recurring_fee"],
                plan["gst"],
                plan["total_price"],
                plan["id"],
                now,
            ),
        )
    return {"registered": True, "client_id": client_id, "order_number": order_num, "default_password": "Demo@1234"}


@app.get("/api/guruji-live")
def guruji_live_status():
    return {
        "session_title": "Lal Kitab & Vashistha Jyotish Live Q&A Satsang",
        "host": "Gurudev GD Vashist Ji",
        "is_live": True,
        "viewer_count": 318,
        "topic": "Saturn & Rahu Karma Correction + Weekly Muhurat Guidance",
        "audio_stream": "/api/audio/9.wav",
    }


# ---------------------------------------------------------------------------
# SPA Static Serving
# ---------------------------------------------------------------------------
if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        target = FRONTEND_DIST / full_path
        if full_path and target.is_file():
            return FileResponse(str(target))
        return FileResponse(str(FRONTEND_DIST / "index.html"))
