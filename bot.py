import telebot
import json
import logging
import json
from langchain_openai import ChatOpenAI
# from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    # HumanMessagePromptTemplate,
    # SystemMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain.memory import ChatMessageHistory

logging.basicConfig(level=logging.DEBUG)

# API keys
with open('keys.json') as keys_file:
    keys = json.load(keys_file)
bot = telebot.TeleBot(keys['TELEGRAM_BOT_TOKEN'])

# System prompt
with open('config.json') as config_file:
    config = json.load(config_file)
system_prompt = config['SYSTEM_CONTENT']

# Initialise chat client and conversation history
chat = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2, openai_api_key=keys['OPENAI_API_KEY'])
conversation_histories = {} # key: val = chat id : ChatMessaageHistory
prompt = ChatPromptTemplate.from_messages([
    (
        'system',
        system_prompt
    ),
    MessagesPlaceholder(variable_name='messages')
])
chain = prompt | chat


def generate_answer(chat_id, text):
    logging.debug('generate_answer function called')

    # Update chat history
    if chat_id not in conversation_histories:
        conversation_histories[chat_id] = ChatMessageHistory()
    conversation_histories[chat_id].add_user_message(text)
    
    try:
        response = chain.invoke({"messages": conversation_histories[chat_id].messages})

        logging.debug(f"Response: {response}")

        result = ''
        result += response.content

        # For tracking token usage
        result += f"\n Completion tokens: {response.response_metadata['token_usage']['completion_tokens']}"
        result += f"\n Prompt tokens: {response.response_metadata['token_usage']['prompt_tokens']}"

        # Update chat history
        conversation_histories[chat_id].add_ai_message(response.content)

        logging.info(f'Conversation history: {conversation_histories[chat_id].messages}')
        logging.debug(f'Reply: {result}')

    except Exception as e:
        return f"Oops!! Some problems with openAI. Reason: {e}"

    return result


@bot.message_handler(content_types=['text'])
def send_text(message):
    logging.debug('send_text function called')

    answer = generate_answer(message.chat.id, message.text)
    bot.send_message(message.chat.id, answer)

if __name__ == '__main__':
    bot.polling()
