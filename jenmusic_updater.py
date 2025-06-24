import requests
from bs4 import BeautifulSoup
import os, json
from datetime import datetime

YANDEX_LOG = "log.json"
HTML_FILE = "index.html"

TEMPLATE = """<div class="track-block">
  <img src="{cover}" alt="{title}" class="cover">
  <div class="track-info">
    <p><strong>{title}</strong></p>
    <p>{description}</p>
    <a href="{link}" target="_blank">Слушать на Яндекс Музыке</a>
  </div>
</div>
"""

def get_yandex_links_from_channel(token, chat_id, limit=20):
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    response = requests.get(url)
    result = []

    if response.status_code == 200:
        data = response.json()
        if data.get("ok"):
            messages = data["result"]
            for msg in messages:
                try:
                    text = msg["message"]["text"]
                    if "music.yandex" in text:
                        links = [word for word in text.split() if "music.yandex" in word]
                        result.extend(links)
                except KeyError:
                    continue
    return list(set(result))

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

def update_html(track_data):
    block = TEMPLATE.format(**track_data)

    if not os.path.exists(HTML_FILE):
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(f"<html><body><h1>JenMusic</h1>\n{block}\n</body></html>")
        return

    with open(HTML_FILE, "r+", encoding="utf-8") as f:
        content = f.read()
        if track_data["link"] in content:
            print("⏩ Уже добавлен:", track_data["link"])
            return
        updated = content.replace("</body>", f"{block}\n</body>")
        f.seek(0)
        f.write(updated)
        f.truncate()
        print("✅ Добавлен:", track_data["title"])

def load_log():
    if os.path.exists("log.json"):
        with open("log.json", "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_log(logged):
    with open("log.json", "w", encoding="utf-8") as f:
        json.dump(sorted(logged), f, ensure_ascii=False, indent=2)

def process_all_new(token, chat_id):
    links = get_yandex_links_from_channel(token, chat_id)
    logged = load_log()

    for link in links:
        if link not in logged:
            try:
                track = parse_yandex_music(link)
                update_html(track)
                logged.add(link)
            except Exception as e:
                print("⚠️ Ошибка:", e)
    save_log(logged)

# Чтобы использовать в GitHub Actions:
if __name__ == "__main__":
    import os
    token = os.environ["TELEGRAM_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    process_all_new(token, chat_id)
