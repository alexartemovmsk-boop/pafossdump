import re

FILE_PATH = 'liteon_firmware.bin'

with open(FILE_PATH, 'rb') as f:
    data = f.read()

print("=================================================================")
print(f"      АНАЛИЗАТОР ПРОШИВКИ: {FILE_PATH} ({len(data)} байт)        ")
print("=================================================================\n")

# 1. Поиск уникальных заводских калибровок в конце флешки (Блок 30/31)
print("--- [1] ЗАВОДСКИЕ КАЛИБРОВКИ И СЕРИЙНЫЙ НОМЕР (Блок 0x1E0000) ---")
nvram_data = data[0x1E0000:0x1E1000] # Первые 4 КБ блока калибровок
# Ищем печатные строки в калибровках
nvram_strings = re.findall(b'[\x20-\x7E]{4,}', nvram_data)
for s in nvram_strings[:10]:
    try:
        print(f"  -> Найдено: {s.decode('ascii')}")
    except:
        pass

# 2. Поиск брендов болванок (Media ID)
print("\n--- [2] ПОИСК БАЗЫ БОЛВАНОК (Disc Write Strategy MID) ---")
# Известные производители матриц CD/DVD
brands = [b'YUDEN', b'SONY', b'RITEK', b'CMC', b'MBI', b'MCC', b'TDK', b'MAXELL', b'PRODISC', b'INFOSMART']
found_brands = set()

for brand in brands:
    matches = [m.start() for m in re.finditer(brand, data)]
    if matches:
        found_brands.add(brand.decode('ascii'))
        print(f"  -> Бренд {brand.decode('ascii'):10} | Встречается раз: {len(matches):2} | Первый адрес: 0x{matches[0]:06X}")

# 3. Поиск системных сообщений, команд и ошибок
print("\n--- [3] ИНЖЕНЕРНЫЕ СТРОКИ И СИСТЕМНЫЕ ОШИБКИ (Выборка) ---")
all_strings = re.findall(b'[\x20-\x7E]{6,}', data)
interesting_keywords = [b'Error', b'Laser', b'DVD', b'CD', b'Fail', b'Buffer', b'Speed', b'Tray', b'MediaTek', b'Firmware']

count = 0
for s in all_strings:
    for kw in interesting_keywords:
        if kw.lower() in s.lower():
            try:
                text = s.decode('ascii').strip()
                # фильтруем слишком длинный мусор
                if 6 <= len(text) <= 50:
                    print(f"  [{kw.decode('ascii')}] {text}")
                    count += 1
                    break
            except:
                pass
    if count >= 20: # ограничим вывод первыми 20 интересными строками
        break

print("\n=================================================================")
print("Анализ завершен!")