#!/usr/bin/env python3
"""
Fetch Printify calendar configurations
Run this to get print provider IDs and variant IDs for all calendar products
"""
import requests
import json
import sys

def fetch_calendar_configs(api_token):
    """Fetch configuration details for all calendar products"""

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    # Calendar blueprints to check
    calendar_blueprints = [
        (1253, "Calendar (2026)"),
        (1170, "Desktop Calendar"),
        (965, "Standard Wall Calendar (2026)"),
        (1183, "Wall Calendars (2026)"),
        (1353, "Desktop Calendar (2026 grid)"),
        (1352, "Simplex Desk Calendar (2026 grid)")
    ]

    results = {}

    for blueprint_id, name in calendar_blueprints:
        print(f"\n{'='*70}")
        print(f"Analyzing: {name} (Blueprint {blueprint_id})")
        print('='*70)

        try:
            # Get print providers
            providers_response = requests.get(
                f"https://api.printify.com/v1/catalog/blueprints/{blueprint_id}/print_providers.json",
                headers=headers,
                timeout=10
            )

            if providers_response.status_code != 200:
                print(f"❌ Error getting providers: {providers_response.status_code}")
                print(f"   Response: {providers_response.text}")
                continue

            providers = providers_response.json()

            if not providers:
                print(f"⚠️  No print providers available")
                continue

            # Use first available provider
            provider = providers[0]
            print(f"✓ Print Provider: {provider['title']} (ID: {provider['id']})")

            # Get variants
            variants_response = requests.get(
                f"https://api.printify.com/v1/catalog/blueprints/{blueprint_id}/print_providers/{provider['id']}/variants.json",
                headers=headers,
                timeout=10
            )

            if variants_response.status_code != 200:
                print(f"❌ Error getting variants: {variants_response.status_code}")
                continue

            variants_data = variants_response.json()
            variants = variants_data.get('variants', [])

            if not variants:
                print(f"⚠️  No variants available")
                continue

            # Use first variant
            variant = variants[0]
            print(f"✓ Variant: {variant.get('title', 'N/A')} (ID: {variant['id']})")

            # Check placeholders
            placeholders = variant.get('placeholders', [])
            print(f"✓ Placeholders: {len(placeholders)}")

            placeholder_info = {}
            for ph in placeholders:
                position = ph.get('position')
                width = ph.get('width')
                height = ph.get('height')
                placeholder_info[position] = f"{width}x{height}px"

            # Check if it has the 13-placeholder structure we need
            has_months = all(
                month in placeholder_info
                for month in ['january', 'february', 'march', 'april', 'may', 'june',
                             'july', 'august', 'september', 'october', 'november', 'december']
            )

            if has_months:
                print(f"✅ Compatible! Has all 12 month placeholders")

                # Show placeholder dimensions
                print(f"\n   Placeholder dimensions:")
                for pos, dims in list(placeholder_info.items())[:3]:
                    print(f"   - {pos}: {dims}")
                if len(placeholder_info) > 3:
                    print(f"   ... and {len(placeholder_info) - 3} more")
            else:
                print(f"⚠️  Incompatible: Missing month placeholders")
                print(f"   Available: {', '.join(list(placeholder_info.keys())[:5])}")

            # Store configuration
            results[blueprint_id] = {
                'name': name,
                'blueprint_id': blueprint_id,
                'print_provider_id': provider['id'],
                'print_provider_name': provider['title'],
                'variant_id': variant['id'],
                'variant_title': variant.get('title', 'N/A'),
                'compatible': has_months,
                'placeholders': placeholder_info
            }

        except Exception as e:
            print(f"❌ Error: {e}")
            continue

    # Print summary
    print(f"\n\n{'='*70}")
    print("CONFIGURATION SUMMARY")
    print('='*70)

    compatible = [r for r in results.values() if r['compatible']]

    if compatible:
        print(f"\n✅ Found {len(compatible)} compatible calendar(s):\n")

        for config in compatible:
            print(f"'{config['name']}':")
            print(f"  blueprint_id: {config['blueprint_id']}")
            print(f"  print_provider_id: {config['print_provider_id']}")
            print(f"  variant_id: {config['variant_id']}")
            print()

    # Save to file
    with open('/tmp/printify_calendar_configs.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("✓ Full details saved to /tmp/printify_calendar_configs.json")

    return results

if __name__ == "__main__":
    # Try to get token from environment or Fly.io secrets
    import os
    import subprocess

    api_token = os.getenv('PRINTIFY_API_TOKEN')

    if not api_token:
        print("Fetching PRINTIFY_API_TOKEN from Fly.io secrets...")
        try:
            result = subprocess.run(
                ['/root/.fly/bin/flyctl', 'ssh', 'console', '-a', 'hunkofthemonth', '-C', 'printenv PRINTIFY_API_TOKEN'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                api_token = result.stdout.strip()
        except Exception as e:
            print(f"⚠️  Could not fetch from Fly.io: {e}")

    if not api_token:
        print("\n❌ PRINTIFY_API_TOKEN not found")
        print("Please provide it as an environment variable:")
        print("  PRINTIFY_API_TOKEN='your_token' python fetch_printify_calendars.py")
        sys.exit(1)

    print(f"Using API token: {api_token[:20]}...")
    fetch_calendar_configs(api_token)
