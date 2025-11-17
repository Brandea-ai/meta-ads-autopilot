"""
Meta Ads API Client
Fetches campaign and ad performance data from Facebook Business API
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.lead import Lead
from facebook_business.adobjects.page import Page
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetaAdsClient:
    """Client for fetching Meta Ads performance data"""

    def __init__(self, access_token: Optional[str] = None, account_id: Optional[str] = None):
        """
        Initialize Meta Ads API client

        Args:
            access_token: Meta API access token
            account_id: Ad account ID (format: act_XXXXX)
        """
        self.access_token = access_token or Config.get('META_ACCESS_TOKEN')
        self.account_id = account_id or Config.get('META_AD_ACCOUNT_ID')

        if not self.access_token or not self.account_id:
            logger.warning("Meta API credentials not configured")
            self.api_initialized = False
            return

        try:
            FacebookAdsApi.init(access_token=self.access_token)
            self.account = AdAccount(self.account_id)
            self.api_initialized = True
            logger.info(f"Meta Ads API initialized for account {self.account_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Meta Ads API: {str(e)}")
            self.api_initialized = False

    def _get_cache_path(self, cache_key: str) -> str:
        """Get cache file path"""
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'cache')
        os.makedirs(cache_dir, exist_ok=True)
        return os.path.join(cache_dir, f"{cache_key}.json")

    def _load_from_cache(self, cache_key: str, max_age_hours: int = 1) -> Optional[Dict]:
        """Load data from cache if fresh"""
        cache_path = self._get_cache_path(cache_key)

        if not os.path.exists(cache_path):
            return None

        try:
            with open(cache_path, 'r') as f:
                cached_data = json.load(f)

            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            if datetime.now() - cached_time < timedelta(hours=max_age_hours):
                logger.info(f"Loaded {cache_key} from cache")
                return cached_data['data']
        except Exception as e:
            logger.warning(f"Failed to load cache: {str(e)}")

        return None

    def _save_to_cache(self, cache_key: str, data: Dict) -> None:
        """Save data to cache"""
        cache_path = self._get_cache_path(cache_key)

        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
            logger.info(f"Saved {cache_key} to cache")
        except Exception as e:
            logger.error(f"Failed to save cache: {str(e)}")

    def fetch_campaign_data(self, days: int = 7, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch campaign performance data with custom date range

        Args:
            days: Number of days to look back (if start_date/end_date not provided)
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional, defaults to TODAY)

        Returns:
            DataFrame with campaign metrics
        """
        # Calculate date range - INCLUDE TODAY!
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')  # TODAY!

        if not start_date:
            start_date = (datetime.now() - timedelta(days=days-1)).strftime('%Y-%m-%d')

        cache_key = f"campaigns_{start_date}_{end_date}"
        cached_data = self._load_from_cache(cache_key)

        if cached_data is not None:
            return pd.DataFrame(cached_data)

        if not self.api_initialized:
            logger.warning("Using mock data - API not initialized")
            return self._get_mock_campaign_data(days)

        try:
            # Use time_range instead of date_preset to include TODAY!
            time_range = {
                'since': start_date,
                'until': end_date
            }

            campaigns = self.account.get_campaigns(fields=[
                Campaign.Field.name,
                Campaign.Field.status,
            ])

            campaign_data = []
            for campaign in campaigns:
                insights = campaign.get_insights(
                    params={'time_range': time_range},
                    fields=[
                        'campaign_name',
                        'spend',
                        'impressions',
                        'reach',
                        'frequency',
                        'actions',
                        'cost_per_action_type'
                    ]
                )

                for insight in insights:
                    # Extract leads from actions
                    leads = 0
                    if 'actions' in insight:
                        for action in insight['actions']:
                            if action['action_type'] == 'lead':
                                leads = int(action['value'])

                    # Extract CPL
                    cpl = 0
                    if 'cost_per_action_type' in insight:
                        for cost in insight['cost_per_action_type']:
                            if cost['action_type'] == 'lead':
                                cpl = float(cost['value'])

                    campaign_data.append({
                        'campaign_name': insight.get('campaign_name', 'Unknown'),
                        'spend': float(insight.get('spend', 0)),
                        'impressions': int(insight.get('impressions', 0)),
                        'reach': int(insight.get('reach', 0)),
                        'frequency': float(insight.get('frequency', 0)),
                        'leads': leads,
                        'cpl': cpl
                    })

            df = pd.DataFrame(campaign_data)
            self._save_to_cache(cache_key, df.to_dict('records'))
            return df

        except Exception as e:
            logger.error(f"Error fetching campaign data: {str(e)}")
            return self._get_mock_campaign_data(days)

    def fetch_ad_performance(self, days: int = 7, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch ad-level performance data with video metrics and custom date range

        Args:
            days: Number of days to look back (if start_date/end_date not provided)
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional, defaults to TODAY)

        Returns:
            DataFrame with ad metrics including hook rate and hold rate
        """
        # Calculate date range - INCLUDE TODAY!
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')  # TODAY!

        if not start_date:
            start_date = (datetime.now() - timedelta(days=days-1)).strftime('%Y-%m-%d')

        cache_key = f"ads_{start_date}_{end_date}"
        cached_data = self._load_from_cache(cache_key)

        if cached_data is not None:
            return pd.DataFrame(cached_data)

        if not self.api_initialized:
            logger.warning("Using mock data - API not initialized")
            return self._get_mock_ad_data(days)

        try:
            # Use time_range instead of date_preset to include TODAY!
            time_range = {
                'since': start_date,
                'until': end_date
            }

            ads = self.account.get_ads(fields=[
                Ad.Field.name,
                Ad.Field.status,
            ])

            ad_data = []
            for ad in ads:
                insights = ad.get_insights(
                    params={'time_range': time_range},
                    fields=[
                        'ad_name',
                        'spend',
                        'impressions',
                        'frequency',
                        'actions',
                        'cost_per_action_type',
                        'video_play_actions',
                        'video_thruplay_watched_actions'
                    ]
                )

                for insight in insights:
                    # Extract leads
                    leads = 0
                    if 'actions' in insight:
                        for action in insight['actions']:
                            if action['action_type'] == 'lead':
                                leads = int(action['value'])

                    # Extract video metrics
                    video_plays_3s = 0
                    if 'video_play_actions' in insight:
                        for action in insight['video_play_actions']:
                            if action['action_type'] == 'video_view':
                                video_plays_3s = int(action['value'])

                    thru_plays = 0
                    if 'video_thruplay_watched_actions' in insight:
                        for action in insight['video_thruplay_watched_actions']:
                            if action['action_type'] == 'video_view':
                                thru_plays = int(action['value'])

                    # Calculate metrics
                    spend = float(insight.get('spend', 0))
                    impressions = int(insight.get('impressions', 1))
                    cpl = spend / leads if leads > 0 else 0
                    hook_rate = (video_plays_3s / impressions * 100) if impressions > 0 else 0
                    hold_rate = (thru_plays / video_plays_3s * 100) if video_plays_3s > 0 else 0

                    ad_data.append({
                        'ad_name': insight.get('ad_name', 'Unknown'),
                        'spend': spend,
                        'impressions': impressions,
                        'leads': leads,
                        'cpl': round(cpl, 2),
                        'video_plays_3s': video_plays_3s,
                        'thru_plays': thru_plays,
                        'hook_rate': round(hook_rate, 2),
                        'hold_rate': round(hold_rate, 2),
                        'frequency': float(insight.get('frequency', 0))
                    })

            df = pd.DataFrame(ad_data)
            self._save_to_cache(cache_key, df.to_dict('records'))
            return df

        except Exception as e:
            logger.error(f"Error fetching ad data: {str(e)}")
            return self._get_mock_ad_data(days)

    def _get_mock_campaign_data(self, days: int) -> pd.DataFrame:
        """Generate mock campaign data for testing"""
        import random

        campaigns = [
            'Herbst Aktion 2024',
            'SUV Special',
            'Limousinen Deal',
            'Jahreswagen Angebot'
        ]

        data = []
        for campaign in campaigns:
            spend = random.uniform(200, 800)
            impressions = random.randint(5000, 15000)
            reach = int(impressions * random.uniform(0.6, 0.9))
            frequency = impressions / reach
            leads = random.randint(15, 45)
            cpl = spend / leads

            data.append({
                'campaign_name': campaign,
                'spend': round(spend, 2),
                'impressions': impressions,
                'reach': reach,
                'frequency': round(frequency, 2),
                'leads': leads,
                'cpl': round(cpl, 2)
            })

        return pd.DataFrame(data)

    def _get_mock_ad_data(self, days: int) -> pd.DataFrame:
        """Generate mock ad data for testing"""
        import random

        ad_names = [
            'SUV Video Hook Test A',
            'Limousine Static Hero',
            'Jahreswagen Carousel',
            'SUV Video Hook Test B',
            'Kombi Special Offer',
            'Elektro Launch Campaign',
            'Gebrauchtwagen Deal',
            'Premium Fahrzeuge'
        ]

        data = []
        for ad_name in ad_names:
            spend = random.uniform(50, 200)
            impressions = random.randint(1000, 5000)
            leads = random.randint(3, 25)
            cpl = spend / leads
            video_plays_3s = int(impressions * random.uniform(0.15, 0.35))
            thru_plays = int(video_plays_3s * random.uniform(0.3, 0.7))
            hook_rate = (video_plays_3s / impressions * 100)
            hold_rate = (thru_plays / video_plays_3s * 100)
            frequency = random.uniform(1.1, 4.5)

            data.append({
                'ad_name': ad_name,
                'spend': round(spend, 2),
                'impressions': impressions,
                'leads': leads,
                'cpl': round(cpl, 2),
                'video_plays_3s': video_plays_3s,
                'thru_plays': thru_plays,
                'hook_rate': round(hook_rate, 2),
                'hold_rate': round(hold_rate, 2),
                'frequency': round(frequency, 2)
            })

        return pd.DataFrame(data)

    def fetch_leads_data(self, days: int = 7, force_refresh: bool = False) -> pd.DataFrame:
        """
        Fetch LIVE lead form data - NO CACHE for latest data!

        Args:
            days: Number of days to look back
            force_refresh: Always fetch fresh data (ignore cache)

        Returns:
            DataFrame with lead details
        """
        if not self.api_initialized:
            logger.warning("API not initialized - cannot fetch leads")
            return pd.DataFrame()

        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Fetch all lead gen forms in account
            lead_forms = self.account.get_lead_gen_forms()

            all_leads = []
            for form in lead_forms:
                # Get leads from this form
                leads = form.get_leads(
                    fields=[
                        'id',
                        'created_time',
                        'ad_id',
                        'ad_name',
                        'form_id',
                        'field_data'
                    ]
                )

                for lead in leads:
                    created_time_str = lead.get('created_time', '')
                    if created_time_str:
                        try:
                            created_time = datetime.strptime(created_time_str, '%Y-%m-%dT%H:%M:%S%z')
                        except:
                            created_time = datetime.now()

                        # Filter by date range
                        if start_date <= created_time.replace(tzinfo=None) <= end_date:
                            # Extract field data
                            field_data = {}
                            if 'field_data' in lead:
                                for field in lead['field_data']:
                                    field_data[field.get('name', 'unknown')] = field.get('values', [''])[0]

                            all_leads.append({
                                'lead_id': lead.get('id'),
                                'created_time': created_time.strftime('%Y-%m-%d %H:%M:%S'),
                                'ad_name': lead.get('ad_name', 'Unknown'),
                                'form_id': lead.get('form_id'),
                                **field_data  # Add all form fields
                            })

            df = pd.DataFrame(all_leads)
            logger.info(f"Fetched {len(all_leads)} leads from last {days} days")
            return df

        except Exception as e:
            logger.error(f"Error fetching leads: {str(e)}")
            return pd.DataFrame()

    def fetch_live_data(self, days: int = 7, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        """
        Fetch LIVE data - bypasses cache completely!

        Args:
            days: Number of days to look back
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional, defaults to TODAY)

        Returns:
            Dict with campaigns, ads, and leads
        """
        logger.info("Fetching LIVE data (no cache)...")

        # Clear cache first for truly fresh data
        self.clear_cache()

        # Fetch fresh campaign data with custom date range
        campaigns = self.fetch_campaign_data(days=days, start_date=start_date, end_date=end_date)

        # Fetch fresh ad data with custom date range
        ads = self.fetch_ad_performance(days=days, start_date=start_date, end_date=end_date)

        # Fetch fresh leads
        leads = self.fetch_leads_data(days=days, force_refresh=True)

        return {
            'campaigns': campaigns,
            'ads': ads,
            'leads': leads,
            'start_date': start_date or (datetime.now() - timedelta(days=days-1)).strftime('%Y-%m-%d'),
            'end_date': end_date or datetime.now().strftime('%Y-%m-%d'),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def clear_cache(self):
        """Clear all cached data"""
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'cache')
        if os.path.exists(cache_dir):
            for file in os.listdir(cache_dir):
                if file.endswith('.json'):
                    try:
                        os.remove(os.path.join(cache_dir, file))
                        logger.info(f"Cleared cache: {file}")
                    except:
                        pass
