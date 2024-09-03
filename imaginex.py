#!/bin/python3
# Tool by VritraSecz

import os
import requests
import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from requests.structures import CaseInsensitiveDict
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)
from colorama import Fore, Style
import sys
from config import *

# Define color codes
RED = Fore.LIGHTRED_EX
YELLOW = Fore.LIGHTYELLOW_EX
CYAN = Fore.LIGHTCYAN_EX
GREEN = Fore.LIGHTGREEN_EX
WHITE = Fore.LIGHTWHITE_EX
BLUE = Fore.LIGHTBLUE_EX
BLACK = Fore.LIGHTBLACK_EX
RESET = Style.RESET_ALL

print(f"{WHITE}~ {RED}Created by{YELLOW} @Devil")

def check_internet_connectivity():
    try:

        response = requests.get("http://www.google.com", timeout=5)

        if response.status_code == 200:
            print(f"{WHITE}~ {CYAN}Internet is connected.")
        else:
            print(f"{RED}Failed to connect to the internet. Status code: {response.status_code}{RESET}")
            sys.exit(1)
    except requests.ConnectionError:
        print(f"{RED}No internet connection available.{RESET}")
        sys.exit(1) 
    except requests.Timeout:
        print(f"{RED}Check your internet connection.{RESET}")
        sys.exit(1) 
    except requests.RequestException as e:
        print(f"{RED}An error occurred: {e}{RESET}")
        sys.exit(1) 

check_internet_connectivity()

# Set up OpenAI API key

def generate_image(prompt):
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["Authorization"] = f"Bearer {openai.api_key}"

    data = {
        "prompt": prompt,
        "num_images": 1,
        "size": "512x512",
        "response_format": "url"
    }

    resp = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=data)

    if resp.status_code != 200:
        print(f"\n{RED}Failed to generate image. HTTP Status Code: {resp.status_code}\n")
        print(f"Response Text: {resp.text}")
        raise ValueError("\nFailed to generate image\n")

    response_json = resp.json()
    return response_json["data"][0]["url"]

def download_image(url):
    response = requests.get(url)
    extension = url.split(".")[-1]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{timestamp}.jpg"
    with open(file_name, "wb") as f:
        f.write(response.content)

    return file_name 

def gen(update: Update, context: CallbackContext):
    update.message.reply_text('Generating image. Please wait...')

    input_text = update.message.text.split('/gen', 1)

    if len(input_text) < 2 or not input_text[1].strip():
        update.message.reply_text('Please provide a description for generating an image after the /gen command.')
        return

    try:
        image_url = generate_image(input_text[1].strip())
        file_path = download_image(image_url)

        with open(file_path, "rb") as photo:
            update.message.reply_photo(photo)

        os.remove(file_path)
    except Exception as e:
        print(f"{RED}Error generating or sending image: {e}")
        update.message.reply_text('Sorry, there was an error generating or sending the image.')

def ask(update: Update, context: CallbackContext):
    update.message.reply_text('Processing your question. Please wait...')

    input_text = update.message.text.split('/ask', 1)

    if len(input_text) < 2 or not input_text[1].strip():
        update.message.reply_text('Please provide a question after the /ask command. For example, /ask How are you?')
        return

    try:
        response_text = get_openai_response(input_text[1].strip())

        update.message.reply_text(response_text)
    except Exception as e:
        print(f"Error processing question: {e}")
        update.message.reply_text('Sorry, there was an error processing your question.')

def get_openai_response(question):
    try:
        response = client.completions.create(model='gpt-3.5-turbo-instruct',
        prompt=question,
        max_tokens=3048,
        top_p=1.0,
        presence_penalty=0.0)
        return response.choices[0].text  
    except Exception as e:
        print(e)
        return 'Sorry, there was an error processing your question.'

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! I'm ImagineX created by @VritraSecz. Use /help to see available commands.")

def help_command(update: Update, context: CallbackContext):
    help_text = "Available commands:\n/start - Start the bot\n/help - Show this message\n/gen - Generate image by text\n/ask - Ask any question to the bot"
    update.message.reply_text(help_text)

def handle_invalid_command(update: Update, context: CallbackContext):
    update.message.reply_text('Invalid command. Please use the right command and use /help to see available commands.')

def main():
    updater = Updater(BOT_TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("gen", gen))
    dp.add_handler(CommandHandler("ask", ask))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(MessageHandler(Filters.command, handle_invalid_command))

    updater.start_polling()

    print(f"{WHITE}~ {CYAN}Bot started successfully!")

    updater.idle()

if __name__ == "__main__":
    main()
