import requests
import asyncio
import time
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.error import TelegramError


def parse_rss_feed(rss_link):
    response = requests.get(rss_link)
    if response.status_code != 200:
        print("Failed to fetch the RSS feed.")
        return []

    soup = BeautifulSoup(response.content, 'xml')
    items = soup.find_all('item')

    parsed_data = []
    print(f"items:  {len(items)}")
    with open('last_item.txt', 'r') as file:
        last_infohash = file.read().strip()

    for item in items:
        current_infohash = item.find('nyaa:infoHash').text

        # If the current item's infoHash matches the last saved infoHash, stop processing
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

    # Save the latest infoHash to the txt file
    if parsed_data:
        with open('last_item.txt', 'w') as file:
            file.write(parsed_data[0]['infoHash'])
    print("parsed_data:")
    print(len(parsed_data))
    return parsed_data


TOKEN = '6737420459:AAEzTOJpxlmrTcMd-KvJ3bVt3J2QjyS0x-M'
CHANNEL_ID = '-1002124029617'


async def send_to_telegram(parsed_data):
    bot = Bot(token=TOKEN)
    i = 0
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
            i += 1
            print(i)
        except TelegramError as e:
            print(f"Error sending message: {e}")
        time.sleep(3)


if name == "main":
    rss_link = 'https://nyaa.si/?page=rss'
    items_data = parse_rss_feed(rss_link)
    asyncio.run(send_to_telegram(items_data))
