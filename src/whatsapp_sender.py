"""
WhatsApp Report Sender
Send reports via WhatsApp using Twilio API
"""
import logging
from typing import Optional
from twilio.rest import Client
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhatsAppSender:
    """Send reports via WhatsApp"""

    def __init__(self):
        """Initialize WhatsApp sender with Twilio"""
        self.account_sid = Config.get('TWILIO_ACCOUNT_SID')
        self.auth_token = Config.get('TWILIO_AUTH_TOKEN')
        self.from_number = Config.get('TWILIO_WHATSAPP_FROM')  # Format: whatsapp:+14155238886

        if self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                self.enabled = True
                logger.info("WhatsApp sender initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio: {str(e)}")
                self.enabled = False
        else:
            logger.warning("Twilio credentials not configured")
            self.enabled = False

    def send_report(self, to_number: str, message: str, media_url: Optional[str] = None) -> bool:
        """
        Send WhatsApp message with optional PDF attachment

        Args:
            to_number: Recipient WhatsApp number (format: whatsapp:+491234567890)
            message: Message text
            media_url: Optional URL to PDF file

        Returns:
            True if sent successfully
        """
        if not self.enabled:
            logger.error("WhatsApp sender not enabled")
            return False

        try:
            # Ensure number has whatsapp: prefix
            if not to_number.startswith('whatsapp:'):
                to_number = f'whatsapp:{to_number}'

            # Send message
            if media_url:
                msg = self.client.messages.create(
                    from_=self.from_number,
                    to=to_number,
                    body=message,
                    media_url=[media_url]
                )
            else:
                msg = self.client.messages.create(
                    from_=self.from_number,
                    to=to_number,
                    body=message
                )

            logger.info(f"WhatsApp message sent: {msg.sid}")
            return True

        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {str(e)}")
            return False

    def send_quick_update(self, to_number: str, spend: float, leads: int, cpl: float) -> bool:
        """
        Send quick performance update

        Args:
            to_number: Recipient number
            spend: Total spend
            leads: Total leads
            cpl: Average CPL

        Returns:
            True if sent successfully
        """
        message = f"""
🚀 *CarCenter Landshut - Performance Update*

📊 *Aktuelle Zahlen:*
💰 Spend: €{spend:,.2f}
📞 Leads: {leads:,}
💸 CPL: €{cpl:.2f}

_Powered by Meta Ads Autopilot_
_Brandea GbR_
        """.strip()

        return self.send_report(to_number, message)
