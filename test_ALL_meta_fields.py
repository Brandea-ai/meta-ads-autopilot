#!/usr/bin/env python3
"""
Test ALLE 200+ Meta Ads API Fields
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adsinsights import AdsInsights

load_dotenv()

ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
AD_ACCOUNT_ID = os.getenv('META_AD_ACCOUNT_ID')

print("=" * 80)
print("🔬 TESTE ALLE 200+ META ADS API FIELDS")
print("=" * 80)
print()

# Initialize
FacebookAdsApi.init(access_token=ACCESS_TOKEN)
account = AdAccount(AD_ACCOUNT_ID)

# Date range
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
time_range = {'since': start_date, 'until': end_date}

# Get ALL fields from SDK
all_field_names = [attr for attr in dir(AdsInsights.Field) if not attr.startswith('_')]
print(f"📊 Found {len(all_field_names)} total fields in SDK")
print()

# Get ads
ads = list(account.get_ads(fields=[Ad.Field.name, Ad.Field.status]))
if not ads:
    print("❌ No ads found!")
    exit(1)

test_ad = ads[0]
print(f"🎯 Testing with Ad: {test_ad.get('name', 'Unknown')}")
print()

# Test in batches (API hat Limits für field count)
batch_size = 50
fields_with_data = {}
fields_without_data = []
fields_with_errors = {}

for i in range(0, len(all_field_names), batch_size):
    batch = all_field_names[i:i+batch_size]
    batch_num = (i // batch_size) + 1
    total_batches = (len(all_field_names) + batch_size - 1) // batch_size

    print(f"Testing batch {batch_num}/{total_batches} ({len(batch)} fields)...")

    try:
        insights = test_ad.get_insights(
            params={'time_range': time_range},
            fields=batch
        )

        insights_list = list(insights)
        if insights_list:
            insight = dict(insights_list[0])

            for field in batch:
                if field in insight:
                    value = insight[field]
                    if value not in [None, '', 0, '0', [], {}]:
                        fields_with_data[field] = value
                    else:
                        fields_without_data.append(field)
                else:
                    fields_without_data.append(field)
        else:
            fields_without_data.extend(batch)

        print(f"  ✅ Batch {batch_num} done")

    except Exception as e:
        error_msg = str(e)
        print(f"  ⚠️ Batch {batch_num} error: {error_msg[:100]}")

        # Try individual fields
        for field in batch:
            try:
                insights = test_ad.get_insights(
                    params={'time_range': time_range},
                    fields=[field]
                )
                insights_list = list(insights)
                if insights_list:
                    insight = dict(insights_list[0])
                    if field in insight and insight[field] not in [None, '', 0, '0', [], {}]:
                        fields_with_data[field] = insight[field]
                    else:
                        fields_without_data.append(field)
                else:
                    fields_without_data.append(field)
            except Exception as e2:
                fields_with_errors[field] = str(e2)[:100]

    print()

# Results
print("=" * 80)
print("📊 ERGEBNISSE")
print("=" * 80)
print()

print(f"✅ Fields MIT Daten: {len(fields_with_data)}")
print(f"⚠️ Fields OHNE Daten: {len(fields_without_data)}")
print(f"❌ Fields mit Errors: {len(fields_with_errors)}")
print()

# Kategorisiere fields_with_data
video_fields = {}
quality_fields = {}
cost_fields = {}
conversion_fields = {}
messaging_fields = {}
ecommerce_fields = {}
recall_fields = {}
other_fields = {}

for field, value in fields_with_data.items():
    if 'video' in field:
        video_fields[field] = value
    elif 'quality' in field or 'ranking' in field:
        quality_fields[field] = value
    elif 'cost' in field or field in ['cpc', 'cpm', 'cpp', 'ctr']:
        cost_fields[field] = value
    elif 'conversion' in field or 'action' in field:
        conversion_fields[field] = value
    elif 'messaging' in field or 'marketing_messages' in field:
        messaging_fields[field] = value
    elif 'catalog' in field or 'product' in field or 'purchase' in field or 'roas' in field:
        ecommerce_fields[field] = value
    elif 'recall' in field or 'estimated_ad' in field:
        recall_fields[field] = value
    else:
        other_fields[field] = value

print("=" * 80)
print("🎥 VIDEO FIELDS MIT DATEN:")
print("=" * 80)
for k, v in video_fields.items():
    if isinstance(v, list):
        print(f"✅ {k}: {len(v)} entries")
    else:
        print(f"✅ {k}: {v}")
print()

print("=" * 80)
print("⭐ QUALITY/RANKING FIELDS MIT DATEN:")
print("=" * 80)
for k, v in quality_fields.items():
    print(f"✅ {k}: {v}")
print()

print("=" * 80)
print("🎯 CONVERSION/ACTION FIELDS MIT DATEN:")
print("=" * 80)
for k, v in list(conversion_fields.items())[:20]:  # First 20
    if isinstance(v, list):
        print(f"✅ {k}: {len(v)} entries")
    else:
        print(f"✅ {k}: {v}")
if len(conversion_fields) > 20:
    print(f"... und {len(conversion_fields) - 20} weitere")
print()

print("=" * 80)
print("🛒 E-COMMERCE FIELDS MIT DATEN:")
print("=" * 80)
for k, v in ecommerce_fields.items():
    if isinstance(v, list):
        print(f"✅ {k}: {len(v)} entries")
    else:
        print(f"✅ {k}: {v}")
print()

print("=" * 80)
print("🧠 AD RECALL FIELDS MIT DATEN:")
print("=" * 80)
for k, v in recall_fields.items():
    print(f"✅ {k}: {v}")
print()

print("=" * 80)
print("💬 MESSAGING FIELDS MIT DATEN:")
print("=" * 80)
for k, v in messaging_fields.items():
    print(f"✅ {k}: {v}")
print()

print("=" * 80)
print("🔧 OTHER FIELDS MIT DATEN:")
print("=" * 80)
for k, v in list(other_fields.items())[:30]:  # First 30
    if isinstance(v, list):
        print(f"✅ {k}: {len(v)} entries")
    else:
        print(f"✅ {k}: {v}")
if len(other_fields) > 30:
    print(f"... und {len(other_fields) - 30} weitere")
print()

print("=" * 80)
print("🎯 NEUE WICHTIGE DISCOVERIES:")
print("=" * 80)
important_new = [
    'video_play_retention_graph_actions',
    'video_play_retention_0_to_15s_actions',
    'video_play_retention_20_to_60s_actions',
    'estimated_ad_recall_rate',
    'objective_results',
    'auction_competitiveness',
    'full_view_impressions',
    'full_view_reach',
]

for field in important_new:
    if field in fields_with_data:
        print(f"✅ {field}: VERFÜGBAR!")
    else:
        print(f"❌ {field}: Nicht verfügbar")
print()

print("=" * 80)
print("📝 ALLE FIELDS MIT DATEN (für meta_ads_client.py):")
print("=" * 80)
print("fields = [")
for field in sorted(fields_with_data.keys()):
    print(f"    '{field}',")
print("]")
print()

print(f"TOTAL: {len(fields_with_data)} fields mit echten Daten!")
print("DONE!")
