import tkinter as tk
from PIL import Image, ImageTk

FILE_PATH = 'vape_4mb.bin'
with open(FILE_PATH, 'rb') as f:
    raw_data = f.read()

class SpriteTuner:
    def __init__(self, root):
        self.root = root
        self.root.title("Инженерный Тюнер Спрайтов")

        self.offset = 0
        self.width = 80
        self.height = 160

        # Панель управления
        ctrl = tk.Frame(root)
        ctrl.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        tk.Label(ctrl, text="Ширина (px):").grid(row=0, column=0)
        self.w_slider = tk.Scale(ctrl, from_=10, to=240, orient=tk.HORIZONTAL, command=self.update)
        self.w_slider.set(self.width)
        self.w_slider.grid(row=0, column=1)

        tk.Label(ctrl, text="Высота (px):").grid(row=0, column=2)
        self.h_slider = tk.Scale(ctrl, from_=10, to=320, orient=tk.HORIZONTAL, command=self.update)
        self.h_slider.set(self.height)
        self.h_slider.grid(row=0, column=3)

        tk.Label(ctrl, text="Смещение в памяти (байт):").grid(row=1, column=0)
        self.off_slider = tk.Scale(ctrl, from_=0, to=len(raw_data)-100000, orient=tk.HORIZONTAL, length=400, command=self.update)
        self.off_slider.grid(row=1, column=1, columnspan=3)

        # Холст для показа
        self.canvas = tk.Label(root)
        self.canvas.pack(pady=10)

        self.update()

    def update(self, *args):
        w = self.w_slider.get()
        h = self.h_slider.get()
        off = self.off_slider.get()

        frame_bytes = w * h * 2
        chunk = raw_data[off : off + frame_bytes]

        img = Image.new('RGB', (w, h))
        pix = img.load()
        idx = 0
        for y in range(h):
            for x in range(w):
                if idx + 1 >= len(chunk): break
                b1, b2 = chunk[idx], chunk[idx+1]
                idx += 2
                val = (b2 << 8) | b1
                pix[x, y] = (
                    ((val >> 11) & 0x1F) * 255 // 31,
                    ((val >> 5) & 0x3F) * 255 // 63,
                    (val & 0x1F) * 255 // 31
                )
        
        # Масштабируем для удобства в 2 раза
        img_zoomed = img.resize((w * 2, h * 2), Image.NEAREST)
        self.photo = ImageTk.PhotoImage(img_zoomed)
        self.canvas.config(image=self.photo)

root = tk.Tk()
app = SpriteTuner(root)
root.mainloop()