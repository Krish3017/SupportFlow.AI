#!/usr/bin/env python3
"""
Test bot - minimal version to debug command responses
"""
import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def test_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test /start command"""
    logger.info(f"📱 /start from user {update.effective_user.id}")
    try:
        await update.message.reply_text("✅ Test bot working! /start received.")
        logger.info("✅ Response sent")
    except Exception as e:
        logger.error(f"❌ Error: {e}")

async def test_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test /faq command"""
    logger.info(f"📱 /faq from user {update.effective_user.id}")
    try:
        await update.message.reply_text("✅ FAQ command received!")
        logger.info("✅ Response sent")
    except Exception as e:
        logger.error(f"❌ Error: {e}")

async def test_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test /order command"""
    logger.info(f"📱 /order from user {update.effective_user.id}")
    try:
        await update.message.reply_text("✅ Order command received!")
        logger.info("✅ Response sent")
    except Exception as e:
        logger.error(f"❌ Error: {e}")

def main():
    logger.info("🚀 Starting test bot...")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", test_start))
    app.add_handler(CommandHandler("faq", test_faq))
    app.add_handler(CommandHandler("order", test_order))

    logger.info("✅ Test bot running. Try /start, /faq, /order")

    app.run_polling()

if __name__ == "__main__":
    main()
