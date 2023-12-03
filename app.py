import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters
import openai

load_dotenv()

# Set up your OpenAI API credentials
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Set up your Telegram bot token
bot_token = os.getenv('BOT_TOKEN')

# OpenAI model configuration
OPENAI_MODEL = "gpt-3.5-turbo"
SYSTEM_MESSAGE = {"role": "system", "content": "You are a helpful assistant."}

# Conversation history dictionary
conversation_history = {}

def sanitize_input(user_message):
    # Remove any potentially harmful content
    # This is a basic example, you might need a more comprehensive check depending on your use case
    user_message = user_message.replace("<", "").replace(">", "")

    # Limit the length of the message
    MAX_MESSAGE_LENGTH = 500
    if len(user_message) > MAX_MESSAGE_LENGTH:
        user_message = user_message[:MAX_MESSAGE_LENGTH]

    return user_message

async def gpt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the user's message
    user_message = update.message.text
    print(f"Received message: {user_message}")

    # Sanitize the user's message
    user_message = sanitize_input(user_message)

    # Retrieve the conversation history for this user
    user_id = update.message.from_user.id
    conversation = conversation_history.get(user_id, [])

    # Append the user's message to the conversation
    conversation.append({"role": "user", "content": user_message})

    try:
        # Determine which model to use based on the user's message
        model = OPENAI_MODEL
        if "code" in user_message.lower():
            model = "codex"

        # Create a chat model using the conversation history
        chat_model = openai.ChatCompletion.create(
            model=model,
            messages=[SYSTEM_MESSAGE] + conversation,
        )

        # Get the assistant's reply
        assistant_reply = chat_model['choices'][0]['message']['content']

        # Append the assistant's reply to the conversation history
        conversation.append({"role": "assistant", "content": assistant_reply})

        # Update the conversation history for this user
        conversation_history[user_id] = conversation

        # Send the reply to the user
        await update.message.reply_text(assistant_reply)

        # Log the bot's reply
        print(f"Sent reply: {assistant_reply}")

    except Exception as e:
        print(f"Error during OpenAI API request: {e}")

if __name__ == '__main__':
    print('Starting the App')
    app = Application.builder().token(bot_token).build()

    # Commands
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_command))  # Use filters.TEXT to trigger for any text message that is not a command

    # Polling
    print('Polling...')
    app.run_polling(poll_interval=5)