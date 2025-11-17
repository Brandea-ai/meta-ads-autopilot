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


def render_sidebar():
    """Render sidebar navigation"""
    st.sidebar.markdown("# 🚀 Meta Ads Autopilot")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Home", "📊 Weekly Report", "📈 Monthly Report",
         "🎯 Ad Performance", "💡 Content Strategy", "⚙️ Settings"]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 AI Provider")
    st.sidebar.info("Google Gemini 2.5 Flash")

    company_name = Config.get('COMPANY_NAME', 'Your Company')
    st.sidebar.markdown(f"### 🏢 {company_name}")

    return page


def render_home():
    """Render home page"""
    st.markdown('<div class="main-header">Meta Ads Autopilot 🚀</div>', unsafe_allow_html=True)
    st.markdown("### AI-powered Performance Dashboard mit Google Gemini")

    st.markdown("---")

    # Fetch current month data
    with st.spinner("Lade aktuelle Daten..."):
        campaign_df = st.session_state.meta_client.fetch_campaign_data(days=30)
        ad_df = st.session_state.meta_client.fetch_ad_performance(days=30)

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

    # Date range picker
    col1, col2 = st.columns([2, 1])

    with col1:
        days = st.selectbox(
            "Zeitraum wählen",
            [7, 14, 30],
            format_func=lambda x: f"Letzte {x} Tage"
        )

    with col2:
        analyze_button = st.button("🤖 Analyze & Generate Report", type="primary", use_container_width=True)

    st.markdown("---")

    if analyze_button:
        with st.spinner("🔄 Lade Meta Ads Daten..."):
            campaign_df = st.session_state.meta_client.fetch_campaign_data(days=days)
            ad_df = st.session_state.meta_client.fetch_ad_performance(days=days)

        if campaign_df.empty and ad_df.empty:
            st.error("Keine Daten verfügbar für den gewählten Zeitraum")
            return

        # Calculate metrics
        campaign_df = st.session_state.data_processor.calculate_metrics(campaign_df)
        ad_df = st.session_state.data_processor.calculate_metrics(ad_df)
        ad_df = st.session_state.data_processor.detect_ad_fatigue(ad_df)

        with st.spinner("🤖 Google Gemini analysiert Performance..."):
            date_range = f"{datetime.now() - timedelta(days=days):%d.%m.%Y} - {datetime.now():%d.%m.%Y}"
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
                st.dataframe(
                    top_performers[['ad_name', 'spend', 'leads', 'cpl', 'hook_rate', 'hold_rate', 'frequency']],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Keine Daten verfügbar")

        with tab4:
            st.markdown("### ⚠️ Underperforming Ads")
            underperformers = st.session_state.data_processor.identify_underperformers(ad_df, 'cpl', 5)

            if not underperformers.empty:
                st.dataframe(
                    underperformers[['ad_name', 'spend', 'leads', 'cpl', 'hook_rate', 'hold_rate', 'frequency']],
                    use_container_width=True,
                    hide_index=True
                )

                # Ad fatigue warnings
                fatigued = ad_df[ad_df['ad_fatigue'] == True]
                if not fatigued.empty:
                    st.warning(f"⚠️ {len(fatigued)} Ads zeigen Anzeichen von Ad Fatigue (Frequency >6)")
            else:
                st.info("Keine Daten verfügbar")

        with tab5:
            st.markdown("### 💡 AI-generierte Empfehlungen")
            st.info("Die Empfehlungen sind im Executive Summary enthalten")

        # PDF Download
        st.markdown("---")
        if st.button("📄 Download PDF Report", type="secondary"):
            with st.spinner("Generiere PDF..."):
                pdf_path = st.session_state.pdf_generator.generate_weekly_report(
                    analysis, campaign_df, ad_df
                )

                with open(pdf_path, 'rb') as f:
                    st.download_button(
                        "📥 Download PDF",
                        f.read(),
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf"
                    )
                st.success(f"✅ PDF erstellt: {os.path.basename(pdf_path)}")


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
            # For demo, we'll use last 30 days vs previous 30 days
            current_month = st.session_state.meta_client.fetch_ad_performance(days=30)
            # In production, you'd fetch previous 30 days specifically

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
            st.dataframe(
                campaign_df[['campaign_name', 'spend', 'leads', 'cpl', 'frequency']],
                use_container_width=True,
                hide_index=True
            )


def render_ad_performance():
    """Render ad performance page"""
    st.markdown("## 🎯 Ad Performance Analysis")

    days = st.selectbox("Zeitraum", [7, 14, 30], index=2)

    with st.spinner("Lade Ad Performance Daten..."):
        ad_df = st.session_state.meta_client.fetch_ad_performance(days=days)

    if ad_df.empty:
        st.warning("Keine Ad-Daten verfügbar")
        return

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

    display_df = filtered_df[['ad_name', 'spend', 'leads', 'cpl', 'hook_rate',
                               'hold_rate', 'frequency', 'performance_score']].copy()

    # Format columns
    display_df['spend'] = display_df['spend'].apply(lambda x: f"€{x:,.2f}")
    display_df['cpl'] = display_df['cpl'].apply(lambda x: f"€{x:.2f}")
    display_df['hook_rate'] = display_df['hook_rate'].apply(lambda x: f"{x:.1f}%")
    display_df['hold_rate'] = display_df['hold_rate'].apply(lambda x: f"{x:.1f}%")
    display_df['frequency'] = display_df['frequency'].apply(lambda x: f"{x:.2f}")
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
            st.warning("⚠️ Nicht konfiguriert (Mock-Daten werden verwendet)")

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
                st.error(f"❌ Google Gemini API Fehler: {str(e)}")

            # Test Meta API
            if st.session_state.meta_client.api_initialized:
                st.success("✅ Meta Ads API: Initialisiert")
            else:
                st.warning("⚠️ Meta Ads API: Nicht konfiguriert (Mock-Modus)")

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
        render_home()
    elif page == "📊 Weekly Report":
        render_weekly_report()
    elif page == "📈 Monthly Report":
        render_monthly_report()
    elif page == "🎯 Ad Performance":
        render_ad_performance()
    elif page == "💡 Content Strategy":
        render_content_strategy()
    elif page == "⚙️ Settings":
        render_settings()


if __name__ == "__main__":
    main()
