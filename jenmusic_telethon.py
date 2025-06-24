from telethon.sync import TelegramClient
from bs4 import BeautifulSoup
import requests
import json
import os

api_id = 22082640
api_hash = "bde2e19aa29f83795d8795aafcb1d517"
channel_username = "lingvo_witcher"

LOG_FILE = "log.json"
HTML_FILE = "index.html"
TEMPLATE = """<div class="track-block">
  <img src="{{cover}}" alt="{{title}}" class="cover">
  <div class="track-info">
    <p><strong>{{title}}</strong></p>
    <p>{{description}}</p>
    <a href="{{link}}" target="_blank">Слушать на Яндекс Музыке</a>
  </div>
</div>
"""

def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()

def save_log(log):
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(sorted(log), f, ensure_ascii=False, indent=2)

def update_html(track_data):
    block = TEMPLATE.format(**track_data)
    if not os.path.exists(HTML_FILE):
        with open(HTML_FILE, 'w', encoding='utf-8') as f:
            f.write("<html><body><h1>JenMusic</h1>\n" + block + "\n</body></html>")
        return
    with open(HTML_FILE, 'r+', encoding='utf-8') as f:
        content = f.read()
        if track_data["link"] in content:
            print("⏩ Уже добавлен:", track_data["link"])
            return
        updated = content.replace("</body>", block + "\n</body>")
        f.seek(0)
        f.write(updated)
        f.truncate()
        print("✅ Добавлен:", track_data["title"])

def parse_yandex_music(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    try:
        title = soup.find("meta", property="og:title")["content"]
        description = soup.find("meta", property="og:description")["content"]
        cover = soup.find("meta", property="og:image")["content"]
    except Exception as e:
        raise ValueError(f"Ошибка парсинга {url}: {e}")
    return {
        "title": title,
        "description": description,
        "cover": cover,
        "link": url
    }

with TelegramClient('session_name', api_id, api_hash) as client:
    all_links = set()
    for message in client.iter_messages(channel_username, limit=1000):
        if message.text and "music.yandex" in message.text:
            links = [word for word in message.text.split() if "music.yandex" in word]
            all_links.update(links)

    logged = load_log()
    for link in all_links:
        if link not in logged:
            try:
                track = parse_yandex_music(link)
                update_html(track)
                logged.add(link)
            except Exception as e:
                print("⚠️ Ошибка:", e)
    save_log(logged)