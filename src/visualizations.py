"""
Visualizations
Create interactive Plotly charts for Meta Ads data
"""
import logging
from typing import Optional, List
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Visualizations:
    """Create interactive visualizations for Meta Ads data"""

    # Brand colors
    PRIMARY_COLOR = '#FF4B4B'
    SECONDARY_COLOR = '#0068C9'
    SUCCESS_COLOR = '#09AB3B'
    WARNING_COLOR = '#FFA500'
    DANGER_COLOR = '#FF4B4B'

    @staticmethod
    def create_spend_trend(df: pd.DataFrame, date_column: str = 'date') -> go.Figure:
        """
        Create spend trend line chart

        Args:
            df: DataFrame with spend data
            date_column: Name of date column

        Returns:
            Plotly figure
        """
        if df.empty:
            return Visualizations._create_empty_chart("Keine Daten verfügbar")

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df.index if date_column not in df.columns else df[date_column],
            y=df['spend'],
            mode='lines+markers',
            name='Spend',
            line=dict(color=Visualizations.PRIMARY_COLOR, width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{x}</b><br>Spend: €%{y:,.2f}<extra></extra>'
        ))

        fig.update_layout(
            title='Spend Trend über Zeit',
            xaxis_title='Datum',
            yaxis_title='Spend (€)',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )

        return fig

    @staticmethod
    def create_cpl_comparison(df: pd.DataFrame, name_column: str = 'ad_name') -> go.Figure:
        """
        Create CPL comparison bar chart

        Args:
            df: DataFrame with CPL data
            name_column: Column name for labels

        Returns:
            Plotly figure
        """
        if df.empty or 'cpl' not in df.columns:
            return Visualizations._create_empty_chart("Keine CPL Daten verfügbar")

        # Sort by CPL
        df_sorted = df.sort_values('cpl', ascending=True)

        # Color code based on CPL value
        colors = [
            Visualizations.SUCCESS_COLOR if cpl < 8 else
            Visualizations.WARNING_COLOR if cpl < 15 else
            Visualizations.DANGER_COLOR
            for cpl in df_sorted['cpl']
        ]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df_sorted['cpl'],
            y=df_sorted[name_column],
            orientation='h',
            marker=dict(color=colors),
            text=df_sorted['cpl'].apply(lambda x: f'€{x:.2f}'),
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>CPL: €%{x:.2f}<extra></extra>'
        ))

        fig.update_layout(
            title='Cost per Lead (CPL) Vergleich',
            xaxis_title='CPL (€)',
            yaxis_title='',
            template='plotly_white',
            height=max(400, len(df_sorted) * 40),
            showlegend=False
        )

        return fig

    @staticmethod
    def create_frequency_histogram(df: pd.DataFrame) -> go.Figure:
        """
        Create frequency distribution histogram

        Args:
            df: DataFrame with frequency data

        Returns:
            Plotly figure
        """
        if df.empty or 'frequency' not in df.columns:
            return Visualizations._create_empty_chart("Keine Frequency Daten verfügbar")

        fig = go.Figure()

        fig.add_trace(go.Histogram(
            x=df['frequency'],
            nbinsx=20,
            marker=dict(
                color=Visualizations.SECONDARY_COLOR,
                line=dict(color='white', width=1)
            ),
            hovertemplate='Frequency: %{x:.2f}<br>Anzahl Ads: %{y}<extra></extra>'
        ))

        # Add vertical line at frequency = 6 (fatigue threshold)
        fig.add_vline(
            x=6,
            line_dash="dash",
            line_color=Visualizations.DANGER_COLOR,
            annotation_text="Fatigue Threshold",
            annotation_position="top"
        )

        fig.update_layout(
            title='Frequency Distribution',
            xaxis_title='Frequency',
            yaxis_title='Anzahl Ads',
            template='plotly_white',
            height=400
        )

        return fig

    @staticmethod
    def create_funnel(
        impressions: int,
        video_plays: int,
        clicks: int,
        leads: int
    ) -> go.Figure:
        """
        Create conversion funnel chart

        Args:
            impressions: Total impressions
            video_plays: Video plays (3s+)
            clicks: Total clicks
            leads: Total leads

        Returns:
            Plotly figure
        """
        fig = go.Figure()

        stages = ['Impressions', '3s Video Views', 'Clicks', 'Leads']
        values = [impressions, video_plays, clicks, leads]

        # Calculate conversion rates
        rates = [
            100,
            (video_plays / impressions * 100) if impressions > 0 else 0,
            (clicks / video_plays * 100) if video_plays > 0 else 0,
            (leads / clicks * 100) if clicks > 0 else 0
        ]

        fig.add_trace(go.Funnel(
            y=stages,
            x=values,
            textinfo="value+percent initial",
            marker=dict(
                color=[Visualizations.SECONDARY_COLOR, Visualizations.PRIMARY_COLOR,
                       Visualizations.WARNING_COLOR, Visualizations.SUCCESS_COLOR]
            ),
            hovertemplate='<b>%{y}</b><br>Anzahl: %{x:,}<br>Rate: %{percentInitial}<extra></extra>'
        ))

        fig.update_layout(
            title='Conversion Funnel',
            template='plotly_white',
            height=500
        )

        return fig

    @staticmethod
    def create_performance_scatter(
        df: pd.DataFrame,
        x_metric: str = 'hook_rate',
        y_metric: str = 'cpl',
        name_column: str = 'ad_name'
    ) -> go.Figure:
        """
        Create scatter plot for performance metrics

        Args:
            df: DataFrame with metrics
            x_metric: Metric for x-axis
            y_metric: Metric for y-axis
            name_column: Column for labels

        Returns:
            Plotly figure
        """
        if df.empty or x_metric not in df.columns or y_metric not in df.columns:
            return Visualizations._create_empty_chart("Keine Daten verfügbar")

        fig = px.scatter(
            df,
            x=x_metric,
            y=y_metric,
            text=name_column,
            size='spend' if 'spend' in df.columns else None,
            color='cpl' if y_metric != 'cpl' and 'cpl' in df.columns else None,
            color_continuous_scale=['green', 'yellow', 'red'],
            hover_data={
                x_metric: ':.2f',
                y_metric: ':.2f',
                'spend': ':,.2f' if 'spend' in df.columns else None
            }
        )

        fig.update_traces(
            textposition='top center',
            marker=dict(line=dict(width=2, color='white'))
        )

        fig.update_layout(
            title=f'{y_metric.upper()} vs {x_metric.upper()}',
            xaxis_title=x_metric.replace('_', ' ').title(),
            yaxis_title=y_metric.replace('_', ' ').title(),
            template='plotly_white',
            height=500
        )

        return fig

    @staticmethod
    def create_metric_cards_chart(
        total_spend: float,
        total_leads: int,
        avg_cpl: float,
        active_campaigns: int
    ) -> go.Figure:
        """
        Create indicator cards for key metrics

        Args:
            total_spend: Total spend
            total_leads: Total leads
            avg_cpl: Average CPL
            active_campaigns: Number of active campaigns

        Returns:
            Plotly figure with metric cards
        """
        fig = make_subplots(
            rows=1,
            cols=4,
            specs=[[{"type": "indicator"}, {"type": "indicator"},
                    {"type": "indicator"}, {"type": "indicator"}]],
            subplot_titles=("Total Spend", "Total Leads", "Avg CPL", "Active Campaigns")
        )

        fig.add_trace(go.Indicator(
            mode="number",
            value=total_spend,
            number={'prefix': "€", 'valueformat': ",.2f"},
            domain={'x': [0, 1], 'y': [0, 1]}
        ), row=1, col=1)

        fig.add_trace(go.Indicator(
            mode="number",
            value=total_leads,
            number={'valueformat': ","},
            domain={'x': [0, 1], 'y': [0, 1]}
        ), row=1, col=2)

        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=avg_cpl,
            number={'prefix': "€", 'valueformat': ".2f"},
            delta={'reference': 10, 'valueformat': ".2f"},
            domain={'x': [0, 1], 'y': [0, 1]}
        ), row=1, col=3)

        fig.add_trace(go.Indicator(
            mode="number",
            value=active_campaigns,
            number={'valueformat': "d"},
            domain={'x': [0, 1], 'y': [0, 1]}
        ), row=1, col=4)

        fig.update_layout(
            height=200,
            template='plotly_white',
            showlegend=False
        )

        return fig

    @staticmethod
    def create_hook_hold_analysis(df: pd.DataFrame, name_column: str = 'ad_name') -> go.Figure:
        """
        Create grouped bar chart for hook rate and hold rate

        Args:
            df: DataFrame with hook and hold rate data
            name_column: Column for ad names

        Returns:
            Plotly figure
        """
        if df.empty or 'hook_rate' not in df.columns or 'hold_rate' not in df.columns:
            return Visualizations._create_empty_chart("Keine Video Metrics verfügbar")

        fig = go.Figure()

        fig.add_trace(go.Bar(
            name='Hook Rate',
            x=df[name_column],
            y=df['hook_rate'],
            marker_color=Visualizations.SECONDARY_COLOR,
            text=df['hook_rate'].apply(lambda x: f'{x:.1f}%'),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Hook Rate: %{y:.2f}%<extra></extra>'
        ))

        fig.add_trace(go.Bar(
            name='Hold Rate',
            x=df[name_column],
            y=df['hold_rate'],
            marker_color=Visualizations.PRIMARY_COLOR,
            text=df['hold_rate'].apply(lambda x: f'{x:.1f}%'),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Hold Rate: %{y:.2f}%<extra></extra>'
        ))

        fig.update_layout(
            title='Hook Rate & Hold Rate Vergleich',
            xaxis_title='',
            yaxis_title='Rate (%)',
            barmode='group',
            template='plotly_white',
            height=500,
            xaxis={'tickangle': -45}
        )

        return fig

    @staticmethod
    def _create_empty_chart(message: str) -> go.Figure:
        """
        Create empty chart with message

        Args:
            message: Message to display

        Returns:
            Empty Plotly figure
        """
        fig = go.Figure()

        fig.add_annotation(
            text=message,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )

        fig.update_layout(
            template='plotly_white',
            height=400,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )

        return fig
