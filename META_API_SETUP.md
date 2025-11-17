# Meta Ads API Setup Guide

## 🎯 Übersicht

Diese Anleitung zeigt dir Schritt-für-Schritt wie du die Meta Ads API einrichtest.

---

## ✅ Voraussetzungen

- [ ] Meta Business Manager Account (business.facebook.com)
- [ ] Ad Account mit Admin-Rechten
- [ ] Aktive Meta Ads Kampagnen

---

## 📝 SCHRITT 1: Facebook Developer App erstellen

### 1.1 App erstellen

1. Gehe zu: https://developers.facebook.com/apps/
2. Klicke **"Create App"**
3. Wähle **"Business"** als App Type
4. Fülle aus:
   - **App Name:** "Meta Ads Autopilot" (oder dein Name)
   - **App Contact Email:** deine@email.de
   - **Business Account:** Wähle dein Business aus

5. Klicke **"Create App"**

### 1.2 Marketing API hinzufügen

1. Im App Dashboard → **"Add Product"**
2. Suche **"Marketing API"**
3. Klicke **"Set Up"**

---

## 🔑 SCHRITT 2: Access Token generieren

### Option A: Quick Token (für Testing - 2 Monate gültig)

1. Gehe zu: https://developers.facebook.com/tools/explorer/
2. Wähle deine App aus (oben rechts)
3. **Add Permissions:**
   - `ads_read`
   - `ads_management`
   - `business_management`
4. Klicke **"Generate Access Token"**
5. **Kopiere den Token** → Speichere ihn sicher!

**Token Format:** `EAABsb...` (sehr lang, ca. 200+ Zeichen)

---

### Option B: Long-lived Token (für Production - nie ablaufend)

**Schritt 1:** Generiere zuerst einen Short-lived Token (Option A)

**Schritt 2:** Konvertiere zu Long-lived Token:

```bash
# Ersetze:
# YOUR_APP_ID = Deine App ID
# YOUR_APP_SECRET = Dein App Secret (in App Settings → Basic)
# SHORT_LIVED_TOKEN = Token aus Option A

curl "https://graph.facebook.com/v18.0/oauth/access_token?\
grant_type=fb_exchange_token&\
client_id=YOUR_APP_ID&\
client_secret=YOUR_APP_SECRET&\
fb_exchange_token=SHORT_LIVED_TOKEN"
```

**Response:**
```json
{
  "access_token": "EAABsb...",  ← Das ist dein Long-lived Token!
  "token_type": "bearer",
  "expires_in": 5183944  ← ~60 Tage
}
```

---

### Option C: System User Token (für Production - BESTE Option!)

**Vorteile:**
- Nie ablaufend
- Nicht an Person gebunden
- Professional Setup

**Setup:**

1. Gehe zu **Business Settings** (business.facebook.com/settings)
2. **Users → System Users**
3. Klicke **"Add"**
4. Name: "Meta Ads Autopilot Bot"
5. Role: **Admin**
6. Klicke **"Create System User"**

7. **Token generieren:**
   - Klicke auf System User
   - **"Generate New Token"**
   - Wähle deine App
   - Permissions: `ads_read`, `ads_management`, `business_management`
   - **Never Expire** ← Wichtig!
   - Klicke **"Generate Token"**

8. **Kopiere Token** → Speichere sicher!

---

## 🆔 SCHRITT 3: Ad Account ID finden

### Methode 1: Business Manager

1. Gehe zu: https://business.facebook.com/settings/ad-accounts
2. Klicke auf deinen Ad Account
3. Oben siehst du: **"Ad Account ID: 123456789"**
4. Format für API: `act_123456789` (mit "act_" prefix!)

### Methode 2: Ads Manager URL

1. Gehe zu: https://adsmanager.facebook.com/
2. Schaue in der URL: `act=123456789`
3. Deine ID: `act_123456789`

---

## ⚙️ SCHRITT 4: Lokale Konfiguration (.env)

Öffne `/Users/brandea/Desktop/meta-ads-autopilot/.env` und füge ein:

```env
# Google Gemini (bereits konfiguriert)
GOOGLE_API_KEY=AIzaSyBDI7FNodzUvdOOUcAU9rMNSXeVdYCIpG8

# Meta Ads API (NEU)
META_ACCESS_TOKEN=EAABsb...dein_token_hier
META_AD_ACCOUNT_ID=act_123456789

# Company Info
COMPANY_NAME=CarCenter Landshut
REPORT_AUTHOR=Brandea GbR
REPORT_AUTHOR_EMAIL=info@brandea.de
REPORT_AUTHOR_WEBSITE=www.brandea.de
```

---

## 🌐 SCHRITT 5: Streamlit Cloud Secrets

1. Gehe zu: https://share.streamlit.io/
2. Wähle deine App: **meta-ads-autopilot**
3. Klicke **"⚙️ Settings"**
4. Gehe zu **"Secrets"**
5. Füge ein:

```toml
# Google Gemini
GOOGLE_API_KEY = "AIzaSyBDI7FNodzUvdOOUcAU9rMNSXeVdYCIpG8"

# Meta Ads API
META_ACCESS_TOKEN = "EAABsb...dein_token_hier"
META_AD_ACCOUNT_ID = "act_123456789"

# Company Info
COMPANY_NAME = "CarCenter Landshut"
REPORT_AUTHOR = "Brandea GbR"
REPORT_AUTHOR_EMAIL = "info@brandea.de"
REPORT_AUTHOR_WEBSITE = "www.brandea.de"
```

6. Klicke **"Save"**
7. App startet automatisch neu

---

## ✅ SCHRITT 6: Testen

### Lokal testen:

```bash
cd ~/Desktop/meta-ads-autopilot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard.py
```

1. Dashboard öffnet sich
2. Gehe zu **"⚙️ Settings"**
3. Klicke **"🔍 Test API Connections"**
4. Sollte zeigen:
   - ✅ Google Gemini API: Funktioniert
   - ✅ Meta Ads API: Initialisiert

### Live-Daten testen:

1. Gehe zu **"🏠 Home"**
2. Solltest jetzt **echte Kampagnen-Daten** sehen
3. Gehe zu **"📊 Weekly Report"**
4. Klicke **"🤖 Analyze & Generate Report"**
5. AI analysiert deine **echten Kampagnen!**

---

## 🔒 SICHERHEIT: Best Practices

### ✅ DO:
- ✅ Access Token NIEMALS in Git committen
- ✅ `.env` ist in `.gitignore` (bereits konfiguriert)
- ✅ Streamlit Secrets für Production verwenden
- ✅ System User Token für langfristige Nutzung
- ✅ Regelmäßig Token-Permissions prüfen

### ❌ DON'T:
- ❌ Token in Code schreiben
- ❌ Token in Screenshots teilen
- ❌ Token in öffentlichen Repos
- ❌ Token per Email verschicken

---

## 🆘 Troubleshooting

### Problem: "Error Code 190: Invalid OAuth access token"

**Lösung:**
- Token ist abgelaufen → Neu generieren
- Token hat keine Permissions → Permissions hinzufügen
- Token ist falsch kopiert → Nochmal kopieren (ohne Leerzeichen!)

### Problem: "Error Code 100: Invalid parameter"

**Lösung:**
- Ad Account ID falsch → Prüfe Format: `act_123456789`
- Kein Zugriff auf Account → Permissions in Business Manager prüfen

### Problem: "GraphMethodException: Unsupported get request"

**Lösung:**
- API Version veraltet → Update facebook-business package
- Field existiert nicht → Check API Documentation

---

## 📚 Weitere Ressourcen

- **Meta API Docs:** https://developers.facebook.com/docs/marketing-apis
- **Business Manager:** https://business.facebook.com
- **Graph API Explorer:** https://developers.facebook.com/tools/explorer/
- **API Changelog:** https://developers.facebook.com/docs/graph-api/changelog

---

## ✅ Checkliste

- [ ] Facebook Developer App erstellt
- [ ] Marketing API hinzugefügt
- [ ] Access Token generiert
- [ ] Ad Account ID gefunden
- [ ] `.env` konfiguriert
- [ ] Streamlit Cloud Secrets gesetzt
- [ ] Lokal getestet
- [ ] Live-Daten funktionieren

---

**Bei Fragen:** info@brandea.de

**Viel Erfolg! 🚀**
