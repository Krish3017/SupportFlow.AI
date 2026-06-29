"""
SupportFlow AI — Email Agent
------------------------------
Responsibility:
    - Poll support Gmail inbox every X minutes
    - Detect new unprocessed emails
    - Save to SQLite
    - Pass through existing multi-agent workflow
    - Send AI reply or escalation emails via Resend

This agent reuses the SAME workflow already built in chat.py.
No duplicate agent logic. Just a new input/output channel.
"""

import asyncio
import logging
from datetime import datetime

from database import is_email_processed, save_email_ticket, update_email_ticket
from services.email_service import EmailService
from gmail_reader import get_gmail_service, fetch_latest_emails
from shared.persistence import persist_workflow_result, emit_activity

logger = logging.getLogger(__name__)

import os

# ── Configuration ─────────────────────────────────────────────────────────────
POLL_INTERVAL_MINUTES = int(os.getenv("EMAIL_POLL_INTERVAL_MINUTES", "2"))  # How often to check inbox


# ── Email Agent ───────────────────────────────────────────────────────────────
class EmailAgent:
    """
    Polls Gmail inbox, processes new emails through the
    multi-agent workflow, and sends replies via Resend.
    """

    def __init__(self, workflow):
        """
        Args:
            workflow: The compiled LangGraph workflow from chat.py
                      Reusing the same pipeline — no duplication.
        """
        self.workflow         = workflow
        self.email_service    = EmailService()
        self.gmail_service    = None
        self.support_label_id = "INBOX"  # default, resolved on connect
        logger.info("📧 Email Agent initialized.")

    def _connect_gmail(self):
        """Establish Gmail API connection and resolve support label ID."""
        try:
            self.gmail_service    = get_gmail_service()
            logger.info("✅ Email Agent connected to Gmail.")
            self.support_label_id = self._get_label_id("support")
            logger.info(f"🏷️  Support label ID: {self.support_label_id}")
        except Exception as e:
            logger.error(f"❌ Email Agent Gmail connection failed: {e}")
            raise

    def _get_label_id(self, label_name: str) -> str:
        """
        Resolve a Gmail label name to its API label ID.
        Gmail API requires the ID (e.g. 'Label_123'), not the display name.
        Falls back to INBOX if label not found.
        """
        try:
            results = self.gmail_service.users().labels().list(userId="me").execute()
            labels  = results.get("labels", [])
            for label in labels:
                if label["name"].lower() == label_name.lower():
                    return label["id"]
            logger.warning(f"⚠️  Label '{label_name}' not found. Falling back to INBOX.")
            return "INBOX"
        except Exception as e:
            logger.error(f"❌ Failed to resolve label ID: {e}")
            return "INBOX"

    async def _process_email(self, email: dict):
        """
        Full pipeline for a single email:
        1. Save to DB
        2. Run through multi-agent workflow
        3. Send reply or escalation emails
        """
        ticket_id = None
        try:
            # ── Step 1: Save to DB ─────────────────────────────────────
            ticket_id = save_email_ticket(email)
            logger.info(f"💾 Ticket #{ticket_id} saved — {email['sender']}")

            # ── Step 2: Run Multi-Agent Workflow ───────────────────────
            logger.info(f"🤖 Running workflow for ticket #{ticket_id}...")
            result = await self.workflow.ainvoke({
                "customer_message": f"Subject: {email['subject']}\n\n{email['body']}",
                "customer_id":      "anonymous",
                "session_id":       f"email_{email['id']}",
                "chat_history":     [],
            })

            final_response = result.get("final_response", "")
            escalate       = result.get("escalate", False)
            intent         = result.get("intent", "unknown")
            priority       = result.get("priority", "medium")
            sentiment      = result.get("sentiment", "neutral")

            logger.info(f"📊 Ticket #{ticket_id} — intent={intent} | priority={priority} | escalate={escalate}")

            # Persist to admin panel
            try:
                persist_workflow_result(
                    customer_id=email["sender"],
                    session_id=f"email_{email['id']}",
                    channel="email",
                    message=f"Subject: {email['subject']}\n\n{email['body']}",
                    result=result,
                )
            except Exception as pe:
                logger.warning(f"Persistence error (non-blocking): {pe}")

            # ── Step 3: Send Email + Update DB ─────────────────────────
            if escalate:
                # Send escalation emails (customer + manager)
                self.email_service.send_escalation(
                    to=email["sender"],
                    subject=email["subject"],
                    original_body=email["body"],
                    intent=intent,
                    priority=priority,
                    sentiment=sentiment,
                    ticket_id=ticket_id,
                )
                update_email_ticket(ticket_id, "escalated", final_response)
                logger.info(f"🚨 Ticket #{ticket_id} escalated.")

            else:
                # Send AI resolution reply to customer
                self.email_service.send_resolution(
                    to=email["sender"],
                    subject=email["subject"],
                    ai_response=final_response,
                )
                update_email_ticket(ticket_id, "resolved", final_response)
                logger.info(f"✅ Ticket #{ticket_id} resolved.")

        except Exception as e:
            logger.error(f"❌ Error processing ticket #{ticket_id}: {e}")
            if ticket_id:
                update_email_ticket(ticket_id, "error", str(e))

    async def _poll(self):
        """
        Single poll cycle:
        - Fetch latest emails from support label
        - Skip already processed ones
        - Process new ones
        """
        logger.info(f"🔍 Polling inbox — {datetime.now().strftime('%H:%M:%S')}")
        try:
            emails = fetch_latest_emails(
                self.gmail_service,
                max_results=10,
                label=self.support_label_id  # uses resolved ID, not name
            )

            new_emails = [
                email for email in emails
                if not is_email_processed(email["id"])
            ]

            if not new_emails:
                logger.info("📭 No new emails.")
                return

            logger.info(f"📬 {len(new_emails)} new email(s) found.")
            for email in new_emails:
                await self._process_email(email)

        except Exception as e:
            logger.error(f"❌ Poll error: {e}")

    async def run(self):
        """
        Main polling loop.
        Runs forever — checks inbox every POLL_INTERVAL_MINUTES.
        Started as a background task in main.py.
        """
        logger.info(f"🚀 Email Agent started. Polling every {POLL_INTERVAL_MINUTES} minute(s).")
        self._connect_gmail()

        while True:
            await self._poll()
            await asyncio.sleep(POLL_INTERVAL_MINUTES * 60)