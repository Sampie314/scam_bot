import telebot
import json
import logging
import json
from scamscraper import scrape_scam_stories
from langchain_openai import ChatOpenAI
# from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    # HumanMessagePromptTemplate,
    # SystemMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents.openai_tools.base import create_openai_tools_agent
from langchain.agents.agent import AgentExecutor
import agenttools

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
logging.getLogger("httpcore.http11").setLevel(logging.WARNING)
logging.getLogger("openai._base_client").setLevel(logging.WARNING)
logging.getLogger("httpcore.connection").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# API keys
with open('keys.json') as keys_file:
    keys = json.load(keys_file)
bot = telebot.TeleBot(keys['TELEGRAM_BOT_TOKEN'])

# System prompt
with open('config.json') as config_file:
    config = json.load(config_file)
system_prompt = config['SYSTEM_CONTENT']
welcome_message = config['WELCOME_MESSAGE']
help_message = config['HELP_MESSAGE']
convo_buffer_window = config['CONVERSATION_BUFFER_WINDOW']

# Initialise chat client and conversation history
chat = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2, openai_api_key=keys['OPENAI_API_KEY'])
conversation_histories = {} # key: val = chat id : ChatMessaageHistory
prompt = ChatPromptTemplate.from_messages([
    ('system', system_prompt),
    ('ai', welcome_message),
    MessagesPlaceholder("chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])
tools = [agenttools.multiplication_tool]
ag = create_openai_tools_agent(chat, tools, prompt)


def generate_answer(chat_id, text):
    logger.debug('generate_answer function called')

    # Create new chat history if new conversation
    if chat_id not in conversation_histories:
        conversation_histories[chat_id] = ConversationBufferWindowMemory(memory_key='chat_history', k=convo_buffer_window, return_messages=True)

    # Instantiate agent with selected memory
    agent = AgentExecutor.from_agent_and_tools(
        agent = ag,
        tools = tools,
        llm = chat,
        verbose = True,
        max_iterations = 3,
        memory = conversation_histories[chat_id]
    )
        
    try:
        response = agent.invoke({"input": text})
        
        result = ''
        result += response["output"]

        # For tracking token usage NO LONGER AVAILABLE INFO
        # result += f"\n Completion tokens: {response.response_metadata['token_usage']['completion_tokens']}"
        # result += f"\n Prompt tokens: {response.response_metadata['token_usage']['prompt_tokens']}"

        logger.info(f'Conversation history: {conversation_histories[chat_id]}')
        logger.debug(f'Reply: {result}')

    except Exception as e:
        return f"Oops!! Some problems with openAI. Reason: {e}"

    return result

def generate_counter_measures(scam_stories):
    print("Generating counter measures...")
    counter_measures_prompt = f"""
    Given the following recent scam stories in Singapore:
    {scam_stories}
    
    Suggest some counter measures to help people avoid falling victim to these scams.
    """
    
    counter_measures = chat.predict(counter_measures_prompt)
    print("Counter measures generated.")
    return counter_measures

def generate_newsletter(scam_stories, counter_measures):
    print("Generating newsletter...")
    newsletter_prompt = f"""
    Latest scam stories in Singapore:

    {scam_stories}

    Tips to protect yourself from these scams:

    {counter_measures}

    Write a concise newsletter message to summarize the latest scam stories and provide tips on how to protect oneself from these scams. You can also add emojis. Use the following format:

    🚨 Scam Alert Newsletter 🚨

    📰 Latest Scam Stories in Singapore:
    1. [Scam Story 1]
    2. [Scam Story 2]
    3. [Scam Story 3]

    💡 Tips to Protect Yourself from These Scams:
    1. [Tip 1]
    2. [Tip 2]
    3. [Tip 3]

    Remember to stay vigilant and informed. Follow these tips to safeguard your personal information and finances. Together, we can combat scams effectively!
    #ScamPreventionNewsletter
    """
    
    newsletter = chat.predict(newsletter_prompt)
    print("Newsletter generated.")
    return newsletter

########## Command Handlers ############
@bot.message_handler(commands=['start'])
def start_new(message):
    logger.debug('start_new function called')

    # Refresh conversation history
    conversation_histories[message.chat.id] = ConversationBufferWindowMemory(memory_key='chat_history', k=convo_buffer_window, return_messages=True)

    keyboard = telebot.types.InlineKeyboardMarkup()
    scam_newsletter_button = telebot.types.InlineKeyboardButton(text="Get Scam Newsletter", callback_data="/scam_newsletter")
    keyboard.add(scam_newsletter_button)
    bot.send_message(message.chat.id, welcome_message, reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def display_help(message):
    logger.debug('display_help function called')

    bot.send_message(message.chat.id, help_message)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "/scam_newsletter":
        scam_newsletter(call.message)

def scam_newsletter(message):
    logger.debug('scam_newsletter function called')
    print("Received /scam_newsletter command.")
    
    try:
        # Scrape recent scams from https://www.scamalert.sg/stories
        print("Scraping recent scams...")
        scam_stories = scrape_scam_stories()
        print("Scam stories scraped.")
        
        # Prompt GPT for counter measures
        counter_measures = generate_counter_measures(scam_stories)
        
        # Generate newsletter message
        newsletter = generate_newsletter(scam_stories, counter_measures)
        
        # Send newsletter message to user
        print("Sending newsletter to user.")
        bot.send_message(message.chat.id, newsletter)
        print("Newsletter sent.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        bot.send_message(message.chat.id, "Oops! Something went wrong. Please try again later.")

########################################
    
@bot.message_handler(content_types=['text'])
def send_text(message):
    logger.debug('send_text function called')

    answer = generate_answer(message.chat.id, message.text)
    bot.send_message(message.chat.id, answer)


if __name__ == '__main__':
    bot.infinity_polling()