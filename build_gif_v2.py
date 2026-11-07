import os
from PIL import Image

IMAGE_PATH = os.path.join('vape_extracted', 'overview_width_80px.png')

if not os.path.exists(IMAGE_PATH):
    print(f"Ошибка: не найден файл {IMAGE_PATH}")
    exit(1)

print("Загружаем ленту спрайтов 80px...")
img = Image.open(IMAGE_PATH).convert('RGB')
w, h = img.size

# 1. Автоматический поиск высоты кадра ракеты
# Ищем расстояние между носами ракет (по красно-зеленым пикселям на центральной оси X = 40)
center_pixels = [img.getpixel((40, y)) for y in range(h)]

# Простой детектор периодичности (ищем шаг повторения от 60 до 160 px)
best_period = 80 # базовое значение
min_diff = float('inf')

# Возьмем тестовую область в середине, где летят ракеты (например, с Y=1500 до Y=3000)
test_y_start = int(h * 0.3)
test_len = 500

for period in range(60, 160):
    diff = 0
    for y in range(test_y_start, test_y_start + test_len):
        p1 = center_pixels[y]
        p2 = center_pixels[y + period]
        # Разница между цветами
        diff += abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) + abs(p1[2] - p2[2])
    
    if diff < min_diff:
        min_diff = diff
        best_period = period

FRAME_HEIGHT = best_period
print(f"-> Автодетектор определил высоту одного кадра: {FRAME_HEIGHT} px!")

# 2. Нарезаем кадры анимации ракеты
# Найдем, где примерно начинаются первые зеленые ракеты
print("Нарезаем кадры ракеты...")

frames = []
# Берем 30 кадров подряд из зоны полета
start_y = 0
# Промотаем верхушку с логотипом PAFOS (первые ~15% высоты)
start_y = int(h * 0.22)

# Выравниваем старт кратно периоду
start_y = (start_y // FRAME_HEIGHT) * FRAME_HEIGHT

for i in range(25): # берем 25 кадров для плавной анимации
    y1 = start_y + i * FRAME_HEIGHT
    y2 = y1 + FRAME_HEIGHT
    if y2 > h:
        break
    
    frame = img.crop((0, y1, w, y2))
    frames.append(frame)

# 3. Сохраняем плавный зацикленный GIF
OUT_GIF = 'flying_rocket.gif'
frames[0].save(
    OUT_GIF,
    save_all=True,
    append_images=frames[1:],
    duration=90, # ~11 кадров в секунду (плавный огонь)
    loop=0
)

print(f"\n[УСПЕХ] Анимация готова: {OUT_GIF}")
print("Открывай в VS Code или браузере — ракета полетела!")