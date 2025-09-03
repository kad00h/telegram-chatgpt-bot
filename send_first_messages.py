#!/usr/bin/env python3
"""
Send First Messages to All Nicknames
Based on the working telegram_chatgpt_bot.py
"""

import asyncio
import openai
import random
import json
import datetime
from telethon import TelegramClient, events
from telethon.tl.types import User

class FirstMessageSender:
    def __init__(self):
        # Hardcoded credentials (from our working test)
        self.api_id = "21291198"
        self.api_hash = "def2b13f8fe9de6b655d3cdee1fee14c"
        self.phone_number = "+380505812213"
        self.openai_key = "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"
        
        self.client = None
        self.openai_client = None
        self.nicknames = []
        self.message_log_file = "message_log.json"
        
    def load_nicknames(self):
        """Load nicknames from file (without @ prefix)"""
        try:
            with open('nicknames.txt', 'r', encoding='utf-8') as f:
                nicknames = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                self.nicknames = nicknames
                print(f"📋 Loaded {len(nicknames)} nicknames from nicknames.txt")
                return True
        except FileNotFoundError:
            print("❌ nicknames.txt not found")
            return False
        except Exception as e:
            print(f"❌ Error loading nicknames: {e}")
            return False
    
    def log_message(self, recipient, message, success=True):
        """Log sent message to JSON file"""
        try:
            log_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "sender_account": "main_account",
                "recipient": recipient,
                "message": message,
                "success": success
            }
            
            # Load existing log or create new
            try:
                with open(self.message_log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                log_data = {"messages": []}
            
            # Add new entry
            log_data["messages"].append(log_entry)
            
            # Save back to file
            with open(self.message_log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            
            print(f"📝 Logged message to {recipient} ({'✅' if success else '❌'})")
            
        except Exception as e:
            print(f"❌ Error logging message: {e}")
    
    async def initialize(self):
        """Initialize clients and load files"""
        try:
            # Load nicknames
            if not self.load_nicknames():
                return False
            
            # Initialize Telegram client
            self.client = TelegramClient('telegram_session', int(self.api_id), self.api_hash)
            
            # Initialize OpenAI client
            self.openai_client = openai.OpenAI(api_key=self.openai_key)
            
            print("✅ Clients initialized successfully")
            print(f"📤 Ready to send to: {len(self.nicknames)} users")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize: {e}")
            return False
    
    async def connect_and_auth(self):
        """Connect to Telegram and authenticate"""
        try:
            await self.client.connect()
            
            if not await self.client.is_user_authorized():
                print("🔐 Starting authentication...")
                await self.client.send_code_request(self.phone_number)
                code = input("Enter the verification code sent to your phone: ")
                await self.client.sign_in(self.phone_number, code)
            
            print("✅ Connected and authenticated to Telegram")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect/authenticate: {e}")
            return False
    
    async def send_message_to_user(self, username, message):
        """Send message to a specific user"""
        try:
            # Add @ prefix if not present
            if not username.startswith('@'):
                username_with_at = '@' + username
            else:
                username_with_at = username
                username = username[1:]  # Remove @ for logging
            
            user = await self.client.get_entity(username_with_at)
            await self.client.send_message(user, message)
            
            # Log successful message
            self.log_message(username, message, success=True)
            return True
            
        except Exception as e:
            print(f"❌ Failed to send message to @{username}: {e}")
            # Log failed message
            self.log_message(username, message, success=False)
            return False
    
    async def send_test_messages(self):
        """Send test messages to all nicknames simultaneously"""
        if not self.nicknames:
            print("❌ No nicknames loaded. Please check nicknames.txt")
            return
        
        print(f"🧪 Starting TEST message campaign to {len(self.nicknames)} users...")
        print("⚡ All messages will be sent simultaneously (no delays)")
        
        # Test message to send
        test_message = """🧪 Тестовое сообщение

Это тестовое сообщение для проверки функциональности.

Если получил - ответь пожалуйста."""
        
        successful = 0
        failed = 0
        
        print(f"📤 Sending test messages to all {len(self.nicknames)} users simultaneously...")
        
        for i, nickname in enumerate(self.nicknames):
            try:
                print(f"📤 [{i+1}/{len(self.nicknames)}] Sending to @{nickname}...")
                
                success = await self.send_message_to_user(nickname, test_message)
                if success:
                    print(f"✅ Test message sent to @{nickname}")
                    successful += 1
                else:
                    print(f"❌ Failed to send to @{nickname}")
                    failed += 1
                
            except Exception as e:
                print(f"❌ Error sending to @{nickname}: {e}")
                failed += 1
        
        print(f"📊 Test message campaign complete!")
        print(f"✅ Successfully sent: {successful}")
        print(f"❌ Failed to send: {failed}")
        print(f"📝 All results logged to {self.message_log_file}")
        
        return {"successful": successful, "failed": failed}
    
    async def send_main_messages(self):
        """Send main messages to all nicknames with random delays"""
        if not self.nicknames:
            print("❌ No nicknames loaded. Please check nicknames.txt")
            return
        
        print(f"📤 Starting MAIN message campaign to {len(self.nicknames)} users...")
        print(f"⏱️ This will take approximately {len(self.nicknames) * 3.5:.1f} minutes")
        print("🔄 Each message is sent individually with 2-5 minute delays")
        
        # Main message to send
        main_message = """Привет! 👋

Хочу пригласить тебя в интересный канал по крипте и трейдингу. 

Там делимся полезной информацией, анализом рынка и обсуждаем актуальные темы.

Интересно? Могу добавить в канал если хочешь."""
        
        successful = 0
        failed = 0
        
        for i, nickname in enumerate(self.nicknames):
            try:
                print(f"📤 [{i+1}/{len(self.nicknames)}] Sending to @{nickname}...")
                
                success = await self.send_message_to_user(nickname, main_message)
                if success:
                    print(f"✅ Main message sent to @{nickname}")
                    successful += 1
                else:
                    print(f"❌ Failed to send to @{nickname}")
                    failed += 1
                
                # Random delay between 2-5 minutes (as per plan)
                if i < len(self.nicknames) - 1:  # Don't delay after last message
                    delay_minutes = random.uniform(2, 5)
                    delay_seconds = delay_minutes * 60
                    print(f"⏳ Waiting {delay_minutes:.1f} minutes before next message...")
                    await asyncio.sleep(delay_seconds)
                
            except Exception as e:
                print(f"❌ Error sending to @{nickname}: {e}")
                failed += 1
        
        print(f"📊 Main message campaign complete!")
        print(f"✅ Successfully sent: {successful}")
        print(f"❌ Failed to send: {failed}")
        print(f"📝 All results logged to {self.message_log_file}")
        
        return {"successful": successful, "failed": failed}
    
    async def run(self):
        """Main run method"""
        try:
            # Initialize
            if not await self.initialize():
                return False
            
            # Connect to Telegram
            if not await self.connect_and_auth():
                return False
            
            print("🤖 Message Sender is ready!")
            print(f"📋 Nicknames to send to:")
            for i, nick in enumerate(self.nicknames, 1):
                print(f"  {i}. @{nick}")
            print("-" * 50)
            
            # Choose mode
            print("🎯 Choose sending mode:")
            print("  0 - 🧪 TEST mode (send simultaneously)")
            print("  1 - 📤 MAIN mode (send with 2-5 min delays)")
            
            while True:
                try:
                    choice = input("\nEnter mode (0 or 1): ").strip()
                    if choice == "0":
                        print("🧪 Starting TEST mode...")
                        results = await self.send_test_messages()
                        break
                    elif choice == "1":
                        print("📤 Starting MAIN mode...")
                        results = await self.send_main_messages()
                        break
                    else:
                        print("❌ Invalid choice. Please enter 0 or 1.")
                except KeyboardInterrupt:
                    print("\n👋 Cancelled by user")
                    return
            
            print(f"\n📊 Final Results:")
            print(f"✅ Successfully sent: {results['successful']}")
            print(f"❌ Failed to send: {results['failed']}")
            
        except KeyboardInterrupt:
            print("\n👋 Message sender stopped by user")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            if self.client:
                await self.client.disconnect()
                print("🔌 Disconnected from Telegram")

async def main():
    """Main function"""
    sender = FirstMessageSender()
    await sender.run()

if __name__ == "__main__":
    asyncio.run(main())
