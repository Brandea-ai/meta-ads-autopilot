# 🚀 PRODUCTION SETUP - Meta Ads Autopilot

## ✅ SCHRITT 1: Streamlit Cloud Secrets konfigurieren

### 1.1 Gehe zu Streamlit Cloud
```
https://share.streamlit.io/
```

### 1.2 Wähle deine App
- **App Name:** meta-ads-autopilot
- Klicke auf die App

### 1.3 Öffne Settings
- Rechts oben: **⋮ Menu** → **Settings**
- Links: **Secrets**

### 1.4 Kopiere KOMPLETTEN Inhalt von STREAMLIT_SECRETS.toml

**Öffne auf deinem Desktop:**
```
~/Desktop/meta-ads-autopilot/STREAMLIT_SECRETS.toml
```

**Kopiere ALLES** (Cmd+A, Cmd+C)

**Füge ein in Streamlit Cloud Secrets** (Cmd+V)

**Klicke:** **Save**

✅ **App startet automatisch neu!**

---

## ✅ SCHRITT 2: Deployment testen

### 2.1 Warte 2-3 Minuten
App baut sich neu mit echten API-Credentials

### 2.2 Öffne deine App
```
https://meta-ads-autopilot-[deine-id].streamlit.app
```

### 2.3 Test: Settings Page
1. Gehe zu **"⚙️ Settings"**
2. Klicke **"🔍 Test API Connections"**

**Erwartetes Ergebnis:**
```
✅ Google Gemini API: Funktioniert
✅ Meta Ads API: Initialisiert
```

### 2.4 Test: Echte Daten
1. Gehe zu **"🏠 Home"**
2. Du solltest sehen:
   - ✅ Echte Kampagnen von CarCenter Landshut
   - ✅ Echte Spend-Zahlen
   - ✅ Echte Leads & CPL

---

## 🎯 FEATURES TESTEN

### Feature 1: Weekly Report
1. **"📊 Weekly Report"**
2. Wähle Zeitraum: 7 Tage
3. **"🤖 Analyze & Generate Report"**
4. Warte 10-20 Sekunden
5. Ergebnis: AI-Analyse deiner echten Kampagnen!

### Feature 2: Ad Performance
1. **"🎯 Ad Performance"**
2. Siehst du deine echten Ads?
3. Klicke auf eine Ad
4. **"Get AI Analysis"**
5. Ergebnis: Detaillierte Ad-Analyse!

### Feature 3: Content Strategy
1. **"💡 Content Strategy"**
2. Wähle Strategie: z.B. "FOMO"
3. **"Generate New Ideas"**
4. Ergebnis: 5 Post-Ideen, 3 Reel-Konzepte!

### Feature 4: PDF Report
1. **"📊 Weekly Report"**
2. Nach Analyse fertig:
3. **"📄 Download PDF Report"**
4. Ergebnis: Professional PDF mit Branding!

---

## 🔒 SICHERHEIT - Production Best Practices

### ✅ BEREITS KONFIGURIERT:

1. **API Keys nicht im Code**
   - ✅ Alle Keys in .env und Streamlit Secrets
   - ✅ .env ist in .gitignore
   - ✅ Keine Keys im GitHub Repository

2. **Access Control**
   - ✅ Meta Token hat minimale Permissions
   - ✅ Nur ads_read, ads_management, business_management

3. **Error Handling**
   - ✅ Graceful degradation bei API-Fehlern
   - ✅ Logging aktiviert
   - ✅ User-friendly Fehlermeldungen

4. **Cache System**
   - ✅ 1h Cache für API-Calls
   - ✅ Reduziert API-Kosten
   - ✅ Verbesserte Performance

---

## 📊 MONITORING & MAINTENANCE

### Tägliche Checks (automatisch):
- ✅ API-Verbindung funktioniert
- ✅ Cache wird aktualisiert
- ✅ Streamlit Cloud läuft

### Wöchentliche Tasks:
- [ ] Generierte Reports prüfen
- [ ] AI-Analyse-Qualität checken
- [ ] User-Feedback sammeln

### Monatliche Tasks:
- [ ] Access Token Gültigkeit prüfen
- [ ] API-Limits checken
- [ ] Performance-Optimierungen

---

## 🆘 TROUBLESHOOTING

### Problem: "Meta API Connection Failed"

**Mögliche Ursachen:**
1. Token abgelaufen → Neu generieren
2. Ad Account ID falsch → Prüfen
3. Permissions fehlen → In Developer Console prüfen

**Fix:**
```bash
# Neue Secrets in Streamlit Cloud eintragen
# App neu starten
```

### Problem: "No campaigns found"

**Mögliche Ursachen:**
1. Ad Account hat keine aktiven Kampagnen
2. Token hat keinen Zugriff auf Account
3. Falscher Ad Account ausgewählt

**Fix:**
- Prüfe in Business Manager: https://business.facebook.com/
- Verifiziere Ad Account ID
- Prüfe Token-Permissions

### Problem: "Google Gemini API Error"

**Mögliche Ursachen:**
1. API Key falsch
2. Generative Language API nicht aktiviert
3. Quota überschritten

**Fix:**
- Check API Key: https://makersuite.google.com/app/apikey
- Aktiviere API: https://console.cloud.google.com/

---

## 📈 NÄCHSTE SCHRITTE

### Sofort verfügbar:
- ✅ Weekly Reports für Kunden
- ✅ Ad Performance Monitoring
- ✅ Content Strategy Generation
- ✅ PDF Reports

### Ausbau-Möglichkeiten:
- [ ] Email-Automation (wöchentliche Reports)
- [ ] Slack-Integration (Alerts)
- [ ] A/B Testing Features
- [ ] Budget Optimizer
- [ ] Multi-Account Management

---

## 📞 SUPPORT

**Bei Problemen:**
- Email: info@brandea.de
- GitHub Issues: https://github.com/Brandea-ai/meta-ads-autopilot/issues

**Dokumentation:**
- Setup Guide: SETUP_INSTRUCTIONS.md
- Meta API Setup: META_API_SETUP.md
- Project Vision: PROJECT_IDEA.md

---

## ✅ PRODUCTION CHECKLIST

- [ ] Streamlit Cloud Secrets konfiguriert
- [ ] API Connections getestet (beide ✅)
- [ ] Echte Kampagnen-Daten sichtbar
- [ ] Weekly Report funktioniert
- [ ] PDF Generation funktioniert
- [ ] Content Strategy funktioniert
- [ ] Ad Performance Dashboard funktioniert

**Sobald alle ✅ → PRODUCTION READY! 🚀**

---

**Entwickelt von Brandea GbR**
**Powered by Google Gemini AI**
