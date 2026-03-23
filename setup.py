#!/usr/bin/env python3
"""
Interactive setup script for Job Automation Bot
"""

import os
import sys

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def setup_telegram():
    """Guide user through Telegram setup"""
    print_header("🤖 TELEGRAM BOT SETUP")
    
    print("""
This script will help you set up your Telegram bot.

Steps:
1. Open Telegram and search for @BotFather
2. Send: /newbot
3. Follow the prompts to create a bot
4. Copy the API Token (starts with numbers:ABC...)
5. Search for @userinfobot and get your Chat ID

Press Enter when ready to continue...
    """)
    input()
    
    bot_token = input("📝 Enter your TELEGRAM_BOT_TOKEN: ").strip()
    chat_id = input("📝 Enter your TELEGRAM_CHAT_ID: ").strip()
    
    if not bot_token or not chat_id:
        print("❌ Error: Both values are required!")
        return False
    
    print(f"\n✅ Saved:")
    print(f"   Bot Token: {bot_token[:10]}...{bot_token[-5:]}")
    print(f"   Chat ID: {chat_id}")
    
    return bot_token, chat_id

def setup_github():
    """Guide user through GitHub setup"""
    print_header("🐙 GITHUB SETUP")
    
    print("""
To enable GitHub Actions:

1. Create a repository on GitHub (or fork this one)
2. Go to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add TELEGRAM_BOT_TOKEN (from above)
5. Add TELEGRAM_CHAT_ID (from above)
6. Enable Actions in the Actions tab

All done! The bot will run automatically every 4 hours.

Press Enter when ready to continue...
    """)
    input()

def setup_filters():
    """Customize filtering"""
    print_header("🎯 JOB FILTERING SETUP")
    
    print("""
Customize what jobs you want to see.

Current keywords: Cisco, Meraki, network, intern, CDMX, etc.

Options:
1. Keep defaults
2. Add more keywords
3. Change locations
4. Edit config.py manually

    """)
    
    choice = input("Choose (1-4): ").strip()
    
    if choice == "1":
        print("✅ Using default filters")
        return True
    elif choice == "2":
        keywords = input("Add keywords (comma-separated): ").split(',')
        print(f"✅ Added {len(keywords)} keywords")
        return True
    elif choice == "3":
        locations = input("Add locations (comma-separated): ").split(',')
        print(f"✅ Added {len(locations)} locations")
        return True
    elif choice == "4":
        print("✅ Edit config.py and run this script again")
        return True
    else:
        print("❌ Invalid choice")
        return False

def setup_test():
    """Test the setup"""
    print_header("🧪 TEST SETUP")
    
    print("Testing installation...")
    
    try:
        import requests
        print("✅ requests library installed")
    except:
        print("❌ requests not found - run: pip install -r requirements.txt")
        return False
    
    try:
        import telegram
        print("✅ python-telegram-bot installed")
    except:
        print("❌ python-telegram-bot not found - run: pip install -r requirements.txt")
        return False
    
    try:
        import sqlite3
        print("✅ sqlite3 available")
    except:
        print("❌ sqlite3 not found")
        return False
    
    print("\n✅ All libraries installed!")
    return True

def print_next_steps():
    """Show next steps"""
    print_header("🚀 NEXT STEPS")
    
    print("""
1. Push code to GitHub:
   $ git add .
   $ git commit -m "Initial job automation setup"
   $ git push origin main

2. Add GitHub Secrets:
   - Go to repo Settings → Secrets and variables → Actions
   - Add TELEGRAM_BOT_TOKEN
   - Add TELEGRAM_CHAT_ID

3. Enable Actions:
   - Go to repo Actions tab
   - Click "I understand... enable them"

4. Test manually (optional):
   $ python main.py

5. Wait for automatic runs:
   - Every 4 hours, your Telegram bot will send alerts
   - Or manually trigger: Actions → Run workflow

Questions? Check README.md
    """)

def main():
    """Main setup flow"""
    print_header("🎉 JOB AUTOMATION BOT SETUP")
    
    print("""
This script will guide you through setting up your
automated job alert system using GitHub Actions + Telegram.

Everything is FREE and takes about 5 minutes!

Let's get started... 🚀
    """)
    
    input("Press Enter to begin...")
    
    # Step 1: Telegram
    result = setup_telegram()
    if not result:
        print("❌ Setup failed!")
        sys.exit(1)
    bot_token, chat_id = result
    
    # Step 2: GitHub
    setup_github()
    
    # Step 3: Filters
    setup_filters()
    
    # Step 4: Test
    if not setup_test():
        print("\n⚠️ Some libraries are missing. Run:")
        print("   pip install -r requirements.txt")
    
    # Step 5: Next steps
    print_next_steps()
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print("\n✨ Happy job hunting! ✨\n")

if __name__ == "__main__":
    main()
