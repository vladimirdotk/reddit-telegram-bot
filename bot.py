import logging
import praw
import os
import telebot
import time
from dotenv import load_dotenv

load_dotenv()

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

reddit = praw.Reddit(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    username=os.getenv("USERNAME"),
    password=os.getenv("PASSWORD"),
    user_agent=os.getenv("USER_AGENT"),
)

bot = telebot.TeleBot(os.getenv("TG_API_TOKEN"))

if os.getenv("USE_PROXY"):
    telebot.apihelper.proxy = {'https': os.getenv("PROXY_STRING")} 

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
Hi there, I am Reddit Bot.
I am here to help you dealing with Reddit!\
To read articles type: {subreddit} {submission_type}.
For example: /archlinux hot.
Submission type can be: controversial|gilded|hot|new|rising|top.
""")

@bot.message_handler(regexp=r"^\/?\w+ (controversial|gilded|hot|new|rising|top)$")
def send_aricles(message):
    subreddit_name, submission_type = message.text.replace("/", "").split()
    subreddit = reddit.subreddit(subreddit_name)
    limit = int(os.getenv("REDDIT_POSTS_LIMIT"))
    delay = int(os.getenv("TG_SENDING_DELAY"))
    for submission in getattr(subreddit, submission_type)(limit=limit):
        bot.reply_to(message, f"{submission.shortlink}\n{submission.title}\n{submission.url}")
        time.sleep(delay)

if os.getenv("MODE") == "polling":
    bot.polling()
elif os.getenv("MODE") == "webhook":
    raise NotImplementedError
else:
    raise TypeError("Invalid MODE for telegram bot")