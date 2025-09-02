# Telegram Bot with ChatGPT Integration

This project implements a Telegram bot that automatically sends messages to users, receives responses, processes them through ChatGPT, and sends back AI-generated replies.

## Features

- **Account Status Checking**: Verifies if the Telegram account is active and not blocked
- **Automated Messaging**: Sends 2-3 predefined messages to all users from a nickname file
- **Message Reception**: Listens for incoming messages from users
- **ChatGPT Integration**: Processes received messages through OpenAI's ChatGPT API
- **Auto-Response**: Automatically sends ChatGPT responses back to users
- **Comprehensive Logging**: Detailed logging for monitoring and debugging
- **Rate Limiting**: Built-in delays to prevent API rate limiting issues

## Project Structure

```
TGChad/
├── config.py              # Configuration and environment variables
├── telegram_client.py     # Telegram client implementation
├── chatgpt_client.py      # ChatGPT API integration
├── main_bot.py           # Main bot orchestrator
├── nicknames.txt         # List of usernames to message
├── requirements.txt      # Python dependencies
├── plan.txt             # Original project plan
└── README.md            # This file
```

## Prerequisites

1. **Python 3.8+** installed on your system
2. **Telegram Account** with phone number
3. **Telegram API Credentials** (API ID and API Hash)
4. **OpenAI API Key** for ChatGPT integration

## Setup Instructions

### 1. Get Telegram API Credentials

1. Go to [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Go to "API development tools"
4. Create a new application
5. Note down your **API ID** and **API Hash**

### 2. Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com)
2. Sign up or log in
3. Navigate to "API Keys"
4. Create a new API key
5. Copy the key (it starts with `sk-`)

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root with the following variables:

```env
# Telegram API Credentials
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE_NUMBER=+1234567890

# OpenAI API Key
OPENAI_API_KEY=sk-your_openai_api_key_here
```

### 5. Configure User List

Edit `nicknames.txt` to include the usernames (without @) of users you want to message:

```
username1
username2
username3
```

### 6. Test ChatGPT Integration

Before running the full bot, test your ChatGPT API:

**Quick Test (Recommended for first time):**
```bash
python quick_chatgpt_test.py
```

**Comprehensive Test Suite:**
```bash
python test_chatgpt.py
```

**Windows Users:**
Double-click `test_chatgpt.bat` and choose your test type.

This will verify that your ChatGPT API key is working correctly before you start the Telegram bot.

## Usage

### Running the Bot

```bash
python main_bot.py
```

### First Run Authentication

On the first run, the bot will:
1. Send a verification code to your phone number
2. Prompt you to enter the code
3. If you have 2FA enabled, prompt for your password
4. Create a session file for future runs

### Bot Operation Flow

1. **Initialization**: Bot connects to Telegram and authenticates
2. **Status Check**: Verifies account is active and not blocked
3. **User Loading**: Reads usernames from `nicknames.txt`
4. **Message Sending**: Sends 2-3 predefined messages to all users
5. **Message Listening**: Waits for user responses
6. **ChatGPT Processing**: Sends received messages to ChatGPT API
7. **Auto-Response**: Sends ChatGPT replies back to users
8. **Continuous Operation**: Keeps running to handle ongoing conversations

## Configuration Options

Edit `config.py` to customize:

- **Message Templates**: Change the predefined messages sent to users
- **Delays**: Adjust timing between messages and API calls
- **ChatGPT Settings**: Modify model, token limits, and temperature
- **Logging**: Configure log levels and file paths

## Message Templates

The bot sends these default messages (configurable in `config.py`):

1. "Hello! How are you doing today?"
2. "I hope you're having a great day!"
3. "Just wanted to check in and say hi!"

## Logging

The bot creates detailed logs in `telegram_bot.log` including:
- Connection status
- Message sending/receiving
- ChatGPT API interactions
- Error messages and debugging information

## Error Handling

The bot includes comprehensive error handling for:
- Network connectivity issues
- API rate limiting
- Invalid usernames
- ChatGPT API failures
- Authentication problems

## Security Considerations

- **API Keys**: Never commit your `.env` file to version control
- **Session Files**: The `telegram_session` file contains authentication data
- **Rate Limiting**: Built-in delays prevent spam and API abuse
- **User Privacy**: Only processes messages from users in your nickname list

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify your API ID and API Hash
   - Check your phone number format (+1234567890)
   - Ensure your Telegram account is active

2. **ChatGPT API Errors**
   - Verify your OpenAI API key
   - Check your OpenAI account balance
   - Ensure the API key has proper permissions

3. **Message Sending Failures**
   - Verify usernames exist and are accessible
   - Check if users have blocked your account
   - Ensure your account isn't rate-limited

4. **Connection Issues**
   - Check your internet connection
   - Verify Telegram servers are accessible
   - Try restarting the bot

### Debug Mode

Set `LOG_LEVEL = "DEBUG"` in `config.py` for more detailed logging.

## Performance Optimization

- **Batch Processing**: Messages are processed efficiently with built-in delays
- **Rate Limiting**: Prevents API abuse and account restrictions
- **Session Persistence**: Reuses authentication sessions for faster startup
- **Async Operations**: Non-blocking I/O for better performance

## Monitoring

Monitor the bot's operation through:
- Log files (`telegram_bot.log`)
- Console output
- Telegram message delivery status
- ChatGPT API response times

## Contributing

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Please ensure compliance with:
- Telegram's Terms of Service
- OpenAI's API Usage Policies
- Local laws and regulations

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Verify your configuration
4. Check API service status pages

## Future Enhancements

Potential improvements:
- Web interface for bot management
- Database storage for conversation history
- Multiple ChatGPT model support
- Advanced message scheduling
- User analytics and reporting
- Multi-account support
