#!/usr/bin/env python3
"""Mini URL Shortener - CLI application using only Python's standard library."""

import argparse
import secrets
import sqlite3
import string
import sys
import webbrowser
from pathlib import Path
from urllib.parse import urlparse


DB_PATH = Path(__file__).resolve().parent / "urls.db"
CODE_ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 6


def get_connection():
    """Open the persistent SQLite database and create its table if needed."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            original_url TEXT NOT NULL,
            clicks INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    return conn


def validate_url(url: str) -> str:
    """Validate that a URL has an HTTP(S) scheme and a hostname."""
    url = url.strip()
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Invalid URL. Use a full http:// or https:// URL.")
    return url


def generate_code(conn) -> str:
    """Generate a short, collision-free random code."""
    while True:
        code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))
        exists = conn.execute(
            "SELECT 1 FROM urls WHERE code = ?", (code,)
        ).fetchone()
        if not exists:
            return code


def shorten(url: str, alias: str | None = None) -> str:
    """Store a URL and return its short code."""
    url = validate_url(url)

    if alias:
        alias = alias.strip()
        if not alias or not alias.isalnum() or len(alias) > 32:
            raise ValueError("Alias must be 1-32 letters/numbers only.")

    with get_connection() as conn:
        # Reusing the same URL returns the existing mapping unless a new alias
        # was explicitly requested.
        if not alias:
            row = conn.execute(
                "SELECT code FROM urls WHERE original_url = ? ORDER BY id LIMIT 1",
                (url,),
            ).fetchone()
            if row:
                return row["code"]

        code = alias or generate_code(conn)

        try:
            conn.execute(
                "INSERT INTO urls (code, original_url) VALUES (?, ?)",
                (code, url),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError(f"Code/alias '{code}' already exists.")

        return code


def resolve(code: str, open_url: bool = False) -> tuple[str, int]:
    """Resolve a code, increment its click count, and optionally open it."""
    code = code.strip()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT original_url, clicks FROM urls WHERE code = ?", (code,)
        ).fetchone()

        if not row:
            raise KeyError(f"No shortened URL found for code '{code}'.")

        new_clicks = row["clicks"] + 1
        conn.execute(
            "UPDATE urls SET clicks = ? WHERE code = ?",
            (new_clicks, code),
        )
        conn.commit()

    url = row["original_url"]
    if open_url:
        webbrowser.open(url)
    return url, new_clicks


def list_urls() -> list[sqlite3.Row]:
    """Return all stored mappings."""
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT code, original_url, clicks, created_at
            FROM urls
            ORDER BY id DESC
            """
        ).fetchall()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="urlshort",
        description="A persistent mini URL shortener using Python + SQLite.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    shorten_parser = subparsers.add_parser(
        "shorten", help="Create a short code for a URL."
    )
    shorten_parser.add_argument("url", help="Full http:// or https:// URL.")
    shorten_parser.add_argument(
        "--alias", help="Optional custom alias, e.g. --alias mysite."
    )

    resolve_parser = subparsers.add_parser(
        "resolve", help="Resolve a short code to its original URL."
    )
    resolve_parser.add_argument("code", help="Short code to resolve.")
    resolve_parser.add_argument(
        "--open", action="store_true", help="Open the resolved URL in your browser."
    )

    subparsers.add_parser("list", help="List all stored URL mappings.")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "shorten":
            code = shorten(args.url, args.alias)
            print(f"Short code: {code}")
            print(f"Short URL:  urlshort://{code}")

        elif args.command == "resolve":
            url, clicks = resolve(args.code, args.open)
            print(f"Original URL: {url}")
            print(f"Click count: {clicks}")
            if args.open:
                print("Opened in your default browser.")

        elif args.command == "list":
            rows = list_urls()
            if not rows:
                print("No shortened URLs yet.")
                return 0

            print(f"{'CODE':<14} {'CLICKS':<8} ORIGINAL URL")
            print("-" * 90)
            for row in rows:
                print(
                    f"{row['code']:<14} {row['clicks']:<8} {row['original_url']}"
                )

        return 0

    except (ValueError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
