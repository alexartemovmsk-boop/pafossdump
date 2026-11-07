import os
from PIL import Image

FILE_PATH = 'vape_4mb.bin'
OUT_DIR = 'rocket_frames'

if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

with open(FILE_PATH, 'rb') as f:
    raw_data = f.read()

WIDTH = 80
HEIGHT = 160
FRAME_SIZE = WIDTH * HEIGHT * 2 # 25600 байт

# Наша выверенная точка идеальной синей ракеты!
START_OFFSET = 743197 
NUM_FRAMES = 16 # Собираем цикл из 16 кадров полета

def decode_frame(chunk):
    img = Image.new('RGB', (WIDTH, HEIGHT))
    pix = img.load()
    idx = 0
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if idx + 1 >= len(chunk): break
            b1, b2 = chunk[idx], chunk[idx+1]
            idx += 2
            # Точный декодер из тюнера (дает правильный синий цвет)
            val = (b2 << 8) | b1
            pix[x, y] = (
                ((val >> 11) & 0x1F) * 255 // 31,
                ((val >> 5) & 0x3F) * 255 // 63,
                (val & 0x1F) * 255 // 31
            )
    return img

print(f"Стартуем с идеального синего кадра {START_OFFSET}...")
print(f"Шаг между кадрами: {FRAME_SIZE} байт\n")

frames = []

for i in range(NUM_FRAMES):
    offset = START_OFFSET + i * FRAME_SIZE
    chunk = raw_data[offset : offset + FRAME_SIZE]
    
    if len(chunk) < FRAME_SIZE:
        print(f"Конец данных на кадре {i}")
        break
        
    frame = decode_frame(chunk)
    
    # Сохраняем каждый кадр отдельно в папку rocket_frames
    frame_path = os.path.join(OUT_DIR, f"frame_{i:02d}.png")
    frame.save(frame_path)
    frames.append(frame)
    print(f"  -> Кадр {i:02d} готов (смещение {offset})")

if frames:
    OUT_GIF = 'blue_rocket_flight.gif'
    # Собираем плавный зацикленный GIF (80 мс на кадр = 12.5 кадров в сек)
    frames[0].save(
        OUT_GIF,
        save_all=True,
        append_images=frames[1:],
        duration=80,
        loop=0
    )
    print("\n========================================================")
    print(f"УСПЕХ! Финальная анимация сохранена: {OUT_GIF}")
    print(f"Все 16 кадров по отдельности лежат в папке: {OUT_DIR}")
    print("========================================================")