# Setup Instructions - Meta Ads Autopilot

Detaillierte Schritt-für-Schritt Anleitung zur Einrichtung des Meta Ads Autopilot Dashboards.

## 📋 Voraussetzungen

- **Python 3.9+** installiert
- **Git** installiert
- **Google Account** für Gemini API
- **Meta Business Account** (optional, für Live-Daten)

---

## 🔧 1. Lokale Installation

### Schritt 1: Repository klonen

```bash
git clone https://github.com/[YOUR_USERNAME]/meta-ads-autopilot.git
cd meta-ads-autopilot
```

### Schritt 2: Virtual Environment erstellen

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Schritt 3: Dependencies installieren

```bash
pip install -r requirements.txt
```

**Bei macOS für PDF-Generierung:**
```bash
brew install cairo pango
```

**Bei Linux (Ubuntu/Debian):**
```bash
sudo apt-get install libcairo2-dev libpango1.0-dev
```

---

## 🔑 2. API Keys Setup

### Google Gemini API (ERFORDERLICH)

#### Schritt 1: API Key erstellen

1. Gehe zu [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Klicke auf "Get API key"
3. Wähle ein Google Cloud Projekt oder erstelle ein neues
4. Kopiere den generierten API Key

#### Schritt 2: Generative Language API aktivieren

1. Gehe zu [Google Cloud Console](https://console.cloud.google.com/)
2. Wähle dein Projekt aus
3. Suche nach "Generative Language API"
4. Klicke auf "Enable" / "Aktivieren"
5. Warte 2-3 Minuten bis Aktivierung abgeschlossen

#### Schritt 3: API Key testen

```bash
# Test-Script ausführen
python3 << 'EOF'
import google.generativeai as genai

genai.configure(api_key='YOUR_API_KEY_HERE')
model = genai.GenerativeModel('gemini-2.5-flash')

response = model.generate_content('Sage nur "API funktioniert"')
print(response.text)
EOF
```

Erwartete Ausgabe: "API funktioniert" oder ähnlich

---

### Meta Ads API (OPTIONAL)

**Hinweis:** Wenn du keine Meta API Keys hast, funktioniert das Dashboard trotzdem mit Mock-Daten!

#### Schritt 1: Facebook App erstellen

1. Gehe zu [Meta for Developers](https://developers.facebook.com/)
2. Klicke auf "My Apps" → "Create App"
3. Wähle "Business" als App Type
4. Fülle App Details aus

#### Schritt 2: Marketing API hinzufügen

1. Im App Dashboard → "Add Product"
2. Wähle "Marketing API"
3. Klicke "Set Up"

#### Schritt 3: Access Token generieren

**Option A: Graph API Explorer (für Testing)**
1. Gehe zu [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Wähle deine App aus
3. Add Permissions:
   - `ads_read`
   - `ads_management`
   - `business_management`
4. Klicke "Generate Access Token"
5. Kopiere Token

**Option B: Langlebiger Token (für Production)**
1. Nutze Graph API Explorer Token
2. Konvertiere zu Long-lived Token:
```bash
curl "https://graph.facebook.com/v18.0/oauth/access_token?\
grant_type=fb_exchange_token&\
client_id=YOUR_APP_ID&\
client_secret=YOUR_APP_SECRET&\
fb_exchange_token=SHORT_LIVED_TOKEN"
```

#### Schritt 4: Ad Account ID finden

1. Gehe zu [Meta Business Suite](https://business.facebook.com/)
2. Settings → Ad Accounts
3. Kopiere Account ID (Format: `act_1234567890`)

---

## ⚙️ 3. Konfiguration

### Schritt 1: .env Datei erstellen

```bash
cp .env.example .env
```

### Schritt 2: .env bearbeiten

Öffne `.env` und füge deine Keys ein:

```env
# Google Gemini API (ERFORDERLICH)
GOOGLE_API_KEY=AIzaSyB...dein_key_hier

# Meta Ads API (OPTIONAL)
META_ACCESS_TOKEN=EAABsb...dein_token_hier
META_AD_ACCOUNT_ID=act_1234567890

# Company Info (Anpassen)
COMPANY_NAME=CarCenter Landshut
REPORT_AUTHOR=Brandea GbR
REPORT_AUTHOR_EMAIL=info@brandea.de
REPORT_AUTHOR_WEBSITE=www.brandea.de
```

### Schritt 3: Konfiguration testen

```bash
streamlit run dashboard.py
```

Im Dashboard:
1. Gehe zu "⚙️ Settings"
2. Klicke "🔍 Test API Connections"
3. Verifiziere dass Google Gemini ✅ funktioniert

---

## 🚀 4. Dashboard starten

### Lokal

```bash
# Virtual Environment aktivieren
source venv/bin/activate  # macOS/Linux
# oder
venv\Scripts\activate     # Windows

# Dashboard starten
streamlit run dashboard.py
```

Dashboard öffnet sich automatisch unter `http://localhost:8501`

### Port ändern (optional)

```bash
streamlit run dashboard.py --server.port 8502
```

---

## 🌐 5. Streamlit Cloud Deployment

### Schritt 1: GitHub Repository erstellen

Wenn noch nicht geschehen:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/[USERNAME]/meta-ads-autopilot.git
git push -u origin main
```

### Schritt 2: Streamlit Cloud Account

1. Gehe zu [share.streamlit.io](https://share.streamlit.io)
2. Login mit GitHub
3. Authorize Streamlit App

### Schritt 3: App deployen

1. Klicke "New app"
2. Repository: `[USERNAME]/meta-ads-autopilot`
3. Branch: `main`
4. Main file: `dashboard.py`
5. Klicke "Deploy"

### Schritt 4: Secrets konfigurieren

1. App Settings → "⚙️ Secrets"
2. Füge hinzu:

```toml
GOOGLE_API_KEY = "AIzaSyB...your_key"
META_ACCESS_TOKEN = "EAABsb...your_token"
META_AD_ACCOUNT_ID = "act_1234567890"
COMPANY_NAME = "Your Company"
REPORT_AUTHOR = "Your Agency"
REPORT_AUTHOR_EMAIL = "your@email.com"
REPORT_AUTHOR_WEBSITE = "www.your-site.com"
```

3. Klicke "Save"
4. App wird automatisch neu gestartet

### Schritt 5: Custom Domain (optional)

Streamlit Cloud bietet URLs wie: `https://your-app.streamlit.app`

---

## 🎨 6. Customization

### Logo hinzufügen

1. Erstelle PNG-Logo (empfohlen: 500x500px)
2. Speichere als `assets/brandea_logo.png`
3. Restart Dashboard

### Farben anpassen

Bearbeite `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FF4B4B"        # Hauptfarbe
backgroundColor = "#FFFFFF"      # Hintergrund
secondaryBackgroundColor = "#F0F2F6"  # Sekundär
textColor = "#262730"           # Text
```

### AI Prompts anpassen

Bearbeite `system_prompts.py`:

```python
WEEKLY_ANALYSIS_PROMPT = """
Dein Custom Prompt hier...
"""
```

---

## 🧪 7. Testing

### Funktionstest

1. **Home Page:**
   - Zeigt Metrics an? ✅
   - Zeigt Top Campaigns/Ads? ✅

2. **Weekly Report:**
   - "Analyze & Generate Report" funktioniert? ✅
   - AI-Analyse wird generiert? ✅
   - PDF Download möglich? ✅

3. **Ad Performance:**
   - Tabelle wird angezeigt? ✅
   - Filter funktionieren? ✅
   - Single Ad Analysis funktioniert? ✅

4. **Content Strategy:**
   - Generate Ideas funktioniert? ✅
   - Export als Markdown? ✅

5. **Settings:**
   - API Status korrekt? ✅
   - Test Connection funktioniert? ✅

---

## 🐛 Troubleshooting

### Problem: "ModuleNotFoundError"

**Lösung:**
```bash
pip install -r requirements.txt
```

### Problem: "Google Gemini API 403 Error"

**Lösung:**
1. Aktiviere "Generative Language API" in Google Cloud Console
2. Warte 2-3 Minuten
3. Teste erneut

### Problem: "Meta API Connection Failed"

**Lösung:**
1. Check ob Access Token noch gültig ist
2. Verifiziere Permissions (`ads_read`, `ads_management`)
3. Check Ad Account ID Format: `act_1234567890`

**Alternative:** Nutze Mock-Daten (lasse META_ACCESS_TOKEN leer)

### Problem: "PDF Generation Failed"

**Lösung macOS:**
```bash
brew install cairo pango
pip install --upgrade reportlab weasyprint
```

**Lösung Linux:**
```bash
sudo apt-get install libcairo2-dev libpango1.0-dev
pip install --upgrade reportlab weasyprint
```

### Problem: "Streamlit Cloud Deployment Failed"

**Lösung:**
1. Check `requirements.txt` ist vollständig
2. Verifiziere Secrets sind gesetzt
3. Check Logs in Streamlit Cloud Dashboard
4. Bei PDF-Problemen: `packages.txt` muss enthalten:
   ```
   libcairo2-dev
   libpango1.0-dev
   ```

### Problem: "No data available"

**Normal!** Wenn Meta API nicht konfiguriert, werden automatisch Mock-Daten verwendet.

---

## 📞 Support

Bei Problemen:

1. **Check Logs:**
   ```bash
   streamlit run dashboard.py --logger.level=debug
   ```

2. **GitHub Issues:**
   https://github.com/[USERNAME]/meta-ads-autopilot/issues

3. **Email Support:**
   info@brandea.de

---

## ✅ Checkliste

- [ ] Python 3.9+ installiert
- [ ] Repository geklont
- [ ] Virtual Environment erstellt
- [ ] Dependencies installiert
- [ ] Google Gemini API Key erstellt
- [ ] Generative Language API aktiviert
- [ ] .env Datei konfiguriert
- [ ] API Connection getestet
- [ ] Dashboard läuft lokal
- [ ] (Optional) Meta API konfiguriert
- [ ] (Optional) Streamlit Cloud Deployment
- [ ] (Optional) Custom Branding hinzugefügt

---

**Viel Erfolg mit Meta Ads Autopilot! 🚀**
