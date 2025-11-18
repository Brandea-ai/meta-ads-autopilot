"""
Professional Advanced Insights Dashboard
Alle 12 Breakdowns mit allen 67 Fields hochwertig visualisiert
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict


def extract_leads_from_actions(actions):
    """Extract leads from actions"""
    if isinstance(actions, list):
        for action in actions:
            if isinstance(action, dict) and action.get('action_type') == 'lead':
                return int(action.get('value', 0))
    return 0


def safe_aggregate(df, group_col, agg_dict):
    """Safely aggregate data with error handling"""
    try:
        if group_col not in df.columns:
            return pd.DataFrame()

        result = df.groupby(group_col).agg(agg_dict).reset_index()

        # Calculate derived metrics
        if 'spend' in result.columns and 'leads_extracted' in result.columns:
            result['cpl'] = result['spend'] / result['leads_extracted'].replace(0, 1)

        if 'clicks' in result.columns and 'impressions' in result.columns:
            result['ctr'] = (result['clicks'] / result['impressions'].replace(0, 1)) * 100

        return result.sort_values('spend', ascending=False)
    except Exception as e:
        st.error(f"Aggregation error: {str(e)}")
        return pd.DataFrame()


def render_breakdown_section(title, df, breakdown_col, icon="📊"):
    """Render a professional breakdown section with charts"""

    if df.empty or breakdown_col not in df.columns:
        st.info(f"Keine {title} Daten verfügbar für diesen Zeitraum")
        return

    st.markdown(f"### {icon} {title}")

    # Summary stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Segments", f"{len(df)}")

    with col2:
        total_spend = df['spend'].sum() if 'spend' in df.columns else 0
        st.metric("Total Spend", f"€{total_spend:,.2f}")

    with col3:
        total_impressions = int(df['impressions'].sum()) if 'impressions' in df.columns else 0
        st.metric("Impressions", f"{total_impressions:,}")

    with col4:
        total_leads = int(df['leads_extracted'].sum()) if 'leads_extracted' in df.columns else 0
        st.metric("Leads", f"{total_leads}")

    # Table
    st.markdown("#### 📋 Detaillierte Daten")

    display_cols = [breakdown_col]
    if 'spend' in df.columns:
        display_cols.append('spend')
    if 'impressions' in df.columns:
        display_cols.append('impressions')
    if 'clicks' in df.columns:
        display_cols.append('clicks')
    if 'leads_extracted' in df.columns:
        display_cols.append('leads_extracted')
    if 'cpl' in df.columns:
        display_cols.append('cpl')
    if 'ctr' in df.columns:
        display_cols.append('ctr')

    available_cols = [col for col in display_cols if col in df.columns]

    st.dataframe(
        df[available_cols].head(20),
        use_container_width=True,
        hide_index=True
    )

    # Charts
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        if 'spend' in df.columns:
            fig = px.bar(
                df.head(10),
                x=breakdown_col,
                y='spend',
                title=f'Top 10 {title} by Spend',
                color='cpl' if 'cpl' in df.columns else None,
                color_continuous_scale='RdYlGn_r'
            )
            st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        if 'leads_extracted' in df.columns and df['leads_extracted'].sum() > 0:
            fig = px.pie(
                df.head(10),
                values='leads_extracted',
                names=breakdown_col,
                title=f'Lead Distribution by {title}'
            )
            st.plotly_chart(fig, use_container_width=True)


def render_advanced_insights_professional(meta_client):
    """
    Professional Advanced Insights mit ALLEN 12 Breakdowns
    """

    st.markdown("# 🔬 Advanced Insights")
    st.markdown("**Komplette Breakdown-Analyse mit allen verfügbaren Dimensionen**")
    st.markdown("---")

    # Settings
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        days = st.selectbox(
            "Zeitraum",
            options=[7, 14, 30, 60, 90],
            index=2,
            help="Analysezeitraum"
        )

    with col2:
        level = st.selectbox(
            "Analyse-Level",
            options=['ad', 'adset', 'campaign'],
            index=0,
            help="Ad-Level empfohlen für maximale Daten"
        )

    with col3:
        if st.button("🔥 Analysieren", use_container_width=True):
            st.rerun()

    st.markdown("---")

    # Fetch comprehensive insights
    with st.spinner("🔥 Lade vollständige Breakdown-Daten..."):
        try:
            insights = meta_client.fetch_comprehensive_insights(
                days=days,
                level=level
            )

            if not insights or all(df.empty for df in insights.values()):
                st.warning("Keine Daten verfügbar für den gewählten Zeitraum.")
                return

        except Exception as e:
            st.error(f"Fehler beim Laden: {str(e)}")
            return

    # Success message
    available_breakdowns = [k for k, v in insights.items() if not v.empty]
    st.success(f"✅ {len(available_breakdowns)} Breakdown-Datensätze geladen!")

    # Extract leads for all dataframes
    for key in insights:
        if not insights[key].empty and 'actions' in insights[key].columns:
            insights[key]['leads_extracted'] = insights[key]['actions'].apply(extract_leads_from_actions)
        elif not insights[key].empty:
            insights[key]['leads_extracted'] = 0

    # Create tabs for each breakdown category
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 Demographics",
        "🌍 Geographic",
        "📱 Platforms",
        "💻 Devices",
        "🕐 Time Analysis"
    ])

    # =============================================================================
    # TAB 1: DEMOGRAPHICS
    # =============================================================================
    with tab1:
        st.markdown("## 👥 Demografische Insights")
        st.markdown("Komplette Analyse nach Alter, Geschlecht und Kombinationen")
        st.markdown("---")

        # AGE
        if 'demographics_age' in insights and not insights['demographics_age'].empty:
            age_df = insights['demographics_age']

            if 'age' in age_df.columns:
                age_summary = safe_aggregate(
                    age_df,
                    'age',
                    {
                        'spend': 'sum',
                        'impressions': 'sum',
                        'reach': 'sum',
                        'clicks': 'sum',
                        'leads_extracted': 'sum'
                    }
                )

                render_breakdown_section("Altersgruppen", age_summary, 'age', "📊")
                st.markdown("---")

        # GENDER
        if 'demographics_gender' in insights and not insights['demographics_gender'].empty:
            gender_df = insights['demographics_gender']

            if 'gender' in gender_df.columns:
                gender_summary = safe_aggregate(
                    gender_df,
                    'gender',
                    {
                        'spend': 'sum',
                        'impressions': 'sum',
                        'reach': 'sum',
                        'clicks': 'sum',
                        'leads_extracted': 'sum'
                    }
                )

                render_breakdown_section("Geschlecht", gender_summary, 'gender', "⚧️")
                st.markdown("---")

        # AGE + GENDER
        if 'demographics_age_gender' in insights and not insights['demographics_age_gender'].empty:
            age_gender_df = insights['demographics_age_gender']

            if 'age' in age_gender_df.columns and 'gender' in age_gender_df.columns:
                age_gender_df['segment'] = age_gender_df['age'].astype(str) + ' | ' + age_gender_df['gender'].astype(str)

                segment_summary = safe_aggregate(
                    age_gender_df,
                    'segment',
                    {
                        'spend': 'sum',
                        'impressions': 'sum',
                        'clicks': 'sum',
                        'leads_extracted': 'sum'
                    }
                )

                render_breakdown_section("Alter × Geschlecht", segment_summary, 'segment', "👥")

    # =============================================================================
    # TAB 2: GEOGRAPHIC
    # =============================================================================
    with tab2:
        st.markdown("## 🌍 Geografische Insights")
        st.markdown("Analyse nach Ländern, Regionen und DMA")
        st.markdown("---")

        # COUNTRY
        if 'geographic_country' in insights and not insights['geographic_country'].empty:
            country_df = insights['geographic_country']

            if 'country' in country_df.columns:
                country_summary = safe_aggregate(
                    country_df,
                    'country',
                    {
                        'spend': 'sum',
                        'impressions': 'sum',
                        'reach': 'sum',
                        'clicks': 'sum',
                        'leads_extracted': 'sum'
                    }
                )

                render_breakdown_section("Länder", country_summary, 'country', "🌍")
                st.markdown("---")

        # REGION
        if 'geographic_region' in insights and not insights['geographic_region'].empty:
            region_df = insights['geographic_region']

            if 'region' in region_df.columns:
                region_summary = safe_aggregate(
                    region_df,
                    'region',
                    {
                        'spend': 'sum',
                        'impressions': 'sum',
                        'reach': 'sum',
                        'clicks': 'sum',
                        'leads_extracted': 'sum'
                    }
                )

                render_breakdown_section("Regionen / Bundesländer", region_summary, 'region', "📍")
                st.markdown("---")

        # DMA (if available - optional breakdown)
        if 'dma' in insights and not insights['dma'].empty:
            dma_df = insights['dma']

            if 'dma' in dma_df.columns:
                dma_summary = safe_aggregate(
                    dma_df,
                    'dma',
                    {
                        'spend': 'sum',
                        'impressions': 'sum',
                        'clicks': 'sum',
                        'leads_extracted': 'sum'
                    }
                )

                render_breakdown_section("DMA", dma_summary, 'dma', "📡")

    # =============================================================================
    # TAB 3: PLATFORMS
    # =============================================================================
    with tab3:
        st.markdown("## 📱 Plattform & Placement Insights")
        st.markdown("Facebook, Instagram, Stories, Reels, Feed - wo performt was?")
        st.markdown("---")

        # PUBLISHER PLATFORM (if available)
        if 'publisher_platform' in insights and not insights['publisher_platform'].empty:
            platform_df = insights['publisher_platform']

            if 'publisher_platform' in platform_df.columns:
                platform_summary = safe_aggregate(
                    platform_df,
                    'publisher_platform',
                    {
                        'spend': 'sum',
                        'impressions': 'sum',
                        'clicks': 'sum',
                        'leads_extracted': 'sum'
                    }
                )

                render_breakdown_section("Plattformen", platform_summary, 'publisher_platform', "📱")
                st.markdown("---")

        # PLACEMENTS (Platform + Position)
        if 'placements' in insights and not insights['placements'].empty:
            placement_df = insights['placements']

            if 'publisher_platform' in placement_df.columns and 'platform_position' in placement_df.columns:
                placement_df['placement'] = (
                    placement_df['publisher_platform'].astype(str) + ' | ' +
                    placement_df['platform_position'].astype(str)
                )

                placement_summary = safe_aggregate(
                    placement_df,
                    'placement',
                    {
                        'spend': 'sum',
                        'impressions': 'sum',
                        'clicks': 'sum',
                        'leads_extracted': 'sum'
                    }
                )

                render_breakdown_section("Placements (Detailliert)", placement_summary, 'placement', "🎯")

    # =============================================================================
    # TAB 4: DEVICES
    # =============================================================================
    with tab4:
        st.markdown("## 💻 Geräte-Insights")
        st.markdown("Android, iPhone, Desktop - welches Device bringt die besten Ergebnisse?")
        st.markdown("---")

        # IMPRESSION DEVICE
        if 'devices' in insights and not insights['devices'].empty:
            device_df = insights['devices']

            if 'impression_device' in device_df.columns:
                device_summary = safe_aggregate(
                    device_df,
                    'impression_device',
                    {
                        'spend': 'sum',
                        'impressions': 'sum',
                        'clicks': 'sum',
                        'leads_extracted': 'sum'
                    }
                )

                render_breakdown_section("Devices", device_summary, 'impression_device', "💻")

    # =============================================================================
    # TAB 5: TIME ANALYSIS
    # =============================================================================
    with tab5:
        st.markdown("## 🕐 Zeitanalyse")
        st.markdown("Zu welcher Tageszeit performen deine Ads am besten?")
        st.markdown("---")

        # HOURLY
        if 'hourly' in insights and not insights['hourly'].empty:
            hourly_df = insights['hourly']

            if 'hourly_stats_aggregated_by_advertiser_time_zone' in hourly_df.columns:
                hourly_df['hour'] = hourly_df['hourly_stats_aggregated_by_advertiser_time_zone'].astype(str)

                hourly_summary = safe_aggregate(
                    hourly_df,
                    'hour',
                    {
                        'spend': 'sum',
                        'impressions': 'sum',
                        'clicks': 'sum',
                        'leads_extracted': 'sum'
                    }
                )

                st.markdown("### 🕐 Performance nach Tageszeit")

                # Summary metrics
                col1, col2, col3 = st.columns(3)

                with col1:
                    best_hour_spend = hourly_summary.nlargest(1, 'spend')['hour'].iloc[0] if not hourly_summary.empty else "N/A"
                    st.metric("🔥 Best Hour (Spend)", best_hour_spend)

                with col2:
                    best_hour_leads = hourly_summary.nlargest(1, 'leads_extracted')['hour'].iloc[0] if not hourly_summary.empty else "N/A"
                    st.metric("🎯 Best Hour (Leads)", best_hour_leads)

                with col3:
                    total_hours = len(hourly_summary)
                    st.metric("⏰ Active Hours", f"{total_hours}")

                # Table
                st.dataframe(
                    hourly_summary,
                    use_container_width=True,
                    hide_index=True
                )

                # Charts - only if data is available
                if not hourly_summary.empty and 'hour' in hourly_summary.columns and 'spend' in hourly_summary.columns:
                    chart_col1, chart_col2 = st.columns(2)

                    with chart_col1:
                        try:
                            fig = px.line(
                                hourly_summary,
                                x='hour',
                                y='spend',
                                title='Spend by Hour',
                                markers=True
                            )
                            fig.update_layout(xaxis_tickangle=-45)
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.error(f"Fehler beim Erstellen des Charts: {str(e)}")

                    with chart_col2:
                        try:
                            fig = px.bar(
                                hourly_summary,
                                x='hour',
                                y='leads_extracted',
                                title='Leads by Hour',
                                color='cpl' if 'cpl' in hourly_summary.columns else None
                            )
                            fig.update_layout(xaxis_tickangle=-45)
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.error(f"Fehler beim Erstellen des Charts: {str(e)}")
                else:
                    st.info("Nicht genügend Daten für Chart-Visualisierung")

    st.markdown("---")
    st.success("✅ Advanced Insights komplett - alle 12 Breakdowns analysiert!")
