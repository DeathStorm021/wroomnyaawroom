import os
import requests
import asyncio
import time
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.error import TelegramError


def parse_rss_feed(rss_link):
    response = requests.get(rss_link)
    if response.status_code != 200:
        print("Failed")
        return []

    soup = BeautifulSoup(response.content, 'xml')
    items = soup.find_all('item')

    parsed_data = []
    with open('last_hash.txt', 'r') as file:
        last_infohash = file.read().strip()

    for item in items:
        current_infohash = item.find('nyaa:infoHash').text

        if current_infohash == last_infohash:
            break

        data = {}
        data['title'] = item.find('title').text
        data['link'] = item.find('link').text
        data['guid'] = item.find('guid').text
        data['category'] = item.find('nyaa:category').text
        data['size'] = item.find('nyaa:size').text
        data['infoHash'] = item.find('nyaa:infoHash').text

        parsed_data.append(data)

    if parsed_data:
        with open('last_hash.txt', 'w') as file:
            file.write(parsed_data[0]['infoHash'])
    print(f"parsed data len: {len(parsed_data)}")
    return parsed_data


TOKEN = os.environ.get('TOKEN', '')
CHANNEL_ID = os.environ.get('CHANNEL_ID', '')


async def send_to_telegram(parsed_data):
    bot = Bot(token=TOKEN)
    for data in parsed_data:
        title = data['title']
        escaped_title = title.replace("_", "\\_")
        size = data['size']
        link = data['link']
        view_link = data['guid']
        category = data['category']

        message = (
            f"{escaped_title}\n"
            f"{size} | ([Download]({link})) | ([View]({view_link}))\n"
            f"#{category}"
        )

        try:
            await bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode='Markdown')
            
        except TelegramError as e:
            print(f"Error sending message: {e}")
        time.sleep(3)


if __name__ == "__main__":
    rss_link = 'https://nyaa.si/?page=rss'
    items_data = parse_rss_feed(rss_link)
    if items_data is not None:
        asyncio.run(send_to_telegram(items_data))
    else:
        print("ntg")
