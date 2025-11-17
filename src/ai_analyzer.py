"""
AI Analyzer using Google Gemini
Generates intelligent insights and recommendations for Meta Ads campaigns
"""
import logging
from typing import Dict, Optional, List
import pandas as pd
import google.generativeai as genai
from config import Config
from system_prompts import (
    WEEKLY_ANALYSIS_PROMPT,
    CONTENT_STRATEGY_PROMPT,
    SINGLE_AD_ANALYSIS_PROMPT,
    MONTHLY_COMPARISON_PROMPT,
    CONTENT_OPTIMIZATION_PROMPT
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIAnalyzer:
    """AI-powered analysis using Google Gemini"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI Analyzer with Google Gemini

        Args:
            api_key: Google API key (optional, will use Config if not provided)
        """
        self.api_key = api_key or Config.get('GOOGLE_API_KEY')

        if not self.api_key:
            logger.warning("Google API key not configured")
            self.model = None
            return

        try:
            genai.configure(api_key=self.api_key)
            # Use gemini-2.5-flash (latest stable model)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("Google Gemini AI initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {str(e)}")
            self.model = None

    def _generate_content(self, prompt: str) -> str:
        """
        Generate content using Gemini

        Args:
            prompt: Input prompt

        Returns:
            Generated text response
        """
        if not self.model:
            return "AI Analyzer nicht verfügbar. Bitte Google API Key konfigurieren."

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return f"Fehler bei AI-Analyse: {str(e)}"

    def analyze_weekly_performance(
        self,
        campaign_df: pd.DataFrame,
        ad_df: pd.DataFrame,
        date_range: str,
        company_name: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Analyze weekly campaign performance

        Args:
            campaign_df: Campaign performance data
            ad_df: Ad performance data
            date_range: Date range string
            company_name: Company name for personalization

        Returns:
            Dictionary with analysis sections
        """
        company_name = company_name or Config.get('COMPANY_NAME', 'Ihr Unternehmen')

        # Format data for prompt
        campaign_summary = self._format_dataframe_summary(campaign_df, [
            'campaign_name', 'spend', 'leads', 'cpl', 'frequency'
        ])

        ad_summary = self._format_dataframe_summary(ad_df, [
            'ad_name', 'spend', 'leads', 'cpl', 'hook_rate', 'hold_rate', 'frequency'
        ])

        # Fill prompt template
        prompt = WEEKLY_ANALYSIS_PROMPT.format(
            company_name=company_name,
            campaign_data=campaign_summary,
            ad_data=ad_summary,
            date_range=date_range
        )

        logger.info("Generating weekly performance analysis...")
        analysis = self._generate_content(prompt)

        return {
            'full_analysis': analysis,
            'date_range': date_range,
            'company_name': company_name
        }

    def generate_content_strategy(
        self,
        top_ads: pd.DataFrame,
        strategy_type: str = "FOMO",
        company_name: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate content strategy based on top performers

        Args:
            top_ads: DataFrame with top performing ads
            strategy_type: Strategy type (FOMO, Loss Aversion, Social Proof, etc.)
            company_name: Company name

        Returns:
            Dictionary with content ideas
        """
        company_name = company_name or Config.get('COMPANY_NAME', 'Ihr Unternehmen')

        # Format top ads
        top_ads_summary = self._format_dataframe_summary(top_ads, [
            'ad_name', 'cpl', 'hook_rate', 'hold_rate'
        ])

        # Fill prompt template
        prompt = CONTENT_STRATEGY_PROMPT.format(
            company_name=company_name,
            top_ads=top_ads_summary,
            strategy_type=strategy_type
        )

        logger.info(f"Generating {strategy_type} content strategy...")
        content_ideas = self._generate_content(prompt)

        return {
            'strategy_type': strategy_type,
            'content_ideas': content_ideas,
            'based_on_ads': len(top_ads)
        }

    def analyze_single_ad(self, ad_data: Dict) -> Dict[str, str]:
        """
        Analyze single ad performance in detail

        Args:
            ad_data: Dictionary with ad metrics

        Returns:
            Dictionary with detailed analysis
        """
        # Format ad data
        ad_summary = "\n".join([f"- {key}: {value}" for key, value in ad_data.items()])

        # Fill prompt template
        prompt = SINGLE_AD_ANALYSIS_PROMPT.format(ad_data=ad_summary)

        logger.info(f"Analyzing ad: {ad_data.get('ad_name', 'Unknown')}")
        analysis = self._generate_content(prompt)

        return {
            'ad_name': ad_data.get('ad_name', 'Unknown'),
            'analysis': analysis
        }

    def compare_monthly_performance(
        self,
        current_month_df: pd.DataFrame,
        previous_month_df: pd.DataFrame,
        date_range: str,
        company_name: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Compare monthly performance metrics

        Args:
            current_month_df: Current month data
            previous_month_df: Previous month data
            date_range: Date range string
            company_name: Company name

        Returns:
            Dictionary with comparison analysis
        """
        company_name = company_name or Config.get('COMPANY_NAME', 'Ihr Unternehmen')

        # Calculate summary metrics
        current_summary = self._calculate_monthly_summary(current_month_df)
        previous_summary = self._calculate_monthly_summary(previous_month_df)

        # Fill prompt template
        prompt = MONTHLY_COMPARISON_PROMPT.format(
            company_name=company_name,
            current_month_data=current_summary,
            previous_month_data=previous_summary,
            date_range=date_range
        )

        logger.info("Generating monthly comparison analysis...")
        analysis = self._generate_content(prompt)

        return {
            'comparison_analysis': analysis,
            'date_range': date_range,
            'current_total_spend': current_summary['total_spend'],
            'previous_total_spend': previous_summary['total_spend']
        }

    def optimize_underperforming_ad(
        self,
        ad_data: Dict,
        identified_problem: str
    ) -> Dict[str, str]:
        """
        Generate optimization suggestions for underperforming ad

        Args:
            ad_data: Ad metrics
            identified_problem: Identified issue

        Returns:
            Dictionary with optimization suggestions
        """
        # Format ad data
        ad_summary = "\n".join([f"- {key}: {value}" for key, value in ad_data.items()])

        # Fill prompt template
        prompt = CONTENT_OPTIMIZATION_PROMPT.format(
            ad_data=ad_summary,
            identified_problem=identified_problem
        )

        logger.info(f"Generating optimization for: {ad_data.get('ad_name', 'Unknown')}")
        optimization = self._generate_content(prompt)

        return {
            'ad_name': ad_data.get('ad_name', 'Unknown'),
            'problem': identified_problem,
            'optimization_suggestions': optimization
        }

    def _format_dataframe_summary(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]] = None
    ) -> str:
        """
        Format DataFrame as readable summary for prompt

        Args:
            df: DataFrame to format
            columns: Specific columns to include

        Returns:
            Formatted string summary
        """
        if df.empty:
            return "Keine Daten verfügbar"

        if columns:
            df = df[columns]

        # Convert to markdown table
        summary = df.to_markdown(index=False)
        return summary

    def _calculate_monthly_summary(self, df: pd.DataFrame) -> Dict:
        """
        Calculate summary metrics for monthly comparison

        Args:
            df: DataFrame with ad/campaign data

        Returns:
            Dictionary with summary metrics
        """
        if df.empty:
            return {
                'total_spend': 0,
                'total_leads': 0,
                'avg_cpl': 0,
                'total_impressions': 0,
                'avg_frequency': 0
            }

        return {
            'total_spend': round(df['spend'].sum(), 2),
            'total_leads': int(df['leads'].sum()),
            'avg_cpl': round(df['spend'].sum() / df['leads'].sum(), 2) if df['leads'].sum() > 0 else 0,
            'total_impressions': int(df['impressions'].sum()),
            'avg_frequency': round(df['frequency'].mean(), 2) if 'frequency' in df.columns else 0,
            'avg_hook_rate': round(df['hook_rate'].mean(), 2) if 'hook_rate' in df.columns else 0,
            'avg_hold_rate': round(df['hold_rate'].mean(), 2) if 'hold_rate' in df.columns else 0
        }
