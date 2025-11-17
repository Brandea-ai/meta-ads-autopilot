#!/usr/bin/env python3
"""
Test ALLE verfügbaren Meta Ads API FIELDS (Metriken)
Findet alle verfügbaren Video-Metriken, Engagement, etc.
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
print("🔬 TESTE ALLE VERFÜGBAREN META ADS API FIELDS")
print("=" * 80)
print()

# Initialize API
FacebookAdsApi.init(access_token=ACCESS_TOKEN)
account = AdAccount(AD_ACCOUNT_ID)

# Date range
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
time_range = {'since': start_date, 'until': end_date}

print(f"📅 Date range: {start_date} to {end_date}")
print()

# ALLE möglichen Fields die Meta API unterstützt
all_fields = [
    # Basic
    'ad_id', 'ad_name', 'adset_id', 'adset_name', 'campaign_id', 'campaign_name',
    'account_id', 'account_name', 'date_start', 'date_stop',

    # Spend & Delivery
    'spend', 'impressions', 'reach', 'frequency',
    'social_spend', 'objective',

    # Clicks & Engagement
    'clicks', 'unique_clicks', 'inline_link_clicks', 'inline_link_click_ctr',
    'ctr', 'unique_ctr', 'cpc', 'cpp', 'cpm',

    # Actions & Conversions
    'actions', 'action_values', 'cost_per_action_type',
    'conversions', 'conversion_values', 'cost_per_conversion',

    # Video Metrics
    'video_play_actions',
    'video_play_curve_actions',  # NEW - retention curve!
    'video_avg_time_watched_actions',
    'video_continuous_2_sec_watched_actions',
    'video_p25_watched_actions',
    'video_p50_watched_actions',
    'video_p75_watched_actions',
    'video_p95_watched_actions',
    'video_p100_watched_actions',
    'video_thruplay_watched_actions',
    'video_30_sec_watched_actions',
    'video_time_watched_actions',

    # Website
    'website_ctr',

    # Attribution
    'attribution_setting',
    'buying_type',
    'optimization_goal',

    # Cost metrics
    'cost_per_inline_link_click',
    'cost_per_inline_post_engagement',
    'cost_per_unique_click',
    'cost_per_unique_inline_link_click',

    # Quality
    'quality_ranking',
    'engagement_rate_ranking',
    'conversion_rate_ranking',

    # Mobile
    'mobile_app_purchase_roas',
    'website_purchase_roas',

    # Outbound clicks
    'outbound_clicks',
    'outbound_clicks_ctr',
    'cost_per_outbound_click',

    # Unique actions
    'unique_actions',
    'unique_outbound_clicks',
    'unique_outbound_clicks_ctr',

    # DDA (Dedicated Delivery Accelerated)
    'dda_countby_convs',

    # Catalog
    'catalog_segment_actions',
    'catalog_segment_value',

    # Purchase
    'purchase_roas',
]

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
print(f"🎯 Testing with Ad: {test_ad.get('name', 'Unknown')}")
print()

print("=" * 80)
print("REQUESTING ALL FIELDS...")
print("=" * 80)
print()

try:
    insights = test_ad.get_insights(
        params={'time_range': time_range},
        fields=all_fields
    )

    insights_list = list(insights)

    if not insights_list:
        print("❌ No insights returned!")
        exit(1)

    insight = dict(insights_list[0])

    print(f"✅ Got insights with {len(insight)} fields!")
    print()

    # Categorize fields
    available = {}
    not_available = []

    for field in all_fields:
        if field in insight:
            value = insight[field]
            if value not in [None, '', 0, '0', []]:
                available[field] = value
            else:
                not_available.append(field)
        else:
            not_available.append(field)

    print("=" * 80)
    print("📊 VERFÜGBARE FIELDS MIT DATEN")
    print("=" * 80)
    print()

    # Group by category
    basic_fields = {}
    video_fields = {}
    engagement_fields = {}
    cost_fields = {}
    quality_fields = {}
    other_fields = {}

    for field, value in available.items():
        if 'video' in field:
            video_fields[field] = value
        elif 'cost' in field or field in ['cpc', 'cpm', 'cpp', 'ctr']:
            cost_fields[field] = value
        elif 'engagement' in field or field in ['like', 'comment', 'post', 'photo_view']:
            engagement_fields[field] = value
        elif 'quality' in field or 'ranking' in field:
            quality_fields[field] = value
        elif field in ['spend', 'impressions', 'reach', 'frequency', 'clicks']:
            basic_fields[field] = value
        else:
            other_fields[field] = value

    print("📌 BASIC METRICS:")
    for k, v in basic_fields.items():
        print(f"   ✅ {k}: {v}")
    print()

    print("🎥 VIDEO METRICS:")
    for k, v in video_fields.items():
        # Handle special formats
        if isinstance(v, list) and len(v) > 0:
            print(f"   ✅ {k}: {len(v)} entries")
            if k == 'video_play_curve_actions':
                print(f"      📊 VIDEO RETENTION CURVE AVAILABLE!")
        else:
            print(f"   ✅ {k}: {v}")
    print()

    print("💬 ENGAGEMENT METRICS:")
    for k, v in engagement_fields.items():
        print(f"   ✅ {k}: {v}")
    print()

    print("💰 COST METRICS:")
    for k, v in cost_fields.items():
        print(f"   ✅ {k}: {v}")
    print()

    print("⭐ QUALITY METRICS:")
    for k, v in quality_fields.items():
        print(f"   ✅ {k}: {v}")
    print()

    print("🔧 OTHER METRICS:")
    for k, v in other_fields.items():
        if isinstance(v, list):
            print(f"   ✅ {k}: {len(v)} entries")
        else:
            print(f"   ✅ {k}: {v}")
    print()

    print("=" * 80)
    print("❌ NICHT VERFÜGBAR / LEER:")
    print("=" * 80)
    for field in not_available[:30]:  # First 30
        print(f"   - {field}")
    if len(not_available) > 30:
        print(f"   ... und {len(not_available) - 30} weitere")
    print()

    print("=" * 80)
    print("🎯 SUMMARY")
    print("=" * 80)
    print(f"✅ Verfügbare Fields mit Daten: {len(available)}")
    print(f"📌 Basic Metrics: {len(basic_fields)}")
    print(f"🎥 Video Metrics: {len(video_fields)}")
    print(f"💬 Engagement Metrics: {len(engagement_fields)}")
    print(f"💰 Cost Metrics: {len(cost_fields)}")
    print(f"⭐ Quality Metrics: {len(quality_fields)}")
    print(f"🔧 Other Metrics: {len(other_fields)}")
    print(f"❌ Nicht verfügbar: {len(not_available)}")
    print()

    print("=" * 80)
    print("🔥 ALLE VERFÜGBAREN FIELDS FÜR DASHBOARD:")
    print("=" * 80)
    print("fields = [")
    for field in sorted(available.keys()):
        print(f"    '{field}',")
    print("]")

except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print()
print("DONE!")
