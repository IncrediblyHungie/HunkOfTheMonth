#!/usr/bin/env python3
"""
Test script to explore Printify API and understand calendar blueprint structure
"""
import requests
import json

PRINTIFY_API_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzN2Q0YmQzMDM1ZmUxMWU5YTgwM2FiN2VlYjNjY2M5NyIsImp0aSI6ImQ3ZDQyYzJlMTAyOGJlMGI4YTRhMjFhNmQ0M2Y1YTU4MTMzNGUxZWI2MGNiYTMyNTAzZGE3Mzk5MzZhOTI0NDIzNjA5NTAxMjU4ZmRjMGRlIiwiaWF0IjoxNzYyMDM0OTk3LjQwMjI3NywibmJmIjoxNzYyMDM0OTk3LjQwMjI3OCwiZXhwIjoxNzkzNTcwOTk3LjM5MzQzNCwic3ViIjoiMjUyMzIwNzQiLCJzY29wZXMiOlsic2hvcHMubWFuYWdlIiwic2hvcHMucmVhZCIsImNhdGFsb2cucmVhZCIsIm9yZGVycy5yZWFkIiwib3JkZXJzLndyaXRlIiwicHJvZHVjdHMucmVhZCIsInByb2R1Y3RzLndyaXRlIiwid2ViaG9va3MucmVhZCIsIndlYmhvb2tzLndyaXRlIiwidXBsb2Fkcy5yZWFkIiwidXBsb2Fkcy53cml0ZSIsInByaW50X3Byb3ZpZGVycy5yZWFkIiwidXNlci5pbmZvIl19.nXm_OPGYRZidVtKUg-99jgMr_hfEembuMwk1p4HgEEwa6PtYwB5UilLR7N5pGdpx_2OF2eYdKUofsUBVMiOk-FfzUYhvI7_SZall8EcaXgE147iTGrOmlr0tDjQF9T9dX0UyurF1GaaNS8ohMy5sB79ksUZrY_c5M29xpLgrGlYGVc971HAZvxZvJtFCXn54yqf0Q_mVk13Jr66wOo2Mxx-3AyVn5_AZfPtDLfIxdlc0fZkK5VIpyGXys5at5N06diMTMtN938fhBUmuBUcXRELBlExWWqTUjyI_BRkxXBG0Q7rlBy1NDbuandakzTk3ZKw5k_wkBsItoNWiKG7_n0RtaCR_cG41qPElH6f--UhAbGbfbUjZfA3aDI3nPcOGOQiRGzVX1IFQ3x8A0fE6rg-6VaPhnnmyFs4IxBCyf_Jf4vYD3Gwq9YAgR3VV_0R-UklvCCMRktzS04wtiQ2QDKzsodC8gJ-eyZU9oarUSNZUF8dfe0rs80ZlssczHsDIZfsPf2231NVvUD2gpg556eAZIY-OAeURi6cKSdlJGmE4Tg42sYIzPD9rId4IuqX1ObVEPdWlnLtPiq_ovwVWpNex9gdpE1LDf8XppK2Fyg07cZDHQLpIrkBBYavnvkNRScyO0Y7pclzKPW3NvHiyoJk5lx3yaZXae70wOIHHK_Q"

def test_printify_connection():
    """Test basic Printify API connection"""
    print("Testing Printify API connection...")

    headers = {
        "Authorization": f"Bearer {PRINTIFY_API_TOKEN}",
        "Content-Type": "application/json"
    }

    # Get catalog blueprints
    response = requests.get(
        "https://api.printify.com/v1/catalog/blueprints.json",
        headers=headers
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        blueprints = response.json()
        print(f"✓ Successfully retrieved {len(blueprints)} blueprints")

        # Find calendar blueprints
        calendar_blueprints = [
            b for b in blueprints
            if 'calendar' in b.get('title', '').lower()
        ]

        print(f"\n📅 Found {len(calendar_blueprints)} calendar blueprints:")
        for cal in calendar_blueprints:
            print(f"  - ID: {cal['id']}, Title: {cal['title']}")

        # Save calendar blueprints for inspection
        with open('/tmp/calendar_blueprints.json', 'w') as f:
            json.dump(calendar_blueprints, f, indent=2)
        print("\n✓ Saved calendar blueprints to /tmp/calendar_blueprints.json")

        return calendar_blueprints
    else:
        print(f"✗ API Error: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def get_blueprint_details(blueprint_id):
    """Get detailed information about a specific blueprint"""
    print(f"\nGetting details for blueprint {blueprint_id}...")

    headers = {
        "Authorization": f"Bearer {PRINTIFY_API_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.get(
        f"https://api.printify.com/v1/catalog/blueprints/{blueprint_id}.json",
        headers=headers
    )

    if response.status_code == 200:
        blueprint = response.json()
        print(f"✓ Blueprint: {blueprint.get('title')}")
        print(f"  Print areas: {len(blueprint.get('print_areas', []))}")

        # Save detailed blueprint
        with open(f'/tmp/blueprint_{blueprint_id}.json', 'w') as f:
            json.dump(blueprint, f, indent=2)
        print(f"✓ Saved to /tmp/blueprint_{blueprint_id}.json")

        return blueprint
    else:
        print(f"✗ Error: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    # Test connection and find calendars
    calendars = test_printify_connection()

    if calendars:
        # Get details for first calendar blueprint
        if len(calendars) > 0:
            print("\n" + "="*60)
            get_blueprint_details(calendars[0]['id'])
