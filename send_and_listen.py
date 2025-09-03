#!/usr/bin/env python3
"""
Send First Messages and Listen for Responses
Sends first message to all users, then listens for responses with ChatGPT
"""

import asyncio
import openai
import random
import json
import datetime
from telethon import TelegramClient, events
from telethon.tl.types import User

class SendAndListenBot:
    def __init__(self):
        # Hardcoded credentials (from our working test)
        self.api_id = "21291198"
        self.api_hash = "def2b13f8fe9de6b655d3cdee1fee14c"
        self.phone_number = "+380505812213"
        self.openai_key = "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"
        
        self.client = None
        self.openai_client = None
        self.nicknames = []
        self.allowed_senders = []
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
    
    def load_allowed_senders(self):
        """Load allowed senders from file"""
        try:
            with open('allowed_senders.txt', 'r', encoding='utf-8') as f:
                senders = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                self.allowed_senders = senders
                print(f"👥 Loaded {len(senders)} allowed senders from allowed_senders.txt")
                return True
        except FileNotFoundError:
            print("❌ allowed_senders.txt not found")
            return False
        except Exception as e:
            print(f"❌ Error loading allowed senders: {e}")
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
            # Load configuration files
            self.load_nicknames()
            self.load_allowed_senders()
            
            # Initialize Telegram client
            self.client = TelegramClient('telegram_session', int(self.api_id), self.api_hash)
            
            # Initialize OpenAI client
            self.openai_client = openai.OpenAI(api_key=self.openai_key)
            
            print("✅ Clients initialized successfully")
            print(f"📤 Ready to send to: {len(self.nicknames)} users")
            print(f"📥 Will respond to: {len(self.allowed_senders)} users")
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
    
    async def process_message_with_chatgpt(self, message, username):
        """Process message through ChatGPT"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are a helpful assistant responding to messages from Telegram user @{username}. Keep responses friendly, helpful, and concise."},
                    {"role": "user", "content": message}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ ChatGPT error: {e}")
            return "Sorry, I'm having trouble processing your message right now."
    
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
    
    async def send_first_messages(self):
        """Send first messages to all nicknames with random delays"""
        if not self.nicknames:
            print("❌ No nicknames loaded. Please check nicknames.txt")
            return
        
        print(f"📤 Starting first message campaign to {len(self.nicknames)} users...")
        print(f"⏱️ This will take approximately {len(self.nicknames) * 3.5:.1f} minutes")
        print("🔄 Each message is sent individually with 2-5 minute delays")
        
        # First message to send
        first_message = """Привет! 👋

Хочу пригласить тебя в интересный канал по крипте и трейдингу. 

Там делимся полезной информацией, анализом рынка и обсуждаем актуальные темы.

Интересно? Могу добавить в канал если хочешь."""
        
        successful = 0
        failed = 0
        
        for i, nickname in enumerate(self.nicknames):
            try:
                print(f"📤 [{i+1}/{len(self.nicknames)}] Sending to @{nickname}...")
                
                success = await self.send_message_to_user(nickname, first_message)
                if success:
                    print(f"✅ First message sent to @{nickname}")
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
        
        print(f"📊 First message campaign complete!")
        print(f"✅ Successfully sent: {successful}")
        print(f"❌ Failed to send: {failed}")
        print(f"📝 All results logged to {self.message_log_file}")
        
        return {"successful": successful, "failed": failed}
    
    async def setup_message_handler(self):
        """Set up message handler for incoming messages from multiple users"""
        @self.client.on(events.NewMessage(incoming=True))
        async def handle_new_message(event):
            try:
                sender = await event.get_sender()
                if isinstance(sender, User):
                    username = sender.username or f"user_{sender.id}"
                    message_text = event.message.text
                    
                    # Process messages from allowed senders
                    if username in self.allowed_senders:
                        print(f"📥 Received message from @{username}: {message_text}")
                        
                        # Process with ChatGPT
                        print("🤖 Processing with ChatGPT...")
                        chatgpt_response = await self.process_message_with_chatgpt(message_text, username)
                        
                        # Send response back
                        print(f"📤 Sending response to @{username}: {chatgpt_response}")
                        success = await self.send_message_to_user(username, chatgpt_response)
                        
                        if success:
                            print("✅ Response sent successfully!")
                        else:
                            print("❌ Failed to send response")
                    else:
                        print(f"📝 Message from @{username} (ignored - not in allowed senders)")
                        
            except Exception as e:
                print(f"❌ Error handling message: {e}")
    
    async def run(self):
        """Main run method"""
        try:
            # Initialize
            if not await self.initialize():
                return False
            
            # Connect to Telegram
            if not await self.connect_and_auth():
                return False
            
            print("🤖 Send and Listen Bot is ready!")
            print(f"📋 Nicknames to send to:")
            for i, nick in enumerate(self.nicknames, 1):
                print(f"  {i}. @{nick}")
            print("-" * 50)
            
            # Step 1: Send first messages
            print("🚀 STEP 1: Sending first messages to all users...")
            results = await self.send_first_messages()
            
            print(f"\n📊 First message results:")
            print(f"✅ Successfully sent: {results['successful']}")
            print(f"❌ Failed to send: {results['failed']}")
            
            # Step 2: Start listening for responses
            print("\n🎧 STEP 2: Starting to listen for responses...")
            print("🤖 ChatGPT bot mode activated!")
            print(f"📥 Listening for messages from: {', '.join(['@' + user for user in self.allowed_senders])}")
            print("🛑 Press Ctrl+C to stop")
            print("-" * 50)
            
            # Set up message handler and start listening
            await self.setup_message_handler()
            
            # Keep running until interrupted
            await self.client.run_until_disconnected()
            
        except KeyboardInterrupt:
            print("\n👋 Bot stopped by user")
        except Exception as e:
            print(f"❌ Bot error: {e}")
        finally:
            if self.client:
                await self.client.disconnect()
                print("🔌 Disconnected from Telegram")

async def main():
    """Main function"""
    bot = SendAndListenBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
