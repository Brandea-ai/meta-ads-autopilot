#!/usr/bin/env python3
"""
Teste ALLE 67 Fields MIT ALLEN 12 Breakdowns
Findet heraus welche Kombinationen echte Daten zurückgeben
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.ad import Ad

load_dotenv()

ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
AD_ACCOUNT_ID = os.getenv('META_AD_ACCOUNT_ID')

print("=" * 80)
print("🔬 TESTE ALLE 67 FIELDS MIT ALLEN 12 BREAKDOWNS")
print("=" * 80)
print()

# Initialize
FacebookAdsApi.init(access_token=ACCESS_TOKEN)
account = AdAccount(AD_ACCOUNT_ID)

# Date range
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
time_range = {'since': start_date, 'until': end_date}

# Alle 67 funktionierende Fields
all_fields = [
    'account_id', 'account_name', 'account_currency',
    'ad_id', 'ad_name',
    'adset_id', 'adset_name',
    'campaign_id', 'campaign_name',
    'date_start', 'date_stop',
    'created_time', 'updated_time',
    'spend', 'impressions', 'reach', 'frequency', 'clicks',
    'ctr', 'unique_ctr',
    'inline_link_clicks', 'inline_link_click_ctr',
    'unique_inline_link_clicks', 'unique_inline_link_click_ctr',
    'unique_link_clicks_ctr',
    'unique_clicks',
    'inline_post_engagement',
    'cpc', 'cpm', 'cpp',
    'cost_per_inline_link_click',
    'cost_per_inline_post_engagement',
    'cost_per_unique_click',
    'cost_per_unique_inline_link_click',
    'cost_per_action_type',
    'cost_per_unique_action_type',
    'cost_per_result',
    'cost_per_thruplay',
    'cost_per_15_sec_video_view',
    'actions',
    'unique_actions',
    'results',
    'result_rate',
    'result_values_performance_indicator',
    'link_clicks_per_results',
    'video_play_actions',
    'video_play_curve_actions',
    'video_avg_time_watched_actions',
    'video_15_sec_watched_actions',
    'video_30_sec_watched_actions',
    'video_p25_watched_actions',
    'video_p50_watched_actions',
    'video_p75_watched_actions',
    'video_p95_watched_actions',
    'video_p100_watched_actions',
    'video_thruplay_watched_actions',
    'video_view_per_impression',
    'unique_video_view_15_sec',
    'quality_ranking',
    'engagement_rate_ranking',
    'conversion_rate_ranking',
    'attribution_setting',
    'buying_type',
    'objective',
    'optimization_goal',
    'creative_media_type',
    'website_ctr',
]

# Alle 12 funktionierende Breakdowns
all_breakdowns = {
    'age': ['age'],
    'gender': ['gender'],
    'age_gender': ['age', 'gender'],
    'country': ['country'],
    'region': ['region'],
    'dma': ['dma'],
    'publisher_platform': ['publisher_platform'],
    'publisher_platform_position': ['publisher_platform', 'platform_position'],
    'device_platform': ['device_platform'],
    'impression_device': ['impression_device'],
    'hourly_advertiser': ['hourly_stats_aggregated_by_advertiser_time_zone'],
    'hourly_audience': ['hourly_stats_aggregated_by_audience_time_zone'],
}

# Get ads
ads = list(account.get_ads(fields=[Ad.Field.name, Ad.Field.status]))
if not ads:
    print("❌ No ads found!")
    exit(1)

test_ad = ads[0]
print(f"🎯 Testing with Ad: {test_ad.get('name', 'Unknown')}")
print()

print(f"📊 Testing {len(all_breakdowns)} breakdowns with {len(all_fields)} fields")
print(f"   Total combinations to test: {len(all_breakdowns) * len(all_fields)} (~800)")
print()

# Results
breakdown_results = {}

for breakdown_name, breakdown_params in all_breakdowns.items():
    print(f"=" * 80)
    print(f"Testing breakdown: {breakdown_name} ({breakdown_params})")
    print(f"=" * 80)

    try:
        # Request all fields for this breakdown
        insights = test_ad.get_insights(
            params={
                'time_range': time_range,
                'breakdowns': breakdown_params
            },
            fields=all_fields
        )

        insights_list = list(insights)

        if not insights_list:
            print(f"⚠️ No data returned for {breakdown_name}")
            breakdown_results[breakdown_name] = {
                'status': 'NO_DATA',
                'data_points': 0,
                'fields_with_data': []
            }
            continue

        # Check which fields have data
        fields_with_data = {}

        for insight in insights_list:
            insight_dict = dict(insight)

            for field in all_fields:
                if field in insight_dict:
                    value = insight_dict[field]

                    # Check if has actual data
                    if value not in [None, '', 0, '0', [], {}]:
                        if field not in fields_with_data:
                            fields_with_data[field] = 0
                        fields_with_data[field] += 1

        # Show breakdown field values
        first_insight = dict(insights_list[0])
        breakdown_values = {}
        for bp in breakdown_params:
            if bp in first_insight:
                breakdown_values[bp] = first_insight[bp]

        print(f"✅ Got {len(insights_list)} data points")
        print(f"   Breakdown values: {breakdown_values}")
        print(f"   Fields with data: {len(fields_with_data)}/{len(all_fields)}")

        # Show which fields have data
        if fields_with_data:
            print(f"   Top fields:")
            for field, count in sorted(fields_with_data.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"      - {field}: {count} data points")

        breakdown_results[breakdown_name] = {
            'status': 'SUCCESS',
            'data_points': len(insights_list),
            'fields_with_data': list(fields_with_data.keys()),
            'field_counts': fields_with_data,
            'breakdowns': breakdown_params
        }

    except Exception as e:
        error_msg = str(e)
        print(f"❌ ERROR: {error_msg[:200]}")
        breakdown_results[breakdown_name] = {
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

successful = {k: v for k, v in breakdown_results.items() if v['status'] == 'SUCCESS'}
no_data = {k: v for k, v in breakdown_results.items() if v['status'] == 'NO_DATA'}
errors = {k: v for k, v in breakdown_results.items() if v['status'] == 'ERROR'}

print(f"✅ SUCCESSFUL: {len(successful)} breakdowns")
print(f"⚠️ NO DATA: {len(no_data)} breakdowns")
print(f"❌ ERRORS: {len(errors)} breakdowns")
print()

# Find common fields across all successful breakdowns
if successful:
    print("=" * 80)
    print("🎯 FIELDS DIE IN ALLEN BREAKDOWNS FUNKTIONIEREN:")
    print("=" * 80)

    # Get intersection of all fields
    all_successful_fields = set(successful[list(successful.keys())[0]]['fields_with_data'])
    for breakdown_name in list(successful.keys())[1:]:
        all_successful_fields &= set(successful[breakdown_name]['fields_with_data'])

    print(f"Fields die in ALLEN {len(successful)} Breakdowns Daten haben:")
    for field in sorted(all_successful_fields):
        print(f"   ✅ {field}")

    print()
    print(f"TOTAL: {len(all_successful_fields)} universal fields")
    print()

    # Find fields that work in SOME breakdowns
    print("=" * 80)
    print("📊 FIELDS PRO BREAKDOWN:")
    print("=" * 80)

    for breakdown_name, result in sorted(successful.items(), key=lambda x: len(x[1]['fields_with_data']), reverse=True):
        print(f"{breakdown_name}: {len(result['fields_with_data'])} fields, {result['data_points']} data points")

    print()

# Detailed breakdown comparison
print("=" * 80)
print("🔍 DETAILLIERTE BREAKDOWN ANALYSE:")
print("=" * 80)
print()

for breakdown_name, result in successful.items():
    print(f"{breakdown_name}:")
    print(f"   Data points: {result['data_points']}")
    print(f"   Fields with data: {len(result['fields_with_data'])}")
    print(f"   Breakdowns: {result['breakdowns']}")

    # Show unique fields for this breakdown
    other_fields = set()
    for other_name, other_result in successful.items():
        if other_name != breakdown_name:
            other_fields.update(other_result['fields_with_data'])

    unique_to_this = set(result['fields_with_data']) - other_fields
    if unique_to_this:
        print(f"   Unique fields (nur hier): {sorted(unique_to_this)}")
    print()

print("DONE!")
