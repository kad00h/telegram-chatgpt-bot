#!/usr/bin/env python3
"""
Telegram + ChatGPT Bot
Listens for messages from @kad00h, processes them through ChatGPT, and sends responses back
"""

import asyncio
import openai
from telethon import TelegramClient, events
from telethon.tl.types import User

class TelegramChatGPTBot:
    def __init__(self):
        # Hardcoded credentials (from our working test)
        self.api_id = "21291198"
        self.api_hash = "def2b13f8fe9de6b655d3cdee1fee14c"
        self.phone_number = "+380505812213"
        self.openai_key = "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"
        
        self.client = None
        self.openai_client = None
        self.target_user = "kad00h"  # The user we're listening to
        
    async def initialize(self):
        """Initialize both Telegram and OpenAI clients"""
        try:
            # Initialize Telegram client
            self.client = TelegramClient('telegram_session', int(self.api_id), self.api_hash)
            
            # Initialize OpenAI client
            self.openai_client = openai.OpenAI(api_key=self.openai_key)
            
            print("✅ Clients initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize clients: {e}")
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
    
    async def process_message_with_chatgpt(self, message):
        """Process message through ChatGPT"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant responding to messages from Telegram users. Keep responses friendly, helpful, and concise."},
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
                username = '@' + username
            
            user = await self.client.get_entity(username)
            await self.client.send_message(user, message)
            return True
            
        except Exception as e:
            print(f"❌ Failed to send message to {username}: {e}")
            return False
    
    async def setup_message_handler(self):
        """Set up message handler for incoming messages"""
        @self.client.on(events.NewMessage(incoming=True))
        async def handle_new_message(event):
            try:
                sender = await event.get_sender()
                if isinstance(sender, User):
                    username = sender.username or f"user_{sender.id}"
                    message_text = event.message.text
                    
                    # Only process messages from our target user
                    if username == self.target_user:
                        print(f"📥 Received message from @{username}: {message_text}")
                        
                        # Process with ChatGPT
                        print("🤖 Processing with ChatGPT...")
                        chatgpt_response = await self.process_message_with_chatgpt(message_text)
                        
                        # Send response back
                        print(f"📤 Sending response to @{username}: {chatgpt_response}")
                        success = await self.send_message_to_user(username, chatgpt_response)
                        
                        if success:
                            print("✅ Response sent successfully!")
                        else:
                            print("❌ Failed to send response")
                    else:
                        print(f"📝 Message from @{username} (ignored - not target user)")
                        
            except Exception as e:
                print(f"❌ Error handling message: {e}")
    
    async def run(self):
        """Main run method"""
        try:
            # Initialize clients
            if not await self.initialize():
                return False
            
            # Connect to Telegram
            if not await self.connect_and_auth():
                return False
            
            # Set up message handler
            await self.setup_message_handler()
            
            print("🤖 Telegram + ChatGPT Bot is running!")
            print(f"📱 Listening for messages from @{self.target_user}")
            print("💬 Send a message to @kad00h to test the bot")
            print("🛑 Press Ctrl+C to stop")
            print("-" * 50)
            
            # Keep the bot running
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
    bot = TelegramChatGPTBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
