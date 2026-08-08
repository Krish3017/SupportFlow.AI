#!/usr/bin/env python3
"""
SupportFlow AI - Email Worker Entrypoint
Runs the EmailAgent background worker explicitly as a standalone process.
"""
import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

from agents.email_agent import EmailAgent
from apps.chat.router import workflow
from core.logging_config import setup_logging, get_logger

setup_logging()
logger = get_logger("email_worker")

async def main():
    logger.info("Starting SupportFlow AI Email Worker process...")
    agent = EmailAgent(workflow=workflow)
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
