"""
DIREKTER TEST: Echte vs Mock-Daten
"""
import sys
sys.path.append('/Users/brandea/Desktop/meta-ads-autopilot')

from src.meta_ads_client import MetaAdsClient
import logging

# Enable logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

print("=" * 80)
print("🔍 DIREKTER TEST: ECHTE VS MOCK-DATEN")
print("=" * 80)

# Initialize client
client = MetaAdsClient()

print(f"\n1️⃣ API Initialized: {client.api_initialized}")
if client.api_initialized:
    print(f"   ✅ Account ID: {client.account_id}")
else:
    print(f"   ❌ API NOT initialized - will use MOCK DATA")
    exit(1)

# Fetch campaign data
print(f"\n2️⃣ Fetching Campaign Data (last 30 days)...")
campaign_df = client.fetch_campaign_data(days=30)

print(f"\n   Campaigns found: {len(campaign_df)}")
print(f"   Columns: {list(campaign_df.columns)}")

if not campaign_df.empty:
    print(f"\n   📋 Campaign Data:")
    for idx, row in campaign_df.iterrows():
        print(f"      Campaign: {row['campaign_name']}")
        print(f"      Spend: €{row['spend']:.2f}")
        print(f"      Leads: {row.get('leads', 0)}")
        print(f"      CPL: €{row.get('cpl', 0):.2f}")
        print()

    # Check if mock
    mock_names = ['Herbst Aktion 2024', 'SUV Special', 'Limousinen Deal']
    is_mock = any(name in campaign_df['campaign_name'].values for name in mock_names)

    if is_mock:
        print(f"   ❌❌❌ MOCK-DATEN ERKANNT! ❌❌❌")
        print(f"   Diese Campaign-Namen sind gefakt!")
    else:
        print(f"   ✅✅✅ ECHTE DATEN! ✅✅✅")

    # Calculate totals
    total_spend = campaign_df['spend'].sum()
    total_leads = campaign_df['leads'].sum()
    print(f"\n   📊 TOTALS:")
    print(f"      Total Spend: €{total_spend:,.2f}")
    print(f"      Total Leads: {int(total_leads)}")

    # Check if these match the fake values
    if abs(total_spend - 2200.85) < 1.0 and abs(total_leads - 132) < 1:
        print(f"\n   ❌❌❌ DIESE SIND FAKE! ❌❌❌")
        print(f"   €2,200.85 und 132 Leads sind Mock-Daten-Werte!")
    else:
        print(f"\n   ✅ Diese Werte sind echt!")

# Fetch ad data
print(f"\n3️⃣ Fetching Ad Performance Data (last 30 days)...")
ad_df = client.fetch_ad_performance(days=30)

print(f"\n   Ads found: {len(ad_df)}")

if not ad_df.empty:
    print(f"\n   📋 Sample Ads:")
    for idx, row in ad_df.head(3).iterrows():
        print(f"      Ad: {row['ad_name']}")
        print(f"      Spend: €{row['spend']:.2f}")
        if 'hook_rate' in row:
            print(f"      Hook Rate: {row['hook_rate']:.1f}%")
        print()

    # Check if mock
    mock_ad_names = ['SUV Video Hook Test A', 'Limousine Static Hero']
    is_mock = any(name in ad_df['ad_name'].values for name in mock_ad_names)

    if is_mock:
        print(f"   ❌❌❌ MOCK-DATEN ERKANNT! ❌❌❌")
    else:
        print(f"   ✅✅✅ ECHTE DATEN! ✅✅✅")

print("\n" + "=" * 80)
print("✅ TEST COMPLETE")
print("=" * 80)
