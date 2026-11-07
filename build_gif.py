import os
from PIL import Image

FILE_PATH = 'vape_4mb.bin'
OUT_DIR = 'frames_check'

if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

with open(FILE_PATH, 'rb') as f:
    raw_data = f.read()

WIDTH = 80
HEIGHT = 160
FRAME_SIZE = WIDTH * HEIGHT * 2 # 25600 байт

START_OFFSET = 1230720 # Твоя выверенная точка!
NUM_FRAMES = 16        # Количество кадров для пробы

def decode_frame(chunk):
    img = Image.new('RGB', (WIDTH, HEIGHT))
    pix = img.load()
    idx = 0
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if idx + 1 >= len(chunk): break
            b1, b2 = chunk[idx], chunk[idx+1]
            idx += 2
            val = (b2 << 8) | b1
            pix[x, y] = (
                ((val >> 11) & 0x1F) * 255 // 31,
                ((val >> 5) & 0x3F) * 255 // 63,
                (val & 0x1F) * 255 // 31
            )
    return img

print(f"Стартуем со смещения {START_OFFSET} с шагом {FRAME_SIZE} байт...")
frames = []

for i in range(NUM_FRAMES):
    offset = START_OFFSET + i * FRAME_SIZE
    chunk = raw_data[offset : offset + FRAME_SIZE]
    
    if len(chunk) < FRAME_SIZE:
        print(f"Конец файла на кадре {i}")
        break
        
    frame = decode_frame(chunk)
    # Сохраняем каждый кадр отдельно для проверки
    frame_name = os.path.join(OUT_DIR, f"frame_{i:02d}_off_{offset}.png")
    frame.save(frame_name)
    frames.append(frame)
    print(f"  -> Кадр {i:02d} сохранен: {frame_name}")

if frames:
    GIF_NAME = 'vape_rocket_movie.gif'
    # Собираем плавную гифку (скорость 80 мс на кадр = ~12.5 FPS)
    frames[0].save(
        GIF_NAME,
        save_all=True,
        append_images=frames[1:],
        duration=80,
        loop=0
    )
    print(f"\n[УСПЕХ] Готовая анимация собрана: {GIF_NAME}")
    print(f"Загляни в папку '{OUT_DIR}' и открой гифку!")