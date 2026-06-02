#!/usr/bin/env python3
"""
sync_listings.py — Niko in London listing sync tool
====================================================
Reads listings.json and rebuilds the INLINE_DATA block inside index.html.
Run this any time listings.json is updated (e.g. after adding a new property).

Usage:
    python3 sync_listings.py
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
LISTINGS_FILE = ROOT / "listings.json"
HTML_FILE = ROOT / "index.html"

POSTCODE_TO_ZONE = {
    # Zone 1
    "EC1A": 1, "EC1M": 1, "EC1N": 1, "EC1R": 1, "EC1V": 1, "EC1Y": 1,
    "EC2A": 1, "EC2M": 1, "EC2N": 1, "EC2R": 1, "EC2V": 1, "EC2Y": 1,
    "EC3A": 1, "EC3M": 1, "EC3N": 1, "EC3R": 1, "EC3V": 1,
    "EC4A": 1, "EC4M": 1, "EC4N": 1, "EC4R": 1, "EC4V": 1, "EC4Y": 1,
    "WC1A": 1, "WC1B": 1, "WC1E": 1, "WC1H": 1, "WC1N": 1, "WC1R": 1,
    "WC1V": 1, "WC1X": 1, "WC2A": 1, "WC2B": 1, "WC2E": 1, "WC2H": 1,
    "WC2N": 1, "WC2R": 1,
    "N1": 1,   # Angel/Old Street area
    "SE1": 1,  # Southwark/London Bridge
    "SW1A": 1, "SW1E": 1, "SW1H": 1, "SW1P": 1, "SW1V": 1, "SW1W": 1,
    "SW1X": 1, "SW1Y": 1,
    "W1A": 1, "W1B": 1, "W1C": 1, "W1D": 1, "W1F": 1, "W1G": 1,
    "W1H": 1, "W1J": 1, "W1K": 1, "W1S": 1, "W1T": 1, "W1U": 1, "W1W": 1,
    "NW1": 1,
    # Zone 2
    "E2": 2, "E3": 2, "E8": 2,
    "EC1V": 2,  # parts of N1/Old St are z2 depending on station
    "N4": 2, "N5": 2, "N7": 2,
    "NW3": 2, "NW5": 2, "NW6": 2, "NW8": 2,
    "SE5": 2, "SE11": 2, "SE15": 2, "SE16": 2, "SE17": 2,
    "SW2": 2, "SW4": 2, "SW6": 2, "SW8": 2, "SW9": 2, "SW10": 2, "SW11": 2,
    "W2": 2, "W6": 2, "W9": 2, "W10": 2, "W11": 2, "W12": 2, "W14": 2,
    # Zone 3
    "E15": 3, "E16": 3,
    "N8": 3, "N15": 3, "N16": 3, "N22": 3,
    "NW2": 3, "NW10": 3,
    "SE4": 3, "SE6": 3, "SE8": 3, "SE14": 3, "SE18": 3, "SE23": 3, "SE24": 3,
    "SW12": 3, "SW16": 3, "SW17": 3,
    "W3": 3, "W4": 3, "W5": 3, "W7": 3,
}

def postcode_to_zone(postcode: str) -> int:
    """Best-effort zone lookup from postcode. Falls back to 2."""
    pc = postcode.strip().upper()
    # Try full outward code first (e.g. "EC1V")
    if pc in POSTCODE_TO_ZONE:
        return POSTCODE_TO_ZONE[pc]
    # Try just letters + first digit (e.g. "SW" doesn't help but "SW8" does)
    # Already handled above. Fall back to zone 2 for central London unknowns.
    return 2


def slugify(text: str) -> str:
    """Convert address/title to URL-safe slug."""
    import unicodedata
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text


def make_image_paths(listing_id: str, count: int = 4) -> list:
    return [f"images/{listing_id}/img_{i}.jpg" for i in range(1, count + 1)]


def load_listings() -> dict:
    with open(LISTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_listings(data: dict) -> None:
    data["exported_at"] = datetime.now(timezone.utc).isoformat()
    data["count"] = len(data["listings"])
    with open(LISTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✓ listings.json updated ({data['count']} listings)")


def sync_html(data: dict) -> None:
    """Replace the INLINE_DATA line in index.html with fresh data."""
    html = HTML_FILE.read_text(encoding="utf-8")
    inline_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    new_line = f"const INLINE_DATA = {inline_json};"
    # Replace everything between the comment marker and the blank line after it
    pattern = r"(// ── INLINE DATA.*?──\n)const INLINE_DATA = \{.*?\};"
    replacement = r"\g<1>" + new_line
    new_html, n = re.subn(pattern, replacement, html, count=1, flags=re.DOTALL)
    if n == 0:
        print("  ✗ Could not find INLINE_DATA block in index.html")
        sys.exit(1)
    HTML_FILE.write_text(new_html, encoding="utf-8")
    print(f"  ✓ index.html INLINE_DATA synced")


def add_listing(listing: dict) -> None:
    """
    Add or replace a listing in listings.json, then sync index.html.
    listing dict must have at minimum: title, address, postcode, weekly, beds
    """
    data = load_listings()

    # Auto-fill derived fields
    listing.setdefault("id", slugify(listing["address"]))
    listing.setdefault("zone", postcode_to_zone(listing["postcode"]))
    listing.setdefault("monthly", round(listing["weekly"] * 52 / 12))
    listing.setdefault("furnish", "带家具")
    listing.setdefault("features", [])
    listing.setdefault("images", make_image_paths(listing["id"]))
    listing.setdefault("format", "niko")
    listing.setdefault("active", True)
    listing["updated_at"] = datetime.now(timezone.utc).isoformat()

    # Upsert: replace if same id exists
    existing_ids = [d["id"] for d in data["listings"]]
    if listing["id"] in existing_ids:
        idx = existing_ids.index(listing["id"])
        data["listings"][idx] = listing
        print(f"  ↺ Updated existing listing: {listing['id']}")
    else:
        data["listings"].append(listing)
        print(f"  + Added new listing: {listing['id']}")

    save_listings(data)
    sync_html(data)


def remove_listing(listing_id: str) -> None:
    """Set a listing to inactive (soft delete)."""
    data = load_listings()
    for d in data["listings"]:
        if d["id"] == listing_id:
            d["active"] = False
            d["updated_at"] = datetime.now(timezone.utc).isoformat()
            print(f"  ✓ Deactivated: {listing_id}")
            break
    else:
        print(f"  ✗ Listing not found: {listing_id}")
        return
    save_listings(data)
    sync_html(data)


def netlify_deploy(site_dir: Path = ROOT) -> None:
    """Deploy to Netlify using the CLI (requires `netlify link` to have been run once)."""
    import subprocess as sp
    print("\n🚀 部署到 Netlify …")
    result = sp.run(
        ["netlify", "deploy", "--prod", "--dir", str(site_dir)],
        capture_output=False,   # show live output
    )
    if result.returncode == 0:
        print("  ✓ 部署成功！网站已更新。")
    else:
        print("  ✗ 部署失败。请检查 netlify CLI 是否已安装并登录（netlify login）。")


if __name__ == "__main__":
    import argparse as _ap
    p = _ap.ArgumentParser(description="Sync listings.json → index.html, optionally deploy.")
    p.add_argument("--deploy", action="store_true", help="部署到 Netlify（需已运行 netlify link）")
    args = p.parse_args()

    print("Syncing listings.json → index.html …")
    data = load_listings()
    sync_html(data)
    print(f"Done. {data['count']} listings active.")

    if args.deploy:
        netlify_deploy()
