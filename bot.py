import telebot
import openai

print('hi')
# bot = telebot.TeleBot ('<Your telegram bot token>')

# openai.api_key = '<Your openai API token>'

# def generate_answer(text):
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "user", "content": text},
#             ]
#         )

#         result = ''
#         for choice in response.choices:
#             result += choice.message.content

#     except Exception as e:
#         return f"Oops!! Some problems with openAI. Reason: {e}"

#     return result


# @bot.message_handler(content_types=['text'])
# def send_text(message):
#     answer = generate_answer(message.text)
#     bot.send_message(message.chat.id, answer)

# bot.polling()
