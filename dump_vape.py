import serial
import time
import sys

PORT = 'COM9' # Проверь, что твой порт по-прежнему COM9
BAUD = 115200
TOTAL_BYTES = 4194304  # Ровно 4 Мегабайта
OUTPUT_FILE = 'vape_4mb.bin'

print("==================================================")
print(f" Подключение к {PORT} (Дамп 4 МБ с вейпа)...")
print("==================================================")

try:
    ser = serial.Serial(PORT, BAUD, timeout=4)
except Exception as e:
    print(f"\n[ОШИБКА] Не удалось открыть {PORT}: {e}")
    sys.exit(1)

time.sleep(1)

print("Отправка команды 'D' на RP2040...")
ser.write(b'D')

print("Выкачиваем 4 МБ памяти...")
start_time = time.time()
received_data = bytearray()

while len(received_data) < TOTAL_BYTES:
    chunk = ser.read(min(8192, TOTAL_BYTES - len(received_data)))
    if not chunk:
        print("\n[ТАЙМАУТ] Данные перестали поступать!")
        break
    received_data.extend(chunk)
    
    progress = (len(received_data) / TOTAL_BYTES) * 100
    mb_down = len(received_data) / (1024 * 1024)
    sys.stdout.write(f"\rСкачано: {mb_down:4.2f} / 4.00 МБ [{progress:5.1f}%]")
    sys.stdout.flush()

elapsed = time.time() - start_time
ser.close()

if len(received_data) == TOTAL_BYTES:
    print(f"\n\n[УСПЕХ] Загружено 4 194 304 байт за {elapsed:.2f} сек!")
    print(f"Скорость: {TOTAL_BYTES / elapsed / 1024:.1f} КБ/с")
    
    with open(OUTPUT_FILE, 'wb') as f:
        f.write(received_data)
    print(f"Файл сохранен: {OUTPUT_FILE}")
else:
    print(f"\n\n[ОШИБКА] Скачалось только {len(received_data)} байт из {TOTAL_BYTES}")