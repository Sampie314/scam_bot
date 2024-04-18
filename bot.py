import telebot
import json
import logging
import json
import time
import validators
import textwrap
from cachetools import TTLCache
from scamscraper import scrape_scam_stories
from urlscan import submit_url_to_urlscan
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
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
import checkscam


cache = TTLCache(maxsize=1, ttl=6 * 60 * 60)  # maxsize=1 because we only need to cache one newsletter

# Dictionary to keep track of the state of each user
url_scan_pending = {}
scam_message_pending = set()
import collections
seen_scams = collections.defaultdict(int)

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


def generate_newsletter(scam_stories, counter_measures, first_read_more_link):
    print("Generating newsletter...")
    newsletter_prompt = f"""
    Latest scam stories in Singapore:

    {scam_stories}

    Tips to protect yourself from these scams:

    {counter_measures}

    Write a SHORT AND CONCISED newsletter message to summarize the latest scam stories and provide tips on how to protect oneself from these scams.
    For the tips refer to the Resource Guide: Understanding and Responding to Scams and tailor it to the specific scam stories.
    Use the following format:

    🚨 Scam Alert Newsletter 🚨

    📰 Latest Scam Stories in Singapore:

    1. [Scam Story 1] 

    Read more at (insert link)

    2. [Scam Story 2] 

    Read more at (insert link)

    3. [Scam Story 3] 

    Read more at (insert link)
    ...

    💡 Tips to Protect Yourself from These Scams:

    1. [Tip 1]

    2. [Tip 2]

    3. [Tip 3]
    ...

    Download the SPF's latest Weekly Scams Bulletin at {first_read_more_link} for more scam stories and prevention tips.
    #ScamPreventionNewsletter

    make sure the newsletter is short, concise, and informative.
    """
    print(newsletter_prompt)
    newsletter = chat.predict(newsletter_prompt)
    print("Newsletter generated.")
    return newsletter


def generate_scan_results_message(scan_data):
    print("Generating scan results message...")

    # Assuming 'scan_data' is a dictionary containing the formatted results from the 'format_scan_results' function
    submitted_url = scan_data.get('Submitted URL', 'N/A')
    results_url = scan_data.get('Results URL', 'N/A')
    malicious_score = scan_data.get('Malicious Score', 0)
    page_title = scan_data.get('Page Title', 'N/A')
    primary_url = scan_data.get('Primary URL', 'N/A')
    ip_addresses = len(scan_data.get('IP Addresses', []))
    countries = scan_data.get('Countries', [])

    # Determine the malicious status based on the score
    malicious_status = ""

    if malicious_score > 50:
        malicious_status = "🔴 Highly Malicious - This website is very likely to be harmful."
    elif malicious_score > 0:
        malicious_status = "🟠 Suspicious - This website could be risky."
    elif malicious_score == 0:
        malicious_status = "🟡 Uncertain - This website's safety is unclear."
    elif malicious_score > -50:
        malicious_status = "🟢 Likely Safe - This website is probably harmless."
    else:
        malicious_status = "🟢 Very Safe - This website is almost certainly legitimate."

    country_label = "country" if len(countries) == 1 else "countries"

    # Build the message
    scan_results_message = textwrap.dedent(f"""
    🚨 URL Scan Results 🚨

    🔗 Submitted URL: {submitted_url}
    🌐 Website Title: {page_title}
    🏠 Primary/Base URL Detected: {primary_url}
    📉 Malicious Score: {malicious_score}% 
    {malicious_status}

    🖥️ IP Addresses: {ip_addresses} IPs were contacted in {len(countries)} {country_label}
    🌍 Countries Contacted: {', '.join(countries) if countries else 'None'}

    Further Details: Read the full report at the following urlscan.io website for more in-depth analysis.
    {results_url}
    """)
    logger.info("Formatted Scan Results Message:")
    logger.info(scan_results_message)
    return scan_results_message


def generate_scam_message_check(message: str, seen: int, chat_id):
    logger.debug('generate_scam_message_check function called')
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
        
    prompt = checkscam.generate_check_scam_prompt(message, seen)

    try:
        response = agent.invoke({"input": prompt})
        
        result = ''
        result += response["output"]

        logger.info(f'Conversation history: {conversation_histories[chat_id]}')
        logger.debug(f'Reply: {result}')

    except Exception as e:
        return f"Oops!! Some problems with openAI. Reason: {e}"
    
    return result


def follow_up_options(chat_id):
    # follow-up message
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        telebot.types.InlineKeyboardButton("Generate Scam Newsletter", callback_data='/scam_newsletter'),
        telebot.types.InlineKeyboardButton("Scan a URL", callback_data='scan_url'),
        telebot.types.InlineKeyboardButton("Stop the Bot", callback_data='stop_bot'),
        telebot.types.InlineKeyboardButton("Check Scam Message", callback_data='check_scam_message'),
        telebot.types.InlineKeyboardButton("Help", callback_data='help')
    )
    bot.send_message(chat_id, "What would you like to do next?", reply_markup=markup)


########## Command Handlers ############
@bot.message_handler(commands=['start'])
def start_new(message):
    logger.debug('start_new function called')

    # Refresh conversation history
    conversation_histories[message.chat.id] = ConversationBufferWindowMemory(memory_key='chat_history', k=convo_buffer_window, return_messages=True)

    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        telebot.types.InlineKeyboardButton("Generate Scam Newsletter", callback_data='/scam_newsletter'),
        telebot.types.InlineKeyboardButton("Scan a URL", callback_data='scan_url'),
        telebot.types.InlineKeyboardButton("Stop the Bot", callback_data='stop_bot'),
        telebot.types.InlineKeyboardButton("Check Scam Message", callback_data='check_scam_message'),
        telebot.types.InlineKeyboardButton("Help", callback_data='help')
    )
    bot.send_message(message.chat.id, welcome_message, reply_markup=markup)


@bot.message_handler(commands=['help'])
def display_help(message):
    logger.debug('display_help function called')

    bot.send_message(message.chat.id, help_message, parse_mode='HTML')
    follow_up_options(message.chat.id) # send follow-up message


@bot.message_handler(content_types=['text'])
def send_text(message):
    user_id = message.from_user.id

    # Check if the message is a command (specifically looking for '/cancel')
    if message.text.strip() == '/cancel':
        cancel(message)
        return

    if user_id in url_scan_pending and url_scan_pending[user_id]:
        url = message.text.strip()
        logger.debug("Received message: " + url)
        logger.debug("Checking URL validity...")

        if is_valid_url(url):
            bot.send_message(message.chat.id, "Scan in progress. I'll send you the results shortly.")
            scan_result = submit_url_to_urlscan(url, logger)

            # Check if the result is an error string or a dictionary
            if isinstance(scan_result, str):
                bot.send_message(message.chat.id, scan_result)  # Send the error message directly
            else:
                results = generate_scan_results_message(scan_result)
                bot.send_message(message.chat.id, results)

            follow_up_options(message.chat.id) # send follow-up message
            url_scan_pending[user_id] = False  # Reset the state ONLY after a valid URL is processed

        else:
            bot.send_message(message.chat.id, "That doesn't seem to be a valid URL. Please send a valid URL, or use /cancel to stop the URL submission process.")
    
    elif user_id in scam_message_pending:
        scam_message = message.text.strip()
        logger.debug(f"Received message: {scam_message}" )

        seen_times = seen_scams[scam_message]
        seen_scams[scam_message] += 1

        scam_message_pending.discard(user_id)
        reply = generate_scam_message_check(scam_message, seen_times, message.chat.id)
        bot.send_message(message.chat.id, f'{reply}')  

    else:
        answer = generate_answer(message.chat.id, message.text)
        bot.send_message(message.chat.id, answer)

        # send follow-up message
        follow_up_options(message.chat.id)


# cancel function in case users want to stop submitting links
@bot.message_handler(commands=['cancel'])
def cancel(message):
    user_id = message.from_user.id
    if user_id in url_scan_pending and url_scan_pending[user_id]:
        bot.send_message(message.chat.id, "URL submission canceled.")
        url_scan_pending[user_id] = False  # Reset the state
    else:
        bot.send_message(message.chat.id, "No active URL submission found.")


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "/scam_newsletter":
        scam_newsletter(call.message)
    elif call.data == "scan_url":
        # Indicate that the next message should be treated as a URL to scan
        url_scan_pending[call.from_user.id] = True
        bot.send_message(call.message.chat.id, "Please send me the URL you want to scan.")
    elif call.data == 'stop_bot':
        # Refresh conversation history
        conversation_histories[call.message.chat.id] = ConversationBufferWindowMemory(memory_key='chat_history', k=convo_buffer_window, return_messages=True)
        # Optionally stop the bot or just say goodbye
        bot.send_message(call.message.chat.id, "Goodbye!")
    elif call.data == 'help':
        # Send help information
        display_help(call.message)
    elif call.data == 'check_scam_message':
        # Indicate that the next message should be treated as a scam message to check
        scam_message_pending.add(call.from_user.id)
        bot.send_message(call.message.chat.id, "Forward or copy paste a message that you would like us to check here!")

    bot.answer_callback_query(call.id)


def scam_newsletter(message):
    logger.debug('scam_newsletter function called')
    print("Received /scam_newsletter command.")

    # Check if the newsletter is cached and still valid
    cached_newsletter = cache.get('newsletter')
    if cached_newsletter:
        print("Sending cached newsletter.")
        bot.send_message(message.chat.id, cached_newsletter)
        return

    try:
        # Scrape recent scams from https://www.scamalert.sg/stories
        print("Scraping recent scams...")
        scam_stories, first_read_more_link = scrape_scam_stories()
        print("Scam stories scraped.")

        # Prompt GPT for counter measures
        counter_measures = generate_counter_measures(scam_stories)

        # Generate newsletter message
        newsletter = generate_newsletter(scam_stories, counter_measures, first_read_more_link)

        # Cache the newsletter
        cache['newsletter'] = newsletter

        # Send newsletter message to user
        print("Sending newsletter to user.")
        bot.send_message(message.chat.id, newsletter)
        print("Newsletter sent.")

        # send follow-up message
        follow_up_options(message.chat.id)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        bot.send_message(message.chat.id, "Oops! Something went wrong. Please try again later.")


def is_valid_url(url):
    if validators.url(url):
        logger.info("URL is valid: " + url)
        return True
    # Check and fix URLs without schema
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
        if validators.url(url):
            logger.info("URL is valid after adding HTTP: " + url)
            return True
    logger.warning("URL is not valid: " + url)
    return False


########################################
    
@bot.message_handler(content_types=['text'])
def send_text(message):
    logger.debug('send_text function called')

    answer = generate_answer(message.chat.id, message.text)
    bot.send_message(message.chat.id, answer)


if __name__ == '__main__':
    bot.infinity_polling()