import tkinter as tk
import json
import os

class PixelArtTool:
    def __init__(self, root, colors=("red", "green", "blue", "yellow", "black", "white", "orange", "purple")):
        self.colors = colors
        self.current_color = None
        self.default_save_path = os.path.join(os.path.dirname(__file__) + "/riddle_storage") 
        os.makedirs(self.default_save_path, exist_ok=True)

        self.canvas1_size = {"width": 7, "height": 3, "name": "image1"}
        self.canvas2_size = {"width": 7, "height": 3, "name": "image2"}

        self.image1 = self.create_image_data(self.canvas1_size["width"], self.canvas1_size["height"])
        self.image2 = self.create_image_data(self.canvas2_size["width"], self.canvas2_size["height"])

        self.create_ui(root)

    def create_image_data(self, width, height):
        return [[None for _ in range(width)] for _ in range(height)]

    def create_ui(self, root):
        # Canvas 1 with size and name inputs
        self.canvas1_frame = tk.Frame(root)
        self.canvas1_frame.grid(row=0, column=0, padx=10, pady=10)
        tk.Label(self.canvas1_frame, text="Canvas 1").pack()
        tk.Label(self.canvas1_frame, text="Size: ").pack(side=tk.LEFT)
        self.canvas1_width_input = tk.Entry(self.canvas1_frame, width=3)
        self.canvas1_width_input.pack(side=tk.LEFT)
        self.canvas1_width_input.insert(0, str(self.canvas1_size["width"]))
        tk.Label(self.canvas1_frame, text="x").pack(side=tk.LEFT)
        self.canvas1_height_input = tk.Entry(self.canvas1_frame, width=3)
        self.canvas1_height_input.pack(side=tk.LEFT)
        self.canvas1_height_input.insert(0, str(self.canvas1_size["height"]))
        apply1_btn = tk.Button(self.canvas1_frame, text="Apply", command=lambda: self.apply_size(self.canvas1, self.canvas1_size, self.image1))
        apply1_btn.pack(side=tk.LEFT)
        tk.Label(self.canvas1_frame, text="Name: ").pack(side=tk.LEFT)
        self.canvas1_name_input = tk.Entry(self.canvas1_frame, width=10)
        self.canvas1_name_input.pack(side=tk.LEFT)
        self.canvas1_name_input.insert(0, self.canvas1_size["name"])
        

        self.canvas1 = self.create_canvas(root, 0, self.image1, self.canvas1_size)

        # Canvas 2 with size and name inputs
        self.canvas2_frame = tk.Frame(root)
        self.canvas2_frame.grid(row=0, column=1, padx=10, pady=10)
        tk.Label(self.canvas2_frame, text="Canvas 2").pack()
        tk.Label(self.canvas2_frame, text="Size: ").pack(side=tk.LEFT)
        self.canvas2_width_input = tk.Entry(self.canvas2_frame, width=3)
        self.canvas2_width_input.pack(side=tk.LEFT)
        self.canvas2_width_input.insert(0, str(self.canvas2_size["width"]))
        tk.Label(self.canvas2_frame, text="x").pack(side=tk.LEFT)
        self.canvas2_height_input = tk.Entry(self.canvas2_frame, width=3)
        self.canvas2_height_input.pack(side=tk.LEFT)
        self.canvas2_height_input.insert(0, str(self.canvas2_size["height"]))
        apply2_btn = tk.Button(self.canvas2_frame, text="Apply", command=lambda: self.apply_size(self.canvas2, self.canvas2_size, self.image2))
        apply2_btn.pack(side=tk.LEFT)
        tk.Label(self.canvas2_frame, text="Name: ").pack(side=tk.LEFT)
        self.canvas2_name_input = tk.Entry(self.canvas2_frame, width=10)
        self.canvas2_name_input.pack(side=tk.LEFT)
        self.canvas2_name_input.insert(0, self.canvas2_size["name"])
        

        self.canvas2 = self.create_canvas(root, 1, self.image2, self.canvas2_size)

        # Color palette
        self.create_color_palette(root)

        # Save/Load buttons
        action_frame = tk.Frame(root)
        action_frame.grid(row=2, column=0, columnspan=2)
        save1_btn = tk.Button(action_frame, text="Save Canvas 1", command=lambda: self.save_image(self.image1, self.canvas1_name_input.get()))
        save1_btn.pack(side=tk.LEFT, padx=5)
        save2_btn = tk.Button(action_frame, text="Save Canvas 2", command=lambda: self.save_image(self.image2, self.canvas2_name_input.get()))
        save2_btn.pack(side=tk.LEFT, padx=5)
        load1_btn = tk.Button(action_frame, text="Load Canvas 1", command=lambda: self.load_image(self.image1, self.canvas1, self.canvas1_size))
        load1_btn.pack(side=tk.LEFT, padx=5)
        load2_btn = tk.Button(action_frame, text="Load Canvas 2", command=lambda: self.load_image(self.image2, self.canvas2, self.canvas2_size))
        load2_btn.pack(side=tk.LEFT, padx=5)

        copy_btn = tk.Button(action_frame, text="Copy Canvas 1 to Canvas 2", command=self.copy_canvas)
        copy_btn.pack(side=tk.LEFT, padx=5)


    def create_canvas(self, root, column, image, size):
        canvas = tk.Canvas(root, width=size["width"] * 20, height=size["height"] * 20, bg="white")
        canvas.grid(row=1, column=column, padx=10, pady=10)
        canvas.bind("<Button-1>", lambda event: self.draw_pixel(event.x // 20, event.y // 20, image, canvas, self.current_color))
        self.draw_grid(canvas, size["width"], size["height"])
        return canvas

    def draw_grid(self, canvas, width, height):
        canvas.delete("grid")
        for i in range(width):
            for j in range(height):
                x1, y1 = i * 20, j * 20
                x2, y2 = x1 + 20, y1 + 20
                canvas.create_rectangle(x1, y1, x2, y2, outline="gray", tags="grid")

    def create_color_palette(self, root):
        palette_frame = tk.Frame(root)
        palette_frame.grid(row=3, column=0, columnspan=2)
        for color in self.colors:
            btn = tk.Button(palette_frame, bg=color, width=3, command=lambda c=color: self.set_color(c))
            btn.pack(side=tk.LEFT)
        erase_btn = tk.Button(palette_frame, text="Erase", command=lambda: self.set_color(None))
        erase_btn.pack(side=tk.LEFT)

    def set_color(self, color):
        self.current_color = color

    def draw_pixel(self, x, y, image, canvas, color):
        if 0 <= x < len(image[0]) and 0 <= y < len(image):
            image[y][x] = color
            color = color if color else "white"
            canvas.create_rectangle(x * 20, y * 20, (x + 1) * 20, (y + 1) * 20, fill=color, outline="gray")

    def save_image(self, image, name):
        file_path = os.path.join(self.default_save_path, f"{name}.json")

        print(image)

        with open(file_path, "w") as file:
            json.dump(image, file)
        print(f"Image saved to {file_path}")

    def load_image(self, image, canvas, size):
        name = self.canvas1_name_input.get() if canvas == self.canvas1 else self.canvas2_name_input.get()
        file_path = os.path.join(self.default_save_path, f"{name}.json")
        
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                loaded_image = json.load(file)
            
            # Update the image data and canvas size
            size["width"] = len(loaded_image[0])
            size["height"] = len(loaded_image)
            image[:] = loaded_image
            canvas.config(width=size["width"] * 20, height=size["height"] * 20)
            
            # Redraw the grid and populate the canvas with the loaded image
            self.draw_grid(canvas, size["width"], size["height"])
            for y, row in enumerate(loaded_image):
                for x, color in enumerate(row):
                    if color:
                        self.draw_pixel(x, y, image, canvas, color)
                        canvas.create_rectangle(
                            x * 20, y * 20, (x + 1) * 20, (y + 1) * 20,
                            fill=color, outline="gray"
                        )
            print(f"Image loaded from {file_path}")
        else:
            print(f"No file found at {file_path}")

    def copy_canvas(self):
        # Copy the content of image1 to image2
        self.image2 = [row[:] for row in self.image1]
        self.canvas2_size["width"] = self.canvas1_size["width"]
        self.canvas2_size["height"] = self.canvas1_size["height"]

        # Update canvas2 size and redraw grid
        self.canvas2.config(width=self.canvas2_size["width"] * 20, height=self.canvas2_size["height"] * 20)
        self.draw_grid(self.canvas2, self.canvas2_size["width"], self.canvas2_size["height"])

        # Populate canvas2 with the copied pixels
        for y, row in enumerate(self.image1):
            for x, color in enumerate(row):
                if color:
                    self.draw_pixel(x, y, self.image2, self.canvas2, color)

    def apply_size(self, canvas, size, image):
        width = int(self.canvas1_width_input.get()) if canvas == self.canvas1 else int(self.canvas2_width_input.get())
        height = int(self.canvas1_height_input.get()) if canvas == self.canvas1 else int(self.canvas2_height_input.get())
        size["width"], size["height"] = width, height
        image[:] = self.create_image_data(width, height)
        canvas.config(width=width * 20, height=height * 20)
        self.draw_grid(canvas, width, height)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Pixel Art Tool")
    app = PixelArtTool(root)
    root.mainloop()
