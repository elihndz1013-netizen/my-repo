"""
Cash Buyers List Manager
========================
Manages a list of cash buyers stored in Supabase.
Supports adding, searching, exporting, and scraping for new leads.
"""

import os
import json
import csv
import time
from datetime import datetime

# ---------------------------------------------------------------------------
# Supabase client setup
# ---------------------------------------------------------------------------

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://rpmpnnwgoknuiikeoals.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "YOUR_SUPABASE_KEY_HERE")

_supabase_client = None


def _get_supabase():
    """Lazy-init Supabase client so import never crashes if lib is missing."""
    global _supabase_client
    if _supabase_client is None:
        try:
            from supabase import create_client
            _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
            print("[Supabase] Connected successfully.")
        except ImportError:
            print("[Supabase] 'supabase' package not installed – running in offline/local mode.")
            _supabase_client = None
        except Exception as e:
            print(f"[Supabase] Connection error: {e}")
            _supabase_client = None
    return _supabase_client


# ---------------------------------------------------------------------------
# Local fallback storage (JSON file) when Supabase is unavailable
# ---------------------------------------------------------------------------

LOCAL_FILE = os.path.join(os.path.dirname(__file__), "cash_buyers_local.json")


def _load_local():
    if os.path.exists(LOCAL_FILE):
        with open(LOCAL_FILE, "r") as f:
            return json.load(f)
    return []


def _save_local(buyers):
    with open(LOCAL_FILE, "w") as f:
        json.dump(buyers, f, indent=2, default=str)


# ---------------------------------------------------------------------------
# CRUD operations
# ---------------------------------------------------------------------------

TABLE = "cash_buyers"


def add_buyer(
    name: str,
    email: str = "",
    phone: str = "",
    location: str = "",
    buy_criteria: str = "",
    max_budget: str = "",
    preferred_property_type: str = "",
    source: str = "manual",
    notes: str = "",
):
    """Add a cash buyer to the list."""
    buyer = {
        "name": name,
        "email": email,
        "phone": phone,
        "location": location,
        "buy_criteria": buy_criteria,
        "max_budget": max_budget,
        "preferred_property_type": preferred_property_type,
        "source": source,
        "notes": notes,
        "added_at": datetime.utcnow().isoformat(),
        "last_contacted": None,
        "status": "active",
    }

    client = _get_supabase()
    if client:
        try:
            result = client.table(TABLE).insert(buyer).execute()
            print(f"[✓] Added buyer '{name}' to Supabase.")
            return result.data
        except Exception as e:
            print(f"[!] Supabase insert failed: {e}")
            print("    Falling back to local storage.")

    # Fallback to local JSON
    buyers = _load_local()
    buyer["id"] = len(buyers) + 1
    buyers.append(buyer)
    _save_local(buyers)
    print(f"[✓] Added buyer '{name}' to local file.")
    return buyer


def list_buyers(status_filter="active"):
    """List all buyers, optionally filtered by status."""
    client = _get_supabase()
    if client:
        try:
            query = client.table(TABLE).select("*")
            if status_filter:
                query = query.eq("status", status_filter)
            result = query.order("added_at", desc=True).execute()
            return result.data
        except Exception as e:
            print(f"[!] Supabase query failed: {e}")

    # Fallback
    buyers = _load_local()
    if status_filter:
        buyers = [b for b in buyers if b.get("status") == status_filter]
    return buyers


def search_buyers(keyword: str):
    """Search buyers by name, location, or buy criteria."""
    keyword_lower = keyword.lower()
    all_buyers = list_buyers(status_filter=None)
    matches = []
    for b in all_buyers:
        searchable = f"{b.get('name','')} {b.get('location','')} {b.get('buy_criteria','')} {b.get('preferred_property_type','')}".lower()
        if keyword_lower in searchable:
            matches.append(b)
    return matches


def update_buyer(buyer_id, **updates):
    """Update a buyer record by ID."""
    client = _get_supabase()
    if client:
        try:
            result = client.table(TABLE).update(updates).eq("id", buyer_id).execute()
            print(f"[✓] Updated buyer {buyer_id}.")
            return result.data
        except Exception as e:
            print(f"[!] Supabase update failed: {e}")

    # Fallback
    buyers = _load_local()
    for b in buyers:
        if b.get("id") == buyer_id:
            b.update(updates)
            _save_local(buyers)
            print(f"[✓] Updated buyer {buyer_id} locally.")
            return b
    print(f"[!] Buyer {buyer_id} not found.")
    return None


def remove_buyer(buyer_id):
    """Soft-delete a buyer by setting status to 'removed'."""
    return update_buyer(buyer_id, status="removed")


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

EXPORT_DIR = os.path.join(os.path.dirname(__file__), "exports")


def export_buyers_csv(filename="cash_buyers_export.csv"):
    """Export the active buyer list to a CSV file."""
    os.makedirs(EXPORT_DIR, exist_ok=True)
    filepath = os.path.join(EXPORT_DIR, filename)
    buyers = list_buyers(status_filter="active")

    if not buyers:
        print("[!] No active buyers to export.")
        return None

    fieldnames = [
        "name", "email", "phone", "location",
        "buy_criteria", "max_budget", "preferred_property_type",
        "source", "notes", "added_at", "last_contacted", "status",
    ]

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(buyers)

    print(f"[✓] Exported {len(buyers)} buyers → {filepath}")
    return filepath


# ---------------------------------------------------------------------------
# Scrape public cash-buyer leads using Oxylabs
# ---------------------------------------------------------------------------

def scrape_cash_buyer_leads(location="Houston TX"):
    """
    Scrape Google search results for cash buyer leads in a given location.
    Uses Oxylabs Realtime API.
    """
    from oxylabs import RealtimeClient

    username = os.environ.get("OXYLABS_USERNAME", "YOUR_OXYLABS_USERNAME_HERE")
    password = os.environ.get("OXYLABS_PASSWORD", "YOUR_OXYLABS_PASSWORD_HERE")

    queries = [
        f"we buy houses cash {location}",
        f"cash home buyers {location}",
        f"real estate investors {location} buy houses",
        f"sell my house fast {location}",
    ]

    leads = []

    try:
        client = RealtimeClient(username=username, password=password)
    except Exception as e:
        print(f"[!] Oxylabs connection failed: {e}")
        return leads

    for query in queries:
        print(f"  🔍 Searching: \"{query}\" ...")
        try:
            response = client.scrape_search(
                source="google",
                query=query,
                domain="com",
                locale="en_us",
                parse=True,
            )

            for item in response.get("results", {}).get("organic", []):
                title = item.get("title", "")
                url = item.get("url", "")
                description = item.get("description", "")

                # Skip irrelevant results
                if not title:
                    continue

                lead = {
                    "name": title,
                    "source": "oxylabs_scrape",
                    "notes": f"URL: {url}\n{description}",
                    "location": location,
                    "buy_criteria": "cash buyer lead",
                }
                leads.append(lead)
                print(f"    → {title}")

            time.sleep(1)  # Small delay between queries

        except Exception as e:
            print(f"    [!] Error on query '{query}': {e}")

    print(f"\n[✓] Found {len(leads)} potential cash buyer leads in {location}.")
    return leads


def scrape_and_save_leads(location="Houston TX"):
    """Scrape leads and auto-add them to the buyer list."""
    leads = scrape_cash_buyer_leads(location)
    added = 0
    for lead in leads:
        add_buyer(
            name=lead["name"],
            location=lead.get("location", ""),
            buy_criteria=lead.get("buy_criteria", ""),
            source=lead.get("source", "scraped"),
            notes=lead.get("notes", ""),
        )
        added += 1
    print(f"[✓] Added {added} new leads to the cash buyers list.")
    return added


# ---------------------------------------------------------------------------
# Pretty-print helpers
# ---------------------------------------------------------------------------

def print_buyer_table(buyers):
    """Print a formatted table of buyers to the console."""
    if not buyers:
        print("  (no buyers found)")
        return

    print(f"\n{'#':<4} {'Name':<30} {'Location':<20} {'Phone':<16} {'Email':<30} {'Status':<8}")
    print("─" * 112)
    for i, b in enumerate(buyers, 1):
        print(
            f"{i:<4} "
            f"{b.get('name','')[:28]:<30} "
            f"{b.get('location','')[:18]:<20} "
            f"{b.get('phone','')[:14]:<16} "
            f"{b.get('email','')[:28]:<30} "
            f"{b.get('status',''):<8}"
        )
    print(f"\nTotal: {len(buyers)} buyer(s)\n")


# ---------------------------------------------------------------------------
# CLI Interface
# ---------------------------------------------------------------------------

def cli():
    """Interactive command-line interface for managing the cash buyers list."""
    import sys

    print("\n" + "=" * 60)
    print("  💰  CASH BUYERS LIST MANAGER")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("""
Usage:
  python cash_buyers.py add       — Add a new buyer interactively
  python cash_buyers.py list      — List all active buyers
  python cash_buyers.py search X  — Search buyers by keyword
  python cash_buyers.py export    — Export list to CSV
  python cash_buyers.py scrape X  — Scrape leads for location X
  python cash_buyers.py demo      — Add sample demo buyers
        """)
        return

    command = sys.argv[1].lower()

    if command == "add":
        print("\n--- Add New Cash Buyer ---")
        name = input("  Name: ").strip()
        if not name:
            print("  [!] Name is required.")
            return
        email = input("  Email: ").strip()
        phone = input("  Phone: ").strip()
        location = input("  Location / Market: ").strip()
        buy_criteria = input("  Buy criteria (e.g. SFH under 200k): ").strip()
        max_budget = input("  Max budget: ").strip()
        prop_type = input("  Preferred property type: ").strip()
        notes = input("  Notes: ").strip()

        add_buyer(
            name=name, email=email, phone=phone,
            location=location, buy_criteria=buy_criteria,
            max_budget=max_budget, preferred_property_type=prop_type,
            notes=notes,
        )

    elif command == "list":
        buyers = list_buyers()
        print_buyer_table(buyers)

    elif command == "search":
        keyword = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        if not keyword:
            keyword = input("  Search keyword: ").strip()
        results = search_buyers(keyword)
        print(f"\n  Results for '{keyword}':")
        print_buyer_table(results)

    elif command == "export":
        export_buyers_csv()

    elif command == "scrape":
        location = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Houston TX"
        print(f"\n  Scraping cash buyer leads in: {location}\n")
        scrape_and_save_leads(location)

    elif command == "demo":
        print("\n  Adding sample demo buyers...\n")
        demo_buyers = [
            {"name": "Marcus Johnson", "email": "marcus.j@investormail.com", "phone": "713-555-0142",
             "location": "Houston TX", "buy_criteria": "SFH under $150k, any condition",
             "max_budget": "$150,000", "preferred_property_type": "Single Family",
             "notes": "Prefers 3bd/2ba. Closes in 10 days. Repeat buyer."},
            {"name": "Apex Capital Holdings LLC", "email": "deals@apexcapital.io", "phone": "832-555-0278",
             "location": "Houston TX", "buy_criteria": "Multi-family 2-8 units, value-add",
             "max_budget": "$500,000", "preferred_property_type": "Multi-Family",
             "notes": "Institutional buyer, proof of funds on file."},
            {"name": "Sandra & Ray Kim", "email": "kimproperties@gmail.com", "phone": "281-555-0399",
             "location": "Katy TX", "buy_criteria": "Turnkey rentals, newer builds",
             "max_budget": "$250,000", "preferred_property_type": "Single Family",
             "notes": "Buy-and-hold strategy. Prefer Katy ISD."},
            {"name": "David Chen", "email": "dchen.rei@outlook.com", "phone": "713-555-0561",
             "location": "Houston TX", "buy_criteria": "Fix & flip, heavy rehab OK",
             "max_budget": "$120,000", "preferred_property_type": "Single Family",
             "notes": "Has own contractor crew. Cash close 7 days."},
            {"name": "Greenfield Investments", "email": "acquisitions@greenfieldinv.com", "phone": "346-555-0833",
             "location": "Sugar Land TX", "buy_criteria": "Land parcels 1-5 acres for development",
             "max_budget": "$300,000", "preferred_property_type": "Land",
             "notes": "Looking for residential subdivision opportunities."},
        ]
        for b in demo_buyers:
            add_buyer(**b)
        print(f"\n  [✓] Added {len(demo_buyers)} demo buyers.")

    else:
        print(f"  [!] Unknown command: '{command}'")
        print("  Run 'python cash_buyers.py' for usage info.")


if __name__ == "__main__":
    cli()
