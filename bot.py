import telebot
from openai import OpenAI
import json
import logging

logging.basicConfig(level=logging.DEBUG)

# API keys
with open('keys.json') as keys_file:
    keys = json.load(keys_file)
bot = telebot.TeleBot(keys['TELEGRAM_BOT_TOKEN'])

# System prompt
with open('config.json') as config_file:
    config = json.load(config_file)
system_prompt = config['SYSTEM_CONTENT']

print(system_prompt)

client = OpenAI(
    # This is the default and can be omitted
    api_key=keys['OPENAI_API_KEY'],
)

def generate_answer(text):
    logging.debug('generate_answer function called')
    logging.debug(f'Text received: {text}')
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": system_prompt
                },
                {
                    "role": "user", 
                    "content": text
                },
            ]
        )
        logging.debug(f"Response: {response}")

        result = ''
        for choice in response.choices:
            result += choice.message.content

        # For tracking token usage
        result += f"\n Completion tokens: {response.usage.completion_tokens}"
        result += f"\n Prompt tokens: {response.usage.prompt_tokens}"

        logging.debug(f'Reply: {result}')

    except Exception as e:
        return f"Oops!! Some problems with openAI. Reason: {e}"

    return result


@bot.message_handler(content_types=['text'])
def send_text(message):
    logging.debug('send_text function called')

    answer = generate_answer(message.text)
    bot.send_message(message.chat.id, answer)

bot.polling()
