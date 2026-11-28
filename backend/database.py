"""SQLite schema and connection helpers for AstroUnified (GDVPanel + AstroScience)."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

DB_PATH = Path(__file__).resolve().parent / "astro_unified.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def db_session() -> Iterator[sqlite3.Connection]:
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with db_session() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_type TEXT NOT NULL DEFAULT 'consumer', -- consumer | acharya | crm
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT UNIQUE,
                country_code TEXT NOT NULL DEFAULT '+91',
                password_hash TEXT,
                role TEXT NOT NULL DEFAULT 'user', -- user | acharya | crm_agent | admin
                crm_order_id TEXT,
                reg_plan_id INTEGER DEFAULT 0,
                subs_plan_id INTEGER DEFAULT 0,
                max_sessions INTEGER NOT NULL DEFAULT 5,
                is_meet_enabled INTEGER NOT NULL DEFAULT 0,
                language TEXT NOT NULL DEFAULT 'En',
                credits_balance INTEGER NOT NULL DEFAULT 300,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sessions (
                jti TEXT PRIMARY KEY,
                account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                portal TEXT NOT NULL DEFAULT 'consumer', -- consumer | acharya | crm
                device_label TEXT NOT NULL DEFAULT 'Web Browser',
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS otp_challenges (
                phone TEXT PRIMARY KEY,
                otp_code TEXT NOT NULL,
                expires_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS family_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                gender TEXT NOT NULL DEFAULT 'Male',
                dob TEXT NOT NULL, -- YYYY-MM-DD
                birth_time TEXT NOT NULL, -- HH:MM
                place_name TEXT NOT NULL,
                state_name TEXT NOT NULL DEFAULT '',
                country_name TEXT NOT NULL DEFAULT 'India',
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                tz_offset REAL NOT NULL DEFAULT 5.5,
                is_primary INTEGER NOT NULL DEFAULT 0,
                plan_id INTEGER NOT NULL DEFAULT 0, -- 0 = Free, >0 = Premium
                plan_name TEXT NOT NULL DEFAULT 'Free Plan',
                expiry_date TEXT
            );

            CREATE TABLE IF NOT EXISTS places_pincodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                place_name TEXT NOT NULL,
                district TEXT NOT NULL,
                state TEXT NOT NULL,
                country TEXT NOT NULL DEFAULT 'India',
                pincode TEXT,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                tz_offset REAL NOT NULL DEFAULT 5.5
            );

            CREATE TABLE IF NOT EXISTS registration_plans (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                plan_scope TEXT NOT NULL, -- portal_reg | consumer_sub
                crm_name TEXT,
                crm_sku TEXT,
                mapped_subscription_plan_id INTEGER,
                base_fee INTEGER NOT NULL,
                recurring_fee INTEGER NOT NULL,
                gst INTEGER NOT NULL DEFAULT 0,
                total_price INTEGER NOT NULL,
                duration_days INTEGER NOT NULL DEFAULT 30,
                max_systems INTEGER NOT NULL DEFAULT 1,
                features_json TEXT NOT NULL,
                is_popular INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                sku TEXT NOT NULL,
                instructor_name TEXT NOT NULL,
                instructor_bio TEXT NOT NULL,
                rating TEXT NOT NULL,
                reviews INTEGER NOT NULL,
                students INTEGER NOT NULL,
                duration_days INTEGER NOT NULL,
                lectures_count INTEGER NOT NULL,
                level TEXT NOT NULL,
                language TEXT NOT NULL,
                price INTEGER NOT NULL,
                original_price INTEGER NOT NULL,
                phone TEXT NOT NULL,
                description TEXT NOT NULL,
                learning_outcomes_json TEXT NOT NULL,
                requirements_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS course_videos (
                id INTEGER PRIMARY KEY,
                course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
                sequence_no INTEGER NOT NULL,
                section_title TEXT NOT NULL,
                title TEXT NOT NULL,
                duration TEXT NOT NULL,
                is_preview INTEGER NOT NULL DEFAULT 0,
                summary TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS course_enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
                enrolled_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                UNIQUE(account_id, course_id)
            );

            CREATE TABLE IF NOT EXISTS horoscope_categories (
                id INTEGER PRIMARY KEY,
                slug TEXT NOT NULL,
                title TEXT NOT NULL,
                title_hi TEXT NOT NULL,
                requires_premium INTEGER NOT NULL DEFAULT 1,
                has_sub_dialog TEXT, -- marriage | child | null
                description TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                category_slug TEXT NOT NULL, -- remedy | kit | bhajan | mantra | service | book
                category_name TEXT NOT NULL,
                title TEXT NOT NULL,
                price INTEGER NOT NULL,
                mrp INTEGER NOT NULL,
                sku TEXT NOT NULL,
                upay_id INTEGER DEFAULT 0,
                plan_type INTEGER DEFAULT 0, -- 0 = product, 2 = digital/subscription service
                is_audio INTEGER NOT NULL DEFAULT 0,
                audio_freq REAL DEFAULT 0,
                in_stock_india INTEGER NOT NULL DEFAULT 1,
                description TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS saved_folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                member_id INTEGER NOT NULL REFERENCES family_members(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS saved_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_id INTEGER NOT NULL REFERENCES saved_folders(id) ON DELETE CASCADE,
                account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                member_id INTEGER NOT NULL REFERENCES family_members(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                prediction_type TEXT NOT NULL,
                sentiment TEXT NOT NULL DEFAULT 'Default', -- Positive | Negative | MadeByYou | Default
                prediction_text TEXT NOT NULL,
                upay_id INTEGER NOT NULL DEFAULT 0,
                upay_text TEXT DEFAULT '',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS cart_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
                member_id INTEGER DEFAULT 0,
                quantity INTEGER NOT NULL DEFAULT 1,
                UNIQUE(account_id, product_id, member_id)
            );

            CREATE TABLE IF NOT EXISTS addresses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                address_type TEXT NOT NULL DEFAULT 'Home', -- Home | Work | Other
                full_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                line1 TEXT NOT NULL,
                line2 TEXT NOT NULL,
                pincode TEXT NOT NULL,
                city TEXT NOT NULL,
                state TEXT NOT NULL,
                country TEXT NOT NULL DEFAULT 'India'
            );

            CREATE TABLE IF NOT EXISTS coupons (
                code TEXT PRIMARY KEY,
                discount_percent INTEGER NOT NULL,
                max_discount INTEGER NOT NULL,
                description TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT UNIQUE NOT NULL,
                account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                member_id INTEGER DEFAULT 0,
                order_kind TEXT NOT NULL, -- product | subscription | registration | course | lalkitab_file
                title TEXT NOT NULL,
                subtotal INTEGER NOT NULL,
                discount INTEGER NOT NULL DEFAULT 0,
                credits_used INTEGER NOT NULL DEFAULT 0,
                gst INTEGER NOT NULL DEFAULT 0,
                total_amount INTEGER NOT NULL,
                payment_method TEXT NOT NULL DEFAULT 'Razorpay Sandbox (UPI/Card)',
                payment_status TEXT NOT NULL DEFAULT 'Paid', -- Paid | Cancelled | Pending
                razorpay_order_id TEXT NOT NULL,
                razorpay_payment_id TEXT,
                address_snapshot TEXT DEFAULT '',
                plan_id_granted INTEGER DEFAULT 0,
                course_id_granted INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
                product_id INTEGER DEFAULT 0,
                title TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                unit_price INTEGER NOT NULL,
                plan_type INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS reward_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                delta INTEGER NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS product_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
                account_name TEXT NOT NULL,
                rating INTEGER NOT NULL DEFAULT 5,
                review_text TEXT NOT NULL,
                verified_buyer INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS acharyas (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                specialty TEXT NOT NULL,
                languages TEXT NOT NULL,
                experience_years INTEGER NOT NULL,
                phone TEXT NOT NULL,
                available INTEGER NOT NULL DEFAULT 1,
                rating TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS acharya_suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER NOT NULL REFERENCES family_members(id) ON DELETE CASCADE,
                suggestion_type TEXT NOT NULL, -- service | product | file
                title TEXT NOT NULL,
                notes TEXT NOT NULL,
                linked_product_id INTEGER DEFAULT 0,
                linked_plan_id INTEGER DEFAULT 0,
                report_summary TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS blogs (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                summary TEXT NOT NULL,
                content TEXT NOT NULL,
                likes INTEGER NOT NULL DEFAULT 12,
                published_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS blog_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                blog_id INTEGER NOT NULL REFERENCES blogs(id) ON DELETE CASCADE,
                account_name TEXT NOT NULL,
                comment TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                duration TEXT NOT NULL,
                is_live INTEGER NOT NULL DEFAULT 0,
                likes INTEGER NOT NULL DEFAULT 28,
                summary TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS video_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
                account_name TEXT NOT NULL,
                comment TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS faqs (
                id INTEGER PRIMARY KEY,
                scope TEXT NOT NULL, -- portal | app
                question TEXT NOT NULL,
                answer TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                is_read INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS visitor_leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact TEXT NOT NULL,
                study_astro TEXT NOT NULL,
                pro_astro TEXT NOT NULL,
                city TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS feedback_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                rating INTEGER NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
