"""
Meta Ads Autopilot Dashboard
AI-powered Meta Ads performance analysis with Google Gemini
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config import Config
from src.meta_ads_client import MetaAdsClient
from src.ai_analyzer import AIAnalyzer
from src.pdf_generator import PDFGenerator
from src.data_processor import DataProcessor
from src.visualizations import Visualizations
from src.whatsapp_sender import WhatsAppSender
from src.dashboard_home import render_home_professional
from src.dashboard_advanced_insights import render_advanced_insights_professional


def safe_select_columns(df, columns):
    """
    Safely select columns from DataFrame, only returning available ones
    """
    if df.empty:
        return df
    available_columns = [col for col in columns if col in df.columns]
    return df[available_columns] if available_columns else df


def convert_meta_strings_to_numbers(df):
    """
    Convert Meta API string numbers to actual floats
    Meta API returns all numeric values as strings, this converts them
    """
    if df.empty:
        return df

    numeric_fields = ['spend', 'impressions', 'reach', 'frequency', 'clicks', 'ctr', 'unique_ctr',
                     'cpc', 'cpm', 'cpp', 'inline_link_clicks', 'unique_clicks', 'inline_post_engagement',
                     'cost_per_inline_link_click', 'cost_per_inline_post_engagement',
                     'cost_per_unique_click', 'cost_per_unique_inline_link_click']

    for field in numeric_fields:
        if field in df.columns:
            df[field] = pd.to_numeric(df[field], errors='coerce').fillna(0)

    return df


# Page config
st.set_page_config(
    page_title="Meta Ads Autopilot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #F0F2F6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .success-box {
        background-color: #D4EDDA;
        border-left: 5px solid #09AB3B;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #FFF3CD;
        border-left: 5px solid #FFA500;
        padding: 1rem;
        margin: 1rem 0;
    }
    .danger-box {
        background-color: #F8D7DA;
        border-left: 5px solid #FF4B4B;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'meta_client' not in st.session_state:
        st.session_state.meta_client = MetaAdsClient()

    if 'ai_analyzer' not in st.session_state:
        st.session_state.ai_analyzer = AIAnalyzer()

    if 'data_processor' not in st.session_state:
        st.session_state.data_processor = DataProcessor()

    if 'visualizations' not in st.session_state:
        st.session_state.visualizations = Visualizations()

    if 'pdf_generator' not in st.session_state:
        st.session_state.pdf_generator = PDFGenerator()

    if 'whatsapp_sender' not in st.session_state:
        st.session_state.whatsapp_sender = WhatsAppSender()

    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = None


def render_sidebar():
    """Render sidebar navigation"""
    st.sidebar.markdown("# 🚀 Meta Ads Autopilot")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Home", "📊 Weekly Report", "📈 Monthly Report",
         "🎯 Ad Performance", "📞 Leads Dashboard", "💡 Content Strategy",
         "💬 AI Chat Assistant", "🔬 Advanced Insights", "⚙️ Settings"]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 AI Provider")
    st.sidebar.info("Google Gemini 2.5 Flash")

    company_name = Config.get('COMPANY_NAME', 'Your Company')
    st.sidebar.markdown(f"### 🏢 {company_name}")

    return page


def render_refresh_button():
    """Render refresh button and timestamp"""
    col1, col2 = st.columns([3, 1])

    with col2:
        if st.button("🔄 Aktualisieren", type="secondary", use_container_width=True):
            # Clear cache and refresh
            st.session_state.meta_client.clear_cache()
            st.session_state.last_refresh = datetime.now()
            st.rerun()

    with col1:
        if st.session_state.last_refresh:
            st.caption(f"Letztes Update: {st.session_state.last_refresh.strftime('%H:%M:%S')}")
        else:
            st.caption("Klicke auf 'Aktualisieren' für Live-Daten")


def render_home():
    """Render home page"""
    st.markdown('<div class="main-header">Meta Ads Autopilot 🚀</div>', unsafe_allow_html=True)
    st.markdown("### AI-powered Performance Dashboard mit Google Gemini")

    # Refresh button
    render_refresh_button()

    st.markdown("---")

    # Fetch current month data
    with st.spinner("Lade aktuelle Daten..."):
        campaign_df = st.session_state.meta_client.fetch_campaign_data(days=30)
        ad_df = st.session_state.meta_client.fetch_ad_performance(days=30)

    # Check API status and data availability
    api_status = st.session_state.meta_client.api_initialized

    if not api_status:
        st.error("""
        ❌ **Meta Ads API nicht verbunden**

        Bitte prüfe deine API-Konfiguration in den Streamlit Cloud Secrets.
        """)
    elif campaign_df.empty and ad_df.empty:
        st.warning("""
        ℹ️ **Keine Daten verfügbar**

        Die Meta API ist verbunden, findet aber keine Campaigns mit Ausgaben im gewählten Zeitraum.

        **Mögliche Gründe:**
        - Keine aktiven Campaigns im Account
        - Campaigns haben keine Ausgaben in den letzten 30 Tagen
        - Campaigns sind pausiert oder haben kein Budget

        **Lösung:** Aktiviere Campaigns im [Meta Ads Manager](https://www.facebook.com/adsmanager/)
        """)
    else:
        st.success(f"✅ Daten erfolgreich geladen | {len(campaign_df)} Campaigns, {len(ad_df)} Ads")

    # Calculate metrics
    total_spend = campaign_df['spend'].sum() if not campaign_df.empty else 0
    total_leads = campaign_df['leads'].sum() if not campaign_df.empty else 0
    avg_cpl = total_spend / total_leads if total_leads > 0 else 0
    active_campaigns = len(campaign_df) if not campaign_df.empty else 0

    # Display metric cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Spend (30d)", f"€{total_spend:,.2f}")

    with col2:
        st.metric("Total Leads (30d)", f"{int(total_leads):,}")

    with col3:
        delta_color = "inverse" if avg_cpl > 10 else "normal"
        st.metric("Avg CPL", f"€{avg_cpl:.2f}", delta=f"Target: €10.00")

    with col4:
        st.metric("Active Campaigns", f"{active_campaigns}")

    st.markdown("---")

    # Quick insights
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Kampagnen Übersicht")
        if not campaign_df.empty:
            # Show top 5 campaigns
            top_campaigns = campaign_df.nsmallest(5, 'cpl')
            st.dataframe(
                top_campaigns[['campaign_name', 'spend', 'leads', 'cpl']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Keine Kampagnendaten verfügbar")

    with col2:
        st.markdown("### 🎯 Top Performing Ads")
        if not ad_df.empty:
            # Show top 5 ads
            top_ads = ad_df.nsmallest(5, 'cpl')
            st.dataframe(
                top_ads[['ad_name', 'leads', 'cpl', 'hook_rate']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Keine Ad-Daten verfügbar")

    st.markdown("---")

    # Recent reports
    st.markdown("### 📄 Letzte Reports")
    reports_dir = os.path.join(os.path.dirname(__file__), 'reports')

    if os.path.exists(reports_dir):
        reports = [f for f in os.listdir(reports_dir) if f.endswith('.pdf')]
        reports.sort(reverse=True)

        if reports[:5]:
            for report in reports[:5]:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(report)
                with col2:
                    report_path = os.path.join(reports_dir, report)
                    with open(report_path, 'rb') as f:
                        st.download_button(
                            "📥 Download",
                            f.read(),
                            file_name=report,
                            mime="application/pdf",
                            key=report
                        )
        else:
            st.info("Noch keine Reports generiert")
    else:
        st.info("Noch keine Reports generiert")


def render_weekly_report():
    """Render weekly report page"""
    st.markdown("## 📊 Weekly Performance Report")

    # Refresh button
    render_refresh_button()

    st.markdown("---")

    # Date range picker - PROFESSIONAL wie bei Meta!
    st.markdown("### 📅 Datumsbereich auswählen")

    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

    with col1:
        # Preset options
        preset = st.selectbox(
            "Schnellauswahl",
            ["Benutzerdefiniert", "Heute", "Gestern", "Letzte 7 Tage", "Letzte 14 Tage", "Letzte 30 Tage", "Dieser Monat", "Letzter Monat"],
            index=3
        )

    # Calculate dates based on preset
    today = datetime.now().date()

    if preset == "Heute":
        start_date_default = today
        end_date_default = today
    elif preset == "Gestern":
        start_date_default = today - timedelta(days=1)
        end_date_default = today - timedelta(days=1)
    elif preset == "Letzte 7 Tage":
        start_date_default = today - timedelta(days=6)
        end_date_default = today
    elif preset == "Letzte 14 Tage":
        start_date_default = today - timedelta(days=13)
        end_date_default = today
    elif preset == "Letzte 30 Tage":
        start_date_default = today - timedelta(days=29)
        end_date_default = today
    elif preset == "Dieser Monat":
        start_date_default = today.replace(day=1)
        end_date_default = today
    elif preset == "Letzter Monat":
        first_day_this_month = today.replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        start_date_default = last_day_last_month.replace(day=1)
        end_date_default = last_day_last_month
    else:  # Benutzerdefiniert
        start_date_default = today - timedelta(days=6)
        end_date_default = today

    with col2:
        start_date = st.date_input(
            "Von",
            value=start_date_default,
            max_value=today,
            disabled=(preset != "Benutzerdefiniert"),
            key="start_date_input"
        )

    with col3:
        end_date = st.date_input(
            "Bis",
            value=end_date_default,
            max_value=today,
            min_value=start_date_default if preset == "Benutzerdefiniert" else None,
            disabled=(preset != "Benutzerdefiniert"),
            key="end_date_input"
        )

    with col4:
        analyze_button = st.button("🤖 Analysieren", type="primary", use_container_width=True)

    # Show selected range - ensure dates are valid
    if start_date and end_date:
        try:
            days_selected = (end_date - start_date).days + 1
            st.caption(f"📊 Ausgewählter Zeitraum: **{days_selected} Tage** ({start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')})")
        except Exception as e:
            st.error(f"Fehler bei Datumsberechnung: {str(e)}")
            start_date = start_date_default
            end_date = end_date_default
    else:
        st.warning("Bitte wähle ein gültiges Von/Bis Datum")
        start_date = start_date_default
        end_date = end_date_default

    st.markdown("---")

    if analyze_button and start_date and end_date:
        with st.spinner("🔄 Lade Meta Ads Daten..."):
            # Use custom date range with start_date and end_date!
            campaign_df = st.session_state.meta_client.fetch_campaign_data(
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )
            ad_df = st.session_state.meta_client.fetch_ad_performance(
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )

        if campaign_df.empty and ad_df.empty:
            st.error("Keine Daten verfügbar für den gewählten Zeitraum")
            return

        # Calculate metrics
        campaign_df = st.session_state.data_processor.calculate_metrics(campaign_df)
        ad_df = st.session_state.data_processor.calculate_metrics(ad_df)
        ad_df = st.session_state.data_processor.detect_ad_fatigue(ad_df)

        with st.spinner("🤖 Google Gemini analysiert Performance..."):
            date_range = f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}"
            analysis = st.session_state.ai_analyzer.analyze_weekly_performance(
                campaign_df, ad_df, date_range
            )

        # Display results in tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Executive Summary",
            "📊 Performance Metrics",
            "🏆 Top Performers",
            "⚠️ Underperformers",
            "💡 Recommendations"
        ])

        with tab1:
            st.markdown("### Executive Summary")
            st.markdown(analysis['full_analysis'])

        with tab2:
            st.markdown("### Performance Metrics")

            # Summary stats
            stats = st.session_state.data_processor.create_summary_stats(ad_df)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Spend", f"€{stats.get('total_spend', 0):,.2f}")
            with col2:
                st.metric("Total Leads", f"{stats.get('total_leads', 0):,}")
            with col3:
                st.metric("Avg CPL", f"€{stats.get('avg_cpl', 0):.2f}")
            with col4:
                st.metric("Avg Frequency", f"{stats.get('avg_frequency', 0):.2f}")

            st.markdown("---")

            # Charts
            col1, col2 = st.columns(2)

            with col1:
                cpl_chart = st.session_state.visualizations.create_cpl_comparison(ad_df)
                st.plotly_chart(cpl_chart, use_container_width=True)

            with col2:
                freq_chart = st.session_state.visualizations.create_frequency_histogram(ad_df)
                st.plotly_chart(freq_chart, use_container_width=True)

            # Hook & Hold Analysis
            hook_hold_chart = st.session_state.visualizations.create_hook_hold_analysis(
                ad_df.head(10)
            )
            st.plotly_chart(hook_hold_chart, use_container_width=True)

        with tab3:
            st.markdown("### 🏆 Top Performing Ads")
            top_performers = st.session_state.data_processor.identify_top_performers(ad_df, 'cpl', 5)

            if not top_performers.empty:
                display_cols = ['ad_name', 'spend', 'leads', 'cpl', 'hook_rate', 'hold_rate', 'frequency']
                st.dataframe(
                    safe_select_columns(top_performers, display_cols),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Keine Daten verfügbar")

        with tab4:
            st.markdown("### ⚠️ Underperforming Ads")
            underperformers = st.session_state.data_processor.identify_underperformers(ad_df, 'cpl', 5)

            if not underperformers.empty:
                display_cols = ['ad_name', 'spend', 'leads', 'cpl', 'hook_rate', 'hold_rate', 'frequency']
                st.dataframe(
                    safe_select_columns(underperformers, display_cols),
                    use_container_width=True,
                    hide_index=True
                )

                # Ad fatigue warnings
                fatigued = ad_df[ad_df['ad_fatigue'] == True]
                if not fatigued.empty:
                    st.info(f"{len(fatigued)} Ads zeigen Anzeichen von Ad Fatigue (Frequency >6)")
            else:
                st.info("Keine Daten verfügbar")

        with tab5:
            st.markdown("### 💡 AI-generierte Empfehlungen")
            st.info("Die Empfehlungen sind im Executive Summary enthalten")

        # PDF Download & WhatsApp
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.markdown("### 📥 Export & Versand")

        with col2:
            if st.button("📄 Download PDF", type="secondary", use_container_width=True):
                with st.spinner("Generiere PDF..."):
                    pdf_path = st.session_state.pdf_generator.generate_weekly_report(
                        analysis, campaign_df, ad_df
                    )

                    with open(pdf_path, 'rb') as f:
                        st.download_button(
                            "📥 PDF herunterladen",
                            f.read(),
                            file_name=os.path.basename(pdf_path),
                            mime="application/pdf",
                            use_container_width=True
                        )
                    st.success(f"✅ PDF erstellt!")

        with col3:
            # WhatsApp send button
            if st.session_state.whatsapp_sender.enabled:
                to_number = Config.get('WHATSAPP_TO_NUMBER')
                if to_number and st.button("📱 An WhatsApp", type="primary", use_container_width=True):
                    # Calculate summary metrics
                    total_spend = ad_df['spend'].sum() if not ad_df.empty else 0
                    total_leads = ad_df['leads'].sum() if not ad_df.empty else 0
                    avg_cpl = total_spend / total_leads if total_leads > 0 else 0

                    with st.spinner("Sende an WhatsApp..."):
                        if st.session_state.whatsapp_sender.send_quick_update(
                            to_number, total_spend, int(total_leads), avg_cpl
                        ):
                            st.success("✅ WhatsApp gesendet!")
                        else:
                            st.error("❌ Versand fehlgeschlagen")
            else:
                st.caption("WhatsApp: Twilio nicht konfiguriert")


def render_monthly_report():
    """Render monthly report page"""
    st.markdown("## 📈 Monthly Performance Report")

    st.info("Monthly Report mit Month-over-Month Vergleich")

    analyze_button = st.button("🤖 Generate Monthly Report", type="primary")

    if analyze_button:
        with st.spinner("Lade Daten für 60 Tage..."):
            # Get last 60 days to compare
            all_data = st.session_state.meta_client.fetch_ad_performance(days=60)

            if all_data.empty:
                st.error("Keine Daten verfügbar")
                return

            # Split into current and previous month
            current_month = st.session_state.meta_client.fetch_ad_performance(days=30)

            campaign_df = st.session_state.meta_client.fetch_campaign_data(days=30)

        # Calculate metrics
        current_month = st.session_state.data_processor.calculate_metrics(current_month)

        # Display metrics
        stats = st.session_state.data_processor.create_summary_stats(current_month)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Monthly Spend", f"€{stats.get('total_spend', 0):,.2f}")
        with col2:
            st.metric("Monthly Leads", f"{stats.get('total_leads', 0):,}")
        with col3:
            st.metric("Avg CPL", f"€{stats.get('avg_cpl', 0):.2f}")

        st.markdown("---")

        # Campaign Performance Table
        st.markdown("### Kampagnen Performance (30 Tage)")
        if not campaign_df.empty:
            display_cols = ['campaign_name', 'spend', 'leads', 'cpl', 'frequency']
            st.dataframe(
                safe_select_columns(campaign_df, display_cols),
                use_container_width=True,
                hide_index=True
            )


def render_ad_performance():
    """Render ad performance page"""
    st.markdown("## 🎯 Ad Performance Analysis")

    # Refresh button
    render_refresh_button()

    col1, col2 = st.columns([3, 1])

    with col1:
        days = st.selectbox("Zeitraum", [7, 14, 30], index=2)

    with col2:
        force_refresh = st.checkbox("⚡ Cache ignorieren", value=False, help="Frische Daten laden")

    with st.spinner("Lade Ad Performance Daten..." if not force_refresh else "⚡ Lade frische Daten von Meta API..."):
        ad_df = st.session_state.meta_client.fetch_ad_performance(days=days, force_refresh=force_refresh)

    if ad_df.empty:
        st.warning("Keine Ad-Daten verfügbar")
        return

    # Convert Meta API strings to numbers
    ad_df = convert_meta_strings_to_numbers(ad_df)

    # Calculate metrics
    ad_df = st.session_state.data_processor.calculate_metrics(ad_df)
    ad_df = st.session_state.data_processor.detect_ad_fatigue(ad_df)

    # Add performance score
    ad_df['performance_score'] = ad_df.apply(
        st.session_state.data_processor.calculate_performance_score,
        axis=1
    )

    # Filters
    st.markdown("### Filter")
    col1, col2, col3 = st.columns(3)

    with col1:
        show_fatigued = st.checkbox("Nur Ad Fatigue zeigen", value=False)

    with col2:
        min_spend = st.number_input("Min Spend (€)", value=0.0, step=10.0)

    with col3:
        max_cpl = st.number_input("Max CPL (€)", value=100.0, step=1.0)

    # Apply filters
    filtered_df = ad_df.copy()

    if show_fatigued:
        filtered_df = filtered_df[filtered_df['ad_fatigue'] == True]

    filtered_df = filtered_df[filtered_df['spend'] >= min_spend]
    filtered_df = filtered_df[filtered_df['cpl'] <= max_cpl]

    st.markdown("---")

    # Display table with color coding
    st.markdown(f"### Ad Performance ({len(filtered_df)} Ads)")

    # Style function for dataframe
    def color_cpl(val):
        if pd.isna(val):
            return ''
        try:
            val_float = float(val)
            if val_float < 8:
                return 'background-color: #D4EDDA'
            elif val_float < 15:
                return 'background-color: #FFF3CD'
            else:
                return 'background-color: #F8D7DA'
        except:
            return ''

    display_cols = ['ad_name', 'spend', 'leads', 'cpl', 'hook_rate',
                    'hold_rate', 'frequency', 'performance_score']
    display_df = safe_select_columns(filtered_df, display_cols).copy()

    # Format columns (only if they exist)
    if 'spend' in display_df.columns:
        display_df['spend'] = display_df['spend'].apply(lambda x: f"€{x:,.2f}")
    if 'cpl' in display_df.columns:
        display_df['cpl'] = display_df['cpl'].apply(lambda x: f"€{x:.2f}")
    if 'hook_rate' in display_df.columns:
        display_df['hook_rate'] = display_df['hook_rate'].apply(lambda x: f"{x:.1f}%")
    if 'hold_rate' in display_df.columns:
        display_df['hold_rate'] = display_df['hold_rate'].apply(lambda x: f"{x:.1f}%")
    if 'frequency' in display_df.columns:
        display_df['frequency'] = display_df['frequency'].apply(lambda x: f"{x:.2f}")
    if 'performance_score' in display_df.columns:
        display_df['performance_score'] = display_df['performance_score'].apply(lambda x: f"{x:.0f}/100")

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Single Ad Analysis
    st.markdown("### 🔍 Einzelne Ad Analysieren")

    selected_ad = st.selectbox(
        "Ad auswählen",
        filtered_df['ad_name'].tolist()
    )

    if st.button("Get AI Analysis", type="primary"):
        ad_data = filtered_df[filtered_df['ad_name'] == selected_ad].iloc[0].to_dict()

        with st.spinner("🤖 Google Gemini analysiert Ad..."):
            analysis = st.session_state.ai_analyzer.analyze_single_ad(ad_data)

        st.markdown("### AI Analysis")
        st.markdown(analysis['analysis'])


def render_content_strategy():
    """Render content strategy page"""
    st.markdown("## 💡 Content Strategy Generator")

    st.info("Generiere neue Content-Ideen basierend auf deinen Top Performern")

    # Get top ads
    with st.spinner("Lade Top Performing Ads..."):
        ad_df = st.session_state.meta_client.fetch_ad_performance(days=30)

    if ad_df.empty:
        st.warning("Keine Daten verfügbar")
        return

    top_ads = st.session_state.data_processor.identify_top_performers(ad_df, 'cpl', 5)

    # Strategy selection
    strategy_type = st.selectbox(
        "Content Strategie wählen",
        ["FOMO", "Loss Aversion", "Social Proof", "Urgency", "Value Proposition"]
    )

    if st.button("💡 Generate New Ideas", type="primary"):
        with st.spinner("🤖 Google Gemini erstellt Content Strategie..."):
            content_strategy = st.session_state.ai_analyzer.generate_content_strategy(
                top_ads, strategy_type
            )

        st.markdown("### Content Ideas")
        st.markdown(content_strategy['content_ideas'])

        # Export button
        if st.button("📄 Export as Markdown"):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"content_strategy_{strategy_type}_{timestamp}.md"

            st.download_button(
                "📥 Download Markdown",
                content_strategy['content_ideas'],
                file_name=filename,
                mime="text/markdown"
            )


def render_leads_dashboard():
    """Render leads dashboard page"""
    st.markdown("## 📞 Leads Dashboard")
    st.markdown("### Aktuelle Lead-Formulare Daten")

    # Refresh button
    render_refresh_button()

    # Date range selector
    col1, col2 = st.columns([2, 2])

    with col1:
        days = st.selectbox(
            "Zeitraum wählen",
            [7, 14, 30, 60],
            index=2,
            format_func=lambda x: f"Letzte {x} Tage"
        )

    with col2:
        force_refresh = st.checkbox("Live-Daten (Cache umgehen)", value=False)

    st.markdown("---")

    # Fetch real lead data with individual details
    with st.spinner("Lade echte Lead-Daten von Meta..."):
        leads_df = st.session_state.meta_client.fetch_leads_data(days=days, force_refresh=force_refresh)

    if leads_df.empty:
        st.info("Keine Leads im gewählten Zeitraum gefunden")
        st.info("""
        **Mögliche Gründe:**
        - Keine Lead-Formulare mit Submissions in diesem Zeitraum
        - Prüfen Sie Ihre Meta Ads auf lead-generierende Kampagnen
        """)
        return

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_leads = len(leads_df)
        st.metric("Total Leads", total_leads)

    with col2:
        # Count leads from last 24h
        if 'created_time' in leads_df.columns:
            leads_df['created_datetime'] = pd.to_datetime(leads_df['created_time'])
            recent_leads = len(leads_df[leads_df['created_datetime'] >= datetime.now() - timedelta(days=1)])
            st.metric("Leads (24h)", recent_leads)
        else:
            st.metric("Leads (24h)", "N/A")

    with col3:
        # Unique forms
        if 'form_name' in leads_df.columns:
            unique_forms = leads_df['form_name'].nunique()
            st.metric("Lead-Formulare", unique_forms)
        else:
            st.metric("Lead-Formulare", "N/A")

    with col4:
        # Page name
        if 'page_name' in leads_df.columns:
            page_name = leads_df['page_name'].iloc[0] if len(leads_df) > 0 else "N/A"
            st.metric("Page", page_name)
        else:
            st.metric("Page", "N/A")

    st.markdown("---")

    # Display leads table
    st.markdown(f"### Lead-Details ({total_leads} Leads)")

    # Prepare display dataframe with available columns
    display_columns = []
    available_columns = leads_df.columns.tolist()

    # Prioritize important columns
    priority_columns = ['created_time', 'form_name', 'first name', 'email', 'phone', 'full_name', 'phone_number', 'lead_id']

    for col in priority_columns:
        if col in available_columns:
            display_columns.append(col)

    # Add remaining columns (except internal ones)
    for col in available_columns:
        if col not in display_columns and col not in ['created_datetime', 'page_name', 'lead_id']:
            display_columns.append(col)

    # Display the table
    if display_columns:
        st.dataframe(
            leads_df[display_columns].sort_values('created_time', ascending=False),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.dataframe(leads_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Export functionality
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown("### 📥 Export")

    with col2:
        # CSV Export
        csv = leads_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📄 Download CSV",
            csv,
            file_name=f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col3:
        # WhatsApp notification (if configured)
        if st.session_state.whatsapp_sender.enabled:
            to_number = Config.get('WHATSAPP_TO_NUMBER')
            if to_number and st.button("📱 WhatsApp Update", use_container_width=True):
                message = f"""
📞 *Lead Update - {Config.get('COMPANY_NAME', 'CarCenter Landshut')}*

📊 *Zeitraum:* Letzte {days} Tage
📞 *Leads:* {len(leads_df)}
🕐 *Stand:* {datetime.now().strftime('%d.%m.%Y %H:%M')}

_Powered by Meta Ads Autopilot_
_Brandea GbR_
                """.strip()

                with st.spinner("Sende WhatsApp..."):
                    if st.session_state.whatsapp_sender.send_report(to_number, message):
                        st.success("✅ WhatsApp gesendet!")
                    else:
                        st.error("❌ WhatsApp Versand fehlgeschlagen")
        else:
            st.caption("WhatsApp nicht konfiguriert")

    # Lead details section
    if not leads_df.empty:
        st.markdown("---")
        st.markdown("### 🔍 Lead Details")

        # Select a lead to view details
        lead_options = []
        for idx, row in leads_df.iterrows():
            lead_label = f"{row.get('created_time', 'Unknown')} - {row.get('ad_name', 'Unknown')}"
            lead_options.append((lead_label, idx))

        if lead_options:
            selected_lead_label, selected_idx = lead_options[0], 0
            selected_lead_label = st.selectbox(
                "Lead auswählen",
                [opt[0] for opt in lead_options]
            )

            # Find the index
            for label, idx in lead_options:
                if label == selected_lead_label:
                    selected_idx = idx
                    break

            # Display selected lead details
            lead_data = leads_df.iloc[selected_idx]

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Lead Information:**")
                for key, value in lead_data.items():
                    if key not in ['form_id', 'created_datetime']:
                        st.text(f"{key}: {value}")

            with col2:
                st.markdown("**Aktionen:**")
                st.info("Lead-Qualifizierung und Follow-up Tracking kommt bald!")


def render_ai_chat():
    """Render interactive AI chat assistant"""
    st.markdown("## 💬 AI Chat Assistant mit Google Gemini")
    st.markdown("### Interaktive Beratung für deine Meta Ads Kampagnen")

    # Refresh button
    render_refresh_button()

    st.markdown("---")

    # Load LIVE DATA for Gemini context
    st.markdown("### 📊 Live-Daten Status")

    col1, col2, col3 = st.columns(3)

    with col1:
        load_data = st.checkbox("🔄 Live-Daten laden", value=True, help="Gibt Gemini Zugriff auf aktuelle Kampagnen-Daten")

    with col2:
        days_context = st.selectbox("Zeitraum", [7, 14, 30], index=0, help="Wie viele Tage Daten für Gemini")

    with col3:
        if load_data:
            st.success("✅ Daten aktiv")
        else:
            st.info("Ohne Live-Daten")

    # Fetch live data if enabled
    campaign_context = ""
    ad_context = ""
    leads_context = ""
    metrics_summary = ""

    if load_data:
        with st.spinner("📥 Lade aktuelle Meta Ads Daten..."):
            try:
                # Get fresh data
                campaign_df = st.session_state.meta_client.fetch_campaign_data(days=days_context)
                ad_df = st.session_state.meta_client.fetch_ad_performance(days=days_context)
                leads_df = st.session_state.meta_client.fetch_leads_data(days=days_context)

                # Convert strings to numbers
                campaign_df = convert_meta_strings_to_numbers(campaign_df)
                ad_df = convert_meta_strings_to_numbers(ad_df)

                # Extract leads from ad_df actions
                if not ad_df.empty:
                    def extract_leads(actions):
                        if isinstance(actions, list):
                            for action in actions:
                                if isinstance(action, dict) and action.get('action_type') == 'lead':
                                    try:
                                        return int(action.get('value', 0))
                                    except:
                                        return 0
                        return 0

                    ad_df['leads'] = ad_df['actions'].apply(extract_leads)
                    ad_df['cpl'] = ad_df.apply(
                        lambda row: round(row['spend'] / row['leads'], 2) if row['leads'] > 0 else 0,
                        axis=1
                    )

                # Create COMPREHENSIVE context strings for Gemini with ALL metrics
                if not campaign_df.empty:
                    campaign_context = f"\n\n{'='*80}\n📊 KAMPAGNEN-DATEN (letzte {days_context} Tage) - VOLLSTÄNDIG:\n{'='*80}\n"

                    # Select important columns for campaigns
                    campaign_cols = ['campaign_name', 'spend', 'impressions', 'reach', 'frequency',
                                    'clicks', 'ctr', 'cpc', 'cpm', 'leads', 'cpl']
                    available_campaign_cols = [col for col in campaign_cols if col in campaign_df.columns]

                    # Convert to markdown table for better structure
                    campaign_table = campaign_df[available_campaign_cols].to_markdown(index=False, floatfmt=".2f")
                    campaign_context += campaign_table + "\n"

                if not ad_df.empty:
                    ad_context = f"\n\n{'='*80}\n🎯 AD-PERFORMANCE DATEN (letzte {days_context} Tage) - ALLE ADS:\n{'='*80}\n"

                    # Select ALL important ad columns
                    ad_cols = ['ad_name', 'spend', 'impressions', 'reach', 'frequency', 'clicks',
                              'ctr', 'cpc', 'cpm', 'leads', 'cpl', 'hook_rate', 'hold_rate',
                              'video_plays', 'video_avg_time_watched']
                    available_ad_cols = [col for col in ad_cols if col in ad_df.columns]

                    # Show ALL ads, not just top 5
                    ad_table = ad_df[available_ad_cols].to_markdown(index=False, floatfmt=".2f")
                    ad_context += ad_table + "\n"

                    # Add statistical insights
                    ad_context += f"\n📈 AD STATISTIKEN:\n"
                    ad_context += f"- Beste CPL: €{ad_df['cpl'].min():.2f} (Ad: {ad_df.loc[ad_df['cpl'].idxmin(), 'ad_name']})\n"
                    ad_context += f"- Schlechteste CPL: €{ad_df['cpl'].max():.2f} (Ad: {ad_df.loc[ad_df['cpl'].idxmax(), 'ad_name']})\n"
                    if 'hook_rate' in ad_df.columns:
                        ad_context += f"- Beste Hook Rate: {ad_df['hook_rate'].max():.1f}% (Ad: {ad_df.loc[ad_df['hook_rate'].idxmax(), 'ad_name']})\n"
                        ad_context += f"- Schlechteste Hook Rate: {ad_df['hook_rate'].min():.1f}% (Ad: {ad_df.loc[ad_df['hook_rate'].idxmin(), 'ad_name']})\n"
                    if 'hold_rate' in ad_df.columns:
                        ad_context += f"- Beste Hold Rate: {ad_df['hold_rate'].max():.1f}% (Ad: {ad_df.loc[ad_df['hold_rate'].idxmax(), 'ad_name']})\n"

                if not leads_df.empty:
                    leads_context = f"\n\n{'='*80}\n📞 LEADS-DATEN (letzte {days_context} Tage) - ALLE INDIVIDUELLEN LEADS:\n{'='*80}\n"
                    leads_context += f"Gesamt: {len(leads_df)} Leads\n\n"

                    # Show lead form performance
                    if 'form_name' in leads_df.columns:
                        form_performance = leads_df['form_name'].value_counts()
                        leads_context += "📋 LEAD-FORMULARE:\n"
                        for form_name, count in form_performance.items():
                            leads_context += f"- {form_name}: {count} Leads\n"

                    # Show recent leads (last 10) with details
                    if 'created_time' in leads_df.columns:
                        leads_context += f"\n📅 LETZTE 10 LEADS (Details):\n"
                        recent_leads = leads_df.sort_values('created_time', ascending=False).head(10)

                        # Select available lead columns
                        lead_display_cols = [col for col in leads_df.columns if col not in ['form_id', 'page_id']]
                        lead_table = recent_leads[lead_display_cols].to_markdown(index=False)
                        leads_context += lead_table + "\n"

                # COMPREHENSIVE Summary metrics with ALL available data
                metrics_summary = f"\n\n{'='*80}\n📊 GESAMT-ÜBERSICHT (letzte {days_context} Tage):\n{'='*80}\n"

                if not ad_df.empty:
                    total_spend = ad_df['spend'].sum()
                    total_leads = ad_df['leads'].sum()
                    total_impressions = ad_df['impressions'].sum()
                    total_reach = ad_df['reach'].sum()
                    total_clicks = ad_df['clicks'].sum()
                    avg_cpl = total_spend / total_leads if total_leads > 0 else 0
                    avg_ctr = ad_df['ctr'].mean() if 'ctr' in ad_df.columns else 0
                    avg_frequency = ad_df['frequency'].mean() if 'frequency' in ad_df.columns else 0
                    avg_hook_rate = ad_df['hook_rate'].mean() if 'hook_rate' in ad_df.columns else 0
                    avg_hold_rate = ad_df['hold_rate'].mean() if 'hold_rate' in ad_df.columns else 0

                    metrics_summary += f"""
💰 BUDGET & KOSTEN:
- Total Spend: €{total_spend:,.2f}
- Durchschnitt CPL: €{avg_cpl:.2f}
- Durchschnitt CPC: €{ad_df['cpc'].mean():.2f}
- Durchschnitt CPM: €{ad_df['cpm'].mean():.2f}

📊 PERFORMANCE:
- Total Leads: {int(total_leads):,}
- Total Impressions: {int(total_impressions):,}
- Total Reach: {int(total_reach):,}
- Total Clicks: {int(total_clicks):,}
- Durchschnitt CTR: {avg_ctr:.2f}%
- Durchschnitt Frequency: {avg_frequency:.2f}

🎥 VIDEO METRIKEN:
- Durchschnitt Hook Rate: {avg_hook_rate:.1f}%
- Durchschnitt Hold Rate: {avg_hold_rate:.1f}%

📈 KAMPAGNEN INFO:
- Anzahl Kampagnen: {len(campaign_df) if not campaign_df.empty else 0}
- Anzahl aktive Ads: {len(ad_df)}
- Anzahl Leads (Forms): {len(leads_df) if not leads_df.empty else 0}
"""

                # Show data preview
                with st.expander("👁️ Geladene Daten anzeigen", expanded=False):
                    st.markdown("**Gemini hat Zugriff auf:**")
                    st.markdown(metrics_summary)
                    if campaign_context:
                        st.markdown(campaign_context)
                    if ad_context:
                        st.markdown(ad_context)
                    if leads_context:
                        st.markdown(leads_context)

            except Exception as e:
                st.error(f"Fehler beim Laden der Daten: {str(e)}")
                load_data = False

    st.markdown("---")

    # System Prompt Editor
    with st.expander("🔧 System-Prompt anzeigen/bearbeiten", expanded=False):
        st.markdown("**Aktueller System-Prompt:**")

        default_chat_prompt = f"""Du bist ein professioneller Meta Ads Berater für {Config.get('COMPANY_NAME', 'CarCenter Landshut')}.

WICHTIGER KONTEXT:
- Branche: Automotive - FAHRZEUG-ANKAUF (wir kaufen Autos, wir verkaufen nicht!)
- Standort: Landshut und Umgebung
- Zielgruppe: Privatpersonen die ihr Auto verkaufen wollen
- Ziel: Lead-Generierung für Auto-Ankauf

DEINE AUFGABE:
- Beantworte Fragen zu Meta Ads Performance
- Gib konkrete Handlungsempfehlungen
- Analysiere Kampagnen-Daten
- Schlage Content-Ideen für Auto-ANKAUF vor (nicht Verkauf!)
- Helfe bei Ad-Optimierung
- Erkläre Metriken (CPL, Hook Rate, Hold Rate, etc.)

WICHTIG:
- Immer Perspektive ANKÄUFER (wir kaufen Autos)
- CTAs: "Auto verkaufen", "Angebot anfordern", etc.
- Seriös, professionell, datengetrieben
- Konkrete Zahlen und Beispiele nutzen
- Keine verbotenen Claims ("garantiert", "beste", etc.)

Antworte auf Deutsch, präzise und umsetzbar."""

        if 'custom_chat_prompt' not in st.session_state:
            st.session_state.custom_chat_prompt = default_chat_prompt

        custom_prompt = st.text_area(
            "Bearbeite den System-Prompt nach deinen Bedürfnissen:",
            value=st.session_state.custom_chat_prompt,
            height=300
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Prompt speichern"):
                st.session_state.custom_chat_prompt = custom_prompt
                st.success("✅ System-Prompt gespeichert!")

        with col2:
            if st.button("🔄 Auf Standard zurücksetzen"):
                st.session_state.custom_chat_prompt = default_chat_prompt
                st.success("✅ Auf Standard-Prompt zurückgesetzt!")

    st.markdown("---")

    # Chat interface
    st.markdown("### 💬 Chat mit Gemini")

    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    chat_container = st.container()

    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"""
                <div style='background-color: #E3F2FD; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                    <strong>👤 Du:</strong><br>{message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background-color: #F5F5F5; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                    <strong>🤖 Gemini:</strong><br>{message['content']}
                </div>
                """, unsafe_allow_html=True)

    # Quick action buttons
    st.markdown("#### 🚀 Schnelle Fragen:")
    col1, col2, col3, col4 = st.columns(4)

    quick_question = None

    with col1:
        if st.button("📊 CPL analysieren", use_container_width=True):
            if load_data and not ad_df.empty:
                quick_question = f"Analysiere meine aktuellen CPL-Werte. Ich habe {len(ad_df)} Ads mit durchschnittlich €{avg_cpl:.2f} CPL. Welche Ads sollte ich optimieren und wie?"
            else:
                quick_question = "Wie kann ich meinen Cost-per-Lead (CPL) senken? Gib mir konkrete, umsetzbare Tipps."

    with col2:
        if st.button("🎯 Top Performer", use_container_width=True):
            if load_data and not ad_df.empty:
                best_ad = ad_df.nsmallest(1, 'cpl').iloc[0]
                quick_question = f"Warum performt '{best_ad['ad_name']}' so gut? (CPL: €{best_ad['cpl']:.2f}, Hook Rate: {best_ad.get('hook_rate', 0):.1f}%) Was kann ich davon lernen?"
            else:
                quick_question = "Was macht einen Top-Performer aus? Welche Eigenschaften sollte eine erfolgreiche Auto-Ankauf Ad haben?"

    with col3:
        if st.button("⚠️ Probleme finden", use_container_width=True):
            if load_data and not ad_df.empty:
                worst_ads = ad_df.nlargest(3, 'cpl')
                quick_question = f"Ich habe {len(worst_ads)} problematische Ads. Analysiere die schlechtesten Performer und sag mir KONKRET was ich ändern muss."
            else:
                quick_question = "Wie erkenne ich problematische Ads? Welche Metriken sind Red Flags?"

    with col4:
        if st.button("💡 Content-Ideen", use_container_width=True):
            if load_data and not ad_df.empty:
                quick_question = f"Basierend auf meinen aktuellen Top-Performern: Gib mir 5 neue, kreative Content-Ideen für Auto-Ankauf Ads. Denk daran: Wir KAUFEN Autos!"
            else:
                quick_question = "Gib mir 5 kreative Content-Ideen für Auto-Ankauf Ads. Denk daran: Wir kaufen Autos, wir verkaufen nicht!"

    # Use quick question if clicked
    if quick_question:
        user_input = quick_question

    # Chat input
    st.markdown("---")
    user_input = st.text_area(
        "Deine Frage an Gemini:",
        placeholder="z.B. 'Analysiere meine Top 3 Kampagnen und gib mir Verbesserungsvorschläge'",
        key="chat_input"
    )

    col1, col2, col3 = st.columns([1, 1, 4])

    with col1:
        send_button = st.button("📤 Senden", type="primary", use_container_width=True)

    with col2:
        if st.button("🗑️ Chat löschen", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    if send_button and user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input
        })

        # Get AI response
        with st.spinner("🤖 Gemini denkt nach..."):
            try:
                # Build conversation context with LIVE DATA
                conversation = st.session_state.custom_chat_prompt + "\n\n"

                # ADD LIVE DATA CONTEXT - Gemini sieht ALLE aktuellen Daten!
                if load_data:
                    conversation += "\n" + "="*60 + "\n"
                    conversation += "🔴 LIVE-DATEN VON META ADS (AKTUELL!):\n"
                    conversation += "="*60 + "\n"

                    if metrics_summary:
                        conversation += metrics_summary

                    if campaign_context:
                        conversation += campaign_context

                    if ad_context:
                        conversation += ad_context

                    if leads_context:
                        conversation += leads_context

                    conversation += "\n" + "="*60 + "\n"
                    conversation += "WICHTIG: Nutze diese AKTUELLEN Daten für deine Antwort!\n"
                    conversation += "Wenn der User nach Kampagnen, Ads oder Performance fragt,\n"
                    conversation += "beziehe dich auf die ECHTEN Zahlen oben!\n"
                    conversation += "="*60 + "\n\n"
                else:
                    conversation += "\nHINWEIS: Keine Live-Daten geladen. Antworte allgemein.\n\n"

                # Add chat history for context
                for msg in st.session_state.chat_history[-5:]:  # Last 5 messages for context
                    if msg['role'] == 'user':
                        conversation += f"\nUser: {msg['content']}\n"
                    else:
                        conversation += f"\nAssistant: {msg['content']}\n"

                # Get response from Gemini
                response = st.session_state.ai_analyzer._generate_content(conversation)

                # Add AI response to history
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response
                })

                # Rerun to show new messages
                st.rerun()

            except Exception as e:
                st.error(f"Fehler bei der AI-Antwort: {str(e)}")

    # Export chat
    if st.session_state.chat_history:
        st.markdown("---")
        st.markdown("### 📥 Chat exportieren")

        # Create markdown export
        chat_export = f"# AI Chat Session - {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                chat_export += f"## 👤 User\n{message['content']}\n\n"
            else:
                chat_export += f"## 🤖 Gemini\n{message['content']}\n\n"

        st.download_button(
            "📄 Als Markdown exportieren",
            chat_export,
            file_name=f"ai_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )


def render_advanced_insights():
    """Render advanced insights page with COMPLETE demographics, placements, devices"""
    st.markdown("## 🔬 Advanced Insights - VOLLSTÄNDIGE DATEN-ANALYSE")
    st.markdown("### 📊 Demografien, Plattformen, Video-Retention & mehr!")

    # Refresh button
    render_refresh_button()

    st.markdown("---")

    # Date range picker
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        days = st.selectbox(
            "Zeitraum",
            [7, 14, 30],
            index=0,
            format_func=lambda x: f"Letzte {x} Tage"
        )

    with col2:
        level = st.selectbox(
            "Analyse-Level",
            ["ad", "adset", "campaign"],
            format_func=lambda x: {"ad": "Ad-Level", "adset": "AdSet-Level", "campaign": "Campaign-Level"}[x]
        )

    with col3:
        analyze_button = st.button("🔥 Analysieren", type="primary", use_container_width=True)

    st.markdown("---")

    if not analyze_button:
        st.info("""
        ### 🎯 Was du hier bekommst:

        **Diese Seite holt ALLE verfügbaren Daten von Meta:**

        ✅ **Demographics**: Alter, Geschlecht (z.B. "18-24 männlich", "35-44 weiblich")
        ✅ **Geographic**: Länder, Regionen, Städte (woher kommen deine Leads?)
        ✅ **Plattformen**: Facebook Feed, Instagram Feed, Stories, Reels, Messenger
        ✅ **Geräte**: Mobile (iPhone/Android), Desktop, Tablet
        ✅ **Tageszeiten**: Welche Stunden performen am besten?
        ✅ **Video-Retention**: 25%, 50%, 75%, 95%, 100% Completion Rate
        ✅ **Engagement**: Likes, Comments, Shares, Saves

        **Hinweis:**
        - **Demographics/Geographic/Placements/Devices** funktionieren am besten auf **AD-LEVEL**
        - Wähle "Ad-Level" oben für vollständige Breakdowns

        Klicke auf "🔥 Analysieren" um die vollständige Analyse zu starten!
        """)
        return

    # Fetch comprehensive insights
    with st.spinner("🔥 Lade ALLE verfügbaren Meta Ads Insights... (Das kann 30-60 Sekunden dauern)"):
        try:
            insights = st.session_state.meta_client.fetch_comprehensive_insights(
                days=days,
                level=level
            )

            # DEBUG OUTPUT
            st.markdown("### 🐛 DEBUG INFO")
            st.code(f"""
Level: {level}
Days: {days}
Total Datasets Returned: {len(insights) if insights else 0}

Dataset Details:
""")

            if insights:
                # Check for error
                if 'error' in insights:
                    st.error("❌ FEHLER beim Fetch von Meta API!")
                    error_df = insights['error']
                    if not error_df.empty:
                        st.code(f"Error: {error_df.iloc[0]['error_message']}")
                        with st.expander("🐛 Full Traceback"):
                            st.code(error_df.iloc[0]['traceback'])
                    return

                for name, df in insights.items():
                    st.code(f"{name}: {len(df)} rows, {len(df.columns) if not df.empty else 0} columns")
                    if not df.empty:
                        st.code(f"Columns: {list(df.columns)[:15]}")
                        st.code(f"Sample data (first row):\n{df.head(1).to_dict('records')}")
            else:
                st.error("❌ insights is None or empty!")

        except Exception as e:
            st.error(f"❌ EXCEPTION beim Fetch: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            insights = {}

    if not insights or all(df.empty for df in insights.values()):
        st.warning("Keine Daten verfügbar für den gewählten Zeitraum. Prüfe ob Ads im gewählten Zeitraum aktiv waren.")
        return

    # Success message with details
    non_empty_datasets = [name for name, df in insights.items() if not df.empty]
    empty_datasets = [name for name, df in insights.items() if df.empty]

    st.success(f"✅ {len(non_empty_datasets)} Breakdown-Datensätze geladen!")

    # Show detailed breakdown info
    with st.expander("📋 Geladene Datensätze - Details", expanded=False):
        if non_empty_datasets:
            st.markdown("**✅ Verfügbare Datensätze:**")
            for name in non_empty_datasets:
                row_count = len(insights[name])
                st.markdown(f"- **{name}**: {row_count} Zeilen")

        if empty_datasets:
            st.markdown("**⚠️ Leere Datensätze (keine Daten für diesen Level/Zeitraum):**")
            for name in empty_datasets:
                st.markdown(f"- {name}")

            if level != 'ad':
                st.info(f"""
                **💡 Tipp:** Du hast '{level.upper()}'-Level gewählt.

                Viele Breakdowns (Demographics, Geographic, Placements) funktionieren am besten auf **AD-LEVEL**.

                Versuche es nochmal mit "Ad-Level" für vollständige Daten!
                """)

    # Helper function to extract actions - GLOBAL für alle Tabs!
    def extract_leads_from_actions(actions):
        if isinstance(actions, list):
            for action in actions:
                if isinstance(action, dict) and action.get('action_type') == 'lead':
                    return int(action.get('value', 0))
        return 0

    # Display insights in tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "👥 Demographics",
        "🌍 Geographic",
        "📱 Placements",
        "💻 Devices",
        "🕐 Hourly",
        "📊 Base Metrics"
    ])

    with tab1:
        st.markdown("### 👥 Demografische Insights")

        # AGE
        if 'demographics_age' in insights and not insights['demographics_age'].empty:
            st.markdown("#### Alter-Verteilung")
            age_df = insights['demographics_age']

            # Process actions
            if 'actions' in age_df.columns:
                age_df['leads_extracted'] = age_df['actions'].apply(extract_leads_from_actions)
            else:
                age_df['leads_extracted'] = 0

            # Group by age
            if 'age' in age_df.columns:
                age_summary = age_df.groupby('age').agg({
                    'spend': 'sum',
                    'impressions': 'sum',
                    'reach': 'sum',
                    'clicks': 'sum',
                    'leads_extracted': 'sum'
                }).reset_index()

                age_summary['cpl'] = age_summary['spend'] / age_summary['leads_extracted'].replace(0, 1)
                age_summary['ctr'] = (age_summary['clicks'] / age_summary['impressions'].replace(0, 1)) * 100

                # Sort by spend
                age_summary = age_summary.sort_values('spend', ascending=False)

                st.dataframe(
                    age_summary[[col for col in ['age', 'spend', 'impressions', 'reach', 'clicks', 'leads_extracted', 'cpl', 'ctr'] if col in age_summary.columns]],
                    use_container_width=True,
                    hide_index=True
                )

                # Chart
                import plotly.express as px
                fig = px.bar(age_summary, x='age', y='spend', title='Spend by Age Group')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Keine Age-Daten verfügbar")
        else:
            st.info("Keine Age-Daten verfügbar")

        st.markdown("---")

        # GENDER
        if 'demographics_gender' in insights and not insights['demographics_gender'].empty:
            st.markdown("#### Geschlechter-Verteilung")
            gender_df = insights['demographics_gender']

            if 'actions' in gender_df.columns:
                gender_df['leads_extracted'] = gender_df['actions'].apply(extract_leads_from_actions)
            else:
                gender_df['leads_extracted'] = 0

            if 'gender' in gender_df.columns:
                gender_summary = gender_df.groupby('gender').agg({
                    'spend': 'sum',
                    'impressions': 'sum',
                    'reach': 'sum',
                    'clicks': 'sum',
                    'leads_extracted': 'sum'
                }).reset_index()

                gender_summary['cpl'] = gender_summary['spend'] / gender_summary['leads_extracted'].replace(0, 1)
                gender_summary['ctr'] = (gender_summary['clicks'] / gender_summary['impressions'].replace(0, 1)) * 100

                st.dataframe(
                    gender_summary[[col for col in ['gender', 'spend', 'impressions', 'reach', 'clicks', 'leads_extracted', 'cpl', 'ctr'] if col in gender_summary.columns]],
                    use_container_width=True,
                    hide_index=True
                )

                # Pie chart
                fig = px.pie(gender_summary, values='spend', names='gender', title='Spend by Gender')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Keine Gender-Daten verfügbar")
        else:
            st.info("Keine Gender-Daten verfügbar")

        st.markdown("---")

        # AGE + GENDER
        if 'demographics_age_gender' in insights and not insights['demographics_age_gender'].empty:
            st.markdown("#### Alter + Geschlecht (Kombiniert)")
            age_gender_df = insights['demographics_age_gender']

            if 'actions' in age_gender_df.columns:
                age_gender_df['leads_extracted'] = age_gender_df['actions'].apply(extract_leads_from_actions)
            else:
                age_gender_df['leads_extracted'] = 0

            if 'age' in age_gender_df.columns and 'gender' in age_gender_df.columns:
                age_gender_df['segment'] = age_gender_df['age'].astype(str) + ' - ' + age_gender_df['gender'].astype(str)

                age_gender_summary = age_gender_df.groupby('segment').agg({
                    'spend': 'sum',
                    'impressions': 'sum',
                    'clicks': 'sum',
                    'leads_extracted': 'sum'
                }).reset_index()

                age_gender_summary['cpl'] = age_gender_summary['spend'] / age_gender_summary['leads_extracted'].replace(0, 1)

                # Sort by leads
                age_gender_summary = age_gender_summary.sort_values('leads_extracted', ascending=False)

                st.dataframe(
                    age_gender_summary[[col for col in ['segment', 'spend', 'impressions', 'clicks', 'leads_extracted', 'cpl'] if col in age_gender_summary.columns]],
                    use_container_width=True,
                    hide_index=True
                )

                # Heatmap-style bar chart
                fig = px.bar(age_gender_summary.head(15), x='segment', y='leads_extracted',
                             title='Top 15 Segments by Leads', color='cpl')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Keine Age+Gender-Daten verfügbar für diesen Zeitraum")
        else:
            st.info("Keine Age+Gender-Daten verfügbar für diesen Zeitraum")

    with tab2:
        st.markdown("### 🌍 Geografische Insights")

        # COUNTRY
        if 'geographic_country' in insights and not insights['geographic_country'].empty:
            st.markdown("#### Länder-Verteilung")
            country_df = insights['geographic_country']

            if 'actions' in country_df.columns:
                country_df['leads_extracted'] = country_df['actions'].apply(extract_leads_from_actions)
            else:
                country_df['leads_extracted'] = 0

            if 'country' in country_df.columns:
                country_summary = country_df.groupby('country').agg({
                    'spend': 'sum',
                    'impressions': 'sum',
                    'reach': 'sum',
                    'clicks': 'sum',
                    'leads_extracted': 'sum'
                }).reset_index()

                country_summary['cpl'] = country_summary['spend'] / country_summary['leads_extracted'].replace(0, 1)

                country_summary = country_summary.sort_values('spend', ascending=False)

                st.dataframe(
                    country_summary.head(20),
                    use_container_width=True,
                    hide_index=True
                )

                fig = px.bar(country_summary.head(10), x='country', y='spend', title='Top 10 Countries by Spend')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Keine Country-Daten verfügbar für diesen Zeitraum")
        else:
            st.info("Keine Country-Daten verfügbar für diesen Zeitraum")

        st.markdown("---")

        # REGION
        if 'geographic_region' in insights and not insights['geographic_region'].empty:
            st.markdown("#### Regionen-Verteilung")
            region_df = insights['geographic_region']

            if 'actions' in region_df.columns:
                region_df['leads_extracted'] = region_df['actions'].apply(extract_leads_from_actions)
            else:
                region_df['leads_extracted'] = 0

            if 'region' in region_df.columns:
                region_summary = region_df.groupby('region').agg({
                    'spend': 'sum',
                    'impressions': 'sum',
                    'clicks': 'sum',
                    'leads_extracted': 'sum'
                }).reset_index()

                region_summary['cpl'] = region_summary['spend'] / region_summary['leads_extracted'].replace(0, 1)

                region_summary = region_summary.sort_values('spend', ascending=False)

                st.dataframe(
                    region_summary.head(20),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Keine Region-Daten verfügbar für diesen Zeitraum")
        else:
            st.info("Keine Region-Daten verfügbar für diesen Zeitraum")

    with tab3:
        st.markdown("### 📱 Plattformen & Placements")

        if 'placements' in insights and not insights['placements'].empty:
            placement_df = insights['placements']

            if 'actions' in placement_df.columns:
                placement_df['leads_extracted'] = placement_df['actions'].apply(extract_leads_from_actions)
            else:
                placement_df['leads_extracted'] = 0

            # Group by platform and position
            if 'publisher_platform' in placement_df.columns and 'platform_position' in placement_df.columns:
                placement_df['placement'] = placement_df['publisher_platform'].astype(str) + ' - ' + placement_df['platform_position'].astype(str)

                placement_summary = placement_df.groupby('placement').agg({
                    'spend': 'sum',
                    'impressions': 'sum',
                    'clicks': 'sum',
                    'leads_extracted': 'sum'
                }).reset_index()

                placement_summary['cpl'] = placement_summary['spend'] / placement_summary['leads_extracted'].replace(0, 1)
                placement_summary['ctr'] = (placement_summary['clicks'] / placement_summary['impressions'].replace(0, 1)) * 100

                placement_summary = placement_summary.sort_values('spend', ascending=False)

                st.dataframe(
                    placement_summary,
                    use_container_width=True,
                    hide_index=True
                )

                # Chart
                fig = px.bar(placement_summary.head(10), x='placement', y='spend',
                             title='Top 10 Placements by Spend', color='cpl')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Keine Placement-Daten verfügbar für diesen Zeitraum")
        else:
            st.info("Keine Placement-Daten verfügbar für diesen Zeitraum")

    with tab4:
        st.markdown("### 💻 Geräte-Insights")

        if 'devices' in insights and not insights['devices'].empty:
            device_df = insights['devices']

            if 'actions' in device_df.columns:
                device_df['leads_extracted'] = device_df['actions'].apply(extract_leads_from_actions)
            else:
                device_df['leads_extracted'] = 0

            if 'impression_device' in device_df.columns:
                device_summary = device_df.groupby('impression_device').agg({
                    'spend': 'sum',
                    'impressions': 'sum',
                    'clicks': 'sum',
                    'leads_extracted': 'sum'
                }).reset_index()

                device_summary['cpl'] = device_summary['spend'] / device_summary['leads_extracted'].replace(0, 1)
                device_summary['ctr'] = (device_summary['clicks'] / device_summary['impressions'].replace(0, 1)) * 100

                device_summary = device_summary.sort_values('spend', ascending=False)

                st.dataframe(
                    device_summary,
                    use_container_width=True,
                    hide_index=True
                )

                fig = px.pie(device_summary, values='spend', names='impression_device', title='Spend by Device')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Keine Device-Daten verfügbar für diesen Zeitraum")
        else:
            st.info("Keine Device-Daten verfügbar für diesen Zeitraum")

    with tab5:
        st.markdown("### 🕐 Tageszeit-Analyse")

        if 'hourly' in insights and not insights['hourly'].empty:
            hourly_df = insights['hourly']

            if 'actions' in hourly_df.columns:
                hourly_df['leads_extracted'] = hourly_df['actions'].apply(extract_leads_from_actions)
            else:
                hourly_df['leads_extracted'] = 0

            if 'hourly_stats_aggregated_by_advertiser_time_zone' in hourly_df.columns:
                hourly_df['hour'] = hourly_df['hourly_stats_aggregated_by_advertiser_time_zone'].astype(str)

                hourly_summary = hourly_df.groupby('hour').agg({
                    'spend': 'sum',
                    'impressions': 'sum',
                    'clicks': 'sum',
                    'leads_extracted': 'sum'
                }).reset_index()

                hourly_summary['cpl'] = hourly_summary['spend'] / hourly_summary['leads_extracted'].replace(0, 1)

                st.dataframe(
                    hourly_summary,
                    use_container_width=True,
                    hide_index=True
                )

                fig = px.line(hourly_summary, x='hour', y='spend', title='Spend by Hour of Day')
                st.plotly_chart(fig, use_container_width=True)

                fig2 = px.line(hourly_summary, x='hour', y='leads_extracted', title='Leads by Hour of Day')
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Keine Hourly-Daten verfügbar für diesen Zeitraum")
        else:
            st.info("Keine Hourly-Daten verfügbar für diesen Zeitraum")

    with tab6:
        st.markdown("### 📊 Basis-Metriken (ohne Breakdowns)")

        if 'base' in insights and not insights['base'].empty:
            base_df = insights['base']

            if 'actions' in base_df.columns:
                base_df['leads_extracted'] = base_df['actions'].apply(extract_leads_from_actions)
            else:
                base_df['leads_extracted'] = 0

            # Show summary - SAFE conversion with error handling
            try:
                total_spend = float(base_df['spend'].sum()) if 'spend' in base_df.columns and not base_df['spend'].isna().all() else 0.0
            except (ValueError, TypeError):
                total_spend = 0.0

            try:
                total_impressions = int(base_df['impressions'].sum()) if 'impressions' in base_df.columns and not base_df['impressions'].isna().all() else 0
            except (ValueError, TypeError):
                total_impressions = 0

            try:
                total_clicks = int(base_df['clicks'].sum()) if 'clicks' in base_df.columns and not base_df['clicks'].isna().all() else 0
            except (ValueError, TypeError):
                total_clicks = 0

            try:
                total_leads = int(base_df['leads_extracted'].sum()) if 'leads_extracted' in base_df.columns and not base_df['leads_extracted'].isna().all() else 0
            except (ValueError, TypeError):
                total_leads = 0

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Spend", f"€{total_spend:,.2f}" if total_spend > 0 else "€0.00")
            with col2:
                st.metric("Impressions", f"{total_impressions:,}")
            with col3:
                st.metric("Clicks", f"{total_clicks:,}")
            with col4:
                st.metric("Leads", f"{total_leads:,}")

            # Show base table
            display_cols = [col for col in ['ad_name', 'spend', 'impressions', 'clicks', 'leads_extracted', 'ctr', 'cpc', 'cpm']
                           if col in base_df.columns]

            st.dataframe(
                base_df[display_cols],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Keine Base-Daten verfügbar für diesen Zeitraum")


def render_settings():
    """Render settings page"""
    st.markdown("## ⚙️ Settings")

    st.markdown("### 🤖 AI Provider")
    st.info("**Google Gemini 2.5 Flash** - Aktiv ✅")

    st.markdown("---")

    st.markdown("### 🔑 API Status")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Google Gemini API**")
        if Config.is_configured('GOOGLE_API_KEY'):
            st.success("✅ Konfiguriert")
        else:
            st.error("❌ Nicht konfiguriert")

    with col2:
        st.markdown("**Meta Ads API**")
        if Config.is_configured('META_ACCESS_TOKEN'):
            st.success("✅ Konfiguriert")
        else:
            st.info("Nicht konfiguriert")

    st.markdown("---")

    # Test connection
    if st.button("🔍 Test API Connections"):
        with st.spinner("Teste Verbindungen..."):
            # Test Google Gemini
            try:
                test_analysis = st.session_state.ai_analyzer._generate_content(
                    "Sage nur 'API funktioniert' ohne weitere Erklärung."
                )
                if "funktioniert" in test_analysis.lower() or "api" in test_analysis.lower():
                    st.success("✅ Google Gemini API: Funktioniert")
                else:
                    st.warning(f"⚠️ Google Gemini API: Unerwartete Antwort")
            except Exception as e:
                st.error(f"Google Gemini API Fehler: {str(e)}")

            # Test Meta API
            if st.session_state.meta_client.api_initialized:
                st.success("✅ Meta Ads API: Initialisiert")
            else:
                st.info("Meta Ads API: Nicht konfiguriert")

    st.markdown("---")

    st.markdown("### 📋 Konfiguration")
    st.code(f"""
Company Name: {Config.get('COMPANY_NAME', 'Not set')}
Report Author: {Config.get('REPORT_AUTHOR', 'Not set')}
Email: {Config.get('REPORT_AUTHOR_EMAIL', 'Not set')}
Website: {Config.get('REPORT_AUTHOR_WEBSITE', 'Not set')}
    """)

    st.markdown("---")

    st.markdown("### ℹ️ Über Meta Ads Autopilot")
    st.info("""
    **Version:** 1.0.0
    **AI Provider:** Google Gemini 2.5 Flash
    **Author:** Brandea GbR

    Dieses Dashboard bietet AI-powered Insights für deine Meta Ads Kampagnen.
    """)


def main():
    """Main application"""
    # Initialize
    init_session_state()

    # Render sidebar and get selected page
    page = render_sidebar()

    # Render selected page
    if page == "🏠 Home":
        render_home_professional(st.session_state.meta_client)
    elif page == "📊 Weekly Report":
        render_weekly_report()
    elif page == "📈 Monthly Report":
        render_monthly_report()
    elif page == "🎯 Ad Performance":
        render_ad_performance()
    elif page == "📞 Leads Dashboard":
        render_leads_dashboard()
    elif page == "💡 Content Strategy":
        render_content_strategy()
    elif page == "💬 AI Chat Assistant":
        render_ai_chat()
    elif page == "🔬 Advanced Insights":
        render_advanced_insights_professional(st.session_state.meta_client)
    elif page == "⚙️ Settings":
        render_settings()


if __name__ == "__main__":
    main()
