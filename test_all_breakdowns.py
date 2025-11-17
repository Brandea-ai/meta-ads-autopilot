#!/usr/bin/env python3
"""
Test ALLE verfügbaren Meta Ads API Breakdowns
Findet heraus welche Breakdowns ECHTE Daten zurückgeben
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from meta_ads_client import MetaAdsClient

def test_all_breakdowns():
    """Test ALLE möglichen Breakdowns systematisch"""

    print("=" * 80)
    print("🔬 TESTE ALLE VERFÜGBAREN META ADS API BREAKDOWNS")
    print("=" * 80)

    # Initialize client
    client = MetaAdsClient()

    if not client.api_initialized:
        print("❌ API not initialized!")
        return

    print(f"✅ API initialized for account: {client.account_id}")
    print()

    # Date range
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    time_range = {'since': start_date, 'until': end_date}

    print(f"📅 Testing date range: {start_date} to {end_date}")
    print()

    # Standard fields to request
    fields = [
        'ad_id', 'ad_name', 'campaign_name',
        'spend', 'impressions', 'reach', 'clicks',
        'actions', 'frequency'
    ]

    # ALLE möglichen Breakdowns von Meta API
    all_breakdowns = {
        # Demographics
        'age': ['age'],
        'gender': ['gender'],
        'age_gender': ['age', 'gender'],

        # Geographic
        'country': ['country'],
        'region': ['region'],
        'dma': ['dma'],
        'impression_device': ['impression_device'],

        # Platforms
        'publisher_platform': ['publisher_platform'],
        'platform_position': ['platform_position'],
        'publisher_platform_position': ['publisher_platform', 'platform_position'],
        'device_platform': ['device_platform'],

        # Time
        'hourly_stats_aggregated_by_advertiser_time_zone': ['hourly_stats_aggregated_by_advertiser_time_zone'],
        'hourly_stats_aggregated_by_audience_time_zone': ['hourly_stats_aggregated_by_audience_time_zone'],

        # Product / Placement
        'product_id': ['product_id'],
        'body_asset': ['body_asset'],
        'call_to_action_asset': ['call_to_action_asset'],
        'description_asset': ['description_asset'],
        'image_asset': ['image_asset'],
        'link_url_asset': ['link_url_asset'],
        'title_asset': ['title_asset'],
        'video_asset': ['video_asset'],

        # Other
        'place_page_id': ['place_page_id'],
        'conversion_device': ['conversion_device'],
    }

    # Get ads to test
    from facebook_business.adobjects.ad import Ad
    ads = list(client.account.get_ads(fields=[Ad.Field.name, Ad.Field.status]))

    if not ads:
        print("❌ No ads found!")
        return

    print(f"✅ Found {len(ads)} ads to test")
    print()

    # Test first ad for all breakdowns
    test_ad = ads[0]
    print(f"🎯 Testing with Ad: {test_ad.get('name', 'Unknown')}")
    print()

    results = {}

    print("=" * 80)
    print("TESTING ALL BREAKDOWNS...")
    print("=" * 80)
    print()

    for breakdown_name, breakdown_params in all_breakdowns.items():
        print(f"Testing: {breakdown_name} (breakdowns={breakdown_params})")

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
                print(f"  ✅ SUCCESS! Got {count} data points")

                # Show first entry
                first = insights_list[0]
                print(f"  📊 Sample data keys: {list(first.keys())[:10]}")

                # Check for breakdown values
                for bp in breakdown_params:
                    if bp in first:
                        print(f"  🔑 {bp} = {first[bp]}")

                results[breakdown_name] = {
                    'status': 'SUCCESS',
                    'count': count,
                    'breakdowns': breakdown_params,
                    'sample_keys': list(first.keys())
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
            print(f"  ❌ ERROR: {error_msg[:100]}")
            results[breakdown_name] = {
                'status': 'ERROR',
                'error': error_msg,
                'breakdowns': breakdown_params
            }

        print()

    # Summary
    print("=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print()

    successful = [k for k, v in results.items() if v['status'] == 'SUCCESS']
    no_data = [k for k, v in results.items() if v['status'] == 'NO_DATA']
    errors = [k for k, v in results.items() if v['status'] == 'ERROR']

    print(f"✅ SUCCESSFUL (has data): {len(successful)}")
    for name in successful:
        print(f"   - {name}: {results[name]['count']} data points")

    print()
    print(f"⚠️ NO DATA (valid but empty): {len(no_data)}")
    for name in no_data:
        print(f"   - {name}")

    print()
    print(f"❌ ERRORS: {len(errors)}")
    for name in errors:
        print(f"   - {name}: {results[name]['error'][:80]}")

    print()
    print("=" * 80)
    print("🎯 BREAKDOWNS TO USE IN DASHBOARD:")
    print("=" * 80)
    for name in successful:
        print(f"✅ {name}: {results[name]['breakdowns']}")

    print()
    print("=" * 80)
    print("DONE!")
    print("=" * 80)

    return results

if __name__ == '__main__':
    test_all_breakdowns()
