#!/usr/bin/env python3
"""
Test ALLE verfügbaren Meta Ads API Breakdowns - EINFACHE VERSION
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.ad import Ad

# Load .env
load_dotenv()

ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
AD_ACCOUNT_ID = os.getenv('META_AD_ACCOUNT_ID')

print("=" * 80)
print("🔬 TESTE ALLE VERFÜGBAREN META ADS API BREAKDOWNS")
print("=" * 80)
print()

# Initialize API
FacebookAdsApi.init(access_token=ACCESS_TOKEN)
account = AdAccount(AD_ACCOUNT_ID)

print(f"✅ API initialized for account: {AD_ACCOUNT_ID}")
print()

# Date range - last 7 days
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
time_range = {'since': start_date, 'until': end_date}

print(f"📅 Date range: {start_date} to {end_date}")
print()

# Standard fields
fields = [
    'ad_id', 'ad_name', 'campaign_name',
    'spend', 'impressions', 'reach', 'clicks',
    'actions', 'frequency', 'ctr', 'cpc', 'cpm'
]

# ALLE Meta API Breakdowns
all_breakdowns = {
    # Demographics
    'age': ['age'],
    'gender': ['gender'],
    'age_gender': ['age', 'gender'],

    # Geographic
    'country': ['country'],
    'region': ['region'],
    'dma': ['dma'],

    # Platforms
    'publisher_platform': ['publisher_platform'],
    'platform_position': ['platform_position'],
    'publisher_platform_position': ['publisher_platform', 'platform_position'],
    'device_platform': ['device_platform'],
    'impression_device': ['impression_device'],

    # Time
    'hourly_advertiser': ['hourly_stats_aggregated_by_advertiser_time_zone'],
    'hourly_audience': ['hourly_stats_aggregated_by_audience_time_zone'],

    # Conversion
    'conversion_device': ['conversion_device'],
}

# Get ads
print("🔍 Fetching ads...")
ads = list(account.get_ads(fields=[Ad.Field.name, Ad.Field.status]))

if not ads:
    print("❌ No ads found!")
    exit(1)

print(f"✅ Found {len(ads)} ads")
print()

# Test with first ad
test_ad = ads[0]
print(f"🎯 Testing with Ad: {test_ad.get('name', 'Unknown')} (ID: {test_ad.get('id')})")
print()

print("=" * 80)
print("TESTING BREAKDOWNS...")
print("=" * 80)
print()

results = {}

for breakdown_name, breakdown_params in all_breakdowns.items():
    print(f"Testing: {breakdown_name}")
    print(f"  Breakdowns: {breakdown_params}")

    try:
        insights = test_ad.get_insights(
            params={
                'time_range': time_range,
                'breakdowns': breakdown_params
            },
            fields=fields
        )

        insights_list = list(insights)
        count = len(insights_list)

        if count > 0:
            print(f"  ✅ SUCCESS! {count} data points")

            # Show sample
            first = dict(insights_list[0])

            # Show breakdown values
            print(f"  📊 Sample:")
            for bp in breakdown_params:
                if bp in first:
                    print(f"     {bp}: {first[bp]}")

            print(f"     spend: {first.get('spend', 'N/A')}")
            print(f"     impressions: {first.get('impressions', 'N/A')}")

            results[breakdown_name] = {
                'status': 'SUCCESS',
                'count': count,
                'breakdowns': breakdown_params
            }
        else:
            print(f"  ⚠️ NO DATA (0 results)")
            results[breakdown_name] = {
                'status': 'NO_DATA',
                'count': 0,
                'breakdowns': breakdown_params
            }

    except Exception as e:
        error_msg = str(e)
        print(f"  ❌ ERROR: {error_msg[:150]}")
        results[breakdown_name] = {
            'status': 'ERROR',
            'error': error_msg,
            'breakdowns': breakdown_params
        }

    print()

# Summary
print("=" * 80)
print("📊 FINAL SUMMARY")
print("=" * 80)
print()

successful = [(k, v) for k, v in results.items() if v['status'] == 'SUCCESS']
no_data = [(k, v) for k, v in results.items() if v['status'] == 'NO_DATA']
errors = [(k, v) for k, v in results.items() if v['status'] == 'ERROR']

print(f"✅ SUCCESSFUL BREAKDOWNS ({len(successful)}):")
print()
for name, data in successful:
    print(f"   {name}:")
    print(f"      Breakdowns: {data['breakdowns']}")
    print(f"      Data points: {data['count']}")
    print()

print()
print(f"⚠️ NO DATA ({len(no_data)}):")
for name, data in no_data:
    print(f"   - {name}: {data['breakdowns']}")

print()
print(f"❌ ERRORS ({len(errors)}):")
for name, data in errors:
    print(f"   - {name}: {data['error'][:100]}")

print()
print("=" * 80)
print("🎯 USE THESE BREAKDOWNS IN DASHBOARD:")
print("=" * 80)
print()
for name, data in successful:
    print(f"✅ {name}: {data['breakdowns']}")

print()
print("DONE!")
