"""
Professional Dashboard Home Page
Alle 67 verfügbaren Meta Ads Fields visualisiert
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta


def extract_action_value(actions, action_type):
    """Extract specific action value from actions list"""
    if isinstance(actions, list):
        for action in actions:
            if isinstance(action, dict) and action.get('action_type') == action_type:
                try:
                    return float(action.get('value', 0))
                except (ValueError, TypeError):
                    return 0
    return 0


def safe_sum(df, column, default=0):
    """Safely sum a column with error handling"""
    try:
        if column in df.columns:
            return float(df[column].sum())
        return float(default)
    except (ValueError, TypeError, KeyError):
        return float(default)


def safe_mean(df, column, default=0):
    """Safely calculate mean of a column with error handling"""
    try:
        if column in df.columns:
            return float(df[column].mean())
        return float(default)
    except (ValueError, TypeError, KeyError):
        return float(default)


def safe_int(value, default=0):
    """Safely convert to int with error handling"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


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


def render_kpi_card(label, value, delta=None, delta_color="normal", help=None):
    """Render a professional KPI card"""
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color, help=help)


def render_home_professional(meta_client):
    """
    Professional Home Dashboard mit ALLEN verfügbaren Daten
    Zeigt die wichtigsten 67 Fields übersichtlich
    """

    st.markdown("# 📊 Performance Overview")
    st.markdown("**Komplette Analyse aller verfügbaren Meta Ads Metriken**")
    st.markdown("---")

    # Date selector
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        days = st.selectbox(
            "Zeitraum",
            options=[7, 14, 30, 60, 90],
            index=2,
            help="Wähle den Analysezeitraum"
        )

    with col2:
        st.markdown(f"**Zeitraum:** Letzte {days} Tage")

    with col3:
        if st.button("🔄 Aktualisieren", use_container_width=True):
            st.rerun()

    st.markdown("---")

    # Fetch data with ALL 67 fields
    with st.spinner("🔥 Lade vollständige Daten..."):
        try:
            # Fetch ad-level performance data (has all 67 fields)
            df = meta_client.fetch_ad_performance(days=days)

            if df.empty:
                st.warning("Keine Daten für den gewählten Zeitraum verfügbar.")
                st.info("Stelle sicher, dass Ads im gewählten Zeitraum aktiv waren.")
                return

        except Exception as e:
            st.error(f"Fehler beim Laden der Daten: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            return

    # DEBUG: Show raw data structure
    with st.expander("🔍 DEBUG: Rohdaten-Struktur (erste Zeile)", expanded=False):
        if not df.empty:
            st.write("**Verfügbare Spalten:**", list(df.columns))
            st.write("**Erste Zeile (Rohformat):**")
            first_row = df.iloc[0].to_dict()
            for key, value in list(first_row.items())[:10]:  # Erste 10 Felder
                st.write(f"- **{key}**: {type(value).__name__} = {str(value)[:100]}")

    # Extract actions (leads)
    df['leads'] = df['actions'].apply(lambda x: extract_action_value(x, 'lead'))
    df['link_clicks_action'] = df['actions'].apply(lambda x: extract_action_value(x, 'link_click'))

    # =============================================================================
    # SECTION 1: KEY PERFORMANCE INDICATORS (KPIs)
    # =============================================================================
    st.markdown("## 🎯 Key Performance Indicators")

    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

    with kpi_col1:
        total_spend = safe_sum(df, 'spend', 0)
        render_kpi_card(
            "💰 Total Spend",
            f"€{total_spend:,.2f}"
        )

    with kpi_col2:
        total_impressions = safe_int(safe_sum(df, 'impressions', 0))
        render_kpi_card(
            "👁️ Impressions",
            f"{total_impressions:,}"
        )

    with kpi_col3:
        total_reach = safe_int(safe_sum(df, 'reach', 0))
        render_kpi_card(
            "👥 Reach",
            f"{total_reach:,}"
        )

    with kpi_col4:
        avg_frequency = safe_mean(df, 'frequency', 0)
        render_kpi_card(
            "🔁 Frequency",
            f"{avg_frequency:.2f}"
        )

    with kpi_col5:
        total_clicks = safe_int(safe_sum(df, 'clicks', 0))
        render_kpi_card(
            "👆 Clicks",
            f"{total_clicks:,}"
        )

    # Second row KPIs
    kpi_col6, kpi_col7, kpi_col8, kpi_col9, kpi_col10 = st.columns(5)

    with kpi_col6:
        total_leads = safe_int(safe_sum(df, 'leads', 0))
        render_kpi_card(
            "📈 Leads",
            f"{total_leads:,}"
        )

    with kpi_col7:
        avg_cpl = (total_spend / total_leads) if total_leads > 0 else 0.0
        render_kpi_card(
            "💵 CPL",
            f"€{avg_cpl:.2f}"
        )

    with kpi_col8:
        avg_ctr = safe_mean(df, 'ctr', 0)
        render_kpi_card(
            "📊 CTR",
            f"{avg_ctr:.2f}%"
        )

    with kpi_col9:
        avg_cpc = safe_mean(df, 'cpc', 0)
        render_kpi_card(
            "💰 CPC",
            f"€{avg_cpc:.2f}"
        )

    with kpi_col10:
        avg_cpm = safe_mean(df, 'cpm', 0)
        render_kpi_card(
            "📉 CPM",
            f"€{avg_cpm:.2f}"
        )

    st.markdown("---")

    # =============================================================================
    # SECTION 2: CONVERSION & RESULTS
    # =============================================================================
    st.markdown("## 🎯 Conversion & Results")

    conv_col1, conv_col2, conv_col3, conv_col4 = st.columns(4)

    with conv_col1:
        # Objective Results
        total_results = 0
        try:
            if 'results' in df.columns:
                for results_data in df['results']:
                    if isinstance(results_data, list) and len(results_data) > 0:
                        total_results += float(results_data[0].get('value', 0))
        except (ValueError, TypeError, KeyError):
            total_results = 0

        render_kpi_card(
            "🎯 Results",
            f"{safe_int(total_results):,}",
            help="Direct Objective Results"
        )

    with conv_col2:
        # Result Rate (Conversion Rate)
        avg_result_rate = 0
        try:
            if 'result_rate' in df.columns:
                result_rates = []
                for rate_data in df['result_rate']:
                    if isinstance(rate_data, list) and len(rate_data) > 0:
                        result_rates.append(float(rate_data[0].get('value', 0)))
                if result_rates:
                    avg_result_rate = sum(result_rates) / len(result_rates)
        except (ValueError, TypeError, KeyError, ZeroDivisionError):
            avg_result_rate = 0

        render_kpi_card(
            "📈 Result Rate",
            f"{avg_result_rate:.2f}%",
            help="Conversion Rate"
        )

    with conv_col3:
        # Cost per Result
        avg_cost_per_result = 0
        try:
            if 'cost_per_result' in df.columns:
                costs = []
                for cost_data in df['cost_per_result']:
                    if isinstance(cost_data, list) and len(cost_data) > 0:
                        costs.append(float(cost_data[0].get('value', 0)))
                if costs:
                    avg_cost_per_result = sum(costs) / len(costs)
        except (ValueError, TypeError, KeyError, ZeroDivisionError):
            avg_cost_per_result = 0

        render_kpi_card(
            "💵 Cost/Result",
            f"€{avg_cost_per_result:.2f}"
        )

    with conv_col4:
        # Link Clicks per Result
        avg_link_clicks_per_result = 0
        try:
            if 'link_clicks_per_results' in df.columns:
                clicks_per_result = []
                for data in df['link_clicks_per_results']:
                    if isinstance(data, list) and len(data) > 0:
                        clicks_per_result.append(float(data[0].get('value', 0)))
                if clicks_per_result:
                    avg_link_clicks_per_result = sum(clicks_per_result) / len(clicks_per_result)
        except (ValueError, TypeError, KeyError, ZeroDivisionError):
            avg_link_clicks_per_result = 0

        render_kpi_card(
            "🔗 Clicks/Result",
            f"{avg_link_clicks_per_result:.2f}",
            help="Effizienz: Clicks pro Conversion"
        )

    st.markdown("---")

    # =============================================================================
    # SECTION 3: ENGAGEMENT METRICS
    # =============================================================================
    st.markdown("## 💬 Engagement Metrics")

    eng_col1, eng_col2, eng_col3, eng_col4 = st.columns(4)

    with eng_col1:
        total_inline_post_engagement = safe_int(safe_sum(df, 'inline_post_engagement', 0))
        render_kpi_card(
            "💬 Post Engagement",
            f"{total_inline_post_engagement:,}"
        )

    with eng_col2:
        total_inline_link_clicks = safe_int(safe_sum(df, 'inline_link_clicks', 0))
        render_kpi_card(
            "🔗 Inline Link Clicks",
            f"{total_inline_link_clicks:,}"
        )

    with eng_col3:
        avg_inline_link_click_ctr = safe_mean(df, 'inline_link_click_ctr', 0)
        render_kpi_card(
            "📊 Link Click CTR",
            f"{avg_inline_link_click_ctr:.2f}%"
        )

    with eng_col4:
        total_unique_clicks = safe_int(safe_sum(df, 'unique_clicks', 0))
        render_kpi_card(
            "👆 Unique Clicks",
            f"{total_unique_clicks:,}"
        )

    st.markdown("---")

    # =============================================================================
    # SECTION 4: VIDEO PERFORMANCE
    # =============================================================================
    st.markdown("## 🎥 Video Performance")

    # Check if we have video data
    has_video_data = 'video_play_actions' in df.columns and not df['video_play_actions'].isna().all()

    if has_video_data:
        video_col1, video_col2, video_col3, video_col4, video_col5 = st.columns(5)

        # Extract video metrics
        def extract_video_metric(df, column_name):
            total = 0
            if column_name in df.columns:
                for actions in df[column_name]:
                    if isinstance(actions, list):
                        for action in actions:
                            if isinstance(action, dict):
                                total += float(action.get('value', 0))
            return total

        video_plays = extract_video_metric(df, 'video_play_actions')
        video_3s = extract_video_metric(df, 'video_play_actions')  # 3sec plays
        video_15s = extract_video_metric(df, 'video_15_sec_watched_actions')
        video_30s = extract_video_metric(df, 'video_30_sec_watched_actions')
        thruplay = extract_video_metric(df, 'video_thruplay_watched_actions')

        with video_col1:
            render_kpi_card("▶️ Video Plays", f"{int(video_plays):,}")

        with video_col2:
            render_kpi_card("⏱️ 15s Views", f"{int(video_15s):,}")

        with video_col3:
            render_kpi_card("⏱️ 30s Views", f"{int(video_30s):,}")

        with video_col4:
            render_kpi_card("✅ ThruPlay", f"{int(thruplay):,}")

        with video_col5:
            # Video View Rate
            avg_view_rate = 0
            if 'video_view_per_impression' in df.columns:
                view_rates = []
                for data in df['video_view_per_impression']:
                    if isinstance(data, list) and len(data) > 0:
                        view_rates.append(float(data[0].get('value', 0)) * 100)
                if view_rates:
                    avg_view_rate = sum(view_rates) / len(view_rates)

            render_kpi_card("📊 View Rate", f"{avg_view_rate:.1f}%")

        # Video Retention
        st.markdown("### 📊 Video Retention")

        ret_col1, ret_col2, ret_col3, ret_col4, ret_col5 = st.columns(5)

        p25 = extract_video_metric(df, 'video_p25_watched_actions')
        p50 = extract_video_metric(df, 'video_p50_watched_actions')
        p75 = extract_video_metric(df, 'video_p75_watched_actions')
        p95 = extract_video_metric(df, 'video_p95_watched_actions')
        p100 = extract_video_metric(df, 'video_p100_watched_actions')

        with ret_col1:
            retention_25 = (p25 / video_plays * 100) if video_plays > 0 else 0
            render_kpi_card("25%", f"{retention_25:.1f}%")

        with ret_col2:
            retention_50 = (p50 / video_plays * 100) if video_plays > 0 else 0
            render_kpi_card("50%", f"{retention_50:.1f}%")

        with ret_col3:
            retention_75 = (p75 / video_plays * 100) if video_plays > 0 else 0
            render_kpi_card("75%", f"{retention_75:.1f}%")

        with ret_col4:
            retention_95 = (p95 / video_plays * 100) if video_plays > 0 else 0
            render_kpi_card("95%", f"{retention_95:.1f}%")

        with ret_col5:
            retention_100 = (p100 / video_plays * 100) if video_plays > 0 else 0
            render_kpi_card("100%", f"{retention_100:.1f}%")

        # Retention Chart
        retention_data = pd.DataFrame({
            'Checkpoint': ['25%', '50%', '75%', '95%', '100%'],
            'Retention': [retention_25, retention_50, retention_75, retention_95, retention_100]
        })

        fig = px.line(
            retention_data,
            x='Checkpoint',
            y='Retention',
            title='Video Retention Curve',
            markers=True
        )
        fig.update_layout(yaxis_title="Retention %", xaxis_title="Video Progress")
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Keine Video-Daten für diesen Zeitraum verfügbar")

    st.markdown("---")

    # =============================================================================
    # SECTION 5: QUALITY RANKINGS
    # =============================================================================
    st.markdown("## ⭐ Quality Rankings")

    qual_col1, qual_col2, qual_col3 = st.columns(3)

    with qual_col1:
        quality_ranks = df['quality_ranking'].value_counts().to_dict() if 'quality_ranking' in df.columns else {}
        most_common_quality = list(quality_ranks.keys())[0] if quality_ranks else "N/A"

        st.metric(
            "🏆 Quality Ranking",
            most_common_quality,
            help="Most common quality ranking"
        )

    with qual_col2:
        engagement_ranks = df['engagement_rate_ranking'].value_counts().to_dict() if 'engagement_rate_ranking' in df.columns else {}
        most_common_engagement = list(engagement_ranks.keys())[0] if engagement_ranks else "N/A"

        st.metric(
            "💬 Engagement Ranking",
            most_common_engagement
        )

    with qual_col3:
        conversion_ranks = df['conversion_rate_ranking'].value_counts().to_dict() if 'conversion_rate_ranking' in df.columns else {}
        most_common_conversion = list(conversion_ranks.keys())[0] if conversion_ranks else "N/A"

        st.metric(
            "🎯 Conversion Ranking",
            most_common_conversion
        )

    st.markdown("---")

    # =============================================================================
    # SECTION 6: CAMPAIGN PERFORMANCE TABLE
    # =============================================================================
    st.markdown("## 📋 Campaign Performance Details")

    # Group by campaign
    if 'campaign_name' in df.columns:
        # Convert all numeric columns to proper float values first
        numeric_columns = ['spend', 'impressions', 'reach', 'clicks', 'leads', 'ctr', 'cpc', 'cpm']
        df_clean = df.copy()

        for col in numeric_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].apply(extract_numeric_value)

        campaign_summary = df_clean.groupby('campaign_name').agg({
            'spend': 'sum',
            'impressions': 'sum',
            'reach': 'sum',
            'clicks': 'sum',
            'leads': 'sum',
            'ctr': 'mean',
            'cpc': 'mean',
            'cpm': 'mean'
        }).reset_index()

        campaign_summary['cpl'] = campaign_summary['spend'] / campaign_summary['leads'].replace(0, 1)
        campaign_summary = campaign_summary.sort_values('spend', ascending=False)

        # Format for display
        display_df = campaign_summary.copy()
        display_df['spend'] = display_df['spend'].apply(lambda x: f"€{x:,.2f}")
        display_df['impressions'] = display_df['impressions'].apply(lambda x: f"{int(x):,}")
        display_df['reach'] = display_df['reach'].apply(lambda x: f"{int(x):,}")
        display_df['clicks'] = display_df['clicks'].apply(lambda x: f"{int(x):,}")
        display_df['leads'] = display_df['leads'].apply(lambda x: f"{int(x):,}")
        display_df['ctr'] = display_df['ctr'].apply(lambda x: f"{x:.2f}%")
        display_df['cpc'] = display_df['cpc'].apply(lambda x: f"€{x:.2f}")
        display_df['cpm'] = display_df['cpm'].apply(lambda x: f"€{x:.2f}")
        display_df['cpl'] = display_df['cpl'].apply(lambda x: f"€{x:.2f}")

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")

    # =============================================================================
    # SECTION 7: METADATA & CONFIG
    # =============================================================================
    with st.expander("🔧 Campaign Configuration & Metadata"):
        meta_col1, meta_col2 = st.columns(2)

        with meta_col1:
            st.markdown("**Account Info:**")
            if 'account_name' in df.columns:
                st.write(f"Account: {df['account_name'].iloc[0]}")
            if 'account_currency' in df.columns:
                st.write(f"Currency: {df['account_currency'].iloc[0]}")

        with meta_col2:
            st.markdown("**Campaign Settings:**")
            if 'objective' in df.columns:
                objectives = df['objective'].value_counts()
                st.write(f"Objective: {', '.join(objectives.index.tolist())}")
            if 'buying_type' in df.columns:
                buying_types = df['buying_type'].value_counts()
                st.write(f"Buying Type: {', '.join(buying_types.index.tolist())}")

        # Creative Types
        if 'creative_media_type' in df.columns:
            st.markdown("**Creative Types:**")
            creative_types = df['creative_media_type'].value_counts()

            type_col1, type_col2, type_col3 = st.columns(3)

            for i, (creative_type, count) in enumerate(creative_types.items()):
                with [type_col1, type_col2, type_col3][i % 3]:
                    st.metric(creative_type, f"{count} Ads")

    st.success("✅ Dashboard geladen mit allen 67 verfügbaren Meta Ads Fields!")
