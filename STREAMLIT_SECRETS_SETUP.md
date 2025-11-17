# 🔑 STREAMLIT CLOUD SECRETS SETUP - KRITISCH!

## ⚠️ PROBLEM IDENTIFIZIERT!

**Das Dashboard zeigt MOCK-DATEN weil die Streamlit Cloud Secrets NICHT GESETZT sind!**

## 🎯 LÖSUNG:

### 1. Gehe zu Streamlit Cloud:
https://share.streamlit.io/

### 2. Finde deine App:
"meta-ads-autopilot"

### 3. Klicke auf "⚙️ Settings" (unten rechts oder oben)

### 4. Gehe zu "Secrets"

### 5. Füge DIESE Secrets hinzu:

```toml
META_ACCESS_TOKEN = "EAAbFEASZCKZAcBP1AaeVDhZBPmspU7hZCiwEkmU1iOMZAMmmQNEDKSVWPTMLlV0pHqKIZBqjr917Cya20ZAhpvJqK52GV4ES3UINVWZCiMLYZBwcOXZABKt7Fz16JkboEm0HV0T3ISEkGgdQtrsDpj3nlhtf9OMI8UIii6O2CutbZA7F5s1nRwLdGroQO1DlD6zSUmFSIudoHwdLH7wbf7stDEVFCSuRbLJWUzyRpJn80cg4lqSBQZDZD"

META_AD_ACCOUNT_ID = "act_1136853371968538"

GOOGLE_API_KEY = "AIzaSyBDI7FNodzUvdOOUcAU9rMNSXeVdYCIpG8"

COMPANY_NAME = "CarCenter Landshut"

REPORT_AUTHOR = "Brandea GbR"

REPORT_AUTHOR_EMAIL = "info@brandea.de"

REPORT_AUTHOR_WEBSITE = "www.brandea.de"
```

### 6. Klicke "Save"

### 7. Die App wird **automatisch neu starten**!

---

## ✅ NACH DEM SETUP:

Wenn die Secrets gesetzt sind, wird die App:
- ✅ **ECHTE Daten** von Meta API holen
- ✅ **KEINE Mock-Daten** mehr anzeigen
- ✅ **Alle 70+ Metriken** extrahieren
- ✅ **Demographics/Geographic/Placements** funktionieren (auf Ad-Level)

---

## 🔍 WIE DU PRÜFST OB ES FUNKTIONIERT:

Nach dem Neu-Start der App:

### Test 1: Home Page
- Gehe zu "🏠 Home"
- Schau dir die "Ad Performance Tabelle" an
- **Echte Daten**: Deine echten Ad-Namen (nicht "SUV Video Hook Test A")
- **Mock-Daten**: Testdaten wie "Limousine Static Hero"

### Test 2: Ad Performance Page
- Gehe zu "🎯 Ad Performance"
- Schau dir die Hook Rate an
- **Echte Daten**: 10-25% Hook Rate (realistisch)
- **Mock-Daten**: 93% Hook Rate (unrealistisch!)

### Test 3: Advanced Insights
- Gehe zu "🔬 Advanced Insights"
- Wähle **"Ad-Level"** (WICHTIG!)
- Klicke "🔥 Analysieren"
- **Echte Daten**: Du siehst deine echten Demographics/Placements
- **Mock-Daten**: "⚠️ Keine Age-Daten verfügbar"

---

## 🚨 WICHTIG:

1. **Secrets MÜSSEN in Streamlit Cloud gesetzt werden**
   - Die `.env` Datei wird NICHT auf Streamlit Cloud hochgeladen (aus Sicherheitsgründen)
   - Deshalb brauchst du Secrets!

2. **Ad-Level für Breakdowns**
   - Demographics/Geographic/Placements funktionieren NUR auf Ad-Level
   - Campaign-Level hat keine Breakdowns (Meta API Limitation)

3. **Meta Access Token kann ablaufen**
   - Long-Lived Tokens halten 60 Tage
   - Danach musst du einen neuen Token generieren

---

## 🔄 TOKEN ERNEUERN (falls nötig):

Wenn der Token abgelaufen ist:

1. Gehe zu: https://developers.facebook.com/tools/explorer/
2. Wähle deine App
3. Klicke "Generate Access Token"
4. Wähle Permissions:
   - `ads_read`
   - `business_management`
   - `leads_retrieval`
5. Kopiere den neuen Token
6. Update ihn in Streamlit Cloud Secrets

---

## ✅ CHECKLIST:

- [ ] Streamlit Cloud Secrets gesetzt
- [ ] App neu gestartet
- [ ] Home Page zeigt echte Ad-Namen
- [ ] Ad Performance zeigt realistische Hook Rates
- [ ] Advanced Insights → Ad-Level → Daten sichtbar

Wenn ALLE Punkte ✅ sind: **Du hast echte Daten!**

Wenn irgendwas ❌ ist: Token abgelaufen oder Secrets falsch gesetzt.

---

**Nach dem Setup siehst du:**
- ✅ Echte Campaign-Namen
- ✅ Echte Ad-Namen
- ✅ Realistische Metriken (Hook Rate 10-25%)
- ✅ Echte Demographics (Alter/Geschlecht deiner Zielgruppe)
- ✅ Echte Placements (wo deine Ads laufen)
- ✅ ALLE 70+ Metriken von Meta API
