#!/usr/bin/env python3
import os
import sys
import json
import logging
from datetime import datetime
from typing import List, Optional

# Настройка логирования
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
        self.telegram_token: Optional[str] = None
        self.telegram_chat_id: Optional[str] = None

    def _load_environment_variables(self) -> None:
        """Загружает необходимые переменные окружения"""
        self.telegram_token = os.environ.get("TELEGRAM_TOKEN")
        self.telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

        if not self.telegram_token or not self.telegram_chat_id:
            logger.error("Не заданы обязательные переменные окружения")
            logger.error("TELEGRAM_TOKEN и TELEGRAM_CHAT_ID должны быть установлены")
            sys.exit(1)

    def _generate_html(self, tracks: List[str]) -> str:
        """Генерирует HTML-страницу со списком треков"""
        html_content = [
            "<!DOCTYPE html>",
            "<html lang='ru'>",
            "<head>",
            "    <meta charset='UTF-8'>",
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            "    <title>JenMusic</title>",
            "    <style>",
            "        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }",
            "        h1 { color: #2c3e50; }",
            "        ul { list-style-type: none; padding: 0; }",
            "        li { margin: 10px 0; }",
            "        a { color: #3498db; text-decoration: none; }",
            "        a:hover { text-decoration: underline; }",
            "    </style>",
            "</head>",
            "<body>",
            "    <h1>🎧 JenMusic</h1>",
            "    <ul>"
        ]

        for track in tracks:
            html_content.append(f"        <li><a href='{track}' target='_blank'>{track}</a></li>")

        html_content.extend([
            "    </ul>",
            "    <footer>",
            f"        <p>Обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
            "    </footer>",
            "</body>",
            "</html>"
        ])

        return "\n".join(html_content)

    def _read_log(self) -> List[str]:
        """Читает существующий лог-файл с треками"""
        if not os.path.exists(self.log_path):
            logger.warning("Лог-файл не найден, будет создан новый")
            return []

        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка при чтении лог-файла: {e}")
            return []

    def _save_log(self, links: List[str]) -> None:
        """Сохраняет список треков в лог-файл"""
        try:
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
            with open(self.log_path, 'w', encoding='utf-8') as f:
                json.dump(links, f, indent=2, ensure_ascii=False)
            logger.info(f"Лог успешно сохранён ({len(links)} треков)")
        except Exception as e:
            logger.error(f"Ошибка при сохранении лога: {e}")
            sys.exit(1)

    def _save_html(self, links: List[str]) -> None:
        """Сохраняет HTML-страницу с треками"""
        try:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            with open(self.index_path, 'w', encoding='utf-8') as f:
                f.write(self._generate_html(links))
            logger.info(f"HTML-страница успешно создана ({len(links)} треков)")
        except Exception as e:
            logger.error(f"Ошибка при создании HTML-страницы: {e}")
            sys.exit(1)

    def _get_yandex_links(self) -> List[str]:
        """Получает ссылки на треки из Telegram"""
        # TODO: Реализовать реальное получение ссылок из Telegram API
        # Временная заглушка для тестирования
        test_links = [
            "https://music.yandex.ru/album/123456/track/7891011",
            "https://music.yandex.ru/album/987654/track/3210123"
        ]
        logger.info(f"Получено {len(test_links)} тестовых ссылок")
        return test_links

    def run(self) -> None:
        """Основной метод выполнения обновления"""
        logger.info("Запуск JenMusic Updater")
        
        self._load_environment_variables()
        logger.info("Переменные окружения успешно загружены")
        
        old_links = self._read_log()
        new_links = self._get_yandex_links()
        
        logger.info(f"Найдено {len(old_links)} существующих и {len(new_links)} новых треков")
        
        # Объединяем и удаляем дубликаты
        unique_links = list(dict.fromkeys(old_links + new_links))
        logger.info(f"Всего уникальных треков: {len(unique_links)}")
        
        self._save_log(unique_links)
        self._save_html(unique_links)
        
        logger.info("Обновление успешно завершено")

if __name__ == "__main__":
    try:
        updater = JenMusicUpdater()
        updater.run()
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}")
        sys.exit(1)