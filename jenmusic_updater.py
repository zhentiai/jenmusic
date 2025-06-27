import os
import json
from datetime import datetime

def generate_html(tracks):
    html = "<html><head><title>JenMusic</title></head><body><h1>🎧 JenMusic</h1><ul>"
    for track in tracks:
        html += f'<li><a href="{track}">{track}</a></li>'
    html += "</ul></body></html>"
    return html

def read_log(log_path):
    if not os.path.exists(log_path):
        return []
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print("⚠️ Не удалось прочитать log.json:", e)
        return []

def save_log(log_path, links):
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(links, f, indent=2, ensure_ascii=False)

def save_html(index_path, links):
    html = generate_html(links)
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ Файл {index_path} успешно создан с {len(links)} ссылками")

def get_yandex_links_from_env():
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("⚠️ Переменные окружения TELEGRAM_TOKEN и/или TELEGRAM_CHAT_ID не заданы")
        return []

    # Место для реального получения ссылок из Telegram
    # Пока тестово — возвращаем одну ссылку
    return ["https://music.yandex.ru/album/123456/track/7891011"]

def main():
    log_path = "docs/log.json"
    index_path = "docs/index.html"

    old_links = read_log(log_path)
    new_links = get_yandex_links_from_env()

    print(f"🔎 Найдено {len(new_links)} новых ссылок")

    unique_links = list(dict.fromkeys(old_links + new_links))  # убираем дубликаты

    save_log(log_path, unique_links)
    save_html(index_path, unique_links)

if __name__ == "__main__":
    main()