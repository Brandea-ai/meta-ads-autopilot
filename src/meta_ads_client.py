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
            logger.info(f"✅ Meta Ads API initialized for account {self.account_id}")
            logger.info(f"✅ Token length: {len(self.access_token)} chars")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Meta Ads API: {str(e)}")
            logger.error(f"❌ This usually means: TOKEN EXPIRED or INVALID PERMISSIONS")
            logger.error(f"❌ Go to https://developers.facebook.com/tools/explorer/ to generate new token")
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
            logger.error("❌ Meta Ads API not initialized")
            logger.error("❌ Check if META_ACCESS_TOKEN and META_AD_ACCOUNT_ID are set correctly")
            return pd.DataFrame()

        try:
            logger.info(f"🔍 Fetching REAL campaign data from Meta API (Account: {self.account_id})")
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
            campaign_count = 0
            for campaign in campaigns:
                campaign_count += 1
                logger.info(f"📊 Processing campaign {campaign_count}: {campaign.get('name', 'Unknown')}")

                # ALLE verfügbaren Insights-Felder abrufen!
                try:
                    insights = campaign.get_insights(
                        params={
                            'time_range': time_range,
                            'level': 'campaign',
                            'breakdowns': []  # Keine Breakdowns für Campaign-Level
                        },
                    fields=[
                        # Basic Info
                        'campaign_id',
                        'campaign_name',
                        'objective',

                        # Spend & Budget
                        'spend',
                        'budget_remaining',
                        'daily_budget',
                        'lifetime_budget',

                        # Delivery
                        'impressions',
                        'reach',
                        'frequency',
                        'social_spend',

                        # Engagement
                        'clicks',
                        'unique_clicks',
                        'ctr',
                        'unique_ctr',
                        'cpc',
                        'cpm',
                        'cpp',

                        # Video Metrics (vollständig!)
                        'video_play_actions',
                        'video_avg_time_watched_actions',
                        'video_p25_watched_actions',
                        'video_p50_watched_actions',
                        'video_p75_watched_actions',
                        'video_p95_watched_actions',
                        'video_p100_watched_actions',
                        'video_thruplay_watched_actions',
                        'video_continuous_2_sec_watched_actions',
                        'video_30_sec_watched_actions',

                        # Conversions
                        'actions',
                        'action_values',
                        'cost_per_action_type',
                        'cost_per_unique_action_type',
                        'conversions',
                        'conversion_values',

                        # Quality & Relevance
                        'quality_score_organic',
                        'quality_score_ectr',
                        'quality_score_ecvr',

                        # Link Clicks
                        'outbound_clicks',
                        'unique_outbound_clicks',
                        'outbound_clicks_ctr',
                        'cost_per_outbound_click',

                        # Landing Page
                        'website_ctr',
                        'purchase_roas',

                        # Age & Gender (wenn verfügbar)
                        'cost_per_estimated_ad_recallers',
                        'estimated_ad_recall_rate',
                        'estimated_ad_recallers'
                    ]
                    )

                except Exception as e:
                    logger.error(f"   ❌ Error getting insights for campaign: {str(e)}")
                    continue

                insights_list = list(insights)
                logger.info(f"   Found {len(insights_list)} insights for this campaign")

                if len(insights_list) == 0:
                    logger.warning(f"   ⚠️ No insights data for campaign - might be paused or no spend")
                    continue

                for insight in insights_list:
                    # Extract ALL actions
                    actions_dict = {}
                    if 'actions' in insight:
                        for action in insight['actions']:
                            action_type = action.get('action_type', 'unknown')
                            actions_dict[f'actions_{action_type}'] = int(action.get('value', 0))

                    # Extract ALL costs
                    costs_dict = {}
                    if 'cost_per_action_type' in insight:
                        for cost in insight['cost_per_action_type']:
                            cost_type = cost.get('action_type', 'unknown')
                            costs_dict[f'cost_per_{cost_type}'] = float(cost.get('value', 0))

                    # Extract video metrics
                    video_dict = {}
                    for video_field in ['video_play_actions', 'video_p25_watched_actions', 'video_p50_watched_actions',
                                       'video_p75_watched_actions', 'video_p95_watched_actions', 'video_p100_watched_actions',
                                       'video_thruplay_watched_actions', 'video_continuous_2_sec_watched_actions',
                                       'video_30_sec_watched_actions', 'video_avg_time_watched_actions']:
                        if video_field in insight:
                            for action in insight[video_field]:
                                action_type = action.get('action_type', 'unknown')
                                video_dict[f'{video_field}_{action_type}'] = float(action.get('value', 0))

                    # Legacy fields for compatibility
                    leads = actions_dict.get('actions_lead', 0)
                    cpl = costs_dict.get('cost_per_lead', 0)

                    # Build comprehensive data dict
                    campaign_data.append({
                        # Basic Info
                        'campaign_id': insight.get('campaign_id', ''),
                        'campaign_name': insight.get('campaign_name', 'Unknown'),
                        'objective': insight.get('objective', ''),

                        # Spend & Budget
                        'spend': float(insight.get('spend', 0)),
                        'budget_remaining': float(insight.get('budget_remaining', 0)),
                        'daily_budget': float(insight.get('daily_budget', 0)),
                        'lifetime_budget': float(insight.get('lifetime_budget', 0)),

                        # Delivery
                        'impressions': int(insight.get('impressions', 0)),
                        'reach': int(insight.get('reach', 0)),
                        'frequency': float(insight.get('frequency', 0)),
                        'social_spend': float(insight.get('social_spend', 0)),

                        # Engagement
                        'clicks': int(insight.get('clicks', 0)),
                        'unique_clicks': int(insight.get('unique_clicks', 0)),
                        'ctr': float(insight.get('ctr', 0)),
                        'unique_ctr': float(insight.get('unique_ctr', 0)),
                        'cpc': float(insight.get('cpc', 0)),
                        'cpm': float(insight.get('cpm', 0)),
                        'cpp': float(insight.get('cpp', 0)),

                        # Link Clicks
                        'outbound_clicks': int(insight.get('outbound_clicks', 0)),
                        'unique_outbound_clicks': int(insight.get('unique_outbound_clicks', 0)),
                        'outbound_clicks_ctr': float(insight.get('outbound_clicks_ctr', 0)),
                        'cost_per_outbound_click': float(insight.get('cost_per_outbound_click', 0)),

                        # Quality
                        'quality_score_organic': float(insight.get('quality_score_organic', 0)),
                        'quality_score_ectr': float(insight.get('quality_score_ectr', 0)),
                        'quality_score_ecvr': float(insight.get('quality_score_ecvr', 0)),

                        # Website
                        'website_ctr': float(insight.get('website_ctr', 0)),
                        'purchase_roas': float(insight.get('purchase_roas', 0)),

                        # Ad Recall
                        'estimated_ad_recallers': int(insight.get('estimated_ad_recallers', 0)),
                        'estimated_ad_recall_rate': float(insight.get('estimated_ad_recall_rate', 0)),

                        # Legacy compatibility
                        'leads': leads,
                        'cpl': cpl,

                        # Add ALL extracted actions
                        **actions_dict,
                        **costs_dict,
                        **video_dict
                    })

            df = pd.DataFrame(campaign_data)

            if df.empty:
                logger.warning("⚠️ No campaigns found in Meta account - using mock data")
            else:
                logger.info(f"✅ Successfully fetched {len(df)} campaigns from Meta API!")

            self._save_to_cache(cache_key, df.to_dict('records'))
            return df

        except Exception as e:
            logger.error(f"❌ Error fetching campaign data: {str(e)}")
            logger.error(f"❌ Check if your Meta Access Token is still valid!")
            return pd.DataFrame()

    def fetch_ad_performance(self, days: int = 7, start_date: Optional[str] = None, end_date: Optional[str] = None, force_refresh: bool = False) -> pd.DataFrame:
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

        # Load from cache unless force refresh is requested
        if not force_refresh:
            cached_data = self._load_from_cache(cache_key)
            if cached_data is not None:
                logger.info(f"📦 Returning cached data for {cache_key}")
                return pd.DataFrame(cached_data)
        else:
            logger.info(f"⚡ Force refresh - skipping cache for {cache_key}")

        if not self.api_initialized:
            logger.error("❌ Meta Ads API not initialized")
            logger.error("❌ Check if META_ACCESS_TOKEN and META_AD_ACCOUNT_ID are set correctly")
            return pd.DataFrame()

        try:
            # Use time_range instead of date_preset to include TODAY!
            time_range = {
                'since': start_date,
                'until': end_date
            }

            logger.info(f"📅 Fetching ad performance from {start_date} to {end_date}")

            ads = self.account.get_ads(fields=[
                Ad.Field.name,
                Ad.Field.status,
            ])

            ads_list = list(ads)
            logger.info(f"🎯 Found {len(ads_list)} ads in account")

            ad_data = []
            for ad in ads_list:
                logger.info(f"   📊 Fetching insights for ad: {ad.get('name', 'Unknown')}")
                # NUR die 67 VERIFIZIERTEN Fields die WIRKLICH funktionieren!
                # (getestet mit test_ALL_meta_fields.py)
                insights = ad.get_insights(
                    params={
                        'time_range': time_range,
                        'level': 'ad',
                        'breakdowns': []
                    },
                    fields=[
                        # IDs & Names & Dates (13 fields)
                        'account_id', 'account_name', 'account_currency',
                        'ad_id', 'ad_name',
                        'adset_id', 'adset_name',
                        'campaign_id', 'campaign_name',
                        'date_start', 'date_stop',
                        'created_time', 'updated_time',

                        # Basic Metrics (5 fields)
                        'spend', 'impressions', 'reach', 'frequency', 'clicks',

                        # CTR & Engagement (13 fields)
                        'ctr', 'unique_ctr',
                        'inline_link_clicks', 'inline_link_click_ctr',
                        'unique_inline_link_clicks', 'unique_inline_link_click_ctr',
                        'unique_link_clicks_ctr',
                        'unique_clicks',
                        'inline_post_engagement',
                        'website_ctr',
                        'unique_actions',
                        'actions',
                        'result_rate',

                        # Costs (13 fields)
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
                        'link_clicks_per_results',

                        # Results & Performance (2 fields)
                        'results',
                        'result_values_performance_indicator',

                        # Video Metrics (13 fields)
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

                        # Quality & Rankings (3 fields)
                        'quality_ranking',
                        'engagement_rate_ranking',
                        'conversion_rate_ranking',

                        # Attribution & Config (5 fields)
                        'attribution_setting',
                        'buying_type',
                        'objective',
                        'optimization_goal',
                        'creative_media_type',
                    ]
                )

                for insight in insights:
                    # Speichere ALLE Daten vom Insight!
                    data = dict(insight)

                    # Extract leads für einfachen Zugriff
                    leads = 0
                    if 'actions' in insight:
                        for action in insight['actions']:
                            if action['action_type'] == 'lead':
                                leads = int(action['value'])

                    data['leads_extracted'] = leads

                    # Extract video metrics für einfachen Zugriff
                    video_plays_3s = 0
                    if 'video_play_actions' in insight:
                        for action in insight['video_play_actions']:
                            if action['action_type'] == 'video_view':
                                video_plays_3s = int(action['value'])

                    data['video_plays_3s'] = video_plays_3s

                    thru_plays = 0
                    if 'video_thruplay_watched_actions' in insight:
                        for action in insight['video_thruplay_watched_actions']:
                            if action['action_type'] == 'video_view':
                                thru_plays = int(action['value'])

                    data['thru_plays'] = thru_plays

                    # Calculate convenience metrics
                    spend = float(insight.get('spend', 0))
                    impressions = int(insight.get('impressions', 1))

                    data['cpl'] = spend / leads if leads > 0 else 0
                    data['hook_rate'] = (video_plays_3s / impressions * 100) if impressions > 0 else 0
                    data['hold_rate'] = (thru_plays / video_plays_3s * 100) if video_plays_3s > 0 else 0

                    ad_data.append(data)

            logger.info(f"✅ Successfully fetched {len(ad_data)} data points from ads")

            df = pd.DataFrame(ad_data)

            if not df.empty:
                logger.info(f"✅ DataFrame created with {len(df)} rows and {len(df.columns)} columns")
                logger.info(f"   Columns: {', '.join(df.columns[:10])}...")
            else:
                logger.warning("⚠️ DataFrame is EMPTY - no insights returned from API")

            self._save_to_cache(cache_key, df.to_dict('records'))
            return df

        except Exception as e:
            logger.error(f"❌ Error fetching ad data: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return pd.DataFrame()


    def fetch_leads_data(self, days: int = 7, force_refresh: bool = False) -> pd.DataFrame:
        """
        Fetch LIVE lead form data via Pages API (works with Instant Forms)

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
            import requests

            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Get pages user has access to
            response = requests.get(
                'https://graph.facebook.com/v21.0/me/accounts',
                params={'access_token': self.access_token, 'fields': 'id,name,access_token'}
            )

            if response.status_code != 200:
                logger.error(f"Failed to get pages: {response.status_code}")
                return pd.DataFrame()

            pages = response.json().get('data', [])
            logger.info(f"Found {len(pages)} pages")

            all_leads = []

            for page in pages:
                page_id = page.get('id')
                page_name = page.get('name')
                page_token = page.get('access_token')

                # Get leadgen forms from this page
                forms_resp = requests.get(
                    f'https://graph.facebook.com/v21.0/{page_id}/leadgen_forms',
                    params={'access_token': page_token, 'fields': 'id,name,status'}
                )

                if forms_resp.status_code != 200:
                    logger.warning(f"Failed to get forms for page {page_name}")
                    continue

                forms = forms_resp.json().get('data', [])
                logger.info(f"Page '{page_name}': Found {len(forms)} forms")

                for form in forms:
                    form_id = form.get('id')
                    form_name = form.get('name')

                    # Get leads from this form
                    leads_resp = requests.get(
                        f'https://graph.facebook.com/v21.0/{form_id}/leads',
                        params={'access_token': page_token, 'fields': 'id,created_time,field_data'}
                    )

                    if leads_resp.status_code != 200:
                        logger.warning(f"Failed to get leads for form {form_name}")
                        continue

                    leads = leads_resp.json().get('data', [])
                    logger.info(f"Form '{form_name}': Retrieved {len(leads)} leads")

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
                                        field_name = field.get('name', 'unknown')
                                        field_value = field.get('values', [''])[0]
                                        field_data[field_name] = field_value

                                all_leads.append({
                                    'lead_id': lead.get('id'),
                                    'created_time': created_time.strftime('%Y-%m-%d %H:%M:%S'),
                                    'form_name': form_name,
                                    'page_name': page_name,
                                    **field_data  # Add all form fields
                                })

            df = pd.DataFrame(all_leads)
            logger.info(f"✅ Fetched {len(all_leads)} leads from last {days} days")
            return df

        except Exception as e:
            logger.error(f"Error fetching leads: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
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

    def fetch_comprehensive_insights(
        self,
        days: int = 7,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        level: str = 'ad'
    ) -> Dict[str, pd.DataFrame]:
        """
        🔥 ULTIMATE FUNCTION - ALLE verfügbaren Meta Ads Insights mit Breakdowns!

        Diese Funktion holt ALLE Daten die Meta bietet:
        ✅ Demographics (Alter, Geschlecht)
        ✅ Geographic (Land, Region, Stadt)
        ✅ Plattformen (Facebook, Instagram, Messenger, Audience Network)
        ✅ Placements (Feed, Stories, Reels, etc.)
        ✅ Geräte (Mobile, Desktop, Tablet)
        ✅ Zeiten (Stunde des Tages)
        ✅ Alle Action-Types (Leads, Engagement, Video-Views, etc.)
        ✅ Vollständige Video-Retention-Metriken
        ✅ Vollständige Engagement-Metriken

        Args:
            days: Number of days to look back
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional, defaults to TODAY)
            level: 'ad', 'adset', or 'campaign'

        Returns:
            Dictionary mit allen Breakdowns:
            {
                'base': DataFrame mit Basis-Metriken,
                'demographics_age': DataFrame mit Age-Breakdown,
                'demographics_gender': DataFrame mit Gender-Breakdown,
                'demographics_age_gender': DataFrame mit Age+Gender kombiniert,
                'geographic_country': DataFrame mit Country-Breakdown,
                'geographic_region': DataFrame mit Region-Breakdown,
                'placements': DataFrame mit Platform & Placement-Breakdown,
                'devices': DataFrame mit Device-Breakdown,
                'hourly': DataFrame mit Hourly-Stats
            }
        """
        if not self.api_initialized:
            logger.warning("API not initialized - cannot fetch comprehensive insights")
            return {}

        # Calculate date range
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=days-1)).strftime('%Y-%m-%d')

        logger.info(f"🔥 Fetching COMPREHENSIVE insights from {start_date} to {end_date}")

        time_range = {'since': start_date, 'until': end_date}

        # ALLE 67 verfügbaren Fields mit ECHTEN Daten (getestet mit test_ALL_meta_fields.py)
        standard_fields = [
            # IDs & Names & Dates
            'account_id', 'account_name', 'account_currency',
            'ad_id', 'ad_name',
            'adset_id', 'adset_name',
            'campaign_id', 'campaign_name',
            'date_start', 'date_stop',
            'created_time', 'updated_time',

            # Basic Metrics
            'spend', 'impressions', 'reach', 'frequency', 'clicks',

            # CTR & Engagement - ERWEITERT!
            'ctr', 'unique_ctr',
            'inline_link_clicks', 'inline_link_click_ctr',
            'unique_inline_link_clicks', 'unique_inline_link_click_ctr',
            'unique_link_clicks_ctr',
            'unique_clicks',
            'inline_post_engagement',  # NEU!

            # Costs - KOMPLETT!
            'cpc', 'cpm', 'cpp',
            'cost_per_inline_link_click',
            'cost_per_inline_post_engagement',
            'cost_per_unique_click',
            'cost_per_unique_inline_link_click',
            'cost_per_action_type',
            'cost_per_unique_action_type',
            'cost_per_result',  # NEU! Cost per Lead/Conversion
            'cost_per_thruplay',
            'cost_per_15_sec_video_view',

            # Actions & Conversions
            'actions',
            'unique_actions',

            # Results & Performance - NEU!
            'results',  # Objective Results!
            'result_rate',  # Conversion Rate!
            'result_values_performance_indicator',
            'link_clicks_per_results',  # Effizienz!

            # Video Metrics (KOMPLETT!)
            'video_play_actions',
            'video_play_curve_actions',  # RETENTION CURVE!
            'video_avg_time_watched_actions',
            'video_15_sec_watched_actions',
            'video_30_sec_watched_actions',
            'video_p25_watched_actions',
            'video_p50_watched_actions',
            'video_p75_watched_actions',
            'video_p95_watched_actions',
            'video_p100_watched_actions',
            'video_thruplay_watched_actions',
            'video_view_per_impression',  # NEU! Video View Rate
            'unique_video_view_15_sec',

            # Quality & Rankings
            'quality_ranking',
            'engagement_rate_ranking',
            'conversion_rate_ranking',

            # Attribution & Config
            'attribution_setting',
            'buying_type',
            'objective',
            'optimization_goal',
            'creative_media_type',  # NEU! Video/Image/Carousel

            # Website
            'website_ctr',
        ]

        results = {}

        try:
            # Helper function to get fresh objects for each breakdown
            def get_objects():
                if level == 'ad':
                    return self.account.get_ads(fields=[Ad.Field.name, Ad.Field.status])
                elif level == 'adset':
                    return self.account.get_ad_sets(fields=['name', 'status'])
                else:
                    return self.account.get_campaigns(fields=[Campaign.Field.name, Campaign.Field.status])

            # 1. BASE INSIGHTS (keine Breakdowns)
            logger.info("📊 Fetching base insights...")
            base_data = []
            for obj in get_objects():
                insights = obj.get_insights(
                    params={'time_range': time_range},
                    fields=standard_fields
                )
                for insight in insights:
                    base_data.append(dict(insight))

            results['base'] = pd.DataFrame(base_data)
            logger.info(f"✅ Base insights: {len(base_data)} entries")

            # 2. DEMOGRAPHICS - AGE
            logger.info("👥 Fetching age demographics...")
            age_data = []
            for obj in get_objects():
                insights = obj.get_insights(
                    params={'time_range': time_range, 'breakdowns': ['age']},
                    fields=standard_fields
                )
                for insight in insights:
                    age_data.append(dict(insight))

            results['demographics_age'] = pd.DataFrame(age_data)
            logger.info(f"✅ Age demographics: {len(age_data)} entries")

            # 3. DEMOGRAPHICS - GENDER
            logger.info("👥 Fetching gender demographics...")
            gender_data = []
            for obj in get_objects():
                insights = obj.get_insights(
                    params={'time_range': time_range, 'breakdowns': ['gender']},
                    fields=standard_fields
                )
                for insight in insights:
                    gender_data.append(dict(insight))

            results['demographics_gender'] = pd.DataFrame(gender_data)
            logger.info(f"✅ Gender demographics: {len(gender_data)} entries")

            # 4. DEMOGRAPHICS - AGE + GENDER (kombiniert!)
            logger.info("👥 Fetching age+gender demographics...")
            age_gender_data = []
            for obj in get_objects():
                insights = obj.get_insights(
                    params={'time_range': time_range, 'breakdowns': ['age', 'gender']},
                    fields=standard_fields
                )
                for insight in insights:
                    age_gender_data.append(dict(insight))

            results['demographics_age_gender'] = pd.DataFrame(age_gender_data)
            logger.info(f"✅ Age+Gender demographics: {len(age_gender_data)} entries")

            # 5. GEOGRAPHIC - COUNTRY
            logger.info("🌍 Fetching country breakdown...")
            country_data = []
            for obj in get_objects():
                insights = obj.get_insights(
                    params={'time_range': time_range, 'breakdowns': ['country']},
                    fields=standard_fields
                )
                for insight in insights:
                    country_data.append(dict(insight))

            results['geographic_country'] = pd.DataFrame(country_data)
            logger.info(f"✅ Country breakdown: {len(country_data)} entries")

            # 6. GEOGRAPHIC - REGION
            logger.info("🌍 Fetching region breakdown...")
            region_data = []
            for obj in get_objects():
                insights = obj.get_insights(
                    params={'time_range': time_range, 'breakdowns': ['region']},
                    fields=standard_fields
                )
                for insight in insights:
                    region_data.append(dict(insight))

            results['geographic_region'] = pd.DataFrame(region_data)
            logger.info(f"✅ Region breakdown: {len(region_data)} entries")

            # 7. PLACEMENTS - Publisher Platform + Platform Position
            logger.info("📱 Fetching placement breakdown...")
            placement_data = []
            for obj in get_objects():
                insights = obj.get_insights(
                    params={'time_range': time_range, 'breakdowns': ['publisher_platform', 'platform_position']},
                    fields=standard_fields
                )
                for insight in insights:
                    placement_data.append(dict(insight))

            results['placements'] = pd.DataFrame(placement_data)
            logger.info(f"✅ Placement breakdown: {len(placement_data)} entries")

            # 8. DEVICES - Impression Device (besser als device_platform)
            logger.info("💻 Fetching device breakdown...")
            device_data = []
            for obj in get_objects():
                insights = obj.get_insights(
                    params={'time_range': time_range, 'breakdowns': ['impression_device']},
                    fields=standard_fields
                )
                for insight in insights:
                    device_data.append(dict(insight))

            results['devices'] = pd.DataFrame(device_data)
            logger.info(f"✅ Device breakdown: {len(device_data)} entries")

            # 9. HOURLY STATS
            logger.info("🕐 Fetching hourly breakdown...")
            hourly_data = []
            for obj in get_objects():
                insights = obj.get_insights(
                    params={'time_range': time_range, 'breakdowns': ['hourly_stats_aggregated_by_advertiser_time_zone']},
                    fields=standard_fields
                )
                for insight in insights:
                    hourly_data.append(dict(insight))

            results['hourly'] = pd.DataFrame(hourly_data)
            logger.info(f"✅ Hourly breakdown: {len(hourly_data)} entries")

            # CONVERT ALL STRINGS TO NUMBERS (Meta API returns everything as strings!)
            logger.info("🔄 Converting Meta API strings to numbers...")
            numeric_fields = [
                'spend', 'impressions', 'reach', 'frequency', 'clicks',
                'ctr', 'unique_ctr', 'inline_link_clicks', 'inline_link_click_ctr',
                'unique_inline_link_clicks', 'unique_inline_link_click_ctr',
                'unique_link_clicks_ctr', 'unique_clicks', 'inline_post_engagement',
                'cpc', 'cpm', 'cpp', 'cost_per_inline_link_click',
                'cost_per_inline_post_engagement', 'cost_per_unique_click',
                'cost_per_unique_inline_link_click', 'cost_per_result',
                'cost_per_thruplay', 'cost_per_15_sec_video_view',
                'result_rate', 'link_clicks_per_results', 'video_view_per_impression',
                'website_ctr'
            ]

            for dataset_name, df in results.items():
                if not df.empty:
                    for field in numeric_fields:
                        if field in df.columns:
                            df[field] = pd.to_numeric(df[field], errors='coerce').fillna(0)
                    logger.info(f"✅ Converted {dataset_name}: {len(df)} rows")

            logger.info(f"🎉 COMPREHENSIVE INSIGHTS COMPLETE! Total datasets: {len(results)}")

            return results

        except Exception as e:
            logger.error(f"❌ Error fetching comprehensive insights: {str(e)}")
            return {}
