#!/usr/bin/env python3
"""
Legal Document Bot - Main Entry Point
"""
import asyncio
from presentation.telegram.bot import run_bot

if __name__ == "__main__":
    asyncio.run(run_bot())
