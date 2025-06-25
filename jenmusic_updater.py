if __name__ == "__main__":
    token = os.environ["TELEGRAM_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    process_all_new(token, chat_id)

    # Гарантируем наличие index.html даже если нет новых ссылок
    if not os.path.exists(HTML_FILE):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write("""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>JenMusic</title>
  <style>
    body { font-family: sans-serif; background: #f8f8f8; padding: 20px; }
    .track-block { background: white; margin: 10px 0; padding: 10px; border-radius: 8px; display: flex; gap: 10px; }
    .cover { width: 80px; height: 80px; object-fit: cover; border-radius: 4px; }
    .track-info { flex: 1; }
    a { color: #3366cc; text-decoration: none; }
  </style>
</head>
<body>
<h1>JenMusic 🎧</h1>
</body>
</html>""")
        print("📄 Создан пустой index.html")
