import asyncio
import logging
import time
from datetime import datetime

from database import is_email_processed, save_email_ticket, update_email_ticket
from services.email_service import EmailService
from gmail_reader import get_gmail_service, fetch_latest_emails
from shared.persistence import (
    ensure_contact,
    get_or_create_conversation,
    store_user_message,
    create_execution,
    complete_execution,
    record_execution_steps,
    store_assistant_message,
    create_ticket_on_escalation,
    update_contact_stats,
    emit_activity,
)

logger = logging.getLogger(__name__)

import os

POLL_INTERVAL_MINUTES = int(os.getenv("EMAIL_POLL_INTERVAL_MINUTES", "2"))


class EmailAgent:

    def __init__(self, workflow):
        self.workflow = workflow
        self.email_service = EmailService()
        self.gmail_service = None
        self.support_label_id = "INBOX"
        logger.info("Email Agent initialized.")

    def _connect_gmail(self):
        try:
            self.gmail_service = get_gmail_service()
            self.support_label_id = self._get_label_id("support")
        except Exception as e:
            logger.error(f"Email Agent Gmail connection failed: {e}")
            raise

    def _get_label_id(self, label_name: str) -> str:
        try:
            results = self.gmail_service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])
            for label in labels:
                if label["name"].lower() == label_name.lower():
                    return label["id"]
            return "INBOX"
        except Exception:
            return "INBOX"

    async def _process_email(self, email: dict):
        ticket_id = None
        try:
            ticket_id = save_email_ticket(email)

            start_time = time.time()
            session_id = f"email_{email['id']}"
            message_content = f"Subject: {email['subject']}\n\n{email['body']}"

            contact_id = ensure_contact(email["sender"], "email")
            conversation_id = get_or_create_conversation(contact_id, "email", session_id)
            user_msg_id = store_user_message(conversation_id, message_content)
            execution_id = create_execution(user_msg_id, conversation_id)

            result = await self.workflow.ainvoke({
                "customer_message": message_content,
                "customer_id": contact_id,
                "session_id": session_id,
                "chat_history": [],
            })

            duration = time.time() - start_time
            record_execution_steps(execution_id, result, message_content, duration)
            complete_execution(execution_id, result, duration)

            final_response = result.get("final_response", "")
            escalate = result.get("escalate", False)
            intent = result.get("intent", "unknown")
            priority = result.get("priority", "medium")
            sentiment = result.get("sentiment", "neutral")

            if final_response:
                store_assistant_message(conversation_id, final_response, execution_id)

            create_ticket_on_escalation(conversation_id, contact_id, result)
            update_contact_stats(contact_id, result)

            emit_activity(
                "conversation",
                f"[EMAIL] {intent} from {email['sender']}",
                metadata={
                    "conversation_id": conversation_id,
                    "execution_id": execution_id,
                    "channel": "email",
                    "intent": intent,
                }
            )

            # Link email_ticket to conversation
            try:
                from database import get_connection
                conn = get_connection()
                conn.execute(
                    "UPDATE email_tickets SET conversation_id = ? WHERE id = ?",
                    (conversation_id, ticket_id)
                )
                conn.commit()
                conn.close()
            except Exception:
                pass

            if escalate:
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
            else:
                self.email_service.send_resolution(
                    to=email["sender"],
                    subject=email["subject"],
                    ai_response=final_response,
                )
                update_email_ticket(ticket_id, "resolved", final_response)

        except Exception as e:
            logger.error(f"Error processing email ticket #{ticket_id}: {e}")
            if ticket_id:
                update_email_ticket(ticket_id, "error", str(e))

    async def _poll(self):
        try:
            emails = fetch_latest_emails(
                self.gmail_service,
                max_results=10,
                label=self.support_label_id
            )

            new_emails = [
                email for email in emails
                if not is_email_processed(email["id"])
            ]

            if not new_emails:
                return

            logger.info(f"{len(new_emails)} new email(s) found.")
            for email in new_emails:
                await self._process_email(email)

        except Exception as e:
            logger.error(f"Poll error: {e}")

    async def run(self):
        logger.info(f"Email Agent started. Polling every {POLL_INTERVAL_MINUTES} minute(s).")
        self._connect_gmail()

        while True:
            await self._poll()
            await asyncio.sleep(POLL_INTERVAL_MINUTES * 60)
