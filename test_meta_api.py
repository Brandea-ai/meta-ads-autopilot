"""
Test Script um zu prüfen ob Meta API funktioniert oder Mock-Daten verwendet werden
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.meta_ads_client import MetaAdsClient
from config import Config

print("=" * 80)
print("🔍 META ADS API CONNECTION TEST")
print("=" * 80)

# Check config
print("\n1️⃣ Checking Configuration...")
print(f"   META_ACCESS_TOKEN: {'✅ SET' if Config.is_configured('META_ACCESS_TOKEN') else '❌ MISSING'}")
print(f"   META_AD_ACCOUNT_ID: {'✅ SET' if Config.is_configured('META_AD_ACCOUNT_ID') else '❌ MISSING'}")

# Initialize client
print("\n2️⃣ Initializing Meta Ads Client...")
client = MetaAdsClient()

if client.api_initialized:
    print(f"   ✅ API Client initialized successfully!")
    print(f"   📊 Account ID: {client.account_id}")
else:
    print(f"   ❌ API Client NOT initialized - will use MOCK DATA!")

# Try to fetch data
print("\n3️⃣ Fetching Campaign Data (last 7 days)...")
try:
    campaign_df = client.fetch_campaign_data(days=7)

    if campaign_df.empty:
        print("   ⚠️  No campaigns found (empty DataFrame)")
    else:
        print(f"   ✅ Found {len(campaign_df)} campaigns!")
        print(f"\n   📋 Campaign Names:")
        for idx, row in campaign_df.head(5).iterrows():
            print(f"      - {row['campaign_name']}: €{row['spend']:.2f} spend")

        # Check if it's mock data
        mock_campaign_names = ['Herbst Aktion 2024', 'SUV Special', 'Limousinen Deal', 'Jahreswagen Angebot']
        is_mock = any(name in campaign_df['campaign_name'].values for name in mock_campaign_names)

        if is_mock:
            print(f"\n   ❌ USING MOCK DATA! (Found test campaign names)")
        else:
            print(f"\n   ✅ USING REAL DATA from Meta API!")

except Exception as e:
    print(f"   ❌ Error: {str(e)}")

# Try to fetch ad data
print("\n4️⃣ Fetching Ad Performance Data (last 7 days)...")
try:
    ad_df = client.fetch_ad_performance(days=7)

    if ad_df.empty:
        print("   ⚠️  No ads found (empty DataFrame)")
    else:
        print(f"   ✅ Found {len(ad_df)} ads!")
        print(f"   📊 Available columns: {len(ad_df.columns)}")

        # Check for extended metrics
        extended_metrics = ['video_p25', 'video_p50', 'video_p75', 'post_reactions', 'quality_ranking']
        has_extended = any(col in ad_df.columns for col in extended_metrics)

        if has_extended:
            print(f"   ✅ EXTENDED METRICS AVAILABLE (70+ fields)!")
        else:
            print(f"   ⚠️  Only basic metrics (8 fields)")

        # Show sample ad
        if not ad_df.empty:
            sample = ad_df.iloc[0]
            print(f"\n   📋 Sample Ad:")
            print(f"      Name: {sample['ad_name']}")
            print(f"      Spend: €{sample['spend']:.2f}")
            print(f"      Impressions: {sample['impressions']:,}")
            if 'hook_rate' in sample:
                print(f"      Hook Rate: {sample['hook_rate']:.1f}%")
            if 'hold_rate' in sample:
                print(f"      Hold Rate: {sample['hold_rate']:.1f}%")

        # Check if mock
        mock_ad_names = ['SUV Video Hook Test A', 'Limousine Static Hero', 'Jahreswagen Carousel']
        is_mock = any(name in ad_df['ad_name'].values for name in mock_ad_names)

        if is_mock:
            print(f"\n   ❌ USING MOCK DATA! (Found test ad names)")
        else:
            print(f"\n   ✅ USING REAL DATA from Meta API!")

except Exception as e:
    print(f"   ❌ Error: {str(e)}")

print("\n" + "=" * 80)
print("✅ TEST COMPLETE")
print("=" * 80)
