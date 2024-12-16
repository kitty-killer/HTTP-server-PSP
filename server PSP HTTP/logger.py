import os
import datetime

# Создаем директорию для логов, если она не существует
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def write_log(message):
    # Имя файла лога на основе текущей даты
    log_file = os.path.join(LOG_DIR, f"log_{datetime.datetime.now().strftime('%Y-%m-%d')}.log")
    
    # Форматирование сообщения с отметкой времени
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"{timestamp} - {message}\n"
    
    # Запись сообщения в файл лога
    with open(log_file, "a", encoding='utf-8') as file:
        file.write(log_message)
