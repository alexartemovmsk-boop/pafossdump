import serial
import time
import sys

# ВНИМАНИЕ: укажите ваш порт (у вас был COM9)
PORT = 'COM9'
BAUD = 115200
TOTAL_BYTES = 2097152  # 2 Мегабайта
OUTPUT_FILE = 'liteon_firmware.bin'

print(f"Подключение к {PORT}...")
try:
    ser = serial.Serial(PORT, BAUD, timeout=3)
except Exception as e:
    print(f"Ошибка открытия порта: {e}")
    print("Убедитесь, что Монитор порта в Arduino IDE закрыт!")
    sys.exit(1)

time.sleep(1) # Пауза для инициализации порта

print("Отправка команды на старт чтения...")
ser.write(b'D') # Отправляем команду 'D'

print("Выкачиваем прошивку...")
start_time = time.time()
received_data = bytearray()

while len(received_data) < TOTAL_BYTES:
    # Читаем порциями
    chunk = ser.read(min(4096, TOTAL_BYTES - len(received_data)))
    if not chunk:
        print("\nТаймаут: данные перестали поступать!")
        break
    received_data.extend(chunk)
    
    # Красивый прогресс-бар
    progress = (len(received_data) / TOTAL_BYTES) * 100
    sys.stdout.write(f"\rСкачано: {len(received_data)} / {TOTAL_BYTES} байт [{progress:.1f}%]")
    sys.stdout.flush()

elapsed = time.time() - start_time
ser.close()

if len(received_data) == TOTAL_BYTES:
    with open(OUTPUT_FILE, 'wb') as f:
        f.write(received_data)
    print(f"\n\nУСПЕХ! Прошивка сохранена в файл: {OUTPUT_FILE}")
    print(f"Время загрузки: {elapsed:.2f} сек (Скорость: {TOTAL_BYTES/elapsed/1024:.1f} КБ/с)")
else:
    print(f"\nОшибка: получено только {len(received_data)} байт из {TOTAL_BYTES}")