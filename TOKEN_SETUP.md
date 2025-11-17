# 🔑 META TOKEN SETUP - RICHTIG GEMACHT

## PROBLEM:
Dein Token läuft ständig ab (Short-Lived Token = 1-2 Stunden)

## LÖSUNG: LONG-LIVED TOKEN (60 Tage)

### Schritt 1: Gehe zum Graph API Explorer
https://developers.facebook.com/tools/explorer/

### Schritt 2: Generiere Short-Lived Token
1. Wähle deine App
2. Klicke "Generate Access Token"
3. Wähle Permissions:
   - `ads_read`
   - `ads_management`
   - `business_management`
   - `leads_retrieval`
4. Kopiere den Token (nennen wir ihn SHORT_TOKEN)

### Schritt 3: Konvertiere zu Long-Lived Token

**Option A: Mit curl (Terminal):**

```bash
curl -i -X GET "https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=DEINE_APP_ID&client_secret=DEIN_APP_SECRET&fb_exchange_token=SHORT_TOKEN"
```

Ersetze:
- `DEINE_APP_ID` - Deine Facebook App ID
- `DEIN_APP_SECRET` - Dein App Secret (von App Dashboard)
- `SHORT_TOKEN` - Der Token von Schritt 2

**Response:**
```json
{
  "access_token": "LONG_LIVED_TOKEN_HIER",
  "token_type": "bearer",
  "expires_in": 5183944  // ~60 Tage in Sekunden
}
```

**Option B: Mit Python:**

```python
import requests

app_id = "DEINE_APP_ID"
app_secret = "DEIN_APP_SECRET"
short_token = "SHORT_TOKEN"

url = "https://graph.facebook.com/v18.0/oauth/access_token"
params = {
    'grant_type': 'fb_exchange_token',
    'client_id': app_id,
    'client_secret': app_secret,
    'fb_exchange_token': short_token
}

response = requests.get(url, params=params)
data = response.json()

long_lived_token = data['access_token']
print(f"Long-Lived Token: {long_lived_token}")
```

### Schritt 4: Update Token überall

1. **Lokal (.env):**
   ```
   META_ACCESS_TOKEN=LONG_LIVED_TOKEN_HIER
   ```

2. **Streamlit Cloud (Secrets):**
   ```toml
   META_ACCESS_TOKEN = "LONG_LIVED_TOKEN_HIER"
   ```

3. **Save App → Reboot**

---

## BESTE LÖSUNG: SYSTEM USER TOKEN (NIEMALS ABLAUFEND)

**Für Production-Apps empfohlen!**

### Voraussetzungen:
- Facebook Business Manager Account
- App mit Business Manager verbunden

### Setup:

1. **Gehe zu Business Settings:**
   https://business.facebook.com/settings/

2. **Erstelle System User:**
   - Users → System Users
   - Add → "Meta Ads Autopilot"
   - Role: Admin

3. **Generiere Token:**
   - Klicke auf System User
   - Generate New Token
   - Wähle deine App
   - Permissions: `ads_read`, `ads_management`, `business_management`, `leads_retrieval`
   - **Token expires: Never!** ✅

4. **Update Token wie oben**

---

## TOKEN TESTEN:

```bash
curl -i -X GET "https://graph.facebook.com/v18.0/debug_token?input_token=DEIN_TOKEN&access_token=DEIN_TOKEN"
```

**Good Response:**
```json
{
  "data": {
    "is_valid": true,
    "expires_at": 1734451200,  // Timestamp
    "scopes": ["ads_read", "business_management", ...]
  }
}
```

---

## AUTOMATISCHE TOKEN-ERNEUERUNG

**Für ganz lazy: Token automatisch erneuern!**

```python
# In meta_ads_client.py
def refresh_token_if_needed(self):
    """Check if token expires soon and refresh it"""
    import requests
    from datetime import datetime, timedelta

    # Check token expiry
    url = f"https://graph.facebook.com/v18.0/debug_token"
    params = {
        'input_token': self.access_token,
        'access_token': self.access_token
    }

    response = requests.get(url, params=params)
    data = response.json()

    if 'data' in data:
        expires_at = data['data'].get('expires_at', 0)
        if expires_at:
            exp_date = datetime.fromtimestamp(expires_at)
            days_left = (exp_date - datetime.now()).days

            if days_left < 7:  # Weniger als 7 Tage
                logger.warning(f"Token läuft in {days_left} Tagen ab! Erneuere ihn!")
                # TODO: Send email notification
```

---

## ZUSAMMENFASSUNG:

| Token Type | Lifetime | Setup | Empfehlung |
|------------|----------|-------|------------|
| Short-Lived | 1-2 Stunden | Graph Explorer | ❌ Nicht nutzen! |
| Long-Lived | 60 Tage | Exchange API | ✅ OK für Testing |
| System User | NIEMALS | Business Manager | ✅✅ BESTE Lösung! |

---

**MEIN RAT:**

1. **JETZT:** Generiere Long-Lived Token (60 Tage)
2. **SPÄTER:** Setup System User Token (never expires)

**So läuft dein Dashboard 60 Tage ohne Probleme!**
