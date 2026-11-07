import os
import re
from PIL import Image

FILE_PATH = 'vape_4mb.bin'
OUTPUT_DIR = 'vape_extracted'

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print("========================================================")
print(f"       ВИЗУАЛИЗАТОР ГРАФИКИ ВЕЙПА: {FILE_PATH}          ")
print("========================================================")

with open(FILE_PATH, 'rb') as f:
    raw_data = f.read()

# 1. Поиск текстовых зацепок (названия контроллеров экрана ST7735, GC9A01 и т.д.)
print("\n[1] Поиск системных строк и драйверов экрана...")
strings = re.findall(b'[\x20-\x7E]{4,}', raw_data)
for s in strings[:15]:
    try:
        txt = s.decode('ascii').strip()
        if any(w in txt.lower() for w in ['lcd', 'tft', 'oled', 'st77', 'gc9', 'disp', 'font', 'ui', 'vape']):
            print(f"  -> Найдена зацепка: {txt}")
    except:
        pass

# 2. Функция конвертации сырых байт RGB565 в картинку
def decode_rgb565(byte_chunk, width, height, little_endian=True):
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    
    idx = 0
    total_bytes = len(byte_chunk)
    for y in range(height):
        for x in range(width):
            if idx + 1 >= total_bytes:
                break
            b1 = byte_chunk[idx]
            b2 = byte_chunk[idx+1]
            idx += 2
            
            # Собираем 16-битный цвет
            val = (b2 << 8) | b1 if little_endian else (b1 << 8) | b2
            
            # Декодируем RGB565 (5 бит Red, 6 бит Green, 5 бит Blue) в RGB888
            r = ((val >> 11) & 0x1F) * 255 // 31
            g = ((val >> 5) & 0x3F) * 255 // 63
            b = (val & 0x1F) * 255 // 31
            
            pixels[x, y] = (r, g, b)
    return img

# 3. Генерируем "Рентген памяти" (Memory Strip)
# Типичные ширины экранов вейпов: 80, 128, 160, 240 пикселей
common_widths = [128, 80, 240]

print("\n[2] Создание обзорных карт памяти (Рентген)...")
for w in common_widths:
    bytes_per_row = w * 2 # 2 байта на пиксель
    # Ограничим высоту свитка первыми 2 МБ, чтобы картинка не была гигантской
    slice_data = raw_data[:2 * 1024 * 1024]
    h = len(slice_data) // bytes_per_row
    
    print(f"  -> Рендерим обзорный холст шириной {w} px (высота {h} px)...")
    overview_img = decode_rgb565(slice_data, w, h, little_endian=True)
    out_file = os.path.join(OUTPUT_DIR, f'overview_width_{w}px.png')
    overview_img.save(out_file)
    print(f"     Сохранено: {out_file}")

# 4. Нарезка первых анимационных кадров (если экран 128x128 или 80x160)
print("\n[3] Нарезка первых кадров (слайсов)...")
frame_size_128 = 128 * 128 * 2 # 32768 байт на кадр
for i in range(10): # нарежем первые 10 кадров
    offset = i * frame_size_128
    if offset + frame_size_128 <= len(raw_data):
        frame = decode_rgb565(raw_data[offset:offset+frame_size_128], 128, 128, little_endian=True)
        frame.save(os.path.join(OUTPUT_DIR, f'frame_128x128_{i:02d}.png'))

print("\n========================================================")
print(f"ГОТОВО! Загляните в папку: {OUTPUT_DIR}")
print("Откройте файлы 'overview_width_128px.png' или 'overview_width_80px.png' прямо в VS Code!")
print("========================================================")