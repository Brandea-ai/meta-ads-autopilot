"""
Quick script to test if Meta Access Token is valid
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('META_ACCESS_TOKEN')
account_id = os.getenv('META_AD_ACCOUNT_ID')

print("=" * 80)
print("🔍 META ACCESS TOKEN VALIDATION TEST")
print("=" * 80)

if not token:
    print("❌ META_ACCESS_TOKEN not found in .env!")
    exit(1)

if not account_id:
    print("❌ META_AD_ACCOUNT_ID not found in .env!")
    exit(1)

print(f"\n✅ Token found: {len(token)} chars")
print(f"✅ Account ID: {account_id}")

# Test 1: Check token validity
print("\n1️⃣ Testing token validity...")
url = f"https://graph.facebook.com/v18.0/me?access_token={token}"

try:
    response = requests.get(url)
    data = response.json()

    if 'error' in data:
        print(f"❌ Token is INVALID!")
        print(f"❌ Error: {data['error']['message']}")
        print(f"❌ Error code: {data['error']['code']}")
        print(f"\n🔧 How to fix:")
        print(f"   1. Go to: https://developers.facebook.com/tools/explorer/")
        print(f"   2. Generate new token with permissions: ads_read, business_management")
        print(f"   3. Update .env and Streamlit Cloud secrets")
    else:
        print(f"✅ Token is VALID!")
        print(f"✅ User: {data.get('name', 'Unknown')}")
        print(f"✅ User ID: {data.get('id', 'Unknown')}")
except Exception as e:
    print(f"❌ Error testing token: {str(e)}")

# Test 2: Check account access
print("\n2️⃣ Testing account access...")
url = f"https://graph.facebook.com/v18.0/{account_id}?access_token={token}"

try:
    response = requests.get(url)
    data = response.json()

    if 'error' in data:
        print(f"❌ Cannot access account!")
        print(f"❌ Error: {data['error']['message']}")
        print(f"❌ Error code: {data['error']['code']}")
    else:
        print(f"✅ Account access OK!")
        print(f"✅ Account ID: {data.get('id', 'Unknown')}")
        print(f"✅ Account Name: {data.get('name', 'Unknown')}")
except Exception as e:
    print(f"❌ Error testing account: {str(e)}")

# Test 3: Try to fetch campaigns
print("\n3️⃣ Testing campaign fetch...")
url = f"https://graph.facebook.com/v18.0/{account_id}/campaigns?fields=name,status&access_token={token}"

try:
    response = requests.get(url)
    data = response.json()

    if 'error' in data:
        print(f"❌ Cannot fetch campaigns!")
        print(f"❌ Error: {data['error']['message']}")
        print(f"❌ Error code: {data['error']['code']}")

        if data['error']['code'] == 190:
            print(f"\n🔧 TOKEN EXPIRED! Generate new token:")
            print(f"   https://developers.facebook.com/tools/explorer/")
    else:
        campaigns = data.get('data', [])
        print(f"✅ Successfully fetched campaigns!")
        print(f"✅ Found {len(campaigns)} campaigns")

        if campaigns:
            print(f"\n📋 Sample campaigns:")
            for i, campaign in enumerate(campaigns[:3], 1):
                print(f"   {i}. {campaign.get('name', 'Unknown')} (Status: {campaign.get('status', 'Unknown')})")
        else:
            print(f"⚠️  No active campaigns found in account")
except Exception as e:
    print(f"❌ Error fetching campaigns: {str(e)}")

print("\n" + "=" * 80)
print("✅ TEST COMPLETE")
print("=" * 80)
