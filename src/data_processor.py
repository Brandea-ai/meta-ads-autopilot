"""
Data Processor
Utilities for calculating metrics, detecting issues, and formatting data
"""
import logging
from typing import Dict, List, Tuple
import pandas as pd

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_numeric_value(value, default=0):
    """
    Extract numeric value from various Meta API formats
    Handles: lists like [{"value": "123"}], plain numbers, strings
    """
    if value is None:
        return default

    # If it's a list (Meta API format)
    if isinstance(value, list):
        if len(value) > 0 and isinstance(value[0], dict):
            try:
                return float(value[0].get('value', default))
            except (ValueError, TypeError, KeyError):
                return default
        return default

    # If it's already a number
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


class DataProcessor:
    """Process and analyze Meta Ads data"""

    @staticmethod
    def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate derived metrics from raw data

        Args:
            df: DataFrame with raw metrics

        Returns:
            DataFrame with calculated metrics
        """
        df = df.copy()

        # Extract numeric values from Meta API format for all relevant columns
        # and update the original columns with clean numeric values
        numeric_columns = ['spend', 'leads', 'video_plays_3s', 'impressions', 'thru_plays', 'clicks', 'frequency']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].apply(extract_numeric_value)

        # Calculate CPL if not present
        if 'cpl' not in df.columns and 'spend' in df.columns and 'leads' in df.columns:
            df['cpl'] = df.apply(
                lambda row: round(row['spend'] / row['leads'], 2) if row['leads'] > 0 else 0,
                axis=1
            )

        # Calculate Hook Rate if video data present
        if 'hook_rate' not in df.columns and 'video_plays_3s' in df.columns and 'impressions' in df.columns:
            df['hook_rate'] = df.apply(
                lambda row: round((row['video_plays_3s'] / row['impressions'] * 100), 2) if row['impressions'] > 0 else 0,
                axis=1
            )

        # Calculate Hold Rate if video data present
        if 'hold_rate' not in df.columns and 'thru_plays' in df.columns and 'video_plays_3s' in df.columns:
            df['hold_rate'] = df.apply(
                lambda row: round((row['thru_plays'] / row['video_plays_3s'] * 100), 2) if row['video_plays_3s'] > 0 else 0,
                axis=1
            )

        # Calculate CTR if clicks data present
        if 'clicks' in df.columns and 'impressions' in df.columns and 'ctr' not in df.columns:
            df['ctr'] = df.apply(
                lambda row: round((row['clicks'] / row['impressions'] * 100), 2) if row['impressions'] > 0 else 0,
                axis=1
            )

        return df

    @staticmethod
    def detect_ad_fatigue(df: pd.DataFrame, frequency_threshold: float = 6.0) -> pd.DataFrame:
        """
        Detect ads showing signs of fatigue

        Args:
            df: DataFrame with frequency data
            frequency_threshold: Frequency threshold for fatigue

        Returns:
            DataFrame with fatigue flag
        """
        df = df.copy()

        if 'frequency' in df.columns:
            # Extract numeric values from frequency column (handles Meta API list format)
            df['frequency'] = df['frequency'].apply(extract_numeric_value)

            df['ad_fatigue'] = df['frequency'] >= frequency_threshold
            df['fatigue_severity'] = df['frequency'].apply(
                lambda f: 'Critical' if f >= 8 else ('High' if f >= 6 else 'Normal')
            )
        else:
            df['ad_fatigue'] = False
            df['fatigue_severity'] = 'Unknown'

        return df

    @staticmethod
    def identify_top_performers(
        df: pd.DataFrame,
        metric: str = 'cpl',
        top_n: int = 3,
        ascending: bool = True
    ) -> pd.DataFrame:
        """
        Identify top performing ads/campaigns

        Args:
            df: DataFrame to analyze
            metric: Metric to rank by
            top_n: Number of top performers to return
            ascending: True for lower is better (CPL), False for higher is better (ROAS)

        Returns:
            DataFrame with top performers
        """
        if df.empty or metric not in df.columns:
            return pd.DataFrame()

        # Filter out zero values
        df_filtered = df[df[metric] > 0].copy()

        if df_filtered.empty:
            return pd.DataFrame()

        return df_filtered.nlargest(top_n, metric) if not ascending else df_filtered.nsmallest(top_n, metric)

    @staticmethod
    def identify_underperformers(
        df: pd.DataFrame,
        metric: str = 'cpl',
        bottom_n: int = 3,
        ascending: bool = True
    ) -> pd.DataFrame:
        """
        Identify underperforming ads/campaigns

        Args:
            df: DataFrame to analyze
            metric: Metric to rank by
            bottom_n: Number of underperformers to return
            ascending: True for lower is better (CPL), False for higher is better (ROAS)

        Returns:
            DataFrame with underperformers
        """
        if df.empty or metric not in df.columns:
            return pd.DataFrame()

        # Filter out zero values
        df_filtered = df[df[metric] > 0].copy()

        if df_filtered.empty:
            return pd.DataFrame()

        return df_filtered.nsmallest(bottom_n, metric) if not ascending else df_filtered.nlargest(bottom_n, metric)

    @staticmethod
    def calculate_performance_score(row: pd.Series) -> float:
        """
        Calculate overall performance score (0-100)

        Args:
            row: DataFrame row with metrics

        Returns:
            Performance score
        """
        score = 50  # Base score

        # CPL scoring (lower is better)
        if 'cpl' in row and row['cpl'] > 0:
            if row['cpl'] < 5:
                score += 20
            elif row['cpl'] < 8:
                score += 10
            elif row['cpl'] > 15:
                score -= 20
            elif row['cpl'] > 10:
                score -= 10

        # Hook rate scoring
        if 'hook_rate' in row:
            if row['hook_rate'] > 25:
                score += 15
            elif row['hook_rate'] > 15:
                score += 10
            elif row['hook_rate'] < 10:
                score -= 10

        # Hold rate scoring
        if 'hold_rate' in row:
            if row['hold_rate'] > 50:
                score += 10
            elif row['hold_rate'] > 30:
                score += 5
            elif row['hold_rate'] < 20:
                score -= 5

        # Frequency penalty
        if 'frequency' in row:
            if row['frequency'] > 8:
                score -= 15
            elif row['frequency'] > 6:
                score -= 10
            elif row['frequency'] < 2:
                score += 5

        return max(0, min(100, score))

    @staticmethod
    def format_currency(value: float, currency: str = '€') -> str:
        """
        Format value as currency

        Args:
            value: Numeric value
            currency: Currency symbol

        Returns:
            Formatted currency string
        """
        return f"{value:,.2f}{currency}"

    @staticmethod
    def format_percentage(value: float) -> str:
        """
        Format value as percentage

        Args:
            value: Numeric value (0-100)

        Returns:
            Formatted percentage string
        """
        return f"{value:.1f}%"

    @staticmethod
    def format_number(value: float, decimals: int = 0) -> str:
        """
        Format number with thousands separator

        Args:
            value: Numeric value
            decimals: Number of decimal places

        Returns:
            Formatted number string
        """
        if decimals == 0:
            return f"{int(value):,}"
        return f"{value:,.{decimals}f}"

    @staticmethod
    def calculate_trend(current: float, previous: float) -> Tuple[str, float]:
        """
        Calculate trend between two values

        Args:
            current: Current period value
            previous: Previous period value

        Returns:
            Tuple of (trend_icon, percentage_change)
        """
        if previous == 0:
            return ("↗️", 0.0)

        change = ((current - previous) / previous) * 100

        if abs(change) < 1:
            icon = "→"
        elif change > 0:
            icon = "↗️"
        else:
            icon = "↘️"

        return (icon, round(change, 1))

    @staticmethod
    def get_cpl_color(cpl: float) -> str:
        """
        Get color coding for CPL value

        Args:
            cpl: Cost per lead

        Returns:
            Color name for display
        """
        if cpl < 8:
            return "green"
        elif cpl < 15:
            return "orange"
        else:
            return "red"

    @staticmethod
    def aggregate_by_period(
        df: pd.DataFrame,
        date_column: str,
        period: str = 'D'
    ) -> pd.DataFrame:
        """
        Aggregate data by time period

        Args:
            df: DataFrame with date column
            date_column: Name of date column
            period: Pandas period string ('D', 'W', 'M')

        Returns:
            Aggregated DataFrame
        """
        if df.empty or date_column not in df.columns:
            return df

        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        df = df.set_index(date_column)

        agg_dict = {
            'spend': 'sum',
            'impressions': 'sum',
            'leads': 'sum',
            'clicks': 'sum'
        }

        # Only include columns that exist
        agg_dict = {k: v for k, v in agg_dict.items() if k in df.columns}

        return df.resample(period).agg(agg_dict).reset_index()

    @staticmethod
    def create_summary_stats(df: pd.DataFrame) -> Dict[str, float]:
        """
        Create summary statistics from DataFrame

        Args:
            df: DataFrame to summarize

        Returns:
            Dictionary with summary stats
        """
        if df.empty:
            return {}

        stats = {}

        if 'spend' in df.columns:
            stats['total_spend'] = round(df['spend'].sum(), 2)
            stats['avg_spend'] = round(df['spend'].mean(), 2)

        if 'leads' in df.columns:
            stats['total_leads'] = int(df['leads'].sum())
            stats['avg_leads'] = round(df['leads'].mean(), 2)

        if 'cpl' in df.columns:
            stats['avg_cpl'] = round(df['cpl'].mean(), 2)
            stats['median_cpl'] = round(df['cpl'].median(), 2)

        if 'frequency' in df.columns:
            stats['avg_frequency'] = round(df['frequency'].mean(), 2)
            stats['max_frequency'] = round(df['frequency'].max(), 2)

        if 'hook_rate' in df.columns:
            stats['avg_hook_rate'] = round(df['hook_rate'].mean(), 2)

        if 'hold_rate' in df.columns:
            stats['avg_hold_rate'] = round(df['hold_rate'].mean(), 2)

        return stats
