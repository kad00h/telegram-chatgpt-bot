#!/usr/bin/env python3
"""
Send First Messages and Listen for Responses - TEST MODE
Sends messages simultaneously and listens for responses at the same time
"""

import asyncio
import openai
import json
import datetime
from telethon import TelegramClient, events
from telethon.tl.types import User

class SendAndListenTestBot:
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
    
    async def send_test_messages_simultaneously(self):
        """Send test messages to all nicknames simultaneously"""
        if not self.nicknames:
            print("❌ No nicknames loaded. Please check nicknames.txt")
            return
        
        print(f"🧪 TEST MODE: Sending messages simultaneously to {len(self.nicknames)} users...")
        print("⚡ All messages will be sent at the same time!")
        
        # Test message to send
        test_message = """🧪 TEST MESSAGE

Это тестовое сообщение для проверки работы бота.

Если ты получил это сообщение, значит бот работает правильно!"""
        
        # Create tasks for all messages
        tasks = []
        for nickname in self.nicknames:
            task = self.send_message_to_user(nickname, test_message)
            tasks.append(task)
        
        # Send all messages simultaneously
        print("🚀 Sending all messages now...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count results
        successful = 0
        failed = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Failed to send to @{self.nicknames[i]}: {result}")
                failed += 1
            elif result:
                print(f"✅ Test message sent to @{self.nicknames[i]}")
                successful += 1
            else:
                print(f"❌ Failed to send to @{self.nicknames[i]}")
                failed += 1
        
        print(f"📊 Test message results:")
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
            
            print("🤖 Send and Listen Test Bot is ready!")
            print(f"📋 Nicknames to send to:")
            for i, nick in enumerate(self.nicknames, 1):
                print(f"  {i}. @{nick}")
            print("-" * 50)
            
            # Set up message handler FIRST (so we can listen while sending)
            print("🎧 Setting up message listener...")
            await self.setup_message_handler()
            print("✅ Message listener is active!")
            print("💬 You can now send messages to test ChatGPT while the bot is running")
            print("-" * 50)
            
            # Step 1: Send test messages simultaneously
            print("🧪 STEP 1: Sending test messages simultaneously...")
            results = await self.send_test_messages_simultaneously()
            
            print(f"\n📊 Test message results:")
            print(f"✅ Successfully sent: {results['successful']}")
            print(f"❌ Failed to send: {results['failed']}")
            
            # Step 2: Continue listening for responses
            print("\n🎧 STEP 2: Listening for responses...")
            print("🤖 ChatGPT bot mode is active!")
            print(f"📥 Listening for messages from: {', '.join(['@' + user for user in self.allowed_senders])}")
            print("💬 Send a message to any of these users to test ChatGPT")
            print("🛑 Press Ctrl+C to stop")
            print("-" * 50)
            
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
    bot = SendAndListenTestBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
