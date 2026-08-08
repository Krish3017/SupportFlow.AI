#!/usr/bin/env python3
"""
SupportFlow AI - Telegram Worker Entrypoint
Runs the Telegram Bot explicitly as a standalone process.
"""
import logging
from dotenv import load_dotenv

load_dotenv()

from telegram_bot import main as run_bot
from core.logging_config import setup_logging, get_logger

setup_logging()
logger = get_logger("telegram_worker")

if __name__ == "__main__":
    logger.info("Starting SupportFlow AI Telegram Worker process...")
    run_bot()
