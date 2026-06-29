import logging
import os
from dotenv import load_dotenv

load_dotenv()

from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)

from routers.chat import workflow
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
    get_conversation_messages,
)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in .env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Conversation states for /feedback
WAITING_FOR_FEEDBACK = 1


# ============================================================================
# HELPER: Process message through existing AI workflow
# ============================================================================
async def process_through_workflow(
    update: Update,
    message: str,
    user_id: str,
    session_id: str
) -> str:
    import time

    try:
        start_time = time.time()

        contact_id = ensure_contact(user_id, "telegram")
        conversation_id = get_or_create_conversation(contact_id, "telegram", session_id)
        chat_history = get_conversation_messages(conversation_id)

        user_msg_id = store_user_message(conversation_id, message)
        execution_id = create_execution(user_msg_id, conversation_id)

        chat_history.append({"role": "user", "content": message})

        result = await workflow.ainvoke({
            "customer_message": message,
            "customer_id": contact_id,
            "session_id": session_id,
            "chat_history": chat_history,
        })

        duration = time.time() - start_time
        record_execution_steps(execution_id, result, message, duration)
        complete_execution(execution_id, result, duration)

        response = result.get(
            "final_response",
            "Sorry, I couldn't process your request.",
        )

        store_assistant_message(conversation_id, response, execution_id)
        create_ticket_on_escalation(conversation_id, contact_id, result)
        update_contact_stats(contact_id, result)

        emit_activity(
            "conversation",
            f"[TELEGRAM] {result.get('intent', 'unknown')} from {contact_id}",
            metadata={
                "conversation_id": conversation_id,
                "execution_id": execution_id,
                "channel": "telegram",
                "intent": result.get("intent"),
            }
        )

        return response

    except Exception as e:
        logger.exception(f"Workflow error: {str(e)}")
        return "Sorry, an internal error occurred. Please try again."


# ============================================================================
# COMMAND HANDLERS
# ============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    try:
        logger.info(f"📱 /start from user {update.effective_user.id}")
        await update.message.reply_text(
            """👋 **Welcome to SupportFlow AI!**

I'm your AI-powered customer support assistant, available 24/7.

I can help you with:
📦 **Order Tracking**
💰 **Refund Requests**
💳 **Billing Issues**
🔧 **Technical Support**
👤 **Account Issues**
📦 **Product Questions**
🚨 **Complaints**
💡 **Feature Requests**

Simply type your question naturally, and I'll assist you instantly.

Type /help to see all available commands.
""",
            parse_mode="Markdown"
        )
        logger.info("✅ /start response sent")
    except Exception as e:
        logger.exception(f"❌ /start error: {e}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    try:
        logger.info(f"📱 /help from user {update.effective_user.id}")
        await update.message.reply_text(
            """🤖 **Available Commands:**

/start - Start the bot
/help - Show this help message
/about - About SupportFlow AI
/faq - Common questions

**Quick Actions:**
/order - Track your order
/refund - Request a refund
/billing - Billing support
/account - Account help
/status - Check order/ticket status
/support - Get human support

**Other:**
/feedback - Share feedback
/clear - Clear conversation history

💬 **You can also just type your question naturally!**
""",
            parse_mode="Markdown"
        )
        logger.info("✅ /help response sent")
    except Exception as e:
        logger.exception(f"❌ /help error: {e}")


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command"""
    try:
        logger.info(f"📱 /about from user {update.effective_user.id}")
        await update.message.reply_text(
            """🤖 **SupportFlow AI**

Multi-Agent AI Customer Support Platform

**Powered by:**
• LangGraph - Multi-agent orchestration
• FastAPI - High-performance backend
• Groq - Lightning-fast LLM inference
• ChromaDB - Vector knowledge base
• SQLite - Session & ticket storage
• Telegram - Real-time messaging

**Features:**
✅ Intent Detection
✅ Knowledge Retrieval (RAG)
✅ Priority Classification
✅ Intelligent Routing
✅ Human Escalation
✅ Context-aware Responses
✅ Multi-channel Support

Built with ❤️ for instant, accurate customer support.
""",
            parse_mode="Markdown"
        )
        logger.info("✅ /about response sent")
    except Exception as e:
        logger.exception(f"❌ /about error: {e}")


async def faq_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /faq command"""
    try:
        logger.info(f"📱 /faq from user {update.effective_user.id}")
        await update.message.reply_text(
            """❓ **Frequently Asked Questions**

**Refund Policy**
• Full refunds within 30 days
• Partial refunds for used products
• Refunds processed in 5-7 business days

**Order Tracking**
• Track orders using your Order ID
• Email notifications at each step
• Typical delivery: 3-5 business days

**Password Reset**
• Click "Forgot Password" on login
• Check email for reset link
• Link expires in 1 hour

**Shipping**
• Free shipping on orders over $50
• Express shipping available
• International shipping supported

**Billing**
• Secure payment processing
• Multiple payment methods accepted
• Invoices sent via email

💬 Need more details? Just ask me anything!
""",
            parse_mode="Markdown"
        )
        logger.info("✅ /faq response sent")
    except Exception as e:
        logger.exception(f"❌ /faq error: {e}")


async def order_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /order - Route to AI workflow"""
    try:
        user = update.effective_user
        user_id = str(user.id)
        session_id = f"telegram_{user_id}"

        logger.info(f"📦 /order command from {user_id}")

        # Send through existing workflow
        response = await process_through_workflow(
            update,
            "I need help tracking my order.",
            user_id,
            session_id
        )

        await update.message.reply_text(response)
        logger.info("✅ /order response sent")
    except Exception as e:
        logger.exception(f"❌ /order error: {e}")
        await update.message.reply_text("Sorry, an error occurred. Please try again.")


async def refund_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /refund - Route to AI workflow"""
    try:
        user = update.effective_user
        user_id = str(user.id)
        session_id = f"telegram_{user_id}"

        logger.info(f"💰 /refund command from {user_id}")

        response = await process_through_workflow(
            update,
            "I want to request a refund.",
            user_id,
            session_id
        )

        await update.message.reply_text(response)
        logger.info("✅ /refund response sent")
    except Exception as e:
        logger.exception(f"❌ /refund error: {e}")
        await update.message.reply_text("Sorry, an error occurred. Please try again.")


async def billing_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /billing - Route to AI workflow"""
    try:
        user = update.effective_user
        user_id = str(user.id)
        session_id = f"telegram_{user_id}"

        logger.info(f"💳 /billing command from {user_id}")

        response = await process_through_workflow(
            update,
            "I have a billing issue.",
            user_id,
            session_id
        )

        await update.message.reply_text(response)
        logger.info("✅ /billing response sent")
    except Exception as e:
        logger.exception(f"❌ /billing error: {e}")
        await update.message.reply_text("Sorry, an error occurred. Please try again.")


async def account_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /account - Route to AI workflow"""
    try:
        user = update.effective_user
        user_id = str(user.id)
        session_id = f"telegram_{user_id}"

        logger.info(f"👤 /account command from {user_id}")

        response = await process_through_workflow(
            update,
            "I have an account problem.",
            user_id,
            session_id
        )

        await update.message.reply_text(response)
        logger.info("✅ /account response sent")
    except Exception as e:
        logger.exception(f"❌ /account error: {e}")
        await update.message.reply_text("Sorry, an error occurred. Please try again.")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status - Ask for order/ticket ID then route to workflow"""
    try:
        logger.info(f"📱 /status from user {update.effective_user.id}")
        await update.message.reply_text(
            """📊 **Status Check**

Please provide your:
• Order ID (e.g., ORD-12345), or
• Ticket ID (e.g., TKT-67890)

I'll check the status for you.
""",
            parse_mode="Markdown"
        )
        logger.info("✅ /status response sent")
    except Exception as e:
        logger.exception(f"❌ /status error: {e}")


async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /support"""
    try:
        logger.info(f"📱 /support from user {update.effective_user.id}")
        await update.message.reply_text(
            """🆘 **Human Support**

Please describe your issue, and I'll do my best to help you.

If your issue requires human attention, I'll automatically escalate it to our support team, and they'll reach out to you shortly.

What can I help you with?
""",
            parse_mode="Markdown"
        )
        logger.info("✅ /support response sent")
    except Exception as e:
        logger.exception(f"❌ /support error: {e}")


async def feedback_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /feedback - Start feedback conversation"""
    await update.message.reply_text(
        """📝 **Feedback**

We'd love to hear from you!

Please type your feedback, and I'll make sure our team sees it.

(Send /cancel to cancel)
"""
    )
    return WAITING_FOR_FEEDBACK


async def feedback_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and store feedback"""
    user = update.effective_user
    feedback_text = update.message.text

    # TODO: Store feedback in database
    logger.info(f"📝 Feedback from {user.id} (@{user.username}): {feedback_text}")

    await update.message.reply_text(
        """✅ **Thank you for your feedback!**

Your input helps us improve SupportFlow AI.

Our team will review it shortly.
""",
        parse_mode="Markdown"
    )

    return ConversationHandler.END


async def feedback_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel feedback"""
    await update.message.reply_text("Feedback canceled.")
    return ConversationHandler.END


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /clear - Close current conversation so next message starts fresh"""
    try:
        user = update.effective_user
        user_id = str(user.id)
        session_id = f"telegram_{user_id}"

        from shared.persistence import close_conversation, _get_db
        conn = _get_db()
        existing = conn.execute("""
            SELECT id FROM conversations
            WHERE session_token = ? AND status NOT IN ('closed', 'archived')
        """, (session_id,)).fetchone()
        conn.close()

        if existing:
            close_conversation(existing['id'])

        logger.info(f"Cleared session for {user_id}")

        await update.message.reply_text(
            """✅ **Conversation cleared successfully.**

Let's start a new conversation. How can I help you?
"""
        )
        logger.info("✅ /clear response sent")
    except Exception as e:
        logger.exception(f"❌ /clear error: {e}")


# ============================================================================
# MESSAGE HANDLER (for natural language queries)
# ============================================================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages - route through AI workflow"""
    user = update.effective_user
    message = update.message.text
    user_id = str(user.id)
    session_id = f"telegram_{user_id}"

    logger.info(f"📱 Message from {user_id}: {message}")

    response = await process_through_workflow(
        update,
        message,
        user_id,
        session_id
    )

    await update.message.reply_text(response)


# ============================================================================
# BOT SETUP
# ============================================================================

async def post_init(application: Application):
    """Set bot commands for Telegram menu"""
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Show help message"),
        BotCommand("about", "About SupportFlow AI"),
        BotCommand("faq", "Common questions"),
        BotCommand("order", "Track your order"),
        BotCommand("refund", "Request a refund"),
        BotCommand("billing", "Billing support"),
        BotCommand("account", "Account help"),
        BotCommand("status", "Check order/ticket status"),
        BotCommand("support", "Get human support"),
        BotCommand("feedback", "Share feedback"),
        BotCommand("clear", "Clear conversation"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("✅ Bot commands registered")


def main():
    """Initialize and run the bot"""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("faq", faq_command))
    app.add_handler(CommandHandler("order", order_command))
    app.add_handler(CommandHandler("refund", refund_command))
    app.add_handler(CommandHandler("billing", billing_command))
    app.add_handler(CommandHandler("account", account_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("support", support_command))
    app.add_handler(CommandHandler("clear", clear_command))

    # Feedback conversation handler
    feedback_handler = ConversationHandler(
        entry_points=[CommandHandler("feedback", feedback_start)],
        states={
            WAITING_FOR_FEEDBACK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, feedback_receive)
            ],
        },
        fallbacks=[CommandHandler("cancel", feedback_cancel)],
    )
    app.add_handler(feedback_handler)

    # Natural language message handler (must be last)
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    logger.info("🤖 Telegram Bot Started")
    logger.info("✅ All commands registered")

    app.run_polling()


if __name__ == "__main__":
    main()