#!/usr/bin/env python3
import os
import sys
import json
import logging
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv
from telethon import TelegramClient, events

# Инициализация окружения и логгирования
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class JenMusicUpdater:
    def __init__(self):
        self.log_path = "docs/log.json"
        self.index_path = "docs/index.html"
        
        # Проверка и загрузка конфигурации
        self._validate_config()
        
        # Инициализация Telegram клиента
        self.client = TelegramClient(
            'jenmusic_session',
            int(os.getenv('API_ID')),
            os.getenv('API_HASH')
        )

    def _validate_config(self):
        """Проверяет обязательные переменные окружения"""
        required_vars = {
            'TELEGRAM_TOKEN': os.getenv('TELEGRAM_TOKEN'),
            'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID'),
            'API_ID': os.getenv('API_ID'),
            'API_HASH': os.getenv('API_HASH')
        }
        
        missing = [name for name, value in required_vars.items() if not value]
        if missing:
            logger.error(f"Отсутствуют обязательные переменные: {', '.join(missing)}")
            sys.exit(1)

    def _generate_html(self, tracks: List[str]) -> str:
        """Генерирует красивую HTML-страницу"""
        return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JenMusic Collection</title>
    <style>
        body {{
            font-family: 'Segoe UI', sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
        }}
        .track-list {{
            list-style: none;
            padding: 0;
        }}
        .track-item {{
            background: white;
            margin: 10px 0;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .track-link {{
            color: #3498db;
            text-decoration: none;
            font-weight: 500;
        }}
        footer {{
            text-align: center;
            margin-top: 30px;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <h1>🎵 Моя коллекция музыки</h1>
    <ul class="track-list">
        {"".join(f'<li class="track-item"><a href="{track}" class="track-link" target="_blank">{track}</a></li>' for track in tracks)}
    </ul>
    <footer>
        Обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </footer>
</body>
</html>"""

    async def _get_telegram_links(self) -> List[str]:
        """Асинхронно получает музыкальные ссылки из Telegram"""
        links = []
        try:
            await self.client.start(bot_token=os.getenv('TELEGRAM_TOKEN'))
            
            chat = await self.client.get_entity(int(os.getenv('TELEGRAM_CHAT_ID')))
            async for message in self.client.iter_messages(chat, limit=50):
                if message.text and 'yandex.ru' in message.text:
                    links.append(message.text)
                    
            logger.info(f"Получено {len(links)} ссылок из Telegram")
        except Exception as e:
            logger.error(f"Ошибка при работе с Telegram: {str(e)}")
        finally:
            await self.client.disconnect()
            
        return links

    def _process_links(self, old_links: List[str], new_links: List[str]) -> List[str]:
        """Обрабатывает и объединяет списки ссылок"""
        # Удаление дубликатов и пустых значений
        combined = [link for link in set(old_links + new_links) if link and link.strip()]
        logger.info(f"Общее количество уникальных треков: {len(combined)}")
        return combined

    def run(self):
        """Основной цикл выполнения"""
        logger.info("Запуск обновления музыкальной коллекции")
        
        # Загрузка существующих ссылок
        old_links = []
        if os.path.exists(self.log_path):
            try:
                with open(self.log_path, 'r', encoding='utf-8') as f:
                    old_links = json.load(f)
                logger.info(f"Загружено {len(old_links)} существующих треков")
            except Exception as e:
                logger.error(f"Ошибка чтения лога: {str(e)}")

        # Получение новых ссылок
        with self.client:
            new_links = self.client.loop.run_until_complete(self._get_telegram_links())
        
        # Обработка и сохранение
        unique_links = self._process_links(old_links, new_links)
        
        try:
            # Сохранение JSON лога
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
            with open(self.log_path, 'w', encoding='utf-8') as f:
                json.dump(unique_links, f, indent=2, ensure_ascii=False)
            
            # Генерация HTML
            with open(self.index_path, 'w', encoding='utf-8') as f:
                f.write(self._generate_html(unique_links))
            
            logger.info("Обновление успешно завершено")
        except Exception as e:
            logger.error(f"Ошибка сохранения данных: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    try:
        updater = JenMusicUpdater()
        updater.run()
    except Exception as e:
        logger.critical(f"Критическая ошибка: {str(e)}")
        sys.exit(1)