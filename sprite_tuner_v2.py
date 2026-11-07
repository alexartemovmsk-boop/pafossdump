import tkinter as tk
from PIL import Image, ImageTk

FILE_PATH = 'vape_4mb.bin'

with open(FILE_PATH, 'rb') as f:
    raw_data = f.read()

TOTAL_LEN = len(raw_data)

class AdvancedSpriteTuner:
    def __init__(self, root):
        self.root = root
        self.root.title("Инженерный Тюнер Спрайтов 2.0 (Fine-Tuning)")
        self.root.geometry("620x720")

        self.width = 80
        self.height = 160
        self.offset = 723179 # Стартуем сразу с твоей ракеты!

        # ----------------- Панель управления -----------------
        ctrl = tk.Frame(root, padx=10, pady=5)
        ctrl.pack(side=tk.TOP, fill=tk.X)

        # 1. ШИРИНА
        row_w = tk.Frame(ctrl)
        row_w.pack(fill=tk.X, pady=2)
        tk.Label(row_w, text="Ширина (W):", width=12, anchor='w').pack(side=tk.LEFT)
        tk.Button(row_w, text="-1", width=3, command=lambda: self.adjust_w(-1)).pack(side=tk.LEFT, padx=1)
        self.ent_w = tk.Entry(row_w, width=6)
        self.ent_w.pack(side=tk.LEFT, padx=3)
        self.ent_w.bind("<Return>", lambda e: self.on_entry_w())
        tk.Button(row_w, text="+1", width=3, command=lambda: self.adjust_w(1)).pack(side=tk.LEFT, padx=1)
        self.scale_w = tk.Scale(row_w, from_=10, to=240, orient=tk.HORIZONTAL, showvalue=0, command=self.on_scale_w)
        self.scale_w.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # 2. ВЫСОТА
        row_h = tk.Frame(ctrl)
        row_h.pack(fill=tk.X, pady=2)
        tk.Label(row_h, text="Высота (H):", width=12, anchor='w').pack(side=tk.LEFT)
        tk.Button(row_h, text="-1", width=3, command=lambda: self.adjust_h(-1)).pack(side=tk.LEFT, padx=1)
        self.ent_h = tk.Entry(row_h, width=6)
        self.ent_h.pack(side=tk.LEFT, padx=3)
        self.ent_h.bind("<Return>", lambda e: self.on_entry_h())
        tk.Button(row_h, text="+1", width=3, command=lambda: self.adjust_h(1)).pack(side=tk.LEFT, padx=1)
        self.scale_h = tk.Scale(row_h, from_=10, to=320, orient=tk.HORIZONTAL, showvalue=0, command=self.on_scale_h)
        self.scale_h.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # 3. СМЕЩЕНИЕ (OFFSET)
        row_off = tk.Frame(ctrl)
        row_off.pack(fill=tk.X, pady=4)
        tk.Label(row_off, text="Смещение (байт):", width=15, anchor='w').pack(side=tk.LEFT)
        
        tk.Button(row_off, text="-160 (стр)", command=lambda: self.adjust_off(-160)).pack(side=tk.LEFT, padx=1)
        tk.Button(row_off, text="-1", width=3, command=lambda: self.adjust_off(-1)).pack(side=tk.LEFT, padx=1)
        
        self.ent_off = tk.Entry(row_off, width=10)
        self.ent_off.pack(side=tk.LEFT, padx=3)
        self.ent_off.bind("<Return>", lambda e: self.on_entry_off())
        
        tk.Button(row_off, text="+1", width=3, command=lambda: self.adjust_off(1)).pack(side=tk.LEFT, padx=1)
        tk.Button(row_off, text="+160 (стр)", command=lambda: self.adjust_off(160)).pack(side=tk.LEFT, padx=1)

        # Ползунок смещения
        self.scale_off = tk.Scale(ctrl, from_=0, to=TOTAL_LEN - 100000, orient=tk.HORIZONTAL, showvalue=0, command=self.on_scale_off)
        self.scale_off.pack(fill=tk.X, pady=2)

        # Кнопка сохранения и подсказка
        btn_frame = tk.Frame(ctrl)
        btn_frame.pack(fill=tk.X, pady=4)
        tk.Button(btn_frame, text="💾 Сохранить текущий кадр в PNG", bg="#d1e7dd", command=self.save_frame).pack(side=tk.LEFT)
        tk.Label(btn_frame, text="Клавиши: ←/→ (±2 байта/пиксель) | ↑/↓ (±1 строка)", fg="#666").pack(side=tk.RIGHT)

        # ----------------- Холст для картинки -----------------
        self.canvas = tk.Label(root, bg="#111")
        self.canvas.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        # Горячие клавиши
        root.bind("<Left>", lambda e: self.adjust_off(-2))
        root.bind("<Right>", lambda e: self.adjust_off(2))
        root.bind("<Up>", lambda e: self.adjust_off(-self.width * 2))
        root.bind("<Down>", lambda e: self.adjust_off(self.width * 2))

        # Первичная синхронизация
        self.sync_all_controls()
        self.render_image()

    def sync_all_controls(self):
        self.scale_w.set(self.width)
        self.scale_h.set(self.height)
        self.scale_off.set(self.offset)

        self.ent_w.delete(0, tk.END)
        self.ent_w.insert(0, str(self.width))

        self.ent_h.delete(0, tk.END)
        self.ent_h.insert(0, str(self.height))

        self.ent_off.delete(0, tk.END)
        self.ent_off.insert(0, str(self.offset))

    # --- Обработчики ручного ввода (Enter) ---
    def on_entry_w(self):
        try:
            val = int(self.ent_w.get())
            self.width = max(10, min(val, 320))
            self.scale_w.set(self.width)
            self.render_image()
        except: pass

    def on_entry_h(self):
        try:
            val = int(self.ent_h.get())
            self.height = max(10, min(val, 480))
            self.scale_h.set(self.height)
            self.render_image()
        except: pass

    def on_entry_off(self):
        try:
            val = int(self.ent_off.get())
            self.offset = max(0, min(val, TOTAL_LEN - 100))
            self.scale_off.set(self.offset)
            self.render_image()
        except: pass

    # --- Обработчики кнопок +/- ---
    def adjust_w(self, delta):
        self.width = max(10, self.width + delta)
        self.sync_all_controls()
        self.render_image()

    def adjust_h(self, delta):
        self.height = max(10, self.height + delta)
        self.sync_all_controls()
        self.render_image()

    def adjust_off(self, delta):
        self.offset = max(0, min(self.offset + delta, TOTAL_LEN - 100))
        self.sync_all_controls()
        self.render_image()

    # --- Обработчики ползунков ---
    def on_scale_w(self, val):
        self.width = int(val)
        self.ent_w.delete(0, tk.END)
        self.ent_w.insert(0, str(self.width))
        self.render_image()

    def on_scale_h(self, val):
        self.height = int(val)
        self.ent_h.delete(0, tk.END)
        self.ent_h.insert(0, str(self.height))
        self.render_image()

    def on_scale_off(self, val):
        self.offset = int(val)
        self.ent_off.delete(0, tk.END)
        self.ent_off.insert(0, str(self.offset))
        self.render_image()

    # --- Рендеринг RGB565 ---
    def render_image(self):
        frame_bytes = self.width * self.height * 2
        chunk = raw_data[self.offset : self.offset + frame_bytes]

        img = Image.new('RGB', (self.width, self.height))
        pix = img.load()
        idx = 0
        for y in range(self.height):
            for x in range(self.width):
                if idx + 1 >= len(chunk): break
                b1, b2 = chunk[idx], chunk[idx+1]
                idx += 2
                val = (b2 << 8) | b1
                pix[x, y] = (
                    ((val >> 11) & 0x1F) * 255 // 31,
                    ((val >> 5) & 0x3F) * 255 // 63,
                    (val & 0x1F) * 255 // 31
                )

        # Масштабируем x2 для комфортного просмотра
        img_zoomed = img.resize((self.width * 2, self.height * 2), Image.NEAREST)
        self.current_img = img # оригинальный размер для сохранения
        self.photo = ImageTk.PhotoImage(img_zoomed)
        self.canvas.config(image=self.photo)

    def save_frame(self):
        filename = f"frame_off{self.offset}_{self.width}x{self.height}.png"
        self.current_img.save(filename)
        print(f"Кадр сохранен: {filename}")

root = tk.Tk()
app = AdvancedSpriteTuner(root)
root.mainloop()