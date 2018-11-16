import logging
import praw
import os
import telebot
import time
from webhook import WebHook
from dotenv import load_dotenv

welcome_message = """
Hi there, I am Reddit Bot.
I am here to help you dealing with Reddit!
To read articles type: {subreddit} {submission_type}.
For example: /archlinux hot.
Submission type can be: controversial|gilded|hot|new|rising|top.
"""

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
    bot.reply_to(message, welcome_message)


@bot.message_handler(regexp=r"^\/?\w+ (controversial|gilded|hot|new|rising|top)$")
def send_aricles(message):
    subreddit_name, submission_type = message.text.replace("/", "").split()
    subreddit = reddit.subreddit(subreddit_name)
    limit = int(os.getenv("REDDIT_POSTS_LIMIT"))
    delay = int(os.getenv("TG_SENDING_DELAY"))
    for submission in getattr(subreddit, submission_type)(limit=limit):
        bot.reply_to(message, "{}\n{}\n{}".format(
            submission.shortlink,
            submission.title,
            submission.url)
        )
        time.sleep(delay)


def run_web_hook():
    webhook = WebHook(
        telebot,
        bot,
        os.getenv("TG_API_TOKEN"),
        os.getenv("WEBHOOK_SSL_CERT"),
        os.getenv("WEBHOOK_SSL_PRIV")
    )
    url = "https://{}:{}/{}".format(
        os.getenv("WEBHOOK_HOST"),
        os.getenv("WEBHOOK_PORT"),
        os.getenv("TG_API_TOKEN")
    )
    bot.set_webhook(url=url, certificate=open(os.getenv("WEBHOOK_SSL_CERT"), 'r'))
    webhook.run(os.getenv("WEBHOOK_HOST"), os.getenv("WEBHOOK_PORT"))


if os.getenv("MODE") == "polling":
    bot.polling()

elif os.getenv("MODE") == "webhook":
    run_web_hook()

else:
    raise TypeError("Invalid MODE for telegram bot")