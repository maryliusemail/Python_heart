import random
from math import sin, cos, pi, log
from tkinter import *

CANVAS_WIDTH = 640
CANVAS_HEIGHT = 480
CANVAS_CENTER_X = CANVAS_WIDTH / 2
CANVAS_CENTER_Y = CANVAS_HEIGHT / 2
IMAGE_ENLARGE = 11
HEART_COLOR = "#FF99CC"
MATRIX_COLOR = "#66FF66"
FONT_SIZE = 12
COLUMNS = CANVAS_WIDTH // FONT_SIZE

def center_window(root, width, height):
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) // 2, (screenheight - height) // 2)
    root.geometry(size)

def heart_function(t, shrink_ratio: float = IMAGE_ENLARGE):
    x = 16 * (sin(t) ** 3)
    y = -(13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))
    x *= shrink_ratio
    y *= shrink_ratio
    x += CANVAS_CENTER_X
    y += CANVAS_CENTER_Y
    return int(x), int(y)

def scatter_inside(x, y, beta=0.15):
    ratio_x = - beta * log(random.random())
    ratio_y = - beta * log(random.random())
    dx = ratio_x * (x - CANVAS_CENTER_X)
    dy = ratio_y * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy

def shrink(x, y, ratio):
    force = -1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.6)
    dx = ratio * force * (x - CANVAS_CENTER_X)
    dy = ratio * force * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy

def curve(p):
    return 2 * (2 * sin(4 * p)) / (2 * pi)

class Heart:
    def __init__(self, generate_frame=20):
        self._points = set()
        self._edge_diffusion_points = set()
        self._center_diffusion_points = set()
        self.all_points = {}
        self.build(2000)
        self.random_halo = 1000
        self.generate_frame = generate_frame
        for frame in range(generate_frame):
            self.calc(frame)

    def build(self, number):
        for _ in range(number):
            t = random.uniform(0, 2 * pi)
            x, y = heart_function(t)
            self._points.add((x, y))

        for _x, _y in list(self._points):
            for _ in range(3):
                x, y = scatter_inside(_x, _y, 0.05)
                self._edge_diffusion_points.add((x, y))

        point_list = list(self._points)
        for _ in range(4000):
            x, y = random.choice(point_list)
            x, y = scatter_inside(x, y, 0.17)
            self._center_diffusion_points.add((x, y))

    @staticmethod
    def calc_position(x, y, ratio):
        force = 1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.520)
        dx = ratio * force * (x - CANVAS_CENTER_X) + random.randint(-1, 1)
        dy = ratio * force * (y - CANVAS_CENTER_Y) + random.randint(-1, 1)
        return x - dx, y - dy

    def calc(self, generate_frame):
        ratio = 10 * curve(generate_frame / 10 * pi)
        halo_radius = int(4 + 6 * (1 + curve(generate_frame / 10 * pi)))
        halo_number = int(3000 + 4000 * abs(curve(generate_frame / 10 * pi) ** 2))
        all_points = []

        for _ in range(halo_number):
            t = random.uniform(0, 2 * pi)
            x, y = heart_function(t, shrink_ratio=11.6)
            x, y = shrink(x, y, halo_radius)
            x += random.randint(-14, 14)
            y += random.randint(-14, 14)
            size = random.choice((1, 2, 2))
            all_points.append((x, y, size))

        for x, y in self._points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 3)
            all_points.append((x, y, size))

        for x, y in self._edge_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))

        for x, y in self._center_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))

        self.all_points[generate_frame] = all_points

    def render(self, render_canvas: Canvas, render_frame):
        for x, y, size in self.all_points[render_frame % self.generate_frame]:
            render_canvas.create_rectangle(x, y, x + size, y + size, width=0, fill=HEART_COLOR)





# Matrix rain effect
class MatrixRain:
    def __init__(self, canvas: Canvas):
        self.canvas = canvas
        self.columns = COLUMNS
        self.font_size = FONT_SIZE
        self.drops = [random.randint(-CANVAS_HEIGHT // FONT_SIZE, 0) for _ in range(self.columns)]
        self.colors = ["#FF99CC", "#FF3366"]  # pink and red

    def update(self):
        self.canvas.delete("matrix")
        for i in range(self.columns):
            word = "LOVE"
            color = random.choice(self.colors)
            x = i * self.font_size
            y = self.drops[i] * self.font_size

            # Make sure there's room to draw the full word vertically
            if y < CANVAS_HEIGHT - self.font_size * 4:
                for j, letter in enumerate(word):
                    self.canvas.create_text(
                        x, y + j * self.font_size,
                        text=letter,
                        fill=color,
                        font=("Courier", self.font_size, "bold"),
                        tags="matrix"
                    )

            self.drops[i] += 1
            if self.drops[i] * self.font_size > CANVAS_HEIGHT or random.random() > 0.975:
                self.drops[i] = random.randint(-10, 0)
def fade_in_to_heart(canvas: Canvas, heart: Heart, matrix: MatrixRain, root: Tk):
    steps = 30           # Total animation frames
    delay = 60           # ms per frame
    overlay_tag = "pulse_heart"

    def pulse(step=0):
        canvas.delete(overlay_tag)
        if step <= steps:
            from math import sin, pi

            # Pulse size: smooth grow and shrink
            pulse_scale = 1 + 0.3 * sin((step / steps) * pi)
            size = int(400 * pulse_scale)

            # Fade in (first half), fade out (second half)
            if step <= steps // 2:
                fade_ratio = step / (steps // 2)
            else:
                fade_ratio = (steps - step) / (steps // 2)

            # Simulated alpha fade: darker pink → brighter pink → darker pink
            r = int(100 + (255 - 100) * fade_ratio)
            g = int(50 + (105 - 50) * fade_ratio)
            b = int(80 + (180 - 80) * fade_ratio)
            heart_color = f"#{r:02x}{g:02x}{b:02x}"

            # Always black background
            canvas.create_rectangle(
                0, 0, CANVAS_WIDTH, CANVAS_HEIGHT,
                fill="black",
                outline="",
                tags=overlay_tag
            )

            # Heart
            canvas.create_text(
                CANVAS_CENTER_X, CANVAS_CENTER_Y,
                text="❤",
                fill=heart_color,
                font=("Helvetica", size, "bold"),
                tags=overlay_tag
            )

            # Caption stays the same
            canvas.create_text(
                CANVAS_CENTER_X, CANVAS_CENTER_Y,
                text="Hi MOM",
                fill="#FF99CC",
                font=("Helvetica", 50, "italic"),
                tags=overlay_tag
            )

            canvas.update()
            canvas.after(delay, pulse, step + 1)
        else:
            # When done, clear and go to main animation
            canvas.delete(overlay_tag)
            canvas.update()
            canvas.after(300, lambda: draw(root, canvas, heart, matrix))

    # Initial black screen
    canvas.create_rectangle(
        0, 0, CANVAS_WIDTH, CANVAS_HEIGHT,
        fill="black",
        outline="",
        tags=overlay_tag
    )
    canvas.update()
    canvas.after(300, pulse)



def draw(main: Tk, render_canvas: Canvas, heart: Heart, matrix: MatrixRain, frame=0):
    if frame == 0:
        Label(main, text="妈妈节日快乐!!\n - Mary", bg="black", fg="#FF99CC", font="Helvetica 20 bold").place(
            relx=.5, rely=.5, anchor=CENTER)

    render_canvas.delete("all")
    matrix.update()
    heart.render(render_canvas, frame)
    main.after(50, draw, main, render_canvas, heart, matrix, frame + 1)

def show_countdown(canvas: Canvas, callback, countdown=3):
    def animate_count(number, step=0):
        canvas.delete("countdown")
        if step <= 10:
            scale = 1 + step * 0.1
            size = int(72 * scale)
            alpha = int(255 * (1 - step / 10))
            color = "#FF%02xCC" % alpha  # pink to white fade

            canvas.create_text(
                CANVAS_CENTER_X, CANVAS_CENTER_Y,
                text=str(number),
                fill=color,
                font=("Helvetica", size, "bold"),
                tags="countdown"
            )
            canvas.update()
            canvas.after(50, animate_count, number, step + 1)
        else:
            if number > 0:
                canvas.after(300, lambda: show_countdown(canvas, callback, number - 1))

            else:
                canvas.after(500, callback)
    animate_count(countdown)
    

if __name__ == '__main__':
    root = Tk()
    root.title("Happy Mother's Day!")
    center_window(root, CANVAS_WIDTH, CANVAS_HEIGHT)

    canvas = Canvas(root, bg='black', height=CANVAS_HEIGHT, width=CANVAS_WIDTH)
    canvas.pack()

    heart = Heart()
    matrix = MatrixRain(canvas)

    def start_animation():
        draw(root, canvas, heart, matrix)
        Label(root, text="妈妈节日快乐!!\n - Mary", bg="black", fg="#FF99CC", font="Helvetica 20 bold").place(
            relx=.2, rely=.2, anchor=CENTER)

    show_countdown(canvas, lambda: fade_in_to_heart(canvas, heart, matrix, root))


    root.mainloop()
