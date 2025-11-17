# Meta Ads Autopilot 🚀

AI-powered Performance Dashboard für Meta Ads mit automatischen Reports powered by **Google Gemini 2.5 Flash**.

![Dashboard Preview](https://img.shields.io/badge/AI-Google%20Gemini-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red)

## 🎯 Features

### 📊 Performance Analytics
- **Real-time Meta Ads Tracking** - Live Daten von Facebook Business API
- **AI-powered Insights** - Intelligente Analysen durch Google Gemini
- **Automatische Reports** - Wöchentliche und monatliche PDF-Reports
- **Visual Dashboards** - Interactive Plotly Charts

### 🤖 AI-Funktionen
- **Weekly Performance Analysis** - KI-generierte Zusammenfassungen
- **Content Strategy Generator** - Neue Ad-Ideen basierend auf Top Performern
- **Single Ad Deep Dive** - Detaillierte Analyse einzelner Ads
- **Automated Recommendations** - Priorisierte Action Items

### 📈 Metrics & KPIs
- Cost per Lead (CPL)
- Hook Rate & Hold Rate
- Ad Fatigue Detection
- Frequency Analysis
- Campaign Performance
- ROI Tracking

## 🚀 Quick Start

### 1. Installation

```bash
# Repository klonen
git clone https://github.com/[YOUR_USERNAME]/meta-ads-autopilot.git
cd meta-ads-autopilot

# Virtual Environment erstellen (empfohlen)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# oder
venv\\Scripts\\activate  # Windows

# Dependencies installieren
pip install -r requirements.txt
```

### 2. Konfiguration

```bash
# .env Datei erstellen
cp .env.example .env

# .env bearbeiten und Keys eintragen:
# - GOOGLE_API_KEY (erforderlich)
# - META_ACCESS_TOKEN (optional, sonst Mock-Daten)
# - META_AD_ACCOUNT_ID (optional)
```

### 3. Dashboard starten

```bash
streamlit run dashboard.py
```

Dashboard öffnet sich automatisch unter `http://localhost:8501`

## 🔑 API Keys Setup

### Google Gemini API (Erforderlich)

1. Gehe zu [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Erstelle neuen API Key
3. Kopiere Key in `.env` als `GOOGLE_API_KEY`
4. Aktiviere "Generative Language API" in Google Cloud Console

### Meta Ads API (Optional)

1. Gehe zu [Meta for Developers](https://developers.facebook.com/)
2. Erstelle neue App
3. Füge "Marketing API" hinzu
4. Generiere Access Token
5. Kopiere Token in `.env` als `META_ACCESS_TOKEN`

**Hinweis:** Ohne Meta API werden automatisch Mock-Daten verwendet für Testing.

## 📁 Projekt-Struktur

```
meta-ads-autopilot/
├── dashboard.py              # Main Streamlit App
├── config.py                 # Configuration Management
├── system_prompts.py         # AI Prompts
├── requirements.txt          # Python Dependencies
├── .env                      # Environment Variables
├── .streamlit/
│   └── config.toml          # Streamlit Config
├── src/
│   ├── meta_ads_client.py   # Facebook API Client
│   ├── ai_analyzer.py       # Google Gemini Integration
│   ├── pdf_generator.py     # PDF Report Generator
│   ├── data_processor.py    # Metrics Calculation
│   └── visualizations.py    # Plotly Charts
├── data/
│   └── cache/               # API Response Cache
├── reports/                 # Generated PDF Reports
└── assets/                  # Images & Styles
```

## 📖 Verwendung

### Home Dashboard
- Übersicht über aktuelle Kampagnen-Performance
- Quick Stats: Spend, Leads, CPL, Active Campaigns
- Letzte generierte Reports

### Weekly Report
1. Zeitraum wählen (7, 14, 30 Tage)
2. "Analyze & Generate Report" klicken
3. AI-Analyse wird generiert
4. Download als PDF möglich

### Ad Performance
- Filterable Tabelle aller Ads
- Performance Score (0-100)
- Ad Fatigue Detection
- Single Ad Deep Dive mit AI-Analyse

### Content Strategy
- Wähle Strategie (FOMO, Loss Aversion, etc.)
- Generiere neue Content-Ideen
- Basierend auf Top Performern
- Export als Markdown

### Settings
- API Status Check
- Connection Tests
- Konfigurationsübersicht

## 🎨 Customization

### Company Branding

In `.env`:
```env
COMPANY_NAME=Dein Firmenname
REPORT_AUTHOR=Deine Agentur
REPORT_AUTHOR_EMAIL=deine@email.de
REPORT_AUTHOR_WEBSITE=www.deine-website.de
```

### Logo hinzufügen

Platziere dein Logo als `brandea_logo.png` in `assets/`

### Prompts anpassen

Bearbeite `system_prompts.py` für Custom AI-Analysen

## 🌐 Deployment auf Streamlit Cloud

1. Push zu GitHub
2. Gehe zu [share.streamlit.io](https://share.streamlit.io)
3. "New app" → Repository auswählen
4. Secrets in App Settings hinzufügen:

```toml
GOOGLE_API_KEY = "your_key_here"
META_ACCESS_TOKEN = "your_token_here"
META_AD_ACCOUNT_ID = "act_your_id"
COMPANY_NAME = "Your Company"
```

5. Deploy!

## 🛠️ Entwicklung

### Virtual Environment Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Testing

```bash
# Dashboard starten
streamlit run dashboard.py

# API Connection testen (Settings Page)
```

### Code Quality

- Type Hints vorhanden
- Docstrings für alle Funktionen
- Error Handling implementiert
- Logging aktiviert

## 📊 Features Roadmap

- [x] Google Gemini Integration
- [x] Meta Ads API Client
- [x] PDF Report Generator
- [x] Interactive Dashboard
- [x] Content Strategy Generator
- [ ] Email Automation
- [ ] Slack Integration
- [ ] Advanced A/B Testing
- [ ] Budget Optimizer
- [ ] Automated Bid Management

## 🐛 Troubleshooting

### "Google Gemini API Error 403"
→ Aktiviere "Generative Language API" in Google Cloud Console

### "Meta API Connection Failed"
→ Check Access Token validity & Permissions

### "No data available"
→ System nutzt automatisch Mock-Daten wenn API nicht konfiguriert

### "PDF Generation Failed"
→ Install system dependencies: `brew install cairo pango` (macOS)

## 📝 License

MIT License - siehe LICENSE Datei

## 👥 Support

- **Email:** info@brandea.de
- **Website:** www.brandea.de
- **Issues:** [GitHub Issues](https://github.com/[USERNAME]/meta-ads-autopilot/issues)

## 🙏 Credits

- **AI:** Google Gemini 2.5 Flash
- **Framework:** Streamlit
- **Charts:** Plotly
- **PDF:** ReportLab
- **Meta API:** Facebook Business SDK

---

**Built with ❤️ by Brandea GbR**

Powered by Google Gemini AI 🤖
