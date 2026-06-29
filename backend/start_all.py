#!/usr/bin/env python3
"""
SupportFlow AI - Single Launcher
Activates venv and starts 3 services in completely separate terminal windows
"""
import os
import sys
import time
import subprocess
import platform

# Fix emoji encoding on Windows
if platform.system() == 'Windows':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def get_python():
    """Get Python executable - check venv first, fallback to system Python"""
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(backend_dir)

    # Check for venv in common locations
    venv_locations = [
        os.path.join(project_dir, 'venv'),
        os.path.join(project_dir, '.venv'),
        os.path.join(backend_dir, 'venv'),
        os.path.join(backend_dir, '.venv'),
    ]

    for venv_dir in venv_locations:
        if platform.system() == 'Windows':
            python_path = os.path.join(venv_dir, 'Scripts', 'python.exe')
        else:
            python_path = os.path.join(venv_dir, 'bin', 'python')

        if os.path.exists(python_path):
            print(f"✅ Using venv: {venv_dir}")
            return python_path

    # Fallback to system Python
    python_path = sys.executable
    print(f"⚠️  No venv found, using system Python: {python_path}")
    return python_path

def start_windows(python_path, backend_dir):
    """Start 3 separate CMD windows on Windows"""
    print("🚀 Starting services in separate Windows terminals...")

    # Telegram Bot - Separate window
    subprocess.Popen(
        f'start "Telegram Bot" cmd /k "cd /d {backend_dir} && {python_path} telegram_bot.py"',
        shell=True
    )
    time.sleep(2)

    # API Server - Separate window
    subprocess.Popen(
        f'start "API Server" cmd /k "cd /d {backend_dir} && {python_path} main.py"',
        shell=True
    )
    time.sleep(2)

    # Email Monitor - Separate window
    subprocess.Popen(
        f'start "Email Monitor" cmd /k "cd /d {backend_dir} && {python_path} -c \\"from agents.email_agent import EmailAgent; from routers.chat import workflow; import asyncio; asyncio.run(EmailAgent(workflow).run())\\"',
        shell=True
    )

def start_macos(python_path, backend_dir):
    """Start 3 separate Terminal windows on macOS"""
    print("🚀 Starting services in separate macOS Terminal windows...")

    # Telegram Bot
    script = f'''
    tell application "Terminal"
        do script "cd {backend_dir} && {python_path} telegram_bot.py"
        activate
    end tell
    '''
    subprocess.run(['osascript', '-e', script])
    time.sleep(2)

    # API Server
    script = f'''
    tell application "Terminal"
        do script "cd {backend_dir} && {python_path} main.py"
        activate
    end tell
    '''
    subprocess.run(['osascript', '-e', script])
    time.sleep(2)

    # Email Monitor
    script = f'''
    tell application "Terminal"
        do script "cd {backend_dir} && {python_path} -c 'from agents.email_agent import EmailAgent; from routers.chat import workflow; import asyncio; asyncio.run(EmailAgent(workflow).run())'"
        activate
    end tell
    '''
    subprocess.run(['osascript', '-e', script])

def start_linux(python_path, backend_dir):
    """Start 3 separate terminal windows on Linux"""
    print("🚀 Starting services in separate Linux terminal windows...")

    # Try gnome-terminal
    if subprocess.run(['which', 'gnome-terminal'], capture_output=True).returncode == 0:
        # Telegram Bot
        subprocess.Popen([
            'gnome-terminal', '--',
            'bash', '-c',
            f'cd {backend_dir} && {python_path} telegram_bot.py; exec bash'
        ])
        time.sleep(2)

        # API Server
        subprocess.Popen([
            'gnome-terminal', '--',
            'bash', '-c',
            f'cd {backend_dir} && {python_path} main.py; exec bash'
        ])
        time.sleep(2)

        # Email Monitor
        subprocess.Popen([
            'gnome-terminal', '--',
            'bash', '-c',
            f'cd {backend_dir} && {python_path} -c "from agents.email_agent import EmailAgent; from routers.chat import workflow; import asyncio; asyncio.run(EmailAgent(workflow).run())"; exec bash'
        ])

    # Try xterm
    elif subprocess.run(['which', 'xterm'], capture_output=True).returncode == 0:
        subprocess.Popen(['xterm', '-e', f'cd {backend_dir} && {python_path} telegram_bot.py'])
        time.sleep(2)
        subprocess.Popen(['xterm', '-e', f'cd {backend_dir} && {python_path} main.py'])
        time.sleep(2)
        subprocess.Popen(['xterm', '-e', f'cd {backend_dir} && {python_path} -c "from agents.email_agent import EmailAgent; from routers.chat import workflow; import asyncio; asyncio.run(EmailAgent(workflow).run())"'])

    # Try konsole
    elif subprocess.run(['which', 'konsole'], capture_output=True).returncode == 0:
        subprocess.Popen(['konsole', '-e', f'cd {backend_dir} && {python_path} telegram_bot.py'])
        time.sleep(2)
        subprocess.Popen(['konsole', '-e', f'cd {backend_dir} && {python_path} main.py'])
        time.sleep(2)
        subprocess.Popen(['konsole', '-e', f'cd {backend_dir} && {python_path} -c "from agents.email_agent import EmailAgent; from routers.chat import workflow; import asyncio; asyncio.run(EmailAgent(workflow).run())"'])

    else:
        print("❌ No supported terminal found. Install: gnome-terminal, xterm, or konsole")
        sys.exit(1)

def main():
    print("=" * 70)
    print("SupportFlow AI - Multi-Service Launcher")
    print("=" * 70)
    print()

    backend_dir = os.path.dirname(os.path.abspath(__file__))
    python_path = get_python()
    print(f"✅ Backend directory: {backend_dir}")
    print()

    system = platform.system()

    if system == "Windows":
        start_windows(python_path, backend_dir)
    elif system == "Darwin":
        start_macos(python_path, backend_dir)
    elif system == "Linux":
        start_linux(python_path, backend_dir)
    else:
        print(f"❌ Unsupported OS: {system}")
        sys.exit(1)

    print()
    print("✅ Launched 3 separate terminals:")
    print("   1. Telegram Bot (telegram_bot.py)")
    print("   2. API Server (main.py)")
    print("   3. Email Monitor (EmailAgent)")
    print()
    print("Press Ctrl+C in each terminal to stop")

if __name__ == "__main__":
    main()
